import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from career_os.api import create_app
from career_os.contracts import FixtureAdapter
from career_os.greenhouse import GreenhouseAdapter, collect_greenhouse
from career_os.ingestion import ingest
from career_os.intelligence_models import AIBudget
from career_os.market import adaptive_plan, extract_mentions, validate_graph
from career_os.models import Source
from career_os.network import bounded_json
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

TOKEN = "test-only-intelligence-key-at-least-32-characters"


def test_mentions_are_spanned_not_mandatory():
    text = "No Python required. Postgres preferred. K8s, SQL. Pythonic is not Python."
    mentions = extract_mentions(text)
    assert {x["skill"] for x in mentions} == {"Python", "PostgreSQL", "Kubernetes", "SQL"}
    assert all(text[x["start"] : x["end"]] == x["span"] for x in mentions)
    assert all(x["requirement"] == "unknown" for x in mentions)
    assert not extract_mentions("Pythonic PostgreSQLish")


def test_graph_prerequisites_override_demand():
    validate_graph()
    p = adaptive_plan({"skill_counts": {"RAG": 100}}, [], ["RAG"])
    skills = [x["skill"] for x in p["sequence"]]
    assert skills.index("Python") < skills.index("PyTorch") < skills.index("RAG")
    assert p == adaptive_plan({"skill_counts": {"RAG": 100}}, [], ["RAG"])
    with pytest.raises(ValueError):
        adaptive_plan({"skill_counts": {}}, [], ["invented"])


def test_market_and_plan_provenance(engine):
    records = json.loads(Path("tests/fixtures/jobs.json").read_text())
    ingest(engine, "DEMO", "snapshot", FixtureAdapter(records))
    with TestClient(
        create_app(engine=engine, api_token=TOKEN), headers={"Authorization": f"Bearer {TOKEN}"}
    ) as c:
        assert (
            c.post("/workspace/intelligence/market", json={"source_ids": ["DEMO"]}).status_code
            == 422
        )
        m = c.post(
            "/workspace/intelligence/market", json={"source_ids": ["DEMO"], "include_demo": True}
        ).json()
        assert m["sample_size"] == 2 and m["synthetic"]
        assert m["skill_counts"]["Python"] == 1
        assert m["jobs"][0]["content_hash"]
        body = {"market_snapshot_id": m["id"], "target_skills": ["FastAPI"]}
        assert c.post("/workspace/intelligence/plans", json=body).status_code == 409
        c.post(
            "/workspace/profile",
            json=dict(
                name="Test",
                target_role="AI_ENGINEER",
                weekly_hours=10,
                english="unknown",
                german="unknown",
                location="Test",
            ),
        )
        p = c.post("/workspace/intelligence/plans", json=body).json()
        assert p["market_snapshot_id"] == m["id"] and p["profile_snapshot_id"]
        assert p["sequence"][-1]["skill"] == "FastAPI"
        exported = c.get("/workspace/export").json()
        assert len(exported["engine_records"]) == 2
        assert (
            c.post(
                "/workspace/intelligence/feedback",
                json=dict(
                    target_type="learning",
                    target_id="unknown",
                    request_key="a",
                    consent_to_send=True,
                ),
            ).status_code
            == 503
        )
        assert (
            c.delete(
                "/workspace", headers={"X-Confirm-Delete": "delete-personal-workspace"}
            ).status_code
            == 204
        )
        assert c.get("/workspace/intelligence").json()["records"] == []


