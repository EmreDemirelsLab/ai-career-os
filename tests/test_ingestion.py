import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from career_os.contracts import FixtureAdapter
from career_os.governance import seed_sources, set_enabled
from career_os.ingestion import ingest, inspect_run
from career_os.models import IngestionRun, Observation, RawJob
from sqlalchemy import func, select, text
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import Session


def fixture():
    return FixtureAdapter(json.loads(Path("tests/fixtures/jobs.json").read_text()))


def count(engine, model):
    with Session(engine) as session:
        return session.scalar(select(func.count()).select_from(model))


def test_ingestion_rerun_preserves_raw_and_observations(engine):
    first = ingest(engine, "DEMO", "first", fixture())
    assert first["status"] == "PARTIAL"
    assert (first["fetched"], first["accepted"], first["inserted"], first["rejected"]) == (
        3,
        2,
        2,
        1,
    )
    assert ingest(engine, "DEMO", "first", fixture()) == first
    assert count(engine, IngestionRun) == 1
    second = ingest(engine, "DEMO", "second", fixture())
    assert (second["inserted"], second["duplicates"]) == (0, 2)
    assert count(engine, RawJob) == 2
    assert count(engine, Observation) == 4
    assert len(inspect_run(engine, first["id"])["rejections"]) == 1


def test_changed_content_new_revision_but_key_conflict(engine):
    ingest(engine, "DEMO", "one", fixture())
    records = list(fixture().records())[:1]
    records[0]["description"] = "New requirements"
    with pytest.raises(ValueError, match="idempotency_key_conflict"):
        ingest(engine, "DEMO", "one", FixtureAdapter(records))
    result = ingest(engine, "DEMO", "two", FixtureAdapter(records))
    assert result["inserted"] == 1
    assert count(engine, RawJob) == 3


def test_disabled_unreviewed_and_missing_source(engine):
    with pytest.raises(ValueError, match="source_policy_incomplete"):
        set_enabled(engine, "GREENHOUSE", True)
    with pytest.raises(ValueError, match="source_disabled"):
        ingest(engine, "GREENHOUSE", "one", fixture())
    with pytest.raises(ValueError, match="source_not_found"):
        ingest(engine, "absent", "one", fixture())
    set_enabled(engine, "DEMO", False)
    seed_sources(engine, Path("seed/source_registry_seed.csv"))
    with pytest.raises(ValueError, match="source_disabled"):
        ingest(engine, "DEMO", "one", fixture())
    assert count(engine, IngestionRun) == 0


def test_source_mismatch_rejected(engine):
    records = list(fixture().records())[:1]
    records[0]["source_id"] = "OTHER"
    result = ingest(engine, "DEMO", "one", FixtureAdapter(records))
    assert result["rejected"] == 1
    assert count(engine, RawJob) == 0


def test_batch_exception_rolls_back_and_hides_secrets(engine, caplog):
    class Broken:
        version = "broken/1"
        fingerprint = "f" * 64

        def records(self):
            yield list(fixture().records())[0]
            raise RuntimeError("TOP_SECRET_TOKEN")

    with caplog.at_level("INFO", logger="career_os.ingestion"):
        result = ingest(engine, "DEMO", "one", Broken())
    assert result["status"] == "FAILED"
    assert result["fetched"] == 0
    assert count(engine, RawJob) == 0
    assert "TOP_SECRET_TOKEN" not in caplog.text
    assert "Synthetic AI Engineer" not in caplog.text
    assert '"event": "ingestion_finished"' in caplog.text


@pytest.mark.parametrize(
    "statement", ["UPDATE raw_jobs SET source_job_id='tampered'", "DELETE FROM raw_jobs"]
)
def test_raw_immutable_at_database(engine, statement):
    ingest(engine, "DEMO", "one", fixture())
    with pytest.raises(DatabaseError), engine.begin() as connection:
        connection.execute(text(statement))
    assert count(engine, RawJob) == 2


def test_invalid_records_do_not_leak_payload(engine):
    record = {"source_id": "DEMO", "description": "SECRET_PAYLOAD"}
    result = ingest(engine, "DEMO", "one", FixtureAdapter([record]))
    assert "SECRET_PAYLOAD" not in json.dumps(inspect_run(engine, result["id"]))


def test_postgres_concurrent_dedupe(engine):
    if engine.dialect.name != "postgresql":
        pytest.skip("Concurrency assertion requires PostgreSQL")
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda key: ingest(engine, "DEMO", key, fixture()), ["one", "two"]))
    assert all(x["status"] == "PARTIAL" for x in results)
    assert sum(x["inserted"] for x in results) == 2
    assert count(engine, RawJob) == 2
    assert count(engine, Observation) == 4


def test_postgres_concurrent_same_request(engine):
    if engine.dialect.name != "postgresql":
        pytest.skip("Concurrency assertion requires PostgreSQL")
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: ingest(engine, "DEMO", "same", fixture()), range(2)))
    assert results[0]["id"] == results[1]["id"]
    assert count(engine, IngestionRun) == 1
    assert count(engine, RawJob) == 2


def test_operator_recovery_of_interrupted_run(engine):
    from datetime import UTC, datetime

    from career_os.ingestion import fail_run

    with Session(engine) as session, session.begin():
        session.add(
            IngestionRun(
                id="interrupted",
                source_id="DEMO",
                request_key="old",
                input_hash="f" * 64,
                adapter_version="fixture/1.0",
                started_at=datetime.now(UTC),
            )
        )
    fail_run(engine, "interrupted")
    result = inspect_run(engine, "interrupted")
    assert result["status"] == "FAILED"
    assert result["error_code"] == "operator_recovery"
    with pytest.raises(ValueError, match="run_not_running"):
        fail_run(engine, "interrupted")
    assert ingest(engine, "DEMO", "new", fixture())["status"] == "PARTIAL"
