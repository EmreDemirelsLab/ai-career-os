from datetime import UTC, datetime, timedelta

import pytest
from career_os.contracts import FixtureAdapter
from career_os.ingestion import ingest
from career_os.intelligence_models import EngineRecord, RetentionRun
from career_os.models import Observation, RawJob, Source
from career_os.retention import retain_source
from career_os.workspace import stamp
from career_os.workspace_models import LearningAttempt
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session


def require_postgres(engine):
    if engine.dialect.name != "postgresql":
        pytest.skip("PostgreSQL maintenance/privilege gate; SQLite is immutable")


def seed_retention(engine):
    now = datetime.now(UTC)
    with Session(engine) as s, s.begin():
        s.add(
            Source(
                id="RET",
                name="Synthetic retention test",
                source_type="greenhouse",
                enabled=True,
                policy_status="APPROVED",
                collection_method="test",
                policy_reference="synthetic-policy",
                reviewed_by="test",
                retention_days=30,
            )
        )

    def envelope(job, days):
        return dict(
            source_id="RET",
            source_job_id=job,
            source_url="https://example.invalid/" + job,
            fetched_at=(now - timedelta(days=days)).isoformat(),
            title="Synthetic " + job,
            company="Example",
            location="Test",
            description="Python synthetic job",
        )

    ingest(
        engine,
        "RET",
        "initial",
        FixtureAdapter([envelope("expired", 40), envelope("refreshed", 40), envelope("fresh", 1)]),
    )
    ingest(engine, "RET", "refresh", FixtureAdapter([envelope("refreshed", 1)]))
    with Session(engine) as s, s.begin():
        rows = {r.source_job_id: r.id for r in s.scalars(select(RawJob))}
        market = EngineRecord(
            **stamp(),
            kind="market",
            data={
                "jobs": [
                    {"raw_id": rows["expired"], "mentions": [{"span": "sensitive source text"}]}
                ],
                "kind": "market",
            },
        )
        plan = EngineRecord(
            **stamp(),
            kind="adaptive_plan",
            data={"kind": "adaptive_plan", "market_snapshot_id": market.id, "sequence": []},
        )
        other = EngineRecord(
            **stamp(),
            kind="market",
            data={"kind": "market", "jobs": [{"raw_id": rows["fresh"]}], "exact_duplicates": []},
        )
        learner = LearningAttempt(
            **stamp(), week=1, data={"concept_answer": "Private learner answer"}
        )
        s.add_all([market, plan, other, learner])
        return rows, market.id, plan.id, other.id, learner.id


def test_retention_dry_run_apply_and_replay(engine):
    require_postgres(engine)
    rows, market, plan, other, learner = seed_retention(engine)
    dry = retain_source(engine, "RET", "cycle-1")
    assert dry["applied"] is False and dry["raw_deleted"] == 1
    assert dry["market_deleted"] == 1 and dry["plans_deleted"] == 1
    with Session(engine) as s:
        assert s.scalar(select(func.count()).select_from(RawJob)) == 3
        assert s.scalar(select(func.count()).select_from(RetentionRun)) == 0
    result = retain_source(engine, "RET", "cycle-1", apply=True)
    assert result["applied"] and result["observations_deleted"] == 1
    assert retain_source(engine, "RET", "cycle-1", apply=True) == result
    with Session(engine) as s:
        assert s.get(RawJob, rows["expired"]) is None
        assert s.get(RawJob, rows["refreshed"]) and s.get(RawJob, rows["fresh"])
        assert s.get(EngineRecord, market) is None and s.get(EngineRecord, plan) is None
        assert s.get(EngineRecord, other) and s.get(LearningAttempt, learner)
        assert s.scalar(select(func.count()).select_from(RetentionRun)) == 1
        assert "sensitive" not in str(s.scalar(select(RetentionRun)).data)
    assert retain_source(engine, "RET", "cycle-2", apply=True)["raw_deleted"] == 0
    with engine.begin() as conn:
        with pytest.raises(DBAPIError):
            conn.execute(text("DELETE FROM raw_jobs"))


def test_retention_missing_policy_fixture_sqlite_fail_closed(engine):
    if engine.dialect.name == "sqlite":
        with pytest.raises(ValueError, match="retention_requires_postgresql"):
            retain_source(engine, "DEMO", "test", apply=True)
    else:
        for source in ["DEMO", "missing"]:
            with pytest.raises(DBAPIError):
                retain_source(engine, source, "test", apply=True)


def test_retention_privileges_and_guc_bypass(engine):
    require_postgres(engine)
    rows, *_ = seed_retention(engine)
    with engine.begin() as c:
        for role in ["career_runtime", "career_retention"]:
            exists = c.scalar(text("SELECT 1 FROM pg_roles WHERE rolname=:role"), {"role": role})
            if not exists:
                c.execute(text(f"CREATE ROLE {role} NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE"))
        c.execute(text("GRANT USAGE ON SCHEMA public TO career_runtime, career_retention"))
        c.execute(text("GRANT SELECT, INSERT, UPDATE, DELETE ON raw_jobs TO career_runtime"))
        c.execute(
            text(
                "GRANT EXECUTE ON FUNCTION public.apply_source_retention(text,text,boolean) "
                "TO career_retention"
            )
        )
    for statement in [
        "SELECT public.apply_source_retention('RET','bypass',true)",
        "DELETE FROM public.raw_jobs",
        "UPDATE public.raw_jobs SET content='{}'::json",
        "ALTER TABLE public.raw_jobs DISABLE TRIGGER raw_immutable",
    ]:
        with pytest.raises(DBAPIError), engine.begin() as c:
            c.execute(text("SET LOCAL ROLE career_runtime"))
            c.execute(text("SET LOCAL career_os.retention='on'"))
            c.execute(text(statement))
    with engine.begin() as c:
        c.execute(text("SET LOCAL ROLE career_retention"))
        # A temporary object cannot shadow a schema-qualified source lookup.
        c.execute(text("CREATE TEMP TABLE sources(id text, retention_days integer) ON COMMIT DROP"))
        c.execute(text("INSERT INTO sources VALUES ('RET',1)"))
        data = c.scalar(text("SELECT public.apply_source_retention('RET','approved',true)"))
        assert data["raw_deleted"] == 1 and data["retention_days"] == 30
    with Session(engine) as s:
        assert s.get(RawJob, rows["fresh"])


def test_retention_rollback_and_new_observation_after_preview(engine):
    require_postgres(engine)
    rows, market, plan, *_ = seed_retention(engine)
    with pytest.raises(RuntimeError), engine.begin() as c:
        result = c.scalar(text("SELECT public.apply_source_retention('RET','rollback',true)"))
        assert result["raw_deleted"] == 1
        raise RuntimeError("simulated caller transaction failure")
    with Session(engine) as s:
        assert (
            s.get(RawJob, rows["expired"])
            and s.get(EngineRecord, market)
            and s.get(EngineRecord, plan)
        )
        assert s.scalar(select(func.count()).select_from(RetentionRun)) == 0
    assert retain_source(engine, "RET", "preview")["raw_deleted"] == 1
    with Session(engine) as s, s.begin():
        observation = s.scalar(select(Observation).where(Observation.raw_job_id == rows["expired"]))
        observation.fetched_at = datetime.now(UTC)
    assert retain_source(engine, "RET", "preview", apply=True)["raw_deleted"] == 0
