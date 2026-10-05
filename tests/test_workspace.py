from datetime import UTC, datetime, timedelta
from pathlib import Path

from career_os.api import create_app
from career_os.workspace import CURRICULUM, SKILLS, evidence_fit
from career_os.workspace_models import LearningAttempt
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

TOKEN = "test-only-token-with-at-least-32-characters"
PROFILE = dict(
    name="Synthetic learner",
    target_role="AI_ENGINEER",
    weekly_hours=12,
    english="B1",
    german="unknown",
    location="Test city",
)


def test_auth_disabled_and_required(engine):
    with TestClient(create_app(engine=engine, api_token="")) as c:
        assert c.get("/workspace").status_code == 503
    with TestClient(create_app(engine=engine, api_token=TOKEN)) as c:
        assert c.get("/workspace").status_code == 401
        assert c.get("/workspace", headers={"Authorization": "Bearer wrong"}).status_code == 401


def test_workspace_lifecycle(engine):
    with TestClient(
        create_app(engine=engine, api_token=TOKEN), headers={"Authorization": f"Bearer {TOKEN}"}
    ) as c:
        assert c.post("/workspace/roadmaps").status_code == 409
        first = c.post("/workspace/profile", json=PROFILE).json()
        roadmap = c.post("/workspace/roadmaps").json()
        assert roadmap["learner_snapshot_id"] == first["id"]
        assert len(roadmap["units"]) == 24
        c.post("/workspace/profile", json={**PROFILE, "weekly_hours": 20})
        attempt = c.post(
            "/workspace/learning",
            json=dict(week=1, concept_answer="A concept", english_answer="An explanation"),
        ).json()
        assert attempt["assessment_status"] == "submitted_unassessed"
        review = dict(attempt_id=attempt["id"], interval=3, notes="Independent recall")
        assert c.post("/workspace/reviews", json=review).status_code == 409
        with Session(engine) as session, session.begin():
            row = session.get(LearningAttempt, attempt["id"])
            row.created_at = datetime.now(UTC) - timedelta(days=4)
        assert c.post("/workspace/reviews", json=review).status_code == 201
        assert c.post("/workspace/reviews", json=review).status_code == 409
        assert (
            c.post("/workspace/interviews", json=dict(question_id="999", answer="Test")).status_code
            == 422
        )
        assert (
            c.post("/workspace/interviews", json=dict(question_id="1", answer="Test")).json()[
                "assessment_status"
            ]
            == "unassessed"
        )
        evidence = dict(
            skill=sorted(SKILLS)[0],
            dimension="implementation",
            artifact_url="https://example.com/project",
            notes="Synthetic example",
            assistance="generated",
            verifier="external_review",
        )
        assert c.post("/workspace/evidence", json=evidence).status_code == 422
        assert (
            c.post("/workspace/evidence", json={**evidence, "verifier": "self_report"}).status_code
            == 201
        )
        opportunity = c.post(
            "/workspace/opportunities",
            json=dict(
                title="Synthetic role",
                company="Example",
                source_url="https://example.com/job",
                observed_on="2026-01-01",
                skills=[sorted(SKILLS)[0]],
                requirements=[],
                review_notes="Synthetic",
            ),
        ).json()
        assert (
            c.post(
                "/workspace/applications", json=dict(opportunity_id="missing", cv_version="v1")
            ).status_code
            == 404
        )
        app = c.post(
            "/workspace/applications", json=dict(opportunity_id=opportunity["id"], cv_version="v1")
        ).json()
        assert (
            c.post(
                f"/workspace/applications/{app['id']}/events", json=dict(stage="applied")
            ).status_code
            == 201
        )
        exported = c.get("/workspace/export").json()
        assert len(exported["profile_history"]) == 2
        assert exported["roadmaps"][0]["weekly_hours"] == 12
        assert len(exported["review_queue"]) == 3
        assert len(exported["application_events"]) == 2
        assert exported["opportunities"][0]["fit"]["eligibility"] == "UNCERTAIN"
        assert TOKEN not in str(exported)
        assert c.delete("/workspace").status_code == 400
        assert c.get("/workspace").json()["profile_versions"] == 2
        assert (
            c.delete(
                "/workspace", headers={"X-Confirm-Delete": "delete-personal-workspace"}
            ).status_code
            == 204
        )
        assert c.get("/workspace").json()["profile"] is None


def test_eligibility_does_not_infer_unknowns():
    requirement = dict(
        kind="german", value="B2", mandatory=True, evidence_span="German B2 required"
    )
    job = dict(requirements=[requirement], skills=[])
    assert evidence_fit(job, PROFILE, [])["eligibility"] == "UNCERTAIN"
    assert evidence_fit(job, {**PROFILE, "german": "A1"}, [])["eligibility"] == "FAIL"
    assert evidence_fit(job, {**PROFILE, "german": "C1"}, [])["eligibility"] == "PASS"
    job["requirements"][0]["mandatory"] = False
    assert evidence_fit(job, {**PROFILE, "german": "A1"}, [])["eligibility"] == "UNCERTAIN"


def test_curriculum_and_taxonomy_are_consistent():
    assert [x["week"] for x in CURRICULUM["units"]] == list(range(1, 25))
    assert all(x["skill"] in SKILLS for x in CURRICULUM["units"])
    assert (
        Path("apps/api/career_os/skill_taxonomy.json").read_bytes()
        == Path("seed/skill_taxonomy_v0.1.json").read_bytes()
    )
