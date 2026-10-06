# P3c1 — offline mention annotation and evaluation

Decision date: 2026-10-06. This implements the first measurement slice from docs/06, docs/14 and docs/16. It does not complete Phase 0 or certify real-market extraction quality.

## Scope decision

The current extractor is `literal-mentions/1`, not a requirement classifier. Gold labels therefore include negated, preferred and contextual literal mentions. `No Python required` has a Python mention; it must not become a mandatory-skill label. Semantic requirements, role/eligibility classification and near-duplicate quality need separate datasets and evaluators. No single score combines them.

## Annotation contract

The JSON artifact is a versioned dataset plus examples. Required dataset fields: schema_version `mention-gold/1`, dataset_id, version, taxonomy_version, origin (`synthetic` or `real`), annotation_policy `all-literal-mentions/1`, examples. Unknown fields are rejected.

Each example includes id, source_id, split (`development` or `holdout`), leakage_group, text, SHA-256 of exact UTF-8 text, observed_on, expires_on, source_reference, policy_reference, reviewer and labels. Labels are canonical skill, start and end (Python Unicode character offsets, half-open `[start,end)`, not UTF-8 byte offsets). Annotate every supported literal mention, including repeated occurrences; no mention is an explicit empty list. Do not derive gold automatically from the extractor being measured. The committed synthetic fixture is authored test data, not independently human-reviewed gold.

IDs/reviewer names are pseudonymous tokens. Actual source/policy references and text remain private for real datasets. Metadata asserts provenance; the validator cannot prove review happened or grant source access. For real examples, tie references to a reviewed exact source/observation and use its retention deadline. Do not extend expiry merely to make evaluation pass.

Put all revisions, reposts, translations and known near duplicates of a job in the same leakage_group before splitting. The validator rejects group overlap and normalized exact text overlap between development and holdout. It cannot automatically recognize paraphrases or enforce truthful grouping. Freeze holdout before tuning; a public synthetic fixture is not a statistically independent holdout.

## Operator workflow

```sh
uv run python -m career_os.market_eval tests/evals/mentions_synthetic_v1.json --split holdout --as-of 2026-10-06
```

Real datasets belong outside the public checkout, or in ignored `evaluation-private/`; .gitignore is not access control or encryption. This command reads at most 5 MB, creates no DB connection, fetches no URL, calls no model and prints JSON to stdout. Redirect output only to an appropriate private location. Input errors exit 2 without logging payloads. `--as-of` enables reproducible historical evaluation; it is not authorization to keep expired data. Default is the execution host's current calendar date; observation/expiry are date-level boundaries, with expiry exclusive.

All examples, including an unselected split, must be valid and unexpired as of that date. Invalid hash, taxonomy, spans, duplicate IDs/labels, split leakage, expired/future data or empty selected split fails closed. This tool refuses expired inputs but does not delete files or backups; operators must apply the source retention policy to private evaluation artifacts too.

## Metrics and boundaries

Exact tuple matching `(skill,start,end)` produces micro TP/FP/FN, precision, recall and F1, overall and per source. Undefined denominators are JSON null, never an invented perfect score. A wrong span counts both FP and FN. Reports include dataset fingerprint, policy/taxonomy versions, split/date, sample size and per-example error counts. They omit source text, URLs, reviewer identities and snippets; IDs and aggregate counts can still be sensitive.

Every report says `market_release_gate: NOT_ASSESSED`. Synthetic success only validates this fixture and evaluator wiring. Real origin metadata alone never turns the gate green. No market frequencies, required-skill inference, independent reviewer agreement, dedupe metric, population estimate or automatic deployment threshold is produced.

## Definition of Done for this slice

- Versioned, provenance-bearing annotation artifact with text integrity and bounded input.
- Tests for incorrect labels/spans, leakage, zero denominators, exact metrics, expiry, deterministic results and payload redaction.
- Existing Python/PostgreSQL, web, Compose/browser and restore regression checks pass remotely.
- Separate PR and durable continuation note, with skipped tests reported.

## P3c2 next: empirical sampling and independent review

Create a private sampling manifest stratified by country (Germany/other EU/outside EU/unknown), target role, seniority, source/company, language and remote restrictions. Record observation dates, excluded jobs and missingness; do not overweight senior comparators as entry-level demand. Review exact collection policy before fetching source text; do not mark existing candidates approved from their public visibility.

Collect the approved corpus, have an independent human review labels and disagreements, then freeze development/holdout by leakage group. Preserve docs16's 500–1,000 reviewed-scope records and 100+ extraction examples as open targets; revisit scope explicitly if access is insufficient. Add dedupe pair/cluster labels and semantic requirement/eligibility schemas separately. Predeclare thresholds against a real baseline and report per-source error analysis before any production quality claim.
