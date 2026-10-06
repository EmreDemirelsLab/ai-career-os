# 06 --- Evaluation, Security and Governance

## 1. Evaluation-first rule

Every AI-powered production feature needs: - purpose - test dataset -
expected behavior - metric - failure taxonomy - regression threshold -
prompt/model version

## 2. Evaluation suites

### Job extraction

Precision/recall/F1 by field and source.

### Skill normalization

Canonical mapping accuracy and unknown detection.

### Role classification

Macro-F1 across role classes.

### Deduplication

Pairwise precision/recall and cluster quality.

### Tutor

Rubric adherence, conceptual correctness, level appropriateness,
unsupported-claim rate.

### Interview evaluator

Agreement with expert rubric on benchmark answers.

### Roadmap explanation

Faithfulness to deterministic score and dependencies.

## 3. Golden datasets

Maintain versioned gold sets in `tests/evals/`. Do not train/tune on the
entire evaluation set. Keep a held-out regression set.

## 4. Human review queues

Required for: - new canonical skills, - ambiguous skill merges, -
suspicious market spikes, - low-confidence extraction, - major roadmap
changes, - evaluator disagreements.

## 5. Security baseline

-   TLS everywhere
-   secrets manager
-   no tokens in repo
-   least-privilege IAM
-   scoped Apify tokens
-   RBAC
-   signed artifact URLs
-   encryption at rest where supported
-   dependency scanning
-   SAST
-   audit logs
-   rate limiting
-   input validation
-   CSRF/session protections as appropriate
-   secure webhook signature/secret validation
-   backup and restore tests

## 6. Prompt-injection/data-poisoning defense

Job descriptions and web pages are untrusted data.

Rules: - never allow scraped text to become system/developer
instructions, - delimit untrusted content, - structured extraction
only, - tool permissions are not granted based on scraped content, -
sanitize rendered HTML, - record provenance, - anomaly detection for
poisoned/repetitive postings.

## 7. Privacy

Minimize personal data. CVs, voice recordings, interview transcripts and
application history require explicit retention/deletion controls.

Provide: - export - deletion - retention configuration - consent
boundaries - purpose limitation

## 8. AI governance

For each AI decision record: - model - prompt - version - inputs -
output - confidence if applicable - human override - downstream effect

High-impact career recommendations must be explainable and reversible.

## 9. Cost governance

Track: - scraping cost/source - LLM extraction cost/job - tutoring
cost/session - interview cost/session - embedding/vector cost - AWS
infrastructure cost

Budgets: - daily ingestion budget - per-user AI budget - alert
thresholds - graceful degradation

Use cheaper deterministic processing before LLM calls where possible.

## 10. Reliability

SLO candidates: - dashboard availability - ingestion completion -
roadmap generation latency - structured-output success - queue age

Backups: - automated - retention defined - restore tested

## 11. Compliance/source governance

Maintain a source registry documenting collection basis and
restrictions. Do not build a production dependency on a source until its
access/collection method has been reviewed.

## 12. Model/provider governance

No provider lock-in at domain level. Provider changes require eval
regression runs. Model upgrade is a deployment change, not a casual
config edit.
