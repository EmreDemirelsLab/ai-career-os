from copy import deepcopy
from datetime import date

import pytest
from career_os.market_eval import Dataset
from career_os.sampling import Manifest, inspect_manifest, labels_fingerprint
from pydantic import ValidationError
from test_market_eval import artifact

TODAY = date(2026, 10, 6)


def bundle():
    data = artifact()
    data["examples"][0]["expires_on"] = "2026-11-05"
    data["examples"][0]["reviewer"] = "reviewer-two"
    gold = Dataset.model_validate(data)
    example = gold.examples[0]
    item = {
        k: v
        for k, v in example.model_dump(mode="json").items()
        if k not in ("text", "labels", "reviewer", "policy_reference")
    }
    item.update(
        company_id="company-one",
        geography="germany",
        role="ai_engineer",
        seniority="unknown",
        language="unknown",
        remote_scope="unknown",
        decision="include",
        exclusion_reason=None,
        review={
            "author": "author-one",
            "reviewer": "reviewer-two",
            "decision": "accepted",
            "reviewed_on": "2026-10-06",
            "labels_fingerprint": labels_fingerprint(example),
        },
    )
    return {
        "schema_version": "sampling-manifest/1",
        "id": "synthetic",
        "version": "1",
        "origin": "synthetic",
        "policies": [
            {
                "source_id": "synthetic",
                "status": "approved",
                "reference": example.policy_reference,
                "reviewer": "policy-reviewer",
                "reviewed_on": "2026-10-01",
                "valid_until": "2026-12-01",
                "retention_days": 30,
            }
        ],
        "samples": [item],
    }, gold


def test_review_linkage_counts_missingness_without_market_claims():
    raw, gold = bundle()
    report = inspect_manifest(Manifest.model_validate(raw), TODAY, gold)
    assert report["linked_reviewed_examples"] == 1
    assert report["coverage"]["seniority"] == {"unknown": 1}
    assert report["market_release_gate"] == "NOT_ASSESSED"
    assert "reviewer-two" not in str(report)
    assert "Python SQL" not in str(report)


@pytest.mark.parametrize(
    "change",
    [
        "revoked",
        "expired_policy",
        "retention",
        "future",
        "excluded",
        "pending_review",
        "changed_labels",
        "different_source",
        "origin",
    ],
)
def test_ineligible_or_stale_gold_is_rejected(change):
    raw, gold = bundle()
    sample = raw["samples"][0]
    if change == "revoked":
        raw["policies"][0]["status"] = "revoked"
    elif change == "expired_policy":
        raw["policies"][0]["valid_until"] = "2026-10-06"
    elif change == "retention":
        raw["policies"][0]["retention_days"] = 1
    elif change == "future":
        sample["observed_on"] = "2026-10-07"
    elif change == "excluded":
        sample.update(decision="exclude", exclusion_reason="out_of_scope")
    elif change == "pending_review":
        sample["review"] = None
    elif change == "changed_labels":
        sample["review"]["labels_fingerprint"] = "0" * 64
    elif change == "different_source":
        sample["source_reference"] = "different"
    else:
        raw["origin"] = "real"
    with pytest.raises(ValueError):
        inspect_manifest(Manifest.model_validate(raw), TODAY, gold)


def test_self_review_and_cross_split_leakage_rejected():
    raw, _ = bundle()
    raw["samples"][0]["review"]["reviewer"] = "author-one"
    with pytest.raises(ValidationError, match="independent_reviewer"):
        Manifest.model_validate(raw)
    raw, _ = bundle()
    second = deepcopy(raw["samples"][0])
    second.update(id="second", split="development")
    raw["samples"].append(second)
    with pytest.raises(ValidationError, match="split_leakage"):
        Manifest.model_validate(raw)


def test_unreviewed_candidates_can_be_reported_but_not_linked_to_gold():
    raw, gold = bundle()
    raw["policies"][0]["status"] = "pending"
    raw["samples"][0]["decision"] = "pending"
    manifest = Manifest.model_validate(raw)
    report = inspect_manifest(manifest, TODAY)
    assert report["included_count"] == 0
    assert report["decisions"] == {"pending": 1}
    with pytest.raises(ValueError, match="gold_not_in_included"):
        inspect_manifest(manifest, TODAY, gold)
