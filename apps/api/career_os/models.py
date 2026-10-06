from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
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


class Source(Base):
    __tablename__ = "sources"
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    source_type: Mapped[str] = mapped_column(String(80))
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    policy_status: Mapped[str] = mapped_column(String(30), default="REVIEW")
    collection_method: Mapped[str] = mapped_column(String(80), default="unreviewed")
    policy_reference: Mapped[str | None] = mapped_column(String(500))
    reviewed_by: Mapped[str | None] = mapped_column(String(120))
    retention_days: Mapped[int | None] = mapped_column(Integer)
    __table_args__ = (CheckConstraint("retention_days IS NULL OR retention_days > 0"),)


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id"))
    request_key: Mapped[str] = mapped_column(String(120))
    input_hash: Mapped[str] = mapped_column(String(64))
    adapter_version: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(20), default="RUNNING")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    fetched: Mapped[int] = mapped_column(Integer, default=0)
    accepted: Mapped[int] = mapped_column(Integer, default=0)
    inserted: Mapped[int] = mapped_column(Integer, default=0)
    duplicates: Mapped[int] = mapped_column(Integer, default=0)
    rejected: Mapped[int] = mapped_column(Integer, default=0)
    error_code: Mapped[str | None] = mapped_column(String(80))
    __table_args__ = (
        UniqueConstraint("source_id", "request_key"),
        CheckConstraint("status IN ('RUNNING','COMPLETED','PARTIAL','FAILED')"),
        CheckConstraint("fetched = accepted + rejected"),
        CheckConstraint("accepted = inserted + duplicates"),
        CheckConstraint(
            "fetched >= 0 AND accepted >= 0 AND inserted >= 0 AND duplicates >= 0 AND rejected >= 0"
        ),
    )


class RawJob(Base):
    __tablename__ = "raw_jobs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id"))
    source_job_id: Mapped[str] = mapped_column(String(200))
    content_hash: Mapped[str] = mapped_column(String(64))
    source_url: Mapped[str] = mapped_column(String(2000))
    content: Mapped[dict[str, Any]] = mapped_column(JSON)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ingestion_run_id: Mapped[str] = mapped_column(ForeignKey("ingestion_runs.id"))
    __table_args__ = (UniqueConstraint("source_id", "source_job_id", "content_hash"),)


class Observation(Base):
    __tablename__ = "observations"
    run_id: Mapped[str] = mapped_column(ForeignKey("ingestion_runs.id"), primary_key=True)
    ordinal: Mapped[int] = mapped_column(Integer, primary_key=True)
    raw_job_id: Mapped[str] = mapped_column(ForeignKey("raw_jobs.id"), index=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Rejection(Base):
    __tablename__ = "rejections"
    run_id: Mapped[str] = mapped_column(ForeignKey("ingestion_runs.id"), primary_key=True)
    ordinal: Mapped[int] = mapped_column(Integer, primary_key=True)
    payload_hash: Mapped[str] = mapped_column(String(64))
    errors: Mapped[list[dict[str, str]]] = mapped_column(JSON)
