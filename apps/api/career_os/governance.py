import csv
from pathlib import Path

from sqlalchemy import Engine
from sqlalchemy.orm import Session

from career_os.models import Source


def assert_source_allowed(source: Source) -> None:
    if not source.enabled:
        raise ValueError("source_disabled")
    if (
        source.policy_status != "APPROVED"
        or not source.policy_reference
        or not source.reviewed_by
        or not source.retention_days
        or source.collection_method == "unreviewed"
    ):
        raise ValueError("source_policy_incomplete")


def seed_sources(engine: Engine, path: Path) -> None:
    with path.open() as stream, Session(engine) as session, session.begin():
        for row in csv.DictReader(stream):
            if session.get(Source, row["source_id"]) is None:
                session.add(
                    Source(
                        id=row["source_id"],
                        name=row["source_name"],
                        source_type=row["source_type"],
                        enabled=False,
                        policy_status=row["collection_policy_status"],
                    )
                )
        if session.get(Source, "DEMO") is None:
            session.add(
                Source(
                    id="DEMO",
                    name="Synthetic fixture",
                    source_type="fixture",
                    enabled=True,
                    policy_status="APPROVED",
                    collection_method="local_fixture",
                    policy_reference="docs/16_ARCHITECTURE_REVIEW_v1_3.md",
                    reviewed_by="repository",
                    retention_days=30,
                )
            )


def set_enabled(engine: Engine, source_id: str, enabled: bool) -> None:
    with Session(engine) as session, session.begin():
        source = session.get(Source, source_id)
        if source is None:
            raise ValueError("source_not_found")
        source.enabled = enabled
        if enabled:
            assert_source_allowed(source)
