import hmac
import json
from datetime import UTC, datetime, timedelta
from importlib.resources import files
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from career_os.workspace_contracts import (
    Application,
    Evidence,
    InterviewSubmission,
    LearningSubmission,
    Opportunity,
    Profile,
    ReviewSubmission,
    Stage,
)
from career_os.workspace_models import (
    ApplicationEvent,
    ApplicationRecord,
    EvidenceRecord,
    InterviewRecord,
    LearnerSnapshot,
    LearningAttempt,
    OpportunityRecord,
    RecallReview,
    Record,
    RoadmapRecord,
)

CURRICULUM: dict[str, Any] = json.loads(files("career_os").joinpath("curriculum.json").read_text())
TAXONOMY: dict[str, Any] = json.loads(
    files("career_os").joinpath("skill_taxonomy.json").read_text()
)
SKILLS = {name for names in TAXONOMY["categories"].values() for name in names}
LEVELS = {level: i for i, level in enumerate(["none", "A1", "A2", "B1", "B2", "C1", "C2"])}


def authorize(request: Request, authorization: str | None = Header(default=None)) -> None:
    expected: str = request.app.state.api_token
    if len(expected) < 32:
        raise HTTPException(503, "Workspace is disabled until CAREER_API_TOKEN is configured")
    supplied = (authorization or "").removeprefix("Bearer ")
    if (
        not authorization
        or not authorization.startswith("Bearer ")
        or not hmac.compare_digest(expected.encode(), supplied.encode())
    ):
        raise HTTPException(401, "Authentication required")


router = APIRouter(prefix="/workspace", dependencies=[Depends(authorize)])


def stamp() -> dict[str, Any]:
    return {"id": str(uuid4()), "created_at": datetime.now(UTC)}


def serialize(row: Record) -> dict[str, Any]:
    return {"id": row.id, "created_at": row.created_at.isoformat(), **row.data}


def all_rows(session: Session, model: Any) -> list[Any]:
    return list(session.scalars(select(model).order_by(model.created_at, model.id)))


def latest_profile(session: Session) -> LearnerSnapshot | None:
    return session.scalar(
        select(LearnerSnapshot)
        .order_by(LearnerSnapshot.created_at.desc(), LearnerSnapshot.id.desc())
        .limit(1)
    )


def evidence_fit(
    opportunity: dict[str, Any], profile: dict[str, Any] | None, evidence: list[dict[str, Any]]
) -> dict[str, Any]:
    checks: list[dict[str, str]] = []
    profile = profile or {}
    for requirement in opportunity["requirements"]:
        if not requirement["mandatory"]:
            continue
        kind, target = requirement["kind"], requirement["value"]
        state = "UNCERTAIN"
        actual = profile.get(
            {"degree": "relevant_degree", "experience": "professional_years"}.get(kind, kind)
        )
        if kind in {"english", "german"} and actual in LEVELS and target in LEVELS:
            state = "PASS" if LEVELS[actual] >= LEVELS[target] else "FAIL"
        elif (
            kind in {"degree", "work_authorization"} and target == "yes" and actual in {"yes", "no"}
        ):
            state = "PASS" if actual == "yes" else "FAIL"
        elif kind == "experience" and actual is not None and target.isdigit():
            state = "PASS" if int(actual) >= int(target) else "FAIL"
        # Location and relocation need human review, not text equality.
        checks.append(
            {"kind": kind, "status": state, "evidence_span": requirement["evidence_span"]}
        )
    status = "FAIL" if any(x["status"] == "FAIL" for x in checks) else "UNCERTAIN"
    if checks and all(x["status"] == "PASS" for x in checks):
        status = "PASS"
    independent = {
        x["skill"]
        for x in evidence
        if x["verifier"] == "external_review"
        and x["assistance"] == "independent"
        and x.get("review_reference")
    }
    return {
        "eligibility": status,
        "checks": checks,
        "evidence_linked_skills": sorted(set(opportunity["skills"]) & independent),
        "unverified_skills": sorted(set(opportunity["skills"]) - independent),
        "policy_version": "manual-observation/1",
        "notice": "Based on self-entered profile and reviewer notes; "
        "not a verified hiring decision or mastery score.",
    }


