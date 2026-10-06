"""One explicit job per invocation, durable attempts, no sleeping or hidden retries."""

from datetime import timedelta
from typing import Any

from sqlalchemy import Engine, select, text
from sqlalchemy.orm import Session

from career_os.collection_models import CollectionJob, CollectionSchedule
from career_os.greenhouse import collect_greenhouse
from career_os.ingestion import fail_run
from career_os.models import IngestionRun, Source
from career_os.scheduling import database_now, postgres_only, source_allowed


def attempt_key(job_id: str, attempt: int) -> str:
    return f"collection:{job_id}:{attempt}"


def finish(engine: Engine, job_id: str, status: str, run_id: str | None = None) -> dict[str, Any]:
    with Session(engine) as session, session.begin():
        job = session.get(CollectionJob, job_id)
        assert job is not None
        job.ingestion_run_id = run_id
        if status in {"COMPLETED", "PARTIAL", "BLOCKED"}:
            job.status = status
            job.error_code = "source_or_schedule_blocked" if status == "BLOCKED" else None
        else:
            job.status = "FAILED" if job.attempts >= 3 else "RETRY"
            job.error_code = "collection_attempt_failed"
            job.next_attempt_at = database_now(session) + timedelta(
                minutes=5 * 2 ** max(0, job.attempts - 1)
            )
        return {
            "id": job.id,
            "status": job.status,
            "attempts": job.attempts,
            "ingestion_run_id": job.ingestion_run_id,
            "error_code": job.error_code,
        }


def work_one(engine: Engine, job_id: str) -> dict[str, Any]:
    postgres_only(engine)
    with Session(engine) as session:
        job = session.get(CollectionJob, job_id)
        if job is None:
            raise ValueError("collection_job_not_found")
        source_id = job.source_id
    # A dedicated checked-out connection owns the session lock across HTTP and commits.
    # Hash collisions serialize unrelated sources safely; no source text is interpolated.
    with engine.connect() as lock:
        acquired = lock.scalar(
            text("SELECT pg_try_advisory_lock(71420602, hashtext(:source))"), {"source": source_id}
        )
        lock.commit()
        if not acquired:
            return {"id": job_id, "status": "BUSY"}
        try:
            return locked_work(engine, job_id)
        finally:
            try:
                lock.execute(
                    text("SELECT pg_advisory_unlock(71420602, hashtext(:source))"),
                    {"source": source_id},
                )
                lock.commit()
            except Exception:
                # Never return a possibly locked DB session to the connection pool.
                lock.invalidate()


def locked_work(engine: Engine, job_id: str) -> dict[str, Any]:
    with Session(engine) as session:
        job = session.get(CollectionJob, job_id)
        assert job is not None
        if job.status not in {"PENDING", "RUNNING", "RETRY"}:
            return {"id": job.id, "status": job.status, "attempts": job.attempts}
        if job.status != "RUNNING" and job.next_attempt_at > database_now(session):
            return {"id": job.id, "status": "NOT_DUE"}
        source_id = job.source_id
        attempts = job.attempts
        was_running = job.status == "RUNNING"
        prior = (
            session.scalar(
                select(IngestionRun).where(
                    IngestionRun.source_id == source_id,
                    IngestionRun.request_key == attempt_key(job_id, attempts),
                )
            )
            if attempts
            else None
        )
        prior_id = prior.id if prior else None
        prior_status = prior.status if prior else None
    # Recover a committed ingestion before considering another network request.
    if prior_status in {"COMPLETED", "PARTIAL"}:
        return finish(engine, job_id, prior_status, prior_id)
    if was_running:
        if prior_status == "RUNNING":
            assert prior_id is not None
            fail_run(engine, prior_id)
        return finish(engine, job_id, "FAILED", prior_id)
    with Session(engine) as session, session.begin():
        job = session.get(CollectionJob, job_id)
        assert job is not None
        schedule = session.get(CollectionSchedule, source_id)
        source = session.get(Source, source_id)
        try:
            source_allowed(source)
            if schedule is None or not schedule.enabled:
                raise ValueError("schedule_disabled")
        except ValueError:
            job.status = "BLOCKED"
            job.error_code = "source_or_schedule_blocked"
            return {"id": job.id, "status": job.status, "attempts": job.attempts}
        if job.attempts >= 3:
            job.status = "FAILED"
            return {"id": job.id, "status": job.status, "attempts": job.attempts}
        assert source is not None
        board = source.collection_method.split(":", 1)[1]
        job.attempts += 1
        job.status = "RUNNING"
        job.error_code = None
        key = attempt_key(job.id, job.attempts)
    try:
        result = collect_greenhouse(engine, source_id, board, key)
    except Exception:
        return finish(engine, job_id, "FAILED")
    return finish(engine, job_id, result["status"], result["id"])
