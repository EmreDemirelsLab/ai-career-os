"""Assisted reference. Tiny synthetic checks do not establish generalization or mastery."""

import math


def summarize(frame):
    if not {"customer_id", "value", "target"} <= set(frame.columns):
        raise ValueError("missing_columns")
    if not frame["target"].isin([0, 1]).all():
        raise ValueError("invalid_target")
    missing = int(frame["value"].isna().sum())
    return dict(
        rows=len(frame),
        missing_values=missing,
        missing_rate=missing / len(frame) if len(frame) else None,
        target_counts={str(k): int((frame["target"] == k).sum()) for k in (0, 1)},
    )


def prepare_split(frame, test_customers):
    summarize(frame)
    if frame["customer_id"].isna().any() or not set(test_customers) <= set(frame["customer_id"]):
        raise ValueError("invalid_groups")
    mask = frame["customer_id"].isin(test_customers)
    train, test = frame.loc[~mask].copy(), frame.loc[mask].copy()
    if train.empty or test.empty:
        raise ValueError("empty_split")
    mean = float(train["value"].mean())
    if not math.isfinite(mean):
        raise ValueError("no_finite_training_mean")
    for part in (train, test):
        part["value"] = part["value"].fillna(mean)
        if not part["value"].map(lambda v: math.isfinite(float(v))).all():
            raise ValueError("non_finite_value")
    return train, test, mean


def majority_predict(training_targets, count):
    if not training_targets or any(x not in (0, 1) for x in training_targets):
        raise ValueError("invalid_training_targets")
    if type(count) is not int or count < 0:
        raise ValueError("invalid_count")
    majority = 1 if sum(training_targets) > len(training_targets) / 2 else 0
    return [majority] * count


def binary_metrics(y_true, y_pred):
    if not y_true or len(y_true) != len(y_pred) or any(x not in (0, 1) for x in [*y_true, *y_pred]):
        raise ValueError("invalid_labels")
    tp = sum(y == p == 1 for y, p in zip(y_true, y_pred, strict=True))
    tn = sum(y == p == 0 for y, p in zip(y_true, y_pred, strict=True))
    fp = sum(y == 0 and p == 1 for y, p in zip(y_true, y_pred, strict=True))
    fn = sum(y == 1 and p == 0 for y, p in zip(y_true, y_pred, strict=True))
    return dict(
        tp=tp,
        fp=fp,
        fn=fn,
        tn=tn,
        accuracy=(tp + tn) / len(y_true),
        precision=tp / (tp + fp) if tp + fp else None,
        recall=tp / (tp + fn) if tp + fn else None,
        f1=2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None,
    )


def threshold_predict(scores, threshold):
    if any(
        not isinstance(x, (int, float))
        or isinstance(x, bool)
        or not math.isfinite(x)
        or not 0 <= x <= 1
        for x in [*scores, threshold]
    ):
        raise ValueError("invalid_scores_or_threshold")
    return [int(x >= threshold) for x in scores]


def error_slices(frame):
    if not {"slice", "target", "prediction"} <= set(frame.columns):
        raise ValueError("missing_columns")
    if frame["slice"].dropna().map(lambda x: not isinstance(x, str)).any():
        raise ValueError("invalid_slice")
    work = frame.copy()
    work["slice"] = work["slice"].fillna("unknown")
    result = {}
    for name, group in work.groupby("slice", sort=True):
        metrics = binary_metrics(group["target"].tolist(), group["prediction"].tolist())
        result[name] = {"n": len(group), **{k: metrics[k] for k in ("fp", "fn", "recall")}}
    return result
