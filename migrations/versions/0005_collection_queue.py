"""Bounded schedule and durable collection-job metadata; no source payload copy."""

import sqlalchemy as sa
from alembic import op

revision = "0005_collection_queue"
down_revision = "0004_retention"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "collection_schedules",
        sa.Column("source_id", sa.String(80), sa.ForeignKey("sources.id"), primary_key=True),
        sa.Column("interval_minutes", sa.Integer(), nullable=False),
        sa.Column("next_due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.CheckConstraint("interval_minutes BETWEEN 60 AND 10080"),
    )
    op.create_table(
        "collection_jobs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("source_id", sa.String(80), sa.ForeignKey("sources.id"), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("next_attempt_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ingestion_run_id", sa.String(36), sa.ForeignKey("ingestion_runs.id")),
        sa.Column("error_code", sa.String(80)),
        sa.UniqueConstraint("source_id", "scheduled_at"),
        sa.CheckConstraint(
            "status IN ('PENDING','RUNNING','RETRY','COMPLETED','PARTIAL','FAILED','BLOCKED')"
        ),
        sa.CheckConstraint("attempts BETWEEN 0 AND 3"),
    )


def downgrade():
    op.drop_table("collection_jobs")
    op.drop_table("collection_schedules")
