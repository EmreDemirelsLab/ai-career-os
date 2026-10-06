import hashlib
import json
from collections.abc import Iterable
from typing import Annotated, Any, Protocol, cast

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, HttpUrl

NonEmpty = Annotated[str, Field(min_length=1, max_length=200)]


class JobEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    source_id: Annotated[str, Field(min_length=1, max_length=80)]
    source_job_id: NonEmpty
    source_url: Annotated[HttpUrl, Field(max_length=2000)]
    fetched_at: AwareDatetime
    published_at: AwareDatetime | None = None
    title: NonEmpty
    company: NonEmpty
    location: NonEmpty
    description: Annotated[str, Field(min_length=1, max_length=100_000)]
    payload: dict[str, Any] = Field(default_factory=dict)

    def content(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"fetched_at"})


def digest(value: object) -> str:
    serialized = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )
    return hashlib.sha256(serialized.encode()).hexdigest()


class Adapter(Protocol):
    version: str
    fingerprint: str

    def records(self) -> Iterable[dict[str, Any]]: ...


class FixtureAdapter:
    version = "fixture/1.0"

    def __init__(self, records: list[dict[str, Any]]) -> None:
        # Freeze the input so fingerprint and iteration cannot diverge.
        self._records = json.loads(json.dumps(records, allow_nan=False))
        self.fingerprint = digest({"version": self.version, "records": self._records})

    def records(self) -> Iterable[dict[str, Any]]:
        return cast(list[dict[str, Any]], json.loads(json.dumps(self._records)))
