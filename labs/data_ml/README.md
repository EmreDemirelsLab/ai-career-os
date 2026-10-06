# Data/ML practice (weeks 5–8)

Run `uv sync --locked --group labs`, then implement `exercises.py` using the app lessons. Commands from repo root:

```sh
uv run --group labs python labs/data_ml/check.py --week 5
uv run --group labs python labs/data_ml/check.py --reference
```

Starter checks intentionally fail until implemented. The second command tests the shipped reference and counts as assisted work. The optional labs dependency group adds pandas/NumPy to the local learning/CI environment, not the production API runtime. No model/API calls, external data downloads or paid services.

5: DataFrame missingness and class counts, preserving input. 6: customer-group split and training-only mean imputation. 7: majority baseline and hand-computed confusion metrics. 8: threshold boundaries and error slices with sample sizes. All inputs are tiny synthetic data, not evidence of real-world generalization.

The lab uses None for undefined precision/recall/F1 denominators; this is an explicit exercise convention, not every library's default. Equality belongs to positive predictions (`score >= threshold`). Tune thresholds on validation data, not the final test. Keep repeated customer records in the same split; time-dependent leakage needs additional handling.

Explain a deliberately failing case, fix an unseen variation, and defend your result in English before treating this as independent evidence. The API stores submissions but never executes learner code or certifies mastery. Reference solutions are readable; do not represent copied work as independent. See docs33.
