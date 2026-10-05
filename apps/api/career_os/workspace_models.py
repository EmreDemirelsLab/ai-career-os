from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from career_os.db import Base


class Record:
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    data: Mapped[dict[str, Any]] = mapped_column(JSON)


class LearnerSnapshot(Record, Base):
    __tablename__ = "learner_snapshots"


class EvidenceRecord(Record, Base):
    __tablename__ = "evidence_records"
    skill: Mapped[str] = mapped_column(String(200), index=True)


class RoadmapRecord(Record, Base):
    __tablename__ = "roadmap_records"
    learner_snapshot_id: Mapped[str] = mapped_column(ForeignKey("learner_snapshots.id"))


class LearningAttempt(Record, Base):
    __tablename__ = "learning_attempts"
    week: Mapped[int] = mapped_column(Integer)


class RecallReview(Record, Base):
    __tablename__ = "recall_reviews"
    attempt_id: Mapped[str] = mapped_column(ForeignKey("learning_attempts.id"))
    interval: Mapped[int] = mapped_column(Integer)
    __table_args__ = (UniqueConstraint("attempt_id", "interval"),)


class InterviewRecord(Record, Base):
    __tablename__ = "interview_records"


class OpportunityRecord(Record, Base):
    __tablename__ = "opportunity_records"


class ApplicationRecord(Record, Base):
    __tablename__ = "application_records"
    opportunity_id: Mapped[str] = mapped_column(ForeignKey("opportunity_records.id"))


class ApplicationEvent(Record, Base):
    __tablename__ = "application_events"
    application_id: Mapped[str] = mapped_column(ForeignKey("application_records.id"))
