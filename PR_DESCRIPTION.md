## Why

AI Career OS had an empty repository and a broad v1.2 design, but no executable ingestion contract. A reproducible foundation is required before collecting jobs or making market/readiness claims.

## Changes

- Preserve all 16 blueprint documents and three seeds; record provenance.
- Review architecture as v1.3 with dated employer evidence, separate foundation and empirical Phase 0 gates, and a narrow Sprint 1 scope.
- Add FastAPI, SQLAlchemy/Alembic, source governance CLI, fixture adapter, immutable raw revisions, run observations, idempotency, structured rejections and counters.
- Add a truthful Next.js/TypeScript shell, lockfiles, Docker Compose and CI jobs.
- Document failure recovery, security boundaries, learning/English defense gates and deferred work.

## Validation

- Local: Ruff, format, strict Mypy, 20 tests, CLI two-run smoke, web lint/typecheck/build passed.
- 15 tests skipped locally: PostgreSQL not available; SQLite concurrency cases intentionally skipped.
- PostgreSQL integration and Compose smoke are configured in CI but NOT yet executed.
- Phase 0 empirical research is NOT complete; five employer observations are qualitative only.

## Acceptance / limitations

Draft until PostgreSQL tests and Compose CI pass. No LLM, extraction, agents, live scraping, learner data, market scoring or production deployment. Redis optional and unused by fixture CLI. Abrupt process death needs operator recovery; production queues/leases are deferred. Initial migration downgrade destroys foundation data and is for disposable environments only.
