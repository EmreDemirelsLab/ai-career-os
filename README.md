# AI Career OS

A market-driven AI/ML learning and career evidence platform. Flagship production engineering portfolio, built in reviewable slices.

**Current:** v1.3 foundation plus a single-owner personal workspace: versioned profile and 24-week baseline, learning/English submissions, delayed recall, evidence, interview rehearsal, manually reviewed opportunities and application history. Greenhouse collection, evidence-linked mention snapshots, prerequisite planning and an opt-in AI feedback gateway are implemented; live source/model quality and hosted production acceptance are not yet verified. See [v1.4 engines and release gates](docs/23_INTELLIGENCE_RELEASE.md). See the [complete-product contract](docs/21_COMPLETE_PRODUCT_CONTRACT.md) and [workspace verification](docs/22_WORKSPACE_VERIFICATION.md).

## Start locally (Docker)

Requires Docker Engine/Desktop with Compose v2. Local development only; example database credentials are disposable and must never be reused in production.

```sh
python3 scripts/init_workspace.py
docker compose up --build -d --wait
docker compose exec api career-os seed
docker compose exec api career-os ingest-fixture --key demo-1
docker compose exec api career-os ingest-fixture --key demo-2
```

Open http://localhost:3000 and sign in using CAREER_API_TOKEN from your local .env. Never commit or share this value. An unset token disables the workspace. If .env already exists, preserve it and add a randomly generated token of at least 32 characters. API: http://localhost:8000/health and http://localhost:8000/ready. First fixture run: 3 fetched, 2 accepted/inserted, 1 rejected. Second key: 0 inserted, 2 duplicates, 1 rejected. Same key/input returns the original run without adding observations. A changed input with the same key is refused.

Inspect errors with `docker compose exec api career-os run <run-id>`. Disable source: `docker compose exec api career-os source-state DEMO disable`. Original source candidates are disabled and cannot be enabled without reviewed policy metadata. Seed reruns preserve operator changes.

`docker compose down` stops services and retains data. `docker compose down -v` **deletes local development data**. Redis is reserved: `docker compose --profile queue up -d redis`; ingestion does not use it yet.

## Native development and checks

Python 3.12, uv 0.12.19, Node 22, npm. Start PostgreSQL through Compose or use an existing disposable development DB.

```sh
uv sync --locked
python3 scripts/init_workspace.py
uv run alembic upgrade head
uv run career-os seed
uv run uvicorn career_os.api:app --reload
```

In a second terminal:

```sh
cd apps/web
npm ci
npm run dev
```

Checks from repository root:

```sh
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest -q
```

Without `TEST_DATABASE_URL`, PostgreSQL tests are explicitly skipped. CI uses a disposable `career_test` database and runs both backends, concurrent ingestion, migration roundtrip and metadata drift. **Tests downgrade/reset that database**. Never point them at production. SQLite exists only for local contract verification and is not a production substitute.

```sh
cd apps/web
npm run lint
npm run typecheck
npm run build
```

## Architecture and decisions

- [Original blueprint](docs/00_README.md), [product](docs/01_PRODUCT_SPEC.md), [data/evidence graph](docs/03_DATA_MODEL_AND_SKILL_GRAPH.md)
- [v1.3 critical review](docs/16_ARCHITECTURE_REVIEW_v1_3.md) — overrides baseline conflicts
- [Dated employer evidence](docs/17_MARKET_EVIDENCE_2026-10-05.md)
- [Sprint acceptance](docs/18_SPRINT1_ACCEPTANCE.md), [verification](docs/19_VERIFICATION_REPORT.md)
- [Six-month capability sequence](docs/11_SIX_MONTH_EMPLOYABILITY_SYSTEM.md), [English/interviews](docs/05_LEARNING_ENGLISH_INTERVIEW_ENGINE.md)
- [Operator/security notes](docs/20_OPERATIONS_AND_SECURITY.md)

Flow: fixture → validated envelope → immutable content revisions + per-run observations → persisted counters/rejections. Revisions use source identity and content hash; cross-source logical-job deduplication is a later benchmarked feature.

Empirical market/model evaluation, live retention enforcement, scheduling, production hosting and user acceptance remain release gates. The current product is single-owner; multi-user SaaS is outside this slice. AI-generated implementation does not establish the learner's mastery.
