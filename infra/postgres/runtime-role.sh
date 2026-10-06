#!/bin/sh
set -eu
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<'SQL'
\getenv runtime_password CAREER_DB_RUNTIME_PASSWORD
CREATE ROLE career_retention NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE;
CREATE ROLE career_runtime LOGIN PASSWORD :'runtime_password' NOSUPERUSER NOCREATEDB NOCREATEROLE;
GRANT CONNECT ON DATABASE career TO career_runtime;
GRANT USAGE ON SCHEMA public TO career_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO career_runtime;
ALTER DEFAULT PRIVILEGES FOR ROLE career IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO career_runtime;
DO $$ BEGIN
  IF to_regclass('public.retention_runs') IS NOT NULL THEN
    REVOKE ALL ON public.retention_runs FROM career_runtime;
    GRANT EXECUTE ON FUNCTION public.apply_source_retention(text,text,boolean) TO career_retention;
  END IF;
END $$;
SQL
