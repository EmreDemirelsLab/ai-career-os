# P3c2 — private sampling and review linkage

2026-10-06. This slice makes source selection and label review auditable without claiming a real corpus exists. It adds no collection permission, network request or human certification.

## Workflow

Keep real manifests/gold outside the public repo or in ignored evaluation-private (not a security boundary). Start from the synthetic structure in tests/evals/sampling_synthetic_v1.json; replace all assertions with actual documented evidence. Do not relabel synthetic examples as real.

Each sample records source/company IDs, exact source reference and text hash, observation/expiry, geography, role, seniority, language, remote restriction, include/exclude/pending, exclusion reason, leakage group and split. Unknown is explicit: an English page is not English-only eligibility; a remote label is not unrestricted remote work. Reports expose selected-sample coverage/missingness only, never population demand.

Each exact source has policy status/reference/reviewer, review and validity dates, and retention days. Included samples require approved/current policy reviewed no later than observation, with expiry no later than source retention permits. Pending/excluded metadata can be audited without granting access or linking it as gold. Policies are assertions to be independently checked; this tool neither reviews terms nor modifies the application's source registry.

A label review carries distinct author/reviewer tokens, accepted/changes_requested, review date and a digest of sorted canonical labels. Distinct tokens do not prove distinct people. Gold linkage requires inclusion, accepted/current review, matching reviewer, unchanged labels and identical source/hash/date/split/group/policy references. Changing labels invalidates review. A gold subset of the included corpus is allowed. Review disagreements remain changes_requested until independently resolved; this tool does not manufacture agreement scores.

## Commands

```sh
uv run python -m career_os.sampling tests/evals/sampling_synthetic_v1.json --dataset tests/evals/review_link_synthetic_v1.json --as-of 2026-10-06
```

Without --dataset, audit selection/coverage; with it, also enforce gold linkage. Inputs capped at 5 MB each. No DB or HTTP calls. JSON reports contain counts/fingerprints and pseudonymous source/company IDs, not text/URLs/reviewer identities. Treat reports as private too. Invalid inputs exit 2 with generic redacted error. As-of enables reproducibility, not permission to retain expired files. Excluded/pending metadata also needs a private retention policy; there is no automatic file purge.

## Acceptance and remaining gates

Tests cover unknown strata, exclusions, stale or self-review, changed label digest/provenance, revoked/expired source policy, retention, future observations, origin mismatch and group/hash split leakage. Required remote regression gates remain Python/PostgreSQL, web, Compose/browser and restore.

Every output leaves market_release_gate NOT_ASSESSED. Real collection, independent human review, representativeness, semantic requirements and dedupe benchmarks remain open. The code is usable for that work; synthetic fixtures are not completion of the 500–1,000 corpus/100+ extraction-example targets. While those empirical gates remain open, P4 learning-content implementation can proceed without pretending market validation is complete.
