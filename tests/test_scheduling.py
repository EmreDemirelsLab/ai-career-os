from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta

import pytest
from career_os.collection_models import CollectionJob, CollectionSchedule
from career_os.models import Source
from career_os.scheduling import configure_schedule, enqueue_due, inspect_schedule
from sqlalchemy.orm import Session


def approved(engine):
    if engine.dialect.name != "postgresql":
        pytest.skip("PostgreSQL locking required")
    with Session(engine) as session, session.begin():
        session.add(
            Source(
                id="QUEUE",
                name="Synthetic board",
                source_type="greenhouse",
                enabled=True,
                policy_status="APPROVED",
                collection_method="greenhouse:synthetic",
                policy_reference="synthetic test only",
                reviewed_by="test",
                retention_days=30,
            )
        )
    configure_schedule(engine, "QUEUE", 60, True)


def make_due(engine):
    with Session(engine) as session, session.begin():
        session.get(CollectionSchedule, "QUEUE").next_due_at = datetime.now(UTC) - timedelta(
            days=20
        )


def test_parallel_ticks_and_backlog_coalesce(engine):
    approved(engine)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: enqueue_due(engine), range(2)))
    assert sum(len(x["queued"]) for x in results) == 1
    assert enqueue_due(engine)["queued"] == []
    make_due(engine)
    result = enqueue_due(engine)
    assert result["coalesced_sources"] == ["QUEUE"]
    assert result["network_requests"] == 0
    status = inspect_schedule(engine, "QUEUE")
    assert len(status["recent_jobs"]) == 1
    job_id = status["recent_jobs"][0]["id"]
    with Session(engine) as session, session.begin():
        session.get(CollectionJob, job_id).status = "COMPLETED"
    make_due(engine)
    assert len(enqueue_due(engine)["queued"]) == 1


def test_disabled_source_stops_queue(engine):
    approved(engine)
    with Session(engine) as session, session.begin():
        session.get(Source, "QUEUE").enabled = False
    assert enqueue_due(engine)["blocked_sources"] == ["QUEUE"]
    assert inspect_schedule(engine, "QUEUE")["enabled"] is False
    with pytest.raises(ValueError, match="source_disabled"):
        configure_schedule(engine, "QUEUE", 60, True)


def test_configure_preserves_due_and_bounds(engine):
    approved(engine)
    first = inspect_schedule(engine, "QUEUE")["next_due_at"]
    configure_schedule(engine, "QUEUE", 120, True)
    assert inspect_schedule(engine, "QUEUE")["next_due_at"] == first
    for interval in (0, 59, 10081):
        with pytest.raises(ValueError, match="interval"):
            configure_schedule(engine, "QUEUE", interval, True)
    for limit in (0, 101):
        with pytest.raises(ValueError, match="tick_limit"):
            enqueue_due(engine, limit)
    with pytest.raises(ValueError):
        configure_schedule(engine, "DEMO", 60, True)


def test_sqlite_fails_closed(engine):
    if engine.dialect.name != "sqlite":
        pytest.skip("SQLite-only guard")
    with pytest.raises(ValueError, match="requires_postgresql"):
        enqueue_due(engine)


def test_locked_schedule_is_skipped_and_limit_is_respected(engine):
    approved(engine)
    from sqlalchemy import select

    with Session(engine) as session, session.begin():
        session.execute(select(CollectionSchedule).with_for_update()).all()
        assert enqueue_due(engine)["queued"] == []
    assert len(enqueue_due(engine, limit=1)["queued"]) == 1


def test_policy_revoked_after_configuration(engine):
    approved(engine)
    with Session(engine) as session, session.begin():
        session.get(Source, "QUEUE").policy_status = "PENDING"
    assert enqueue_due(engine)["blocked_sources"] == ["QUEUE"]
    assert inspect_schedule(engine, "QUEUE")["recent_jobs"] == []
