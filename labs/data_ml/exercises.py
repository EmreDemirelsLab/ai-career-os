"""Weeks 5–8: implement locally; reference.py counts as assistance."""


def summarize(frame):
    raise NotImplementedError("Week 5: rows, missing values/rate, target counts")


def prepare_split(frame, test_customers):
    raise NotImplementedError("Week 6: group split, fit mean on train only, fill copies")


def majority_predict(training_targets, count):
    raise NotImplementedError("Week 7: train-only majority baseline, ties choose zero")


def binary_metrics(y_true, y_pred):
    raise NotImplementedError("Week 7: TP/FP/FN/TN and undefined-safe metrics")


def threshold_predict(scores, threshold):
    raise NotImplementedError("Week 8: finite [0,1] scores, positive when score >= threshold")


def error_slices(frame):
    raise NotImplementedError("Week 8: slice size, FP/FN and recall; retain unknown slice")
