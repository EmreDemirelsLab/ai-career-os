# Sprint 1 acceptance and review contract

As of 2026-10-05. Scope source: docs/15 with explicit v1.3 amendments in docs/16.

| Gate | Acceptance | Verification |
| --- | --- | --- |
| A1–A2 | Reproducible Python/Node workspace and lockfiles | uv sync --locked; npm ci |
| A3 | API, web, PostgreSQL boot; Redis optional queue profile | Compose smoke in CI; do not claim locally verified without Docker |
| A4 | Database URL validated, secrets not committed | config unit tests; .env.example; ignore rules |
| A5 | Lint, format, type, unit/integration tests | CI Python + web jobs |
| A6 | Liveness independent of DB; readiness requires current migration | endpoint tests, stopped/stale DB tests |
| A7 | Migrate zero → head → base → head, metadata drift check | PostgreSQL CI and disposable SQLite local tests |
| A8 | Structured ingestion logs, no raw payload or credentials | log redaction tests |
| B1–B3 | Seed candidates disabled; enable requires reviewed policy; disable blocks ingestion | governance tests and operator CLI |
| C1–C2 | Versioned protocol + local synthetic fixture adapter | contract tests |
| C4 | Durable completed/partial/failed lifecycle; missing run inspect error | adapter failure and metrics tests |
| C5–C6 | Append-only revisions, observations, idempotent retry and changed-key conflict | rerun/revision/immutability/concurrency tests |
| C7 | Invalid records visible without raw payload leakage | rejection endpoint/CLI; field and code report |
| C9 | fetched = accepted + rejected; accepted = inserted + duplicates | persisted counters and invariant constraints |
| Security | Loopback-only host ports, no network ingestion or public mutation endpoint | Compose and interface review |
| Documentation | Setup, limitations, recovery, provenance and English defense | docs and README |
| Remote delivery | Requested branch, PR, successful CI | remote evidence required; local tests do not satisfy this gate |

## Scope exclusions

No actual market ingestion, scraping adapter, retry queue, authentication system, extraction/model evaluation, market dashboard, readiness score or recommendation engine. AI evaluation is not applicable because there is no AI feature. Production rollout is not authorized by a green fixture test. A crash can leave RUNNING; operator must inspect before `fail-run`. The completed raw batch is atomic; failed runs keep no half-committed raw rows.
