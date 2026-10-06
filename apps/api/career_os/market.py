"""Deterministic, evidence-linked mentions; not a semantic requirements classifier."""

import json
import re
from collections import Counter
from datetime import UTC, datetime, timedelta
from importlib.resources import files
from typing import Any

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from career_os.contracts import digest
from career_os.governance import assert_source_allowed
from career_os.models import Observation, RawJob, Source
from career_os.workspace import SKILLS, TAXONOMY

GRAPH: dict[str, Any] = json.loads(files("career_os").joinpath("skill_graph.json").read_text())
POLICY = "literal-mentions/2"


def extract_mentions(text: str) -> list[dict[str, Any]]:
    aliases = {**{s: s for s in SKILLS}, **TAXONOMY["aliases"]}
    found: dict[tuple[str, int, int], dict[str, Any]] = {}
    for alias, canonical in sorted(aliases.items(), key=lambda p: (-len(p[0]), p[0])):
        for match in re.finditer(r"(?<!\w)" + re.escape(alias) + r"(?!\w)", text, re.IGNORECASE):
            start, end = match.span()
            found[(canonical, start, end)] = dict(
                skill=canonical,
                start=start,
                end=end,
                span=text[start:end],
                status="mention_only",
                requirement="unknown",
            )
    # For one canonical skill, keep maximal spans; separate occurrences survive.
    # Sorting avoids quadratic pairwise comparisons on repetitive source content.
    maximal = []
    furthest: dict[str, int] = {}
    for mention in sorted(found.values(), key=lambda x: (x["skill"], x["start"], -x["end"])):
        skill = mention["skill"]
        if mention["end"] <= furthest.get(skill, -1):
            continue
        maximal.append(mention)
        furthest[skill] = mention["end"]
    return sorted(maximal, key=lambda x: (x["start"], x["end"], x["skill"]))


def retention_read_lock(session: Session) -> None:
    if session.get_bind().dialect.name == "postgresql":
        session.execute(text("SELECT pg_advisory_xact_lock_shared(71420601)"))


def market_snapshot(session: Session, source_ids: list[str], include_demo: bool) -> dict[str, Any]:
    retention_read_lock(session)
    sources = list(session.scalars(select(Source).where(Source.id.in_(source_ids))))
    if len(sources) != len(set(source_ids)):
        raise ValueError("source_not_found")
    for source in sources:
        assert_source_allowed(source)
        if source.source_type == "fixture" and not include_demo:
            raise ValueError("synthetic_source_requires_explicit_opt_in")
    retention = {s.id: s.retention_days for s in sources}
    fixture_ids = {s.id for s in sources if s.source_type == "fixture"}
    last_seen = dict(
        session.execute(
            select(Observation.raw_job_id, func.max(Observation.fetched_at)).group_by(
                Observation.raw_job_id
            )
        ).all()
    )
    candidates = session.scalars(select(RawJob).where(RawJob.source_id.in_(source_ids)))
    latest: dict[tuple[str, str], tuple[datetime, RawJob]] = {}
    now = datetime.now(UTC)
    for row in candidates:
        seen = last_seen.get(row.id, row.fetched_at)
        if seen.tzinfo is None:
            seen = seen.replace(tzinfo=UTC)
        if row.source_id not in fixture_ids and seen < now - timedelta(
            days=retention[row.source_id] or 1
        ):
            continue
        key = (row.source_id, row.source_job_id)
        if key not in latest or (seen, row.id) > (latest[key][0], latest[key][1].id):
            latest[key] = (seen, row)
    jobs = []
    fingerprints: set[str] = set()
    counts: Counter[str] = Counter()
    duplicate_ids = []
    for _, row in sorted(latest.values(), key=lambda item: item[1].id):
        c = row.content
        normalized = {
            k: " ".join(str(c.get(k, "")).casefold().split())
            for k in ["title", "company", "location", "description"]
        }
        fp = digest(normalized)
        if fp in fingerprints:
            duplicate_ids.append(row.id)
            continue
        fingerprints.add(fp)
        text = str(c.get("title", "")) + "\n" + str(c.get("description", ""))
        mentions = extract_mentions(text)
        counts.update({m["skill"] for m in mentions})
        jobs.append(
            dict(
                raw_id=row.id,
                content_hash=row.content_hash,
                source_id=row.source_id,
                source_url=row.source_url,
                title=c.get("title"),
                company=c.get("company"),
                location=c.get("location"),
                mentions=mentions,
            )
        )
    return dict(
        policy_version=POLICY,
        taxonomy_version=TAXONOMY["version"],
        source_ids=sorted(source_ids),
        synthetic=any(s.source_type == "fixture" for s in sources),
        sample_size=len(jobs),
        skill_counts=dict(sorted(counts.items())),
        jobs=jobs,
        exact_duplicates=duplicate_ids,
        scope="Reviewed selected sources; latest observed revision within retention window.",
        limitations=[
            "Literal mentions include negated/preferred/contextual mentions.",
            "No population representativeness or mandatory-requirement inference.",
            "Exact normalized dedupe only; near duplicates may remain.",
        ],
    )


def validate_graph() -> None:
    nodes = {n["id"]: n for n in GRAPH["nodes"]}
    if len(nodes) != len(GRAPH["nodes"]):
        raise ValueError("duplicate_graph_id")
    visited: set[str] = set()
    active: set[str] = set()

    def visit(key: str) -> None:
        if key in active:
            raise ValueError("cyclic_graph")
        if key in visited:
            return
        if key not in nodes:
            raise ValueError("unknown_prerequisite")
        active.add(key)
        for dep in nodes[key]["prerequisites"]:
            visit(dep)
        active.remove(key)
        visited.add(key)

    for key in nodes:
        visit(key)


def adaptive_plan(
    market: dict[str, Any], evidence: list[dict[str, Any]], target_skills: list[str]
) -> dict[str, Any]:
    validate_graph()
    nodes = {n["id"]: n for n in GRAPH["nodes"]}
    by_skill = {n["skill"]: n["id"] for n in GRAPH["nodes"]}
    if not target_skills or not set(target_skills) <= SKILLS:
        raise ValueError("unknown_or_empty_target_skills")
    # Evidence changes review emphasis, never certifies prerequisites as mastered.
    evidence_skills = {
        e["skill"]
        for e in evidence
        if e.get("assistance") == "independent"
        and e.get("verifier") == "external_review"
        and e.get("review_reference")
    }
    needed: set[str] = set()

    def include(key: str) -> None:
        if key in needed:
            return
        needed.add(key)
        for dep in nodes[key]["prerequisites"]:
            include(dep)

    for skill in target_skills:
        include(by_skill[skill])
    ordered = []
    remaining = set(needed)
    while remaining:
        ready = [n for n in remaining if not set(nodes[n]["prerequisites"]) & remaining]
        chosen = sorted(
            ready, key=lambda n: (-market["skill_counts"].get(nodes[n]["skill"], 0), n)
        )[0]
        node = nodes[chosen]
        ordered.append(
            {
                **node,
                "observed_job_mentions": market["skill_counts"].get(node["skill"], 0),
                "action": "independent_recheck"
                if node["skill"] in evidence_skills
                else "learn_then_demonstrate",
            }
        )
        remaining.remove(chosen)
    return dict(
        graph_version=GRAPH["version"],
        policy_version="prerequisite-demand/1",
        target_skills=target_skills,
        sequence=ordered,
        notice="Demand prioritizes ready prerequisites only. Counts are sample mentions, "
        "not mastery "
        "or hiring probability. External-review references are self-entered assertions.",
    )
