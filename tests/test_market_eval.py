import hashlib
import json
from copy import deepcopy
from datetime import date

import pytest
from career_os.market_eval import Dataset, evaluate, main, scores
from career_os.workspace import TAXONOMY
from pydantic import ValidationError


def artifact(text="Python SQL", labels=None):
    return {
        "schema_version": "mention-gold/1",
        "dataset_id": "synthetic-test",
        "version": "1",
        "taxonomy_version": TAXONOMY["version"],
        "origin": "synthetic",
        "annotation_policy": "all-literal-mentions/1",
        "examples": [
            {
                "id": "e1",
                "source_id": "synthetic",
                "split": "holdout",
                "leakage_group": "group1",
                "text": text,
                "text_sha256": hashlib.sha256(text.encode()).hexdigest(),
                "observed_on": "2026-10-06",
                "expires_on": "2026-11-06",
                "source_reference": "synthetic:test",
                "policy_reference": "synthetic:test",
                "reviewer": "fixture-author",
                "labels": labels
                if labels is not None
                else [{"skill": "Python", "start": 0, "end": 6}],
            }
        ],
    }


def test_metrics_expose_false_positive_and_do_not_claim_market_quality():
    report = evaluate(Dataset.model_validate(artifact()), "holdout", date(2026, 10, 6))
    assert report["metrics"] == {
        "tp": 1,
        "fp": 1,
        "fn": 0,
        "precision": 0.5,
        "recall": 1.0,
        "f1": 2 / 3,
    }
    assert report["by_source"]["synthetic"] == report["metrics"]
    assert report["market_release_gate"] == "NOT_ASSESSED"
    assert "Python SQL" not in json.dumps(report)
    assert "fixture-author" not in json.dumps(report)


def test_undefined_denominators_are_not_perfect_scores():
    assert scores(0, 0, 0)["f1"] is None
    assert scores(0, 0, 2) == {
        "tp": 0,
        "fp": 0,
        "fn": 2,
        "precision": None,
        "recall": 0.0,
        "f1": 0.0,
    }


@pytest.mark.parametrize(
    "mutation", ["hash", "span", "skill", "duplicate_label", "duplicate_id", "taxonomy", "extra"]
)
def test_invalid_gold_is_rejected(mutation):
    data = artifact()
    example = data["examples"][0]
    if mutation == "hash":
        example["text"] = "tampered"
    elif mutation == "span":
        example["labels"][0]["end"] = 999
    elif mutation == "skill":
        example["labels"][0]["skill"] = "invented skill"
    elif mutation == "duplicate_label":
        example["labels"] *= 2
    elif mutation == "duplicate_id":
        data["examples"] *= 2
    elif mutation == "taxonomy":
        data["taxonomy_version"] = "future"
    else:
        example["unexpected"] = "secret"
    with pytest.raises(ValidationError):
        Dataset.model_validate(data)


@pytest.mark.parametrize("same_group", [True, False])
def test_split_leakage_by_group_or_normalized_text(same_group):
    data = artifact()
    second = deepcopy(data["examples"][0])
    second.update(id="e2", split="development")
    if same_group:
        second["text"] = "Python SQL Git"
        second["text_sha256"] = hashlib.sha256(second["text"].encode()).hexdigest()
    else:
        second["leakage_group"] = "different"
    data["examples"].append(second)
    with pytest.raises(ValidationError, match="development_holdout_leakage"):
        Dataset.model_validate(data)


@pytest.mark.parametrize("as_of", [date(2026, 10, 5), date(2026, 11, 6)])
def test_expired_or_future_data_fails_closed(as_of):
    with pytest.raises(ValueError, match="expired_or_future"):
        evaluate(Dataset.model_validate(artifact()), "holdout", as_of)


def test_empty_split_is_not_silent_success():
    with pytest.raises(ValueError, match="empty_selected_split"):
        evaluate(Dataset.model_validate(artifact()), "development", date(2026, 10, 6))


def test_cli_failure_redacts_input(tmp_path, monkeypatch, capsys):
    path = tmp_path / "private.json"
    path.write_text('{"private_personal_text":"DO_NOT_PRINT"}')
    monkeypatch.setattr("sys.argv", ["eval", str(path), "--split", "holdout"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2
    captured = capsys.readouterr()
    assert not captured.out
    assert "DO_NOT_PRINT" not in captured.err


def test_versioned_synthetic_fixture_is_reproducible():
    from pathlib import Path

    dataset = Dataset.model_validate_json(
        Path("tests/evals/mentions_synthetic_v1.json").read_text()
    )
    first = evaluate(dataset, "holdout", date(2026, 10, 6))
    assert first == evaluate(dataset, "holdout", date(2026, 10, 6))
    assert first["origin"] == "synthetic"
    # Policy v2 removes nested aliases without changing authored gold.
    assert first["metrics"]["tp"] == 6
    assert first["metrics"]["fp"] == 0
    assert first["metrics"]["fn"] == 0


def test_longest_alias_keeps_separate_occurrences_and_skills():
    from career_os.market import POLICY, extract_mentions

    text = "AWS Cloud AWS and SQL; AWS Cloud"
    mentions = extract_mentions(text)
    assert POLICY == "literal-mentions/2"
    assert [(m["skill"], m["span"], m["start"]) for m in mentions] == [
        ("AWS", "AWS Cloud", 0),
        ("AWS", "AWS", 10),
        ("SQL", "SQL", 18),
        ("AWS", "AWS Cloud", 23),
    ]
    assert all(m["requirement"] == "unknown" for m in mentions)
