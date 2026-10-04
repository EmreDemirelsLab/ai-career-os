import json
from pathlib import Path

import pytest
from career_os.config import Settings
from career_os.contracts import FixtureAdapter, JobEnvelope, digest
from pydantic import ValidationError


def test_hash_ignores_fetch_time_and_json_key_order():
    raw = json.loads(Path("tests/fixtures/jobs.json").read_text())[0]
    first = JobEnvelope.model_validate(raw)
    raw["fetched_at"] = "2026-10-05T21:00:00Z"
    second = JobEnvelope.model_validate(raw)
    assert digest(first.content()) == digest(second.content())
    assert digest({"a": 1, "b": 2}) == digest({"b": 2, "a": 1})
    raw["description"] = "Changed requirements"
    assert digest(first.content()) != digest(JobEnvelope.model_validate(raw).content())


@pytest.mark.parametrize(
    "field,value",
    [
        ("title", " "),
        ("source_url", "javascript:alert(1)"),
        ("fetched_at", "2026-10-04T21:00:00"),
        ("source_job_id", ""),
    ],
)
def test_invalid_envelope(field, value):
    raw = json.loads(Path("tests/fixtures/jobs.json").read_text())[0]
    raw[field] = value
    with pytest.raises(ValidationError):
        JobEnvelope.model_validate(raw)


def test_fixture_is_frozen():
    records = [{"title": "original"}]
    adapter = FixtureAdapter(records)
    records[0]["title"] = "modified"
    assert list(adapter.records()) == [{"title": "original"}]


def test_config_rejects_unsupported_database():
    with pytest.raises(ValidationError):
        Settings(database_url="mysql://localhost/db", _env_file=None)


def test_seed_aliases_resolve_and_role_ids_unique():
    skills = json.loads(Path("seed/skill_taxonomy_v0.1.json").read_text())
    names = {name for values in skills["categories"].values() for name in values}
    assert set(skills["aliases"].values()) <= names
    roles = json.loads(Path("seed/role_taxonomy_v0.1.json").read_text())["roles"]
    assert len({x["id"] for x in roles}) == len(roles)
