"""Personal workspace schema; explicit snapshot, no runtime metadata imports."""

import sqlalchemy as sa
from alembic import op

revision = "0002_workspace"
down_revision = "0001_foundation"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "evidence_records",
        sa.Column("skill", sa.String(length=200), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_evidence_records_skill"), "evidence_records", ["skill"], unique=False)
    op.create_table(
        "interview_records",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "learner_snapshots",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "learning_attempts",
        sa.Column("week", sa.Integer(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "opportunity_records",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "application_records",
        sa.Column("opportunity_id", sa.String(length=36), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ["opportunity_id"],
            ["opportunity_records.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "recall_reviews",
        sa.Column("attempt_id", sa.String(length=36), nullable=False),
        sa.Column("interval", sa.Integer(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ["attempt_id"],
            ["learning_attempts.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("attempt_id", "interval"),
    )
    op.create_table(
        "roadmap_records",
        sa.Column("learner_snapshot_id", sa.String(length=36), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ["learner_snapshot_id"],
            ["learner_snapshots.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "application_events",
        sa.Column("application_id", sa.String(length=36), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ["application_id"],
            ["application_records.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("application_events")
    op.drop_table("roadmap_records")
    op.drop_table("recall_reviews")
    op.drop_table("application_records")
    op.drop_table("opportunity_records")
    op.drop_table("learning_attempts")
    op.drop_table("learner_snapshots")
    op.drop_table("interview_records")
    op.drop_index(op.f("ix_evidence_records_skill"), table_name="evidence_records")
    op.drop_table("evidence_records")
