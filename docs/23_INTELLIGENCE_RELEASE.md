# Intelligence engines and release gates — 2026-10-05

This extension implements executable market analysis, prerequisite planning and an opt-in AI feedback gateway. It supersedes older statements saying these components do not exist. It does **not** claim the empirical market study, semantic extraction quality, expert-calibrated teaching, or hosted production acceptance has been completed.

## Architecture review v1.4

Keep the modular monolith and single-owner product. A graph database, autonomous agent team, vector database and multi-user SaaS are not prerequisites for this user's personal career OS. Relational snapshots and an authored acyclic prerequisite graph are sufficient for the current workflow. Broader semantic retrieval can be added only against a measured need.

Separate four kinds of evidence: source-text mentions, reviewed hiring requirements, learner artifacts and AI-generated suggestions. A literal mention never becomes a mandatory requirement; an AI response never becomes verified mastery. Market demand prioritizes only skills whose prerequisites already occur earlier in the generated sequence; it cannot remove fundamentals. Profile, evidence IDs, market snapshot and graph/policy versions are captured with each saved plan.

## Implemented and testable

| Component | Behavior | Remaining limitation |
| --- | --- | --- |
| Greenhouse collector | Fixed HTTPS host, board token validation, reviewed per-board source metadata checked before network, bounded bytes/jobs/time, no redirects, HTML to plain text, existing ingestion idempotency | No live collection executed here; no automatic source approval; no scheduler/retry worker |
| Extraction | Canonical aliases and exact source spans, explicit mention-only/unknown requirement status | Not semantic extraction; negation, mandatory/preferred and role/country classifications require review |
| Market | Latest observed revision per source identity, retention-window selection, exact normalized-content dedupe, frozen counts/source IDs/content hashes | Not representative market statistics; near duplicates can remain; synthetic sources require explicit opt-in and are timeless demo fixtures |
| Skill graph/plan | Stable graph node IDs, cycle check, authored prerequisites, deterministic demand ordering, profile/evidence/snapshot provenance | Authored policy, not empirically calibrated; no numerical mastery or job probability |
| AI coach/interview | Responses API JSON Schema, separate technical/English feedback, follow-up exercise/question, no tool execution, consent per submission | Provider/model/account and live quality evaluation not configured; draft feedback only |
| AI governance | Opt-in, daily atomic call reservation, bounded input/output, durable idempotency key, sanitized errors, no automatic paid retry, usage metadata | Call cap is not a dollar spending cap; interrupted RUNNING requests need inspection and are not automatically retried |
| Identity | Random 8-hour server-side sessions, only token hashes stored, expiry/revocation, master-key rotation invalidates sessions | Single owner; no accounts, tenant isolation, password reset or SSO |
| Recovery | Private-permission pg_dump, checksum validation, restore only to a newly created disposable database, CI checks restored data | Backup encryption, offsite scheduling, retention and production restore drill still need deployment setup |

## Start and use

Follow README to start Compose, then migrate/seed/ingest the demo. Open **Analiz & AI**. Select the synthetic fixture with explicit demo opt-in to build a snapshot, then choose target skills to create a prerequisite plan. Synthetic counts must not be cited as employer demand.

Actual Greenhouse collection requires an operator's source-specific policy review. Generic ATS candidates are not blanket approval. Register a **new employer-specific source**, then enable it deliberately:

```sh
career-os register-greenhouse EMPLOYER_ID --name 'Employer name' --board BOARD_TOKEN \
  --policy-reference 'review record URL or path' --reviewed-by 'reviewer' --retention-days 30
career-os source-state EMPLOYER_ID enable
career-os collect-greenhouse EMPLOYER_ID --board BOARD_TOKEN --key UNIQUE_COLLECTION_KEY
```

Registration saves the entered review and leaves the source disabled; it does not conduct or certify the review. No live employer was registered by this implementation. A source's retention window affects snapshot inclusion; it does not delete immutable raw rows. **A compliant deletion/retention maintenance procedure is still a live-production collection gate.** Network failures are bounded and sanitized; a changed payload under an old key remains a conflict. Create a new collection key for a new observation cycle.

## Optional AI configuration

Set `OPENAI_API_KEY`, `CAREER_AI_MODEL`, `CAREER_AI_DAILY_CALLS` and `CAREER_AI_ENABLED=true` in the local/deployment environment and recreate the API service. Choose a model that supports Responses structured output; no model or price is silently assumed. This change does not provision a provider account or make a paid call.

The UI explains which saved answer is sent, requires consent and uses a request key. Only the selected question/answer is sent, not the full profile, CV or market text. The provider request uses `store:false`; this is not a claim about all provider-side retention policies. The daily limit uses UTC and counts reservations, including failures. There are no automatic retries. Do not change request keys merely because the browser timed out: first inspect the request status. An interrupted RUNNING request remains visible. AI history is exported/deleted with the workspace; anonymous daily counters remain to prevent deleting history to bypass the call cap.

AI contract tests use synthetic transport responses, including invalid schema and refusal. The injection test verifies separation and lack of tools, **not proven semantic prompt-injection immunity**. Real-model accuracy and coaching quality remain unmeasured until live evaluation against expert-reviewed cases.

## Recovery

```sh
python3 scripts/backup.py backups/career-YYYY-MM-DD.dump
python3 scripts/restore_drill.py backups/career-YYYY-MM-DD.dump career_restore_drill
```

The backup refuses to overwrite a file; restore refuses to overwrite an existing database. Archive data is sensitive and unencrypted: encrypt before external storage, keep credentials out of the repo and rotate the master key after restoring a database containing sessions. Restoring is tested against a disposable database, never against the user's original database.

## Sources checked 2026-10-05

- [Greenhouse Job Board API](https://docs.greenhouse.io/job-board.html): GET list jobs, board identity and `content=true` payload.
- [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses): Responses `text.format` JSON Schema and refusal handling. Schema conformity is not factual correctness.

## Completion boundary

Full completion still requires real reviewed source coverage/gold extraction and dedupe benchmarks, quality-calibrated lessons and learner assessment, live AI evaluation with an approved model/budget, retention/deletion maintenance, hosting credentials/domain/TLS, restricted DB roles, monitored deployment and user acceptance. Passing mocked-provider tests does not close these gates. See PR checks for actual execution results; do not infer Docker/PostgreSQL verification from local SQLite.

## Verification at implementation time

Local Python lint/format/mypy passed. Pytest: **33 passed, 23 skipped** (PostgreSQL unavailable; three PostgreSQL-only concurrency cases also skip on SQLite). Frontend lint/typecheck/production build passed. Remote CI must verify PostgreSQL, concurrent budget reservation, expanded browser flow, Compose and backup restore before this PR is accepted. No paid model call, live employer collection or production deployment was executed.

The [hosting runbook](24_HOSTING_RUNBOOK.md) now includes a concrete single-owner Compose target, generated separate owner/runtime credentials, Caddy TLS configuration and CI checks for restricted-role DDL denial. No target was deployed; live TLS, monitoring and offsite backup remain unverified.

Remote P2 acceptance verified 2026-10-06 Europe/Istanbul: [CI run 37380972149](https://github.com/EmreDemirelsLab/ai-career-os/actions/runs/37380972149), code head `d934411f562d0aef79634bc27cc86c39f2c1abbd`: 53 Python tests passed, 3 skipped SQLite variants of PostgreSQL-only concurrency; web checks, 1 Playwright test, Compose, hosted/Caddy config, restricted-role DDL denial and backup/restore passed. This closes the P2 software acceptance slice, not the full product or live deployment gates.
