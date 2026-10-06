from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from career_os.db import Base


class CollectionSchedule(Base):
    __tablename__ = "collection_schedules"
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id"), primary_key=True)
    interval_minutes: Mapped[int] = mapped_column(Integer)
    next_due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    enabled: Mapped[bool] = mapped_column(Boolean)
    __table_args__ = (CheckConstraint("interval_minutes BETWEEN 60 AND 10080"),)


class CollectionJob(Base):
    __tablename__ = "collection_jobs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id"))
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20))
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    next_attempt_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ingestion_run_id: Mapped[str | None] = mapped_column(ForeignKey("ingestion_runs.id"))
    error_code: Mapped[str | None] = mapped_column(String(80))
    __table_args__ = (
        UniqueConstraint("source_id", "scheduled_at"),
        CheckConstraint(
            "status IN ('PENDING','RUNNING','RETRY','COMPLETED','PARTIAL','FAILED','BLOCKED')"
        ),
        CheckConstraint("attempts BETWEEN 0 AND 3"),
    )
