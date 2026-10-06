"""Explicit maintenance interface; never registered as a web route."""

from typing import Any

from sqlalchemy import Engine, text


def retain_source(
    engine: Engine, source_id: str, key: str, *, apply: bool = False
) -> dict[str, Any]:
    if engine.dialect.name != "postgresql":
        raise ValueError("retention_requires_postgresql")
    if not source_id.strip() or len(source_id) > 80 or not key.strip() or len(key) > 120:
        raise ValueError("invalid_retention_input")
    with engine.begin() as connection:
        result = connection.scalar(
            text("SELECT public.apply_source_retention(:source,:key,:apply)"),
            {"source": source_id, "key": key, "apply": apply},
        )
        if not isinstance(result, dict):
            raise ValueError("invalid_retention_result")
        return result
