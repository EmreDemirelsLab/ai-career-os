"""Offline exact-span evaluation. No model calls, source collection or market inference."""

import argparse
import hashlib
import json
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from career_os.contracts import digest
from career_os.market import POLICY, extract_mentions
from career_os.workspace import SKILLS, TAXONOMY

Name = Annotated[str, Field(min_length=1, max_length=120, pattern=r"^[a-zA-Z0-9_.:/-]+$")]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Label(StrictModel):
    skill: str
    start: Annotated[int, Field(strict=True, ge=0)]
    end: Annotated[int, Field(strict=True, gt=0)]


class Example(StrictModel):
    id: Name
    source_id: Name
    split: Literal["development", "holdout"]
    leakage_group: Name
    text: Annotated[str, Field(min_length=1, max_length=100_000)]
    text_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    observed_on: date
    expires_on: date
    source_reference: Annotated[str, Field(min_length=1, max_length=2000)]
    policy_reference: Annotated[str, Field(min_length=1, max_length=500)]
    reviewer: Name
    labels: Annotated[list[Label], Field(max_length=1000)]

    @model_validator(mode="after")
    def validate_evidence(self) -> "Example":
        if hashlib.sha256(self.text.encode()).hexdigest() != self.text_sha256:
            raise ValueError("text_hash_mismatch")
        if self.expires_on <= self.observed_on:
            raise ValueError("invalid_retention_window")
        keys = [(x.skill, x.start, x.end) for x in self.labels]
        if len(set(keys)) != len(keys):
            raise ValueError("duplicate_label")
        for label in self.labels:
            if label.skill not in SKILLS or not 0 <= label.start < label.end <= len(self.text):
                raise ValueError("invalid_skill_or_span")
        return self


class Dataset(StrictModel):
    schema_version: Literal["mention-gold/1"]
    dataset_id: Name
    version: Name
    taxonomy_version: str
    origin: Literal["synthetic", "real"]
    annotation_policy: Literal["all-literal-mentions/1"]
    examples: Annotated[list[Example], Field(min_length=1, max_length=1000)]

    @model_validator(mode="after")
    def validate_dataset(self) -> "Dataset":
        if self.taxonomy_version != TAXONOMY["version"]:
            raise ValueError("taxonomy_version_mismatch")
        ids = [x.id for x in self.examples]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate_example_id")
        groups: dict[str, str] = {}
        hashes: dict[str, str] = {}
        for example in self.examples:
            normalized = " ".join(example.text.casefold().split())
            for lookup, key in ((groups, example.leakage_group), (hashes, normalized)):
                if key in lookup and lookup[key] != example.split:
                    raise ValueError("development_holdout_leakage")
                lookup[key] = example.split
        return self


def scores(tp: int, fp: int, fn: int) -> dict[str, int | float | None]:
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": tp / (tp + fp) if tp + fp else None,
        "recall": tp / (tp + fn) if tp + fn else None,
        "f1": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None,
    }


def evaluate(dataset: Dataset, split: str, as_of: date) -> dict[str, Any]:
    if split not in {"development", "holdout"}:
        raise ValueError("invalid_split")
    selected = [x for x in dataset.examples if x.split == split]
    if not selected:
        raise ValueError("empty_selected_split")
    # Reject the whole artifact: expired unselected content also must not be retained.
    if any(x.expires_on <= as_of or x.observed_on > as_of for x in dataset.examples):
        raise ValueError("expired_or_future_dataset")
    totals: Counter[str] = Counter()
    per_source: dict[str, Counter[str]] = {}
    errors = []
    for example in selected:
        gold = {(x.skill, x.start, x.end) for x in example.labels}
        predicted = {(x["skill"], x["start"], x["end"]) for x in extract_mentions(example.text)}
        counts = {
            "tp": len(gold & predicted),
            "fp": len(predicted - gold),
            "fn": len(gold - predicted),
        }
        totals.update(counts)
        per_source.setdefault(example.source_id, Counter()).update(counts)
        # No text, snippets, URLs, reviewer identities or source documents in reports.
        errors.append({"example_id": example.id, **counts})
    return {
        "dataset_id": dataset.dataset_id,
        "dataset_version": dataset.version,
        "dataset_fingerprint": digest(dataset.model_dump(mode="json")),
        "extractor_policy": POLICY,
        "annotation_policy": dataset.annotation_policy,
        "taxonomy_version": dataset.taxonomy_version,
        "as_of": as_of.isoformat(),
        "origin": dataset.origin,
        "split": split,
        "sample_size": len(selected),
        "metrics": scores(totals["tp"], totals["fp"], totals["fn"]),
        "by_source": {
            key: scores(c["tp"], c["fp"], c["fn"]) for key, c in sorted(per_source.items())
        },
        "examples": errors,
        "market_release_gate": "NOT_ASSESSED",
        "limitations": [
            "Exact skill/span matching only; negated/preferred mentions count.",
            "No semantic requirement, eligibility, dedupe or representativeness assessment.",
            "Reviewer metadata is an assertion, not proof of independent human review.",
            "Synthetic results do not measure real-market quality.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Offline literal-mention evaluation; JSON to stdout"
    )
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--split", required=True, choices=["development", "holdout"])
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    args = parser.parse_args()
    try:
        with args.dataset.open("rb") as stream:
            body = stream.read(5_000_001)
        if len(body) > 5_000_000:
            raise ValueError("dataset_exceeds_5MB")
        dataset = Dataset.model_validate_json(body)
        report = evaluate(dataset, args.split, args.as_of)
    except (OSError, ValueError, ValidationError):
        parser.exit(
            2,
            "Evaluation refused: check schema, provenance, splits and retention. "
            "No input content logged.\n",
        )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
