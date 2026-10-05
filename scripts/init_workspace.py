"""Generate a local-only access key without printing it or overwriting existing settings."""

import secrets
from pathlib import Path

path = Path(".env")
if path.exists():
    raise SystemExit(".env already exists; preserve it and configure CAREER_API_TOKEN locally")
path.write_text(
    "DATABASE_URL=postgresql+psycopg://career:local_dev_only@localhost:5432/career\nCAREER_API_TOKEN="
    + secrets.token_urlsafe(48)
    + "\n"
)
path.chmod(0o600)
print("Created .env. Use its CAREER_API_TOKEN to sign in locally; do not share it.")
