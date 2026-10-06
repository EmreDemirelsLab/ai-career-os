"""Reference only: viewing/copying this solution is assisted work, not independent proof."""

import hashlib
import json

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field


def validate_job(value):
    if not isinstance(value, dict) or set(value) != {"source_job_id", "title"}:
        raise ValueError("invalid_fields")
    clean = {}
    for key, item in value.items():
        if not isinstance(item, str) or not 1 <= len(item.strip()) <= 200:
            raise ValueError("invalid_text")
        clean[key] = item.strip()
    return clean


def create_schema(connection):
    connection.execute("PRAGMA foreign_keys=ON")
    connection.executescript("""
        CREATE TABLE IF NOT EXISTS sources(id INTEGER PRIMARY KEY, name TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS jobs(
          id INTEGER PRIMARY KEY, source_id INTEGER NOT NULL REFERENCES sources(id),
          external_id TEXT NOT NULL, UNIQUE(source_id, external_id));
    """)


def source_counts(connection):
    return connection.execute("""
        SELECT sources.name, COUNT(jobs.id) FROM sources
        LEFT JOIN jobs ON sources.id = jobs.source_id
        GROUP BY sources.id, sources.name ORDER BY sources.id
    """).fetchall()


class JobBody(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, strict=True)
    source_job_id: str = Field(min_length=1, max_length=200)
    title: str = Field(min_length=1, max_length=200)


def create_app():
    app = FastAPI()

    @app.post("/jobs", status_code=201)
    def post_job(body: JobBody):
        return body.model_dump()

    return app


def ingest_revision(store, record):
    expected = {"source_id", "source_job_id", "title", "description", "fetched_at"}
    if not isinstance(record, dict) or set(record) != expected:
        raise ValueError("invalid_fields")
    if any(not isinstance(x, str) or not x.strip() for x in record.values()):
        raise ValueError("invalid_text")
    key = (record["source_id"], record["source_job_id"])
    content = {k: record[k] for k in ("title", "description")}
    fingerprint = hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()
    old = store.get(key)
    state = "inserted" if old is None else ("duplicate" if old == fingerprint else "revised")
    store[key] = fingerprint
    return state
