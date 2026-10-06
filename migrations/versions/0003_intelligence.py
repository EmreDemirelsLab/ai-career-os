"""Market/plan snapshots and bounded AI request ledger."""

import sqlalchemy as sa
from alembic import op

revision = "0003_intelligence"
down_revision = "0002_workspace"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "workspace_sessions",
        sa.Column("token_hash", sa.String(64), primary_key=True),
        sa.Column("master_hash", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "engine_records",
        sa.Column("kind", sa.String(40), nullable=False),
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
    )
    op.create_index("ix_engine_records_kind", "engine_records", ["kind"])
    op.create_table(
        "ai_requests",
        sa.Column("request_key", sa.String(100), nullable=False, unique=True),
        sa.Column("input_hash", sa.String(64), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
    )
    op.create_table(
        "ai_budgets",
        sa.Column("day", sa.String(10), primary_key=True),
        sa.Column("used", sa.Integer(), nullable=False),
    )


def downgrade():
    op.drop_table("workspace_sessions")
    op.drop_table("ai_budgets")
    op.drop_table("ai_requests")
    op.drop_index("ix_engine_records_kind", table_name="engine_records")
    op.drop_table("engine_records")
