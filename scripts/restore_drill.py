"""Restore only into a newly created disposable database, never over existing data."""

import hashlib
import re
import subprocess
import sys
from pathlib import Path

from compose_command import compose_command

path = Path(sys.argv[1])
name = sys.argv[2] if len(sys.argv) > 2 else "career_restore_drill"
if not re.fullmatch(r"career_restore_[a-z0-9_]{1,40}", name):
    raise SystemExit("Restore drill requires a disposable career_restore_* database")
expected = path.with_suffix(path.suffix + ".sha256").read_text().strip()
if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
    raise SystemExit("Backup checksum mismatch")
base = [*compose_command(), "exec", "-T", "postgres"]
subprocess.run([*base, "createdb", "-U", "career", name], check=True)
with path.open("rb") as stream:
    subprocess.run(
        [*base, "pg_restore", "--exit-on-error", "--no-owner", "-U", "career", "-d", name],
        stdin=stream,
        check=True,
    )
# The restored database is disposable and not exposed to the application.
subprocess.run(
    [
        *base,
        "psql",
        "-U",
        "career",
        "-d",
        name,
        "-v",
        "ON_ERROR_STOP=1",
        "-c",
        "SELECT public.apply_source_retention(id, 'restore-drill', true) "
        "FROM public.sources WHERE source_type <> 'fixture';",
    ],
    check=True,
)
subprocess.run(
    [
        *base,
        "psql",
        "-U",
        "career",
        "-d",
        name,
        "-v",
        "ON_ERROR_STOP=1",
        "-c",
        "SELECT version_num FROM alembic_version; SELECT count(*) FROM raw_jobs; "
        "SELECT count(*) FROM learner_snapshots; SELECT count(*) FROM engine_records;",
    ],
    check=True,
)
print("Restore verified in the disposable database. Original database was not changed.")