@router.get("")
def workspace(request: Request) -> dict[str, Any]:
    with Session(request.app.state.engine) as session:
        profile = latest_profile(session)
        evidence = [serialize(x) for x in all_rows(session, EvidenceRecord)]
        opportunities = [serialize(x) for x in all_rows(session, OpportunityRecord)]
        attempts = all_rows(session, LearningAttempt)
        reviews = all_rows(session, RecallReview)
        covered = {(x.attempt_id, x.interval) for x in reviews}
        review_queue = []
        for attempt in attempts:
            created = (
                attempt.created_at.replace(tzinfo=UTC)
                if attempt.created_at.tzinfo is None
                else attempt.created_at
            )
            for interval in [3, 7, 14, 30]:
                if (attempt.id, interval) not in covered:
                    review_queue.append(
                        {
                            "attempt_id": attempt.id,
                            "week": attempt.week,
                            "interval": interval,
                            "due_at": (created + timedelta(days=interval)).isoformat(),
                        }
                    )
        return {
            "profile": serialize(profile) if profile else None,
            "profile_versions": len(all_rows(session, LearnerSnapshot)),
            "evidence": evidence,
            "roadmaps": [serialize(x) for x in all_rows(session, RoadmapRecord)],
            "attempts": [serialize(x) for x in attempts],
            "reviews": [serialize(x) for x in reviews],
            "review_queue": sorted(review_queue, key=lambda x: str(x["due_at"])),
            "interviews": [serialize(x) for x in all_rows(session, InterviewRecord)],
            "opportunities": [
                {**x, "fit": evidence_fit(x, profile.data if profile else None, evidence)}
                for x in opportunities
            ],
            "applications": [serialize(x) for x in all_rows(session, ApplicationRecord)],
            "application_events": [serialize(x) for x in all_rows(session, ApplicationEvent)],
            "curriculum": CURRICULUM,
            "skills": sorted(SKILLS),
            "integrations": {
                "live_market": "not_configured",
                "llm_tutor": "not_configured",
                "deployment": "local_personal_workspace",
            },
        }


@router.post("/profile", status_code=201)
def save_profile(body: Profile, request: Request) -> dict[str, Any]:
    with Session(request.app.state.engine) as session, session.begin():
        row = LearnerSnapshot(**stamp(), data=body.model_dump(mode="json"))
        session.add(row)
        return serialize(row)


@router.post("/evidence", status_code=201)
def save_evidence(body: Evidence, request: Request) -> dict[str, Any]:
    if body.skill not in SKILLS:
        raise HTTPException(422, "Unknown canonical skill")
    if body.verifier == "external_review" and body.review_reference is None:
        raise HTTPException(422, "An external review needs a review reference")
    with Session(request.app.state.engine) as session, session.begin():
        row = EvidenceRecord(
            **stamp(),
            skill=body.skill,
            data={
                **body.model_dump(mode="json"),
                "taxonomy_version": TAXONOMY["version"],
                "verification_status": "user_entered_not_independently_verified",
            },
        )
        session.add(row)
        return serialize(row)


@router.post("/roadmaps", status_code=201)
def save_roadmap(request: Request) -> dict[str, Any]:
    with Session(request.app.state.engine) as session, session.begin():
        profile = latest_profile(session)
        if profile is None:
            raise HTTPException(409, "Create a profile first")
        row = RoadmapRecord(
            **stamp(),
            learner_snapshot_id=profile.id,
            data={
                "learner_snapshot_id": profile.id,
                "curriculum_version": CURRICULUM["version"],
                "taxonomy_version": TAXONOMY["version"],
                "policy_version": "baseline/1",
                "market_snapshot_id": None,
                "weekly_hours": profile.data["weekly_hours"],
                "units": CURRICULUM["units"],
                "notice": "Baseline sequence, not market-adaptive. Hours are your capacity, "
                "not estimated task durations. Submissions do not certify mastery.",
            },
        )
        session.add(row)
        return serialize(row)


@router.post("/learning", status_code=201)
def save_learning(body: LearningSubmission, request: Request) -> dict[str, Any]:
    with Session(request.app.state.engine) as session, session.begin():
        row = LearningAttempt(
            **stamp(),
            week=body.week,
            data={
                **body.model_dump(mode="json"),
                "curriculum_version": CURRICULUM["version"],
                "assessment_status": "submitted_unassessed",
            },
        )
        session.add(row)
        return serialize(row)


