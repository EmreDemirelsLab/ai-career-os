import json
import logging
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import ValidationError
from sqlalchemy import Engine, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from career_os.contracts import Adapter, JobEnvelope, digest
from career_os.governance import assert_source_allowed
from career_os.models import IngestionRun, Observation, RawJob, Rejection, Source

logger = logging.getLogger("career_os.ingestion")


def insert_for(engine: Engine, model: Any) -> Any:
    if engine.dialect.name == "postgresql":
        return pg_insert(model)
    if engine.dialect.name == "sqlite":
        return sqlite_insert(model)
    raise ValueError("unsupported_database")


def run_summary(run: IngestionRun) -> dict[str, Any]:
    return {
        k: getattr(run, k)
        for k in (
            "id",
            "source_id",
            "status",
            "fetched",
            "accepted",
            "inserted",
            "duplicates",
            "rejected",
            "error_code",
        )
    }


def inspect_run(engine: Engine, run_id: str) -> dict[str, Any]:
    with Session(engine, autoflush=False) as session:
        run = session.get(IngestionRun, run_id)
        if run is None:
            raise ValueError("run_not_found")
        result = run_summary(run)
        result["rejections"] = [
            {"ordinal": x.ordinal, "errors": x.errors}
            for x in session.scalars(
                select(Rejection).where(Rejection.run_id == run_id).order_by(Rejection.ordinal)
            )
        ]
        return result


def fail_run(engine: Engine, run_id: str) -> None:
    # Run row lock also protects against marking an actively committing batch failed.
    with Session(engine, autoflush=False) as session, session.begin():
        run = session.scalar(
            select(IngestionRun).where(IngestionRun.id == run_id).with_for_update()
        )
        if run is None or run.status != "RUNNING":
            raise ValueError("run_not_running")
        run.status = "FAILED"
        run.error_code = "operator_recovery"
        run.completed_at = datetime.now(UTC)


def ingest(engine: Engine, source_id: str, request_key: str, adapter: Adapter) -> dict[str, Any]:
    if not request_key.strip() or len(request_key) > 120:
        raise ValueError("invalid_request_key")
    run_id = str(uuid4())
    with Session(engine, autoflush=False) as session, session.begin():
        source = session.get(Source, source_id)
        if source is None:
            raise ValueError("source_not_found")
        assert_source_allowed(source)
        created = session.scalar(
            insert_for(engine, IngestionRun)
            .values(
                id=run_id,
                source_id=source_id,
                request_key=request_key,
                input_hash=adapter.fingerprint,
                adapter_version=adapter.version,
                started_at=datetime.now(UTC),
                status="RUNNING",
                fetched=0,
                accepted=0,
                inserted=0,
                duplicates=0,
                rejected=0,
            )
            .on_conflict_do_nothing(index_elements=["source_id", "request_key"])
            .returning(IngestionRun.id)
        )
        if created is None:
            old = session.scalar(
                select(IngestionRun).where(
                    IngestionRun.source_id == source_id, IngestionRun.request_key == request_key
                )
            )
            assert old is not None
            if old.input_hash != adapter.fingerprint or old.adapter_version != adapter.version:
                raise ValueError("idempotency_key_conflict")
            return run_summary(old)
    try:
        with Session(engine, autoflush=False) as session, session.begin():
            run = session.scalar(
                select(IngestionRun).where(IngestionRun.id == run_id).with_for_update()
            )
            assert run is not None
            if run.status != "RUNNING":
                return run_summary(run)
            for ordinal, record in enumerate(adapter.records(), 1):
                run.fetched += 1
                errors: list[dict[str, str]] = []
                try:
                    envelope = JobEnvelope.model_validate(record)
                    if envelope.source_id != source_id:
                        errors = [{"field": "source_id", "code": "source_mismatch"}]
                except ValidationError as exc:
                    errors = [
                        {"field": ".".join(map(str, e["loc"])), "code": e["type"]}
                        for e in exc.errors(
                            include_input=False, include_context=False, include_url=False
                        )
                    ]
                if errors:
                    session.add(
                        Rejection(
                            run_id=run_id,
                            ordinal=ordinal,
                            payload_hash=digest(record),
                            errors=errors,
                        )
                    )
                    run.rejected += 1
                    continue
                content = envelope.content()
                content_hash = digest(content)
                raw_id = session.scalar(
                    insert_for(engine, RawJob)
                    .values(
                        id=str(uuid4()),
                        source_id=source_id,
                        source_job_id=envelope.source_job_id,
                        content_hash=content_hash,
                        source_url=str(envelope.source_url),
                        content=content,
                        fetched_at=envelope.fetched_at,
                        ingestion_run_id=run_id,
                    )
                    .on_conflict_do_nothing(
                        index_elements=["source_id", "source_job_id", "content_hash"]
                    )
                    .returning(RawJob.id)
                )
                run.accepted += 1
                if raw_id is None:
                    raw_id = session.scalar(
                        select(RawJob.id).where(
                            RawJob.source_id == source_id,
                            RawJob.source_job_id == envelope.source_job_id,
                            RawJob.content_hash == content_hash,
                        )
                    )
                    run.duplicates += 1
                else:
                    run.inserted += 1
                assert raw_id is not None
                session.add(
                    Observation(
                        run_id=run_id,
                        ordinal=ordinal,
                        raw_job_id=raw_id,
                        fetched_at=envelope.fetched_at,
                    )
                )
            run.status = "PARTIAL" if run.rejected else "COMPLETED"
            run.completed_at = datetime.now(UTC)
            result = run_summary(run)
    except Exception:
        # Exception text may contain external content or connection secrets.
        with Session(engine, autoflush=False) as session, session.begin():
            failed = session.get(IngestionRun, run_id)
            assert failed is not None
            failed.status = "FAILED"
            failed.error_code = "batch_failed"
            failed.completed_at = datetime.now(UTC)
            result = run_summary(failed)
    logger.info(json.dumps({"event": "ingestion_finished", **result}))
    return result
