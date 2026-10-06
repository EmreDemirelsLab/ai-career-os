from datetime import UTC, datetime

from career_os.api import create_app
from career_os.career_pack import prepare_pack
from fastapi.testclient import TestClient

TOKEN = "synthetic-career-pack-token-at-least-32"


def opportunity():
    return dict(
        id="example",
        title="AI Engineer",
        company="Synthetic",
        source_url="https://example.com/job",
        observed_on="2026-10-06",
        skills=["Python", "SQL"],
        review_notes="Synthetic only",
        requirements=[
            dict(kind="english", value="B2", mandatory=True, evidence_span="English B2 required")
        ],
    )


def test_pack_uses_only_relevant_user_evidence_and_keeps_unknowns():
    job = opportunity()
    records = [
        dict(
            skill="Python",
            dimension="implementation",
            artifact_url="https://example.com/code",
            assistance="generated",
            verifier="self_report",
            notes="User-authored project note",
        ),
        dict(
            skill="Git",
            dimension="implementation",
            artifact_url="https://example.com/unrelated",
            assistance="independent",
            verifier="self_report",
            notes="Unrelated note",
        ),
    ]
    pack = prepare_pack(job, None, records)
    assert pack["eligibility"]["eligibility"] == "UNCERTAIN"
    assert pack["unlinked_skills"] == ["SQL"]
    assert pack["sent"] is False
    assert pack["evidence_count"] == 1
    assert "User-authored project note" in pack["text"]
    assert "Assistance: generated" in pack["text"]
    assert "Unrelated note" not in pack["text"]
    assert "NOT INDEPENDENTLY VERIFIED" in pack["text"]
    assert prepare_pack(job, None, [])["evidence_count"] == 0


def test_pack_auth_missing_opportunity_and_personal_deletion(engine):
    with TestClient(create_app(engine, TOKEN)) as c:
        assert c.get("/workspace/career-pack/example").status_code == 401
        c.headers["Authorization"] = f"Bearer {TOKEN}"
        assert c.get("/workspace/career-pack/example").status_code == 404
        job = opportunity()
        del job["id"]
        job["observed_on"] = datetime.now(UTC).date().isoformat()
        job["requirements"].append(
            dict(kind="degree", value="yes", mandatory=False, evidence_span="Degree preferred")
        )
        created = c.post("/workspace/opportunities", json=job)
        assert created.status_code == 201
        identifier = created.json()["id"]
        pack = c.get(f"/workspace/career-pack/{identifier}")
        assert pack.status_code == 200
        assert pack.json()["eligibility"]["checks"][0]["status"] == "UNCERTAIN"
        assert len(pack.json()["eligibility"]["checks"]) == 1
        assert (
            c.delete(
                "/workspace", headers={"X-Confirm-Delete": "delete-personal-workspace"}
            ).status_code
            == 204
        )
        assert c.get(f"/workspace/career-pack/{identifier}").status_code == 404
