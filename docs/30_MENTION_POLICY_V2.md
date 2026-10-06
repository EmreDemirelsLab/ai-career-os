# Literal mention policy v2 — overlapping alias correction

Decision/evaluation date: 2026-10-06. This overrides the extractor-version description in docs29; annotation policy and authored gold remain unchanged.

The P3c1 evaluator exposed nested duplicate spans: `AWS Cloud` emitted both `AWS` and `AWS Cloud` for canonical AWS. Policy `literal-mentions/2` keeps maximal containing spans for the same canonical skill. Separate occurrences and different skills survive. It sorts spans and tracks the furthest end per skill; it does not use quadratic pairwise comparisons on repetitive text.

On the unchanged seven-example synthetic holdout fixture (`120e66be07d37ebc3e43d0630ca4b005098b870db420827b615246b10b63cad6`), v1 produced 6 TP / 1 FP / 0 FN; v2 produces 6 TP / 0 FP / 0 FN. These are authored regression cases, not real-market statistics or independent held-out quality evidence; the fixture was inspected to make this fix.

New market snapshots and evaluation reports record `literal-mentions/2`. Persisted snapshots keep their original policy/version and are not rewritten. Counts already used a per-job skill set, so the intended change is mention-span evidence, not invented market demand growth. Mandatory/negated/preferred requirements remain unknown; no semantic inference is added.

Acceptance: unchanged gold, exact offsets and separate repeated occurrences preserved, policy version recorded, existing Python/PostgreSQL/web/browser/restore CI passed. Source collection approval, independent annotation and real Phase 0 sample remain open. No migration, model call or deployment.
