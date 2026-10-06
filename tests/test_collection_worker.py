from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from threading import Event

import pytest
from career_os import collection_worker, greenhouse
from career_os.collection_models import CollectionJob, CollectionSchedule
from career_os.models import RawJob, Source
from career_os.scheduling import configure_schedule, enqueue_due
from sqlalchemy import func, select
from sqlalchemy.orm import Session


def queued(engine, monkeypatch):
    if engine.dialect.name != "postgresql":
        pytest.skip("PostgreSQL session locks required")
    with Session(engine) as s, s.begin():
        s.add(
            Source(
                id="WORK",
                name="Synthetic",
                source_type="greenhouse",
                enabled=True,
                policy_status="APPROVED",
                collection_method="greenhouse:synthetic",
                policy_reference="synthetic test",
                reviewed_by="test",
                retention_days=30,
            )
        )
    configure_schedule(engine, "WORK", 60, True)
    monkeypatch.setattr(
        greenhouse,
        "bounded_json",
        lambda *a, **k: {
            "jobs": [
                {
                    "id": 1,
                    "absolute_url": "https://example.com/job",
                    "title": "AI Engineer",
                    "location": {"name": "Berlin"},
                    "content": "Python engineering",
                }
            ]
        },
    )
    return enqueue_due(engine)["queued"][0]["id"]


def due(engine, job_id):
    with Session(engine) as s, s.begin():
        s.get(CollectionJob, job_id).next_attempt_at = datetime.now(UTC) - timedelta(minutes=1)


def test_crash_after_ingestion_commit_recovers_without_refetch(engine, monkeypatch):
    job_id = queued(engine, monkeypatch)
    original = collection_worker.finish

    def crash(*a, **k):
        raise SystemExit("simulated process death")

    monkeypatch.setattr(collection_worker, "finish", crash)
    with pytest.raises(SystemExit):
        collection_worker.work_one(engine, job_id)
    monkeypatch.setattr(collection_worker, "finish", original)

    def forbidden(*a, **k):
        pytest.fail("completed ingestion must not refetch")

    monkeypatch.setattr(greenhouse, "bounded_json", forbidden)
    result = collection_worker.work_one(engine, job_id)
    assert result["status"] == "COMPLETED"
    assert result["attempts"] == 1
    assert collection_worker.work_one(engine, job_id)["status"] == "COMPLETED"
    with Session(engine) as s:
        assert s.scalar(select(func.count()).select_from(RawJob)) == 1


def test_concurrent_workers_only_one_request(engine, monkeypatch):
    job_id = queued(engine, monkeypatch)
    entered, release = Event(), Event()
    original = greenhouse.bounded_json
    calls = []

    def blocking(*a, **k):
        calls.append(1)
        entered.set()
        assert release.wait(5)
        return original(*a, **k)

    monkeypatch.setattr(greenhouse, "bounded_json", blocking)
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(collection_worker.work_one, engine, job_id)
        try:
            assert entered.wait(5)
            assert collection_worker.work_one(engine, job_id)["status"] == "BUSY"
        finally:
            release.set()
        assert first.result()["status"] == "COMPLETED"
    assert len(calls) == 1


def test_retry_cap_and_due_time(engine, monkeypatch):
    job_id = queued(engine, monkeypatch)

    def failure(*a, **k):
        raise ValueError("external secret text must not persist")

    monkeypatch.setattr(greenhouse, "bounded_json", failure)
    for attempt in range(1, 4):
        result = collection_worker.work_one(engine, job_id)
        assert result["attempts"] == attempt
        assert result["status"] == ("FAILED" if attempt == 3 else "RETRY")
        assert "secret" not in str(result)
        if attempt < 3:
            assert collection_worker.work_one(engine, job_id)["status"] == "NOT_DUE"
            due(engine, job_id)
    assert collection_worker.work_one(engine, job_id)["attempts"] == 3


@pytest.mark.parametrize("disable", ["source", "schedule"])
def test_disabled_before_work_never_fetches(engine, monkeypatch, disable):
    job_id = queued(engine, monkeypatch)
    with Session(engine) as s, s.begin():
        s.get(Source if disable == "source" else CollectionSchedule, "WORK").enabled = False

    def forbidden(*a, **k):
        pytest.fail("disabled work must not fetch")

    monkeypatch.setattr(greenhouse, "bounded_json", forbidden)
    result = collection_worker.work_one(engine, job_id)
    assert result["status"] == "BLOCKED"
    assert result["attempts"] == 0


def test_crash_before_ingestion_consumes_attempt_then_retries(engine, monkeypatch):
    job_id = queued(engine, monkeypatch)
    original = greenhouse.bounded_json

    def crash(*a, **k):
        raise SystemExit("simulated process death")

    monkeypatch.setattr(greenhouse, "bounded_json", crash)
    with pytest.raises(SystemExit):
        collection_worker.work_one(engine, job_id)
    monkeypatch.setattr(greenhouse, "bounded_json", original)
    assert collection_worker.work_one(engine, job_id)["status"] == "RETRY"
    due(engine, job_id)
    result = collection_worker.work_one(engine, job_id)
    assert result["status"] == "COMPLETED"
    assert result["attempts"] == 2


def test_orphaned_ingestion_run_is_closed_before_new_attempt(engine, monkeypatch):
    from career_os.contracts import FixtureAdapter
    from career_os.ingestion import ingest
    from career_os.models import IngestionRun

    job_id = queued(engine, monkeypatch)
    original = collection_worker.collect_greenhouse

    class InterruptedAdapter(FixtureAdapter):
        def records(self):
            raise SystemExit("interrupted atomic batch")

    def interrupted(db, source, board, key):
        return ingest(db, source, key, InterruptedAdapter([]))

    monkeypatch.setattr(collection_worker, "collect_greenhouse", interrupted)
    with pytest.raises(SystemExit):
        collection_worker.work_one(engine, job_id)
    result = collection_worker.work_one(engine, job_id)
    assert result["status"] == "RETRY"
    with Session(engine) as s:
        previous = s.get(IngestionRun, result["ingestion_run_id"])
        assert previous.status == "FAILED"
        assert previous.error_code == "operator_recovery"
        assert s.scalar(select(func.count()).select_from(RawJob)) == 0
    monkeypatch.setattr(collection_worker, "collect_greenhouse", original)
    due(engine, job_id)
    assert collection_worker.work_one(engine, job_id)["status"] == "COMPLETED"
