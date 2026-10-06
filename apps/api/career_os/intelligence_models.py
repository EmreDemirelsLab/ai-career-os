from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from career_os.db import Base
from career_os.workspace_models import Record


class EngineRecord(Record, Base):
    __tablename__ = "engine_records"
    kind: Mapped[str] = mapped_column(String(40), index=True)


class AIRequest(Record, Base):
    __tablename__ = "ai_requests"
    request_key: Mapped[str] = mapped_column(String(100), unique=True)
    input_hash: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(20))


class AIBudget(Base):
    __tablename__ = "ai_budgets"
    day: Mapped[str] = mapped_column(String(10), primary_key=True)
    used: Mapped[int] = mapped_column(Integer)


class RetentionRun(Record, Base):
    __tablename__ = "retention_runs"
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id"))
    request_key: Mapped[str] = mapped_column(String(120))
    __table_args__ = (UniqueConstraint("source_id", "request_key"),)
