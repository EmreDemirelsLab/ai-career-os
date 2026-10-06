"""Small offline engineering examples, not production ML/LLM implementations."""

import hashlib
import json
import math
from urllib.parse import urlsplit


def finite(values):
    if any(type(x) not in (int, float) or not math.isfinite(x) for x in values):
        raise ValueError("Expected finite numbers")


def loss_gradient(xs, ys, weight):
    """Week 9: MSE and d(MSE)/dw for y_hat=w*x, without autograd."""
    if not xs or len(xs) != len(ys):
        raise ValueError("Nonempty aligned data required")
    finite([*xs, *ys, weight])
    errors = [weight * x - y for x, y in zip(xs, ys, strict=True)]
    return sum(e * e for e in errors) / len(xs), 2 * sum(
        e * x for e, x in zip(errors, xs, strict=True)
    ) / len(xs)


def train_linear(xs, ys, validation_x, validation_y, lr, steps):
    """Week 10: train-only updates and separate validation loss; initial w=0."""
    finite([lr])
    if lr <= 0 or type(steps) is not int or not 1 <= steps <= 10000:
        raise ValueError("Invalid training settings")
    loss_gradient(validation_x, validation_y, 0)
    weight, history = 0.0, []
    for _ in range(steps):
        _, gradient = loss_gradient(xs, ys, weight)
        weight -= lr * gradient
        finite([weight])
        history.append(
            {
                "train": loss_gradient(xs, ys, weight)[0],
                "validation": loss_gradient(validation_x, validation_y, weight)[0],
            }
        )
    return {"weight": weight, "history": history}


