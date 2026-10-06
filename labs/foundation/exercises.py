"""Implement these functions yourself. See README before opening reference.py."""


def validate_job(value):
    raise NotImplementedError("Week 1: validate and normalize without mutating input")


def create_schema(connection):
    raise NotImplementedError("Week 2: sources/jobs, foreign key and composite uniqueness")


def source_counts(connection):
    raise NotImplementedError("Week 2: include zero-job sources, order by source id")


def create_app():
    raise NotImplementedError("Week 3: stateless FastAPI POST /jobs, 201 or 422")


def ingest_revision(store, record):
    raise NotImplementedError("Week 4: identity versus content, ignore fetched_at in hash")
