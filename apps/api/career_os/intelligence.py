from datetime import UTC, datetime
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import Field
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from career_os.ai_gateway import PROMPT_VERSION, AISettings, generate_feedback
from career_os.auth import authorize
from career_os.contracts import digest
from career_os.ingestion import insert_for
from career_os.intelligence_models import AIBudget, AIRequest, EngineRecord
from career_os.market import GRAPH, adaptive_plan, market_snapshot
from career_os.models import Source
from career_os.workspace import CURRICULUM, all_rows, latest_profile, serialize, stamp
from career_os.workspace_contracts import Contract, Short
from career_os.workspace_models import EvidenceRecord, InterviewRecord, LearningAttempt

router = APIRouter(prefix="/workspace/intelligence", dependencies=[Depends(authorize)])


class MarketInput(Contract):
    source_ids: Annotated[list[Short], Field(min_length=1, max_length=30)]
    include_demo: bool = False


class PlanInput(Contract):
    market_snapshot_id: Short
    target_skills: Annotated[list[Short], Field(min_length=1, max_length=30)]


class FeedbackInput(Contract):
    target_type: Literal["learning", "interview"]
    target_id: Short
    request_key: Annotated[str, Field(min_length=1, max_length=100)]
    consent_to_send: Literal[True]


@router.get("")
def overview(request: Request) -> dict[str, Any]:
    config = AISettings()
    with Session(request.app.state.engine) as session:
        budget = session.get(AIBudget, datetime.now(UTC).date().isoformat())
        return dict(
            records=[serialize(x) for x in all_rows(session, EngineRecord)],
            feedback=[{**serialize(x), "status": x.status} for x in all_rows(session, AIRequest)],
            graph=GRAPH,
            sources=[
                dict(
                    id=s.id,
                    name=s.name,
                    enabled=s.enabled,
                    policy_status=s.policy_status,
                    method=s.collection_method,
                )
                for s in session.scalars(select(Source).order_by(Source.id))
            ],
            ai=dict(
                configured=config.ready(),
                model=config.career_ai_model or None,
                daily_limit=config.career_ai_daily_calls,
                used_today=budget.used if budget else 0,
            ),
        )


@router.post("/market", status_code=201)
def build_market(body: MarketInput, request: Request) -> dict[str, Any]:
    with Session(request.app.state.engine) as session, session.begin():
        try:
            data = market_snapshot(session, sorted(set(body.source_ids)), body.include_demo)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from None
        if not data["sample_size"]:
            raise HTTPException(409, "No retained observations for this source selection")
        row = EngineRecord(**stamp(), kind="market", data={"kind": "market", **data})
        session.add(row)
        return serialize(row)


@router.post("/plans", status_code=201)
def build_plan(body: PlanInput, request: Request) -> dict[str, Any]:
    with Session(request.app.state.engine) as session, session.begin():
        market = session.get(EngineRecord, body.market_snapshot_id)
        profile = latest_profile(session)
        if not market or market.kind != "market":
            raise HTTPException(404, "Market snapshot not found")
        if not profile:
            raise HTTPException(409, "Create a profile first")
        evidence = [serialize(x) for x in all_rows(session, EvidenceRecord)]
        try:
            plan = adaptive_plan(market.data, evidence, body.target_skills)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from None
        row = EngineRecord(
            **stamp(),
            kind="adaptive_plan",
            data={
                **plan,
                "kind": "adaptive_plan",
                "market_snapshot_id": market.id,
                "profile_snapshot_id": profile.id,
                "evidence_ids": [x["id"] for x in evidence],
                "weekly_hours": profile.data["weekly_hours"],
                "synthetic_market": market.data["synthetic"],
            },
        )
        session.add(row)
        return serialize(row)


def feedback_payload(session: Session, body: FeedbackInput) -> dict[str, Any]:
    if body.target_type == "learning":
        attempt = session.get(LearningAttempt, body.target_id)
        if not attempt:
            raise HTTPException(404, "Learning attempt not found")
        unit = next(x for x in CURRICULUM["units"] if x["week"] == attempt.week)
        payload = dict(
            task="tutor",
            topic=unit["title"],
            question=unit["english_question"],
            concept_answer=attempt.data["concept_answer"],
            english_answer=attempt.data["english_answer"],
        )
    else:
        interview = session.get(InterviewRecord, body.target_id)
        if not interview:
            raise HTTPException(404, "Interview response not found")
        payload = dict(
            task="interview", question=interview.data["question"], answer=interview.data["answer"]
        )
    return payload


@router.post("/feedback")
def feedback(body: FeedbackInput, request: Request) -> dict[str, Any]:
    config = AISettings()
    if not config.ready():
        raise HTTPException(503, "AI disabled: configure model, provider key and daily call budget")
    engine = request.app.state.engine
    with Session(engine) as session, session.begin():
        payload = feedback_payload(session, body)
        identity = digest(
            dict(
                payload=payload,
                target_type=body.target_type,
                target_id=body.target_id,
                model=config.career_ai_model,
                prompt=PROMPT_VERSION,
            )
        )
        values = stamp()
        inserted = session.scalar(
            insert_for(engine, AIRequest)
            .values(
                **values,
                request_key=body.request_key,
                input_hash=identity,
                status="RUNNING",
                data=dict(
                    target_type=body.target_type,
                    target_id=body.target_id,
                    model=config.career_ai_model,
                    prompt_version=PROMPT_VERSION,
                    assessment_status="ai_draft_requires_human_review",
                ),
            )
            .on_conflict_do_nothing(index_elements=["request_key"])
            .returning(AIRequest.id)
        )
        if inserted is None:
            previous = session.scalar(
                select(AIRequest).where(AIRequest.request_key == body.request_key)
            )
            assert previous is not None
            if previous.input_hash != identity:
                raise HTTPException(409, "Request key already used for different input")
            return {**serialize(previous), "status": previous.status}
        day = datetime.now(UTC).date().isoformat()
        session.execute(
            insert_for(engine, AIBudget)
            .values(day=day, used=0)
            .on_conflict_do_nothing(index_elements=["day"])
        )
        reserved = session.scalar(
            update(AIBudget)
            .where(AIBudget.day == day, AIBudget.used < config.career_ai_daily_calls)
            .values(used=AIBudget.used + 1)
            .returning(AIBudget.used)
        )
        if reserved is None:
            raise HTTPException(429, "Daily call budget exhausted")
    # No automatic retries: network failure may still have incurred provider cost.
    try:
        result = generate_feedback(config, payload)
        status = "COMPLETED"
    except Exception:
        result = {"error_code": "feedback_failed_or_invalid", "prompt_version": PROMPT_VERSION}
        status = "FAILED"
    with Session(engine) as session, session.begin():
        row = session.get(AIRequest, inserted)
        if row is None:
            raise HTTPException(410, "Workspace deleted while request was running")
        row.status = status
        row.data = {**row.data, **result}
        return {**serialize(row), "status": row.status}