def experiment_id(config):
    """Week 11: identity requires data/code versions as well as hyperparameters."""
    required = {"data_version", "code_version", "seed", "parameters"}
    if set(config) != required or not config["data_version"] or not config["code_version"]:
        raise ValueError("Incomplete experiment provenance")
    body = json.dumps(config, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(body.encode()).hexdigest()


def predict_batch(model, values):
    """Week 12: bounded inference contract, no executable pickle or network."""
    if set(model) != {"version", "weight"} or not isinstance(model["version"], str):
        raise ValueError("Invalid model manifest")
    if not model["version"].strip() or not 1 <= len(values) <= 100:
        raise ValueError("Missing version or invalid batch size")
    finite([model["weight"], *values])
    predictions = [model["weight"] * x for x in values]
    finite(predictions)
    return {"model_version": model["version"], "predictions": predictions}


def pack_context(chunks, capacity, reserved):
    """Week 13: input token IDs from an external tokenizer; never character counts."""
    if type(capacity) is not int or type(reserved) is not int or not 0 <= reserved <= capacity:
        raise ValueError("Invalid context budget")
    if any(type(t) is not int or t < 0 for chunk in chunks for t in chunk):
        raise ValueError("Invalid token ID")
    result, used = [], 0
    for index, chunk in enumerate(chunks):
        if used + len(chunk) <= capacity - reserved:
            result.append(index)
            used += len(chunk)
    return {"indices": result, "input_tokens": used, "reserved_tokens": reserved}


def cosine_rank(query, documents, k):
    """Week 14: supplied vectors, deterministic document-ID tie break."""
    if not query or type(k) is not int or k < 1:
        raise ValueError("Invalid query or k")
    finite(query)
    qnorm = math.hypot(*query)
    if qnorm == 0:
        raise ValueError("Zero query vector")
    scored = []
    for doc_id, vector in documents.items():
        if len(vector) != len(query):
            raise ValueError("Dimension mismatch")
        finite(vector)
        norm = math.hypot(*vector)
        if norm == 0:
            raise ValueError("Zero document vector")
        score = sum((a / qnorm) * (b / norm) for a, b in zip(query, vector, strict=True))
        scored.append((doc_id, score))
    return sorted(scored, key=lambda item: (-item[1], item[0]))[:k]


def validate_citations(claims, documents):
    """Week 15: exact quote provenance only; this cannot establish entailment."""
    if not claims:
        return {"status": "abstain", "checked": 0}
    for claim in claims:
        if set(claim) != {"claim", "source_id", "quote"} or not claim["claim"].strip():
            raise ValueError("Invalid claim")
        quote = claim["quote"]
        if not isinstance(quote, str) or not quote.strip():
            raise ValueError("Empty quote")
        if claim["source_id"] not in documents or quote not in documents[claim["source_id"]]:
            raise ValueError("Unsupported citation")
    return {"status": "quotes_found_entailment_unassessed", "checked": len(claims)}


def retrieval_eval(gold, ranked):
    """Week 16: macro recall at supplied cutoff; exact case alignment required."""
    if set(gold) != set(ranked):
        raise ValueError("Missing or extra evaluated cases")
    recalls, unanswerable, correct_abstentions = [], 0, 0
    for case, relevant in gold.items():
        if len(ranked[case]) != len(set(ranked[case])):
            raise ValueError("Duplicate retrieved IDs")
        if relevant:
            recalls.append(len(set(relevant) & set(ranked[case])) / len(set(relevant)))
        else:
            unanswerable += 1
            correct_abstentions += not ranked[case]
    return {
        "cases": len(gold),
        "answerable": len(recalls),
        "recall": sum(recalls) / len(recalls) if recalls else None,
        "abstention_accuracy": correct_abstentions / unanswerable if unanswerable else None,
    }


def dispatch_read(call, documents):
    """Week 17: allowlisted read-only in-memory tool; never eval/shell/HTTP."""
    if set(call) != {"name", "arguments"} or call["name"] != "read_document":
        raise ValueError("Tool not allowed")
    args = call["arguments"]
    if not isinstance(args, dict) or set(args) != {"id"} or not isinstance(args["id"], str):
        raise ValueError("Invalid arguments")
    if args["id"] not in documents:
        raise ValueError("Document not allowed")
    return documents[args["id"]]


def retry_delay(attempt, status):
    """Week 18: bounded schedule; caller must separately ensure safe side effects."""
    if type(attempt) is not int or attempt < 1 or type(status) is not int:
        raise ValueError("Invalid attempt/status")
    if attempt >= 3 or status not in {429, 500, 502, 503, 504}:
        return None
    return 5 * 2 ** (attempt - 1)


def compare_candidate(baseline, candidate, min_gain, max_cost):
    """Week 19: illustrative predeclared gate; no statistical significance claim."""
    if not baseline["eval_version"] or baseline["eval_version"] != candidate["eval_version"]:
        raise ValueError("Different evaluation sets")
    finite([baseline["quality"], candidate["quality"], candidate["cost"], min_gain, max_cost])
    if not 0 <= baseline["quality"] <= 1 or not 0 <= candidate["quality"] <= 1:
        raise ValueError("Invalid quality")
    if min_gain < 0 or max_cost < 0 or candidate["cost"] < 0:
        raise ValueError("Invalid policy")
    return candidate["quality"] - baseline["quality"] >= min_gain and candidate["cost"] <= max_cost


def request_cost(input_tokens, output_tokens, input_per_million, output_per_million):
    """Week 20: operator-supplied rates, no hardcoded current provider prices."""
    if any(type(x) is not int or x < 0 for x in (input_tokens, output_tokens)):
        raise ValueError("Invalid token usage")
    finite([input_per_million, output_per_million])
    if min(input_per_million, output_per_million) < 0:
        raise ValueError("Invalid prices")
    return (input_tokens * input_per_million + output_tokens * output_per_million) / 1_000_000


def safe_event(payload):
    """Week 21: field allowlist; arbitrary user text is never logged."""
    if payload.get("status") not in {"ok", "failed"}:
        raise ValueError("Invalid event status")
    duration = payload.get("duration_ms")
    finite([duration])
    if duration < 0:
        raise ValueError("Invalid duration")
    return {"status": payload["status"], "duration_ms": duration}


def service_summary(events):
    """Week 22: nearest-rank p95 and error rate, with sample size."""
    clean = [safe_event(x) for x in events]
    durations = sorted(x["duration_ms"] for x in clean)
    n = len(clean)
    return {
        "n": n,
        "error_rate": sum(x["status"] == "failed" for x in clean) / n if n else None,
        "p95_ms": durations[math.ceil(0.95 * n) - 1] if n else None,
    }


def decision_gaps(record):
    """Week 23: structural ADR checklist; prose quality remains human-reviewed."""
    required = ("context", "decision", "alternative", "tradeoff", "evidence", "rollback")
    return [
        key for key in required if not isinstance(record.get(key), str) or not record[key].strip()
    ]


def claim_inventory(claims, evidence):
    """Week 24: reject invented artifact links; don't certify factual claims."""
    result = []
    for claim in claims:
        if set(claim) != {"text", "evidence_id"} or not claim["text"].strip():
            raise ValueError("Invalid claim")
        item = evidence.get(claim["evidence_id"])
        if item is None:
            raise ValueError("Missing evidence")
        url = urlsplit(item["url"])
        if url.scheme != "https" or not url.netloc or url.username or url.password:
            raise ValueError("Invalid artifact URL")
        if item["assistance"] not in {"independent", "assisted", "generated"}:
            raise ValueError("Missing assistance provenance")
        result.append({**claim, **item, "status": "linked_not_verified"})
    return result
