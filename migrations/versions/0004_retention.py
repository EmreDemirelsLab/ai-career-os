"""Scoped PostgreSQL retention; SQLite remains strictly immutable."""

import sqlalchemy as sa
from alembic import op

revision = "0004_retention"
down_revision = "0003_intelligence"
branch_labels = None
depends_on = None

TRIGGER = """
CREATE OR REPLACE FUNCTION public.reject_raw_mutation() RETURNS trigger
LANGUAGE plpgsql SET search_path = pg_catalog, pg_temp AS $$
BEGIN
  IF TG_OP = 'DELETE'
     AND current_setting('career_os.retention', true) = 'on'
     AND current_user = pg_get_userbyid((SELECT relowner FROM pg_class WHERE oid=TG_RELID))
  THEN RETURN OLD; END IF;
  RAISE EXCEPTION 'raw_jobs is immutable';
END; $$;
"""
FUNCTION = """
CREATE FUNCTION public.apply_source_retention(
  p_source text, p_key text, p_apply boolean DEFAULT false)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER
SET search_path = pg_catalog, pg_temp
SET career_os.retention = 'on'
SET lock_timeout = '5s'
AS $$
DECLARE
  v_days integer; v_type text; v_now timestamptz := clock_timestamp();
  v_ids text[]; v_markets text[]; v_plans text[];
  v_observations bigint; v_result jsonb; v_previous jsonb;
BEGIN
  IF p_source IS NULL OR length(p_source) NOT BETWEEN 1 AND 80
     OR p_key IS NULL OR length(btrim(p_key)) NOT BETWEEN 1 AND 120 OR p_apply IS NULL
  THEN RAISE EXCEPTION 'invalid_retention_input'; END IF;
  PERFORM pg_advisory_xact_lock(71420601);
  SELECT data::jsonb INTO v_previous FROM public.retention_runs
    WHERE source_id=p_source AND request_key=p_key;
  IF p_apply AND v_previous IS NOT NULL THEN RETURN v_previous; END IF;
  SELECT retention_days, source_type INTO v_days, v_type
    FROM public.sources WHERE id=p_source FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'source_not_found'; END IF;
  IF v_days IS NULL OR v_days <= 0 OR v_type='fixture'
    THEN RAISE EXCEPTION 'retention_policy_missing_or_fixture'; END IF;
  LOCK TABLE public.raw_jobs, public.observations, public.engine_records
    IN SHARE ROW EXCLUSIVE MODE;
  SELECT coalesce(array_agg(r.id::text), ARRAY[]::text[]) INTO v_ids
  FROM public.raw_jobs r WHERE r.source_id=p_source
    AND coalesce((SELECT max(o.fetched_at) FROM public.observations o WHERE o.raw_job_id=r.id),
                 r.fetched_at) < v_now - make_interval(days => v_days);
  SELECT coalesce(array_agg(e.id::text), ARRAY[]::text[]) INTO v_markets
  FROM public.engine_records e WHERE e.kind='market' AND (
    EXISTS (SELECT 1 FROM jsonb_array_elements(coalesce(e.data::jsonb->'jobs','[]'::jsonb)) j
            WHERE j->>'raw_id'=ANY(v_ids))
    OR EXISTS (SELECT 1 FROM jsonb_array_elements_text(
                 coalesce(e.data::jsonb->'exact_duplicates','[]'::jsonb)) d WHERE d=ANY(v_ids)));
  SELECT coalesce(array_agg(e.id::text), ARRAY[]::text[]) INTO v_plans
  FROM public.engine_records e WHERE e.kind='adaptive_plan'
    AND e.data::jsonb->>'market_snapshot_id'=ANY(v_markets);
  SELECT count(*) INTO v_observations FROM public.observations WHERE raw_job_id=ANY(v_ids);
  v_result := jsonb_build_object('policy_version','retention/1','source_id',p_source,
    'request_key',p_key,'checked_at',v_now,'retention_days',v_days,'applied',p_apply,
    'raw_deleted',cardinality(v_ids),'observations_deleted',v_observations,
    'market_deleted',cardinality(v_markets),'plans_deleted',cardinality(v_plans));
  IF NOT p_apply THEN RETURN v_result; END IF;
  DELETE FROM public.engine_records WHERE id=ANY(v_plans) OR id=ANY(v_markets);
  DELETE FROM public.observations WHERE raw_job_id=ANY(v_ids);
  DELETE FROM public.raw_jobs WHERE id=ANY(v_ids);
  INSERT INTO public.retention_runs(id,created_at,source_id,request_key,data)
    VALUES(gen_random_uuid()::text,v_now,p_source,p_key,v_result::json);
  RETURN v_result;
END; $$;
REVOKE ALL ON FUNCTION public.apply_source_retention(text,text,boolean) FROM PUBLIC;
"""


def upgrade():
    op.create_table(
        "retention_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_id", sa.String(80), sa.ForeignKey("sources.id"), nullable=False),
        sa.Column("request_key", sa.String(120), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.UniqueConstraint("source_id", "request_key"),
    )
    if op.get_bind().dialect.name == "postgresql":
        op.execute(TRIGGER)
        op.execute(FUNCTION)
        op.execute("""
          DO $$ BEGIN
            IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname='career_runtime') THEN
              REVOKE ALL ON public.retention_runs FROM career_runtime;
              REVOKE ALL ON FUNCTION public.apply_source_retention(text,text,boolean)
                FROM career_runtime;
            END IF;
            IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname='career_retention') THEN
              GRANT EXECUTE ON FUNCTION public.apply_source_retention(text,text,boolean)
                TO career_retention;
            END IF;
          END $$;
        """)


def downgrade():
    if op.get_bind().dialect.name == "postgresql":
        op.execute("DROP FUNCTION public.apply_source_retention(text,text,boolean)")
        op.execute("""CREATE OR REPLACE FUNCTION public.reject_raw_mutation() RETURNS trigger
          LANGUAGE plpgsql SET search_path = pg_catalog, pg_temp AS $$
          BEGIN RAISE EXCEPTION 'raw_jobs is immutable'; END; $$""")
    op.drop_table("retention_runs")
