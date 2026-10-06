"""Private sampling metadata and annotation-review linkage; no collection authorization."""

import argparse
import json
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import Field, model_validator

from career_os.contracts import digest
from career_os.market_eval import Dataset, Example, Name, StrictModel

Sha = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


class SourcePolicy(StrictModel):
    source_id: Name
    status: Literal["pending", "approved", "revoked"]
    reference: Annotated[str, Field(min_length=1, max_length=500)]
    reviewer: Name
    reviewed_on: date
    valid_until: date
    retention_days: Annotated[int, Field(strict=True, ge=1, le=365)]

    @model_validator(mode="after")
    def dates(self) -> "SourcePolicy":
        if self.valid_until <= self.reviewed_on or not self.reference.strip():
            raise ValueError("invalid_policy")
        return self


class LabelReview(StrictModel):
    author: Name
    reviewer: Name
    decision: Literal["accepted", "changes_requested"]
    reviewed_on: date
    labels_fingerprint: Sha

    @model_validator(mode="after")
    def independence(self) -> "LabelReview":
        if self.author == self.reviewer:
            raise ValueError("independent_reviewer_required")
        return self


class Sample(StrictModel):
    id: Name
    source_id: Name
    company_id: Name
    source_reference: Annotated[str, Field(min_length=1, max_length=2000)]
    text_sha256: Sha
    observed_on: date
    expires_on: date
    geography: Literal["germany", "other_eu", "outside_eu", "unknown"]
    role: Literal["ai_engineer", "ml_engineer", "applied_ai", "llm_engineer", "other", "unknown"]
    seniority: Literal["entry", "mid", "senior", "unknown"]
    language: Literal["english_only_explicit", "german_required", "other", "unknown"]
    remote_scope: Literal[
        "onsite", "hybrid", "country_restricted", "unrestricted_explicit", "unknown"
    ]
    decision: Literal["include", "exclude", "pending"]
    exclusion_reason: (
        Literal["out_of_scope", "duplicate", "expired", "policy", "unavailable"] | None
    )
    leakage_group: Name
    split: Literal["development", "holdout", "unassigned"]
    review: LabelReview | None = None

    @model_validator(mode="after")
    def consistency(self) -> "Sample":
        if (self.decision == "exclude") != (self.exclusion_reason is not None):
            raise ValueError("exclusion_reason_mismatch")
        if self.expires_on <= self.observed_on or not self.source_reference.strip():
            raise ValueError("invalid_observation")
        return self


class Manifest(StrictModel):
    schema_version: Literal["sampling-manifest/1"]
    id: Name
    version: Name
    origin: Literal["real", "synthetic"]
    policies: Annotated[list[SourcePolicy], Field(min_length=1, max_length=1000)]
    samples: Annotated[list[Sample], Field(min_length=1, max_length=5000)]

    @model_validator(mode="after")
    def references(self) -> "Manifest":
        if len({p.source_id for p in self.policies}) != len(self.policies):
            raise ValueError("duplicate_source_policy")
        if len({s.id for s in self.samples}) != len(self.samples):
            raise ValueError("duplicate_sample")
        policies = {p.source_id: p for p in self.policies}
        groups: dict[str, str] = {}
        hashes: dict[str, str] = {}
        for sample in self.samples:
            if sample.source_id not in policies:
                raise ValueError("missing_source_policy")
            if sample.decision != "include" or sample.split == "unassigned":
                continue
            for mapping, key in ((groups, sample.leakage_group), (hashes, sample.text_sha256)):
                if key in mapping and mapping[key] != sample.split:
                    raise ValueError("split_leakage")
                mapping[key] = sample.split
        return self


def labels_fingerprint(example: Example) -> str:
    return digest(
        [x.model_dump() for x in sorted(example.labels, key=lambda x: (x.skill, x.start, x.end))]
    )


def inspect_manifest(
    manifest: Manifest, as_of: date, dataset: Dataset | None = None
) -> dict[str, Any]:
    policies = {p.source_id: p for p in manifest.policies}
    included = [s for s in manifest.samples if s.decision == "include"]
    for sample in included:
        policy = policies[sample.source_id]
        if not (
            policy.status == "approved"
            and policy.reviewed_on <= sample.observed_on <= as_of < policy.valid_until
        ):
            raise ValueError("included_source_policy_not_current")
        if not (
            as_of < sample.expires_on <= sample.observed_on + timedelta(days=policy.retention_days)
        ):
            raise ValueError("included_retention_invalid")
    reviewed = 0
    if dataset is not None:
        if dataset.origin != manifest.origin:
            raise ValueError("origin_mismatch")
        samples = {s.id: s for s in included}
        for example in dataset.examples:
            matched = samples.get(example.id)
            if matched is None:
                raise ValueError("gold_not_in_included_sample")
            sample = matched
            policy = policies[sample.source_id]
            for field in (
                "source_id",
                "source_reference",
                "text_sha256",
                "observed_on",
                "expires_on",
                "leakage_group",
                "split",
            ):
                if getattr(example, field) != getattr(sample, field):
                    raise ValueError("gold_provenance_mismatch")
            if example.policy_reference != policy.reference:
                raise ValueError("gold_policy_mismatch")
            review = sample.review
            if (
                review is None
                or review.decision != "accepted"
                or not sample.observed_on <= review.reviewed_on <= as_of
            ):
                raise ValueError("gold_review_pending")
            if (
                review.reviewer != example.reviewer
                or review.labels_fingerprint != labels_fingerprint(example)
            ):
                raise ValueError("gold_review_stale")
            reviewed += 1
    return {
        "manifest_id": manifest.id,
        "manifest_version": manifest.version,
        "manifest_fingerprint": digest(manifest.model_dump(mode="json")),
        "origin": manifest.origin,
        "as_of": as_of.isoformat(),
        "decisions": dict(Counter(s.decision for s in manifest.samples)),
        "exclusions": dict(
            Counter(s.exclusion_reason for s in manifest.samples if s.exclusion_reason)
        ),
        "included_count": len(included),
        "coverage": {
            field: dict(sorted(Counter(getattr(s, field) for s in included).items()))
            for field in (
                "geography",
                "role",
                "seniority",
                "language",
                "remote_scope",
                "source_id",
                "company_id",
                "split",
            )
        },
        "linked_reviewed_examples": reviewed,
        "dataset_fingerprint": digest(dataset.model_dump(mode="json")) if dataset else None,
        "market_release_gate": "NOT_ASSESSED",
        "limitations": [
            "Counts describe this selected sample, not the labor market.",
            "Distinct reviewer tokens do not prove independent human review.",
            "Policy metadata does not grant access or verify source terms.",
            "Excluded/pending entries are metadata only; operator retention still applies.",
        ],
    }


def read_bounded(path: Path) -> bytes:
    with path.open("rb") as stream:
        body = stream.read(5_000_001)
    if len(body) > 5_000_000:
        raise ValueError("artifact_too_large")
    return body


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Private sampling/review linkage audit; no network"
    )
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--dataset", type=Path)
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    args = parser.parse_args()
    try:
        manifest = Manifest.model_validate_json(read_bounded(args.manifest))
        dataset = Dataset.model_validate_json(read_bounded(args.dataset)) if args.dataset else None
        report = inspect_manifest(manifest, args.as_of, dataset)
    except (ValueError, OSError):
        parser.exit(2, "Sampling audit refused: check policy, dates, provenance and review.\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