def test_ai_budget_idempotency_failure_and_no_mastery(engine, monkeypatch):
    for k, v in {
        "CAREER_AI_ENABLED": "true",
        "OPENAI_API_KEY": "synthetic-not-a-real-key",
        "CAREER_AI_MODEL": "test-model",
        "CAREER_AI_DAILY_CALLS": "2",
    }.items():
        monkeypatch.setenv(k, v)
    calls = []

    def fake(config, payload):
        calls.append(payload)
        return {
            "feedback": {"technical_feedback": "Synthetic test feedback"},
            "usage": {"total_tokens": 5},
        }

    monkeypatch.setattr("career_os.intelligence.generate_feedback", fake)
    with TestClient(
        create_app(engine=engine, api_token=TOKEN), headers={"Authorization": f"Bearer {TOKEN}"}
    ) as c:
        a = c.post(
            "/workspace/learning",
            json=dict(week=1, concept_answer="Example", english_answer="Example"),
        ).json()
        body = dict(
            target_type="learning", target_id=a["id"], request_key="same", consent_to_send=True
        )
        assert (
            c.post(
                "/workspace/intelligence/feedback", json={**body, "consent_to_send": False}
            ).status_code
            == 422
        )
        result = c.post("/workspace/intelligence/feedback", json=body).json()
        assert result["status"] == "COMPLETED"
        assert c.post("/workspace/intelligence/feedback", json=body).json()["id"] == result["id"]
        assert len(calls) == 1
        assert c.get("/workspace").json()["evidence"] == []
        assert (
            c.get("/workspace").json()["attempts"][0]["assessment_status"] == "submitted_unassessed"
        )

        def broken(config, payload):
            raise ValueError("secret provider details must not leak")

        monkeypatch.setattr("career_os.intelligence.generate_feedback", broken)
        failed = c.post(
            "/workspace/intelligence/feedback", json={**body, "request_key": "second"}
        ).json()
        assert failed["status"] == "FAILED" and "secret" not in str(failed)
        assert (
            c.post(
                "/workspace/intelligence/feedback", json={**body, "request_key": "third"}
            ).status_code
            == 429
        )
        c.delete("/workspace", headers={"X-Confirm-Delete": "delete-personal-workspace"})
        with Session(engine) as s:
            assert s.get(AIBudget, datetime.now(UTC).date().isoformat()).used == 2


def test_greenhouse_policy_before_network_and_mapping(engine, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("unapproved source must not trigger network")

    monkeypatch.setattr("career_os.greenhouse.bounded_json", forbidden)
    with pytest.raises(ValueError):
        collect_greenhouse(engine, "DEMO", "example", "key")
    with pytest.raises(ValueError):
        collect_greenhouse(engine, "DEMO", "../evil", "key")
    payload = {
        "jobs": [
            {
                "id": 1,
                "title": "ML Engineer",
                "absolute_url": "https://example.com/job",
                "location": {"name": "Berlin"},
                "content": "<p>Python &amp; SQL</p><script>bad()</script>",
            }
        ]
    }
    adapter = GreenhouseAdapter("G", "test", "Test company", payload)
    row = list(adapter.records())[0]
    assert "Python & SQL" in row["description"] and "bad" not in row["description"]
    assert (
        adapter.fingerprint == GreenhouseAdapter("G", "test", "Test company", payload).fingerprint
    )
    with Session(engine) as s, s.begin():
        s.add(
            Source(
                id="G",
                name="Test company",
                source_type="greenhouse",
                enabled=True,
                policy_status="APPROVED",
                collection_method="greenhouse:test",
                policy_reference="synthetic-review",
                reviewed_by="test",
                retention_days=30,
            )
        )
    monkeypatch.setattr("career_os.greenhouse.bounded_json", lambda url: payload)
    assert collect_greenhouse(engine, "G", "test", "key")["inserted"] == 1
    assert collect_greenhouse(engine, "G", "test", "key")["inserted"] == 1
    assert collect_greenhouse(engine, "G", "test", "new")["duplicates"] == 1


def test_network_allowlist():
    for url in [
        "http://api.openai.com",
        "https://localhost",
        "https://api.openai.com.evil.test",
        "https://key@api.openai.com",
        "https://api.openai.com:8000",
    ]:
        with pytest.raises(ValueError, match="network_destination_denied"):
            bounded_json(url)


def test_postgres_ai_reservation_is_atomic(engine, monkeypatch):
    if engine.dialect.name != "postgresql":
        pytest.skip("PostgreSQL concurrency gate")
    from concurrent.futures import ThreadPoolExecutor

    for k, v in {
        "CAREER_AI_ENABLED": "true",
        "OPENAI_API_KEY": "synthetic-key",
        "CAREER_AI_MODEL": "test",
        "CAREER_AI_DAILY_CALLS": "1",
    }.items():
        monkeypatch.setenv(k, v)
    calls = []
    monkeypatch.setattr(
        "career_os.intelligence.generate_feedback",
        lambda config, payload: calls.append(payload) or {"feedback": {}},
    )
    with TestClient(
        create_app(engine=engine, api_token=TOKEN), headers={"Authorization": f"Bearer {TOKEN}"}
    ) as c:
        a = c.post(
            "/workspace/learning", json=dict(week=1, concept_answer="A", english_answer="B")
        ).json()

        def submit(key):
            return c.post(
                "/workspace/intelligence/feedback",
                json=dict(
                    target_type="learning", target_id=a["id"], request_key=key, consent_to_send=True
                ),
            ).status_code

        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(submit, ["one", "two"]))
        assert sorted(outcomes) == [200, 429]
        assert len(calls) == 1
