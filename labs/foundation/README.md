# Foundation practice (weeks 1–4)

Use the app's **Temel alıştırmalar** tab for the why, worked example, questions and English defense. Complete only `exercises.py`. Run from the repository root:

```sh
uv sync --locked
uv run python labs/foundation/check.py --week 1
```

The starter intentionally fails until you implement it. Choose weeks 1–4 or omit --week for all checks. Tests run locally; the API never runs learner code. Dependencies come from the project lockfile. Use a disposable local environment, never production credentials/data. Week 2 uses an in-memory SQLite database; this is not a PostgreSQL concurrency demonstration.

Before coding, predict expected output. Make a boundary case fail, explain it, implement the smallest correction, and rerun. Record your own code/test artifact plus a short English defense in the app. Correct diagnostic answers do not establish independent implementation skill.

`reference.py` is available after your attempt. `uv run python labs/foundation/check.py --reference` validates the shipped reference. Reading/copying it is assisted work; the resulting test pass is not evidence that you solved the problem independently. There is no automatic upload of local test results.

Week 4 keeps only the latest content hash in memory. It demonstrates identity/replay classification, not durable immutable revisions, distributed exactly-once processing or production recovery. Compare with the actual ingestion model after completing the exercise.

For independent review: explain one design choice, show a failing test, fix an unseen variation without the reference, then defend a limitation in English. Record assistance truthfully. These authored exercises have not been externally validated as a complete course.
