"""One bounded operator tick; queues work but never fetches source content."""

import re
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session

from career_os.collection_models import CollectionJob, CollectionSchedule
from career_os.governance import assert_source_allowed
from career_os.models import Source

ACTIVE = ("PENDING", "RUNNING", "RETRY")


def postgres_only(engine: Engine) -> None:
    if engine.dialect.name != "postgresql":
        raise ValueError("scheduling_requires_postgresql")


def source_allowed(source: Source | None) -> None:
    if source is None:
        raise ValueError("source_not_found")
    assert_source_allowed(source)
    if source.source_type != "greenhouse" or not re.fullmatch(
        r"greenhouse:[a-zA-Z0-9_-]{1,80}", source.collection_method
    ):
        raise ValueError("schedule_requires_reviewed_greenhouse_board")


def database_now(session: Session) -> datetime:
    value = session.scalar(select(func.now()))
    assert isinstance(value, datetime)
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value


def configure_schedule(
    engine: Engine, source_id: str, interval_minutes: int, enabled: bool
) -> None:
    postgres_only(engine)
    if not 60 <= interval_minutes <= 10080:
        raise ValueError("interval_must_be_60_to_10080_minutes")
    with Session(engine) as session, session.begin():
        source = session.scalar(select(Source).where(Source.id == source_id).with_for_update())
        if enabled:
            source_allowed(source)
        elif source is None:
            raise ValueError("source_not_found")
        schedule = session.get(CollectionSchedule, source_id)
        if schedule is None:
            session.add(
                CollectionSchedule(
                    source_id=source_id,
                    interval_minutes=interval_minutes,
                    enabled=enabled,
                    next_due_at=database_now(session),
                )
            )
        else:
            schedule.enabled = enabled
            schedule.interval_minutes = interval_minutes
            # Preserve due time: repeated configuration must not enqueue a new cycle early.


def enqueue_due(engine: Engine, limit: int = 25) -> dict[str, Any]:
    postgres_only(engine)
    if not 1 <= limit <= 100:
        raise ValueError("tick_limit_must_be_1_to_100")
    queued = []
    blocked = []
    coalesced = []
    with Session(engine) as session, session.begin():
        now = database_now(session)
        schedules = list(
            session.scalars(
                select(CollectionSchedule)
                .where(CollectionSchedule.enabled.is_(True), CollectionSchedule.next_due_at <= now)
                .order_by(CollectionSchedule.next_due_at, CollectionSchedule.source_id)
                .limit(limit)
                .with_for_update(skip_locked=True)
            )
        )
        for schedule in schedules:
            try:
                source_allowed(session.get(Source, schedule.source_id))
            except ValueError:
                schedule.enabled = False
                blocked.append(schedule.source_id)
                continue
            outstanding = session.scalar(
                select(CollectionJob.id)
                .where(
                    CollectionJob.source_id == schedule.source_id, CollectionJob.status.in_(ACTIVE)
                )
                .limit(1)
            )
            if outstanding:
                coalesced.append(schedule.source_id)
            else:
                job = CollectionJob(
                    id=str(uuid4()),
                    source_id=schedule.source_id,
                    scheduled_at=schedule.next_due_at,
                    created_at=now,
                    status="PENDING",
                    attempts=0,
                    next_attempt_at=now,
                    ingestion_run_id=None,
                    error_code=None,
                )
                session.add(job)
                queued.append({"id": job.id, "source_id": job.source_id})
            # Missed periods are coalesced; no unbounded historical backfill.
            schedule.next_due_at = now + timedelta(minutes=schedule.interval_minutes)
    return {
        "queued": queued,
        "blocked_sources": blocked,
        "coalesced_sources": coalesced,
        "network_requests": 0,
    }


def inspect_schedule(engine: Engine, source_id: str) -> dict[str, Any]:
    postgres_only(engine)
    with Session(engine) as session:
        schedule = session.get(CollectionSchedule, source_id)
        if schedule is None:
            raise ValueError("schedule_not_found")
        jobs = list(
            session.scalars(
                select(CollectionJob)
                .where(CollectionJob.source_id == source_id)
                .order_by(CollectionJob.created_at.desc(), CollectionJob.id)
                .limit(50)
            )
        )
        return {
            "source_id": source_id,
            "enabled": schedule.enabled,
            "interval_minutes": schedule.interval_minutes,
            "next_due_at": schedule.next_due_at.isoformat(),
            "recent_jobs": [
                {
                    "id": x.id,
                    "status": x.status,
                    "attempts": x.attempts,
                    "scheduled_at": x.scheduled_at.isoformat(),
                    "error_code": x.error_code,
                    "ingestion_run_id": x.ingestion_run_id,
                }
                for x in jobs
            ],
        }
