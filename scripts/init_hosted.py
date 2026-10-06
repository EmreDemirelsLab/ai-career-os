"""Prepare secrets locally; does not create hosting, DNS or deploy anything."""

import os
import re
import secrets
import sys
from pathlib import Path

domain = sys.argv[1] if len(sys.argv) > 1 else ""
if not re.fullmatch(r"(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}", domain):
    raise SystemExit("Usage: python3 scripts/init_hosted.py your-domain.example")
admin = secrets.token_hex(32)
runtime = secrets.token_hex(32)
lines = [
    f"CAREER_DOMAIN={domain}",
    f"CAREER_DB_ADMIN_PASSWORD={admin}",
    f"CAREER_DB_RUNTIME_PASSWORD={runtime}",
    f"CAREER_MIGRATION_DATABASE_URL=postgresql+psycopg://career:{admin}@postgres:5432/career",
    f"CAREER_RUNTIME_DATABASE_URL=postgresql+psycopg://career_runtime:{runtime}@postgres:5432/career",
    "CAREER_API_TOKEN=" + secrets.token_urlsafe(48),
    "CAREER_AI_ENABLED=false",
    "CAREER_AI_DAILY_CALLS=0",
    "CAREER_AI_MODEL=",
    "OPENAI_API_KEY=",
]
fd = os.open(Path(".env.hosted"), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(fd, "w") as out:
    out.write("\n".join(lines) + "\n")
print("Prepared .env.hosted without printing secrets. No deployment performed.")
