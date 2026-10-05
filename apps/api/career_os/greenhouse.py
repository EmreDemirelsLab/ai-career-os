import re
from collections.abc import Iterable
from datetime import UTC, datetime
from html import unescape
from html.parser import HTMLParser
from typing import Any

from sqlalchemy import Engine
from sqlalchemy.orm import Session

from career_os.contracts import digest
from career_os.governance import assert_source_allowed
from career_os.ingestion import ingest
from career_os.models import Source
from career_os.network import bounded_json


class PlainText(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.hidden = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self.hidden += 1
        elif tag in {"p", "br", "li", "div"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self.hidden:
            self.hidden -= 1
        elif tag in {"p", "li", "div"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.hidden:
            self.parts.append(data)


class GreenhouseAdapter:
    version = "greenhouse-job-board/1"

    def __init__(self, source_id: str, board: str, company: str, payload: dict[str, Any]) -> None:
        jobs = payload.get("jobs")
        if not isinstance(jobs, list) or len(jobs) > 1000:
            raise ValueError("greenhouse_expected_at_most_1000_jobs")
        self._records = []
        for job in jobs:
            if not isinstance(job, dict):
                raise ValueError("greenhouse_invalid_record")
            parser = PlainText()
            parser.feed(unescape(str(job.get("content", ""))))
            self._records.append(
                dict(
                    source_id=source_id,
                    source_job_id=str(job["id"]) if job.get("id") is not None else "",
                    source_url=job.get("absolute_url", ""),
                    fetched_at=datetime.now(UTC).isoformat(),
                    title=job.get("title", ""),
                    company=company,
                    location=(job.get("location") or {}).get("name", "unknown"),
                    description="".join(parser.parts).strip(),
                    payload={"board": board},
                )
            )
        self.fingerprint = digest(
            {
                "adapter": self.version,
                "records": [
                    {k: v for k, v in r.items() if k != "fetched_at"} for r in self._records
                ],
            }
        )

    def records(self) -> Iterable[dict[str, Any]]:
        return self._records


def collect_greenhouse(engine: Engine, source_id: str, board: str, key: str) -> dict[str, Any]:
    if not re.fullmatch("[a-zA-Z0-9_-]{1,80}", board):
        raise ValueError("invalid_board_token")
    with Session(engine) as session:
        source = session.get(Source, source_id)
        if source is None:
            raise ValueError("source_not_found")
        assert_source_allowed(source)
        if source.collection_method != "greenhouse:" + board:
            raise ValueError("source_not_approved_for_this_board")
        company = source.name
    # Authorization is checked before network I/O; no arbitrary URL is accepted.
    payload = bounded_json(f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true")
    return ingest(engine, source_id, key, GreenhouseAdapter(source_id, board, company, payload))
