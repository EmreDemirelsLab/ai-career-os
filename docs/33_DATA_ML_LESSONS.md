# P4b — data/ML practice, weeks 5–8

2026-10-06. Catalog version foundation-lessons/2 adds four authored lessons while preserving baseline week/skill alignment. Existing attempts retain old version/fingerprint and feedback. API rejects stale catalog submissions until reload.

## Content and execution

Week 5: DataFrame missingness, empty denominators and class counts. Week 6: customer-group split, training-only mean imputation and unchanged inputs. Week 7: train-only majority baseline, confusion counts, precision/recall/F1 with explicit undefined values. Week 8: finite score thresholds, equality boundary and error slices with sample sizes/unknown groups.

Run `uv sync --locked --group labs`; then `uv run --group labs python labs/data_ml/check.py --week 5`. The optional labs group locks pandas and its dependencies without adding them to production runtime requirements. Python CI installs the labs group and tests both shipped reference and intentionally failing starter behavior. Reference runs five checks; inspecting it counts as assistance. API never executes learner code.

Official reading references opened 2026-10-06: pandas summary statistics, scikit-learn common pitfalls/data leakage, and model evaluation (URLs in catalog). Explanations and synthetic examples are authored. The lab reports None for undefined denominators; that convention differs from some library defaults. A majority baseline is not a fitted production ML service. No actual hiring, business or model generalization claim follows from tiny fixture scores.

## Acceptance

Unchanged input data; customer groups disjoint; held-out outlier cannot influence learned mean; all-missing training data rejected; baseline rare-class recall failure visible despite higher accuracy; confusion counts/unequal lengths checked; threshold NaN/range/boundary checks; slice size and unknown group preserved. Existing lesson API/web/privacy/recall and full CI remain regression gates.

Only weeks 1–8 are authored pilots. Weeks 9–24, external pedagogical validation, real learner diagnosis and independent implementation/English assessment remain open. No paid/model call, live collection, deployment or merge.