@router.post("/reviews", status_code=201)
def save_review(body: ReviewSubmission, request: Request) -> dict[str, Any]:
    with Session(request.app.state.engine) as session, session.begin():
        attempt = session.get(LearningAttempt, body.attempt_id)
        if attempt is None:
            raise HTTPException(404, "Attempt not found")
        # Lock the parent so concurrent review submissions have a single winner on PostgreSQL.
        session.execute(
            select(LearningAttempt).where(LearningAttempt.id == body.attempt_id).with_for_update()
        )
        old = session.scalar(
            select(RecallReview).where(
                RecallReview.attempt_id == body.attempt_id, RecallReview.interval == body.interval
            )
        )
        if old:
            raise HTTPException(409, "Review already recorded")
        created = (
            attempt.created_at.replace(tzinfo=UTC)
            if attempt.created_at.tzinfo is None
            else attempt.created_at
        )
        if datetime.now(UTC) < created + timedelta(days=body.interval):
            raise HTTPException(409, "Review is not due yet")
        row = RecallReview(
            **stamp(),
            attempt_id=body.attempt_id,
            interval=body.interval,
            data=body.model_dump(mode="json"),
        )
        session.add(row)
        return serialize(row)


@router.post("/interviews", status_code=201)
def save_interview(body: InterviewSubmission, request: Request) -> dict[str, Any]:
    questions = {str(x["week"]): x["english_question"] for x in CURRICULUM["units"]}
    if body.question_id not in questions:
        raise HTTPException(422, "Unknown question")
    with Session(request.app.state.engine) as session, session.begin():
        row = InterviewRecord(
            **stamp(),
            data={
                **body.model_dump(mode="json"),
                "question": questions[body.question_id],
                "assessment_status": "unassessed",
                "rubric_version": "rehearsal/1",
                "technical_rubric": ["correctness", "evidence", "tradeoffs", "limitations"],
                "english_rubric": ["clarity", "structure", "terminology"],
            },
        )
        session.add(row)
        return serialize(row)


@router.post("/opportunities", status_code=201)
def save_opportunity(body: Opportunity, request: Request) -> dict[str, Any]:
    if not set(body.skills) <= SKILLS:
        raise HTTPException(422, "Unknown canonical skills")
    if body.observed_on > datetime.now(UTC).date():
        raise HTTPException(422, "Observation date cannot be in the future")
    with Session(request.app.state.engine) as session, session.begin():
        row = OpportunityRecord(
            **stamp(),
            data={
                **body.model_dump(mode="json"),
                "provenance": "manual_reviewer_observation",
                "taxonomy_version": TAXONOMY["version"],
            },
        )
        session.add(row)
        return serialize(row)


@router.post("/applications", status_code=201)
def save_application(body: Application, request: Request) -> dict[str, Any]:
    with Session(request.app.state.engine) as session, session.begin():
        if session.get(OpportunityRecord, body.opportunity_id) is None:
            raise HTTPException(404, "Opportunity not found")
        row = ApplicationRecord(
            **stamp(), opportunity_id=body.opportunity_id, data=body.model_dump(mode="json")
        )
        session.add(row)
        session.flush()
        session.add(
            ApplicationEvent(
                **stamp(),
                application_id=row.id,
                data={"application_id": row.id, "stage": "saved", "notes": ""},
            )
        )
        return serialize(row)


@router.post("/applications/{application_id}/events", status_code=201)
def add_application_event(application_id: str, body: Stage, request: Request) -> dict[str, Any]:
    with Session(request.app.state.engine) as session, session.begin():
        if session.get(ApplicationRecord, application_id) is None:
            raise HTTPException(404, "Application not found")
        row = ApplicationEvent(
            **stamp(),
            application_id=application_id,
            data={"application_id": application_id, **body.model_dump(mode="json")},
        )
        session.add(row)
        return serialize(row)


@router.get("/export")
def export_workspace(request: Request) -> dict[str, Any]:
    result = workspace(request)
    with Session(request.app.state.engine) as session:
        result["profile_history"] = [serialize(x) for x in all_rows(session, LearnerSnapshot)]
    return {"export_version": "1", "exported_at": datetime.now(UTC).isoformat(), **result}


@router.delete("", status_code=204)
def delete_workspace(request: Request) -> None:
    if request.headers.get("X-Confirm-Delete") != "delete-personal-workspace":
        raise HTTPException(400, "Explicit deletion confirmation required")
    with Session(request.app.state.engine) as session, session.begin():
        for model in [
            ApplicationEvent,
            ApplicationRecord,
            OpportunityRecord,
            RecallReview,
            LearningAttempt,
            InterviewRecord,
            RoadmapRecord,
            EvidenceRecord,
            LearnerSnapshot,
        ]:
            session.execute(delete(model))
