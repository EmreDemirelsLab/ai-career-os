# 15 --- Repo Bootstrap Contract

## We are ready to create the repository when all items below are true

\[x\] Product mission defined \[x\] MVP scope defined \[x\] Architecture
style defined \[x\] Core runtime modules defined \[x\] Raw/normalized
temporal data model defined \[x\] Skill/evidence graph defined \[x\]
Source governance model defined \[x\] Initial role taxonomy defined
\[x\] Initial skill taxonomy defined \[x\] Eligibility separated from
capability \[x\] Evaluation strategy defined \[x\] Security/governance
baseline defined \[x\] 24-week employability model defined \[x\]
Portfolio strategy defined \[x\] Master implementation prompt defined
\[x\] Initial backlog defined

## Repository creation target

Name: `ai-career-os`

Initial tree:

-   `apps/web`
-   `apps/api`
-   `modules/market`
-   `modules/taxonomy`
-   `modules/learner`
-   `modules/roadmap`
-   `modules/learning`
-   `modules/english`
-   `modules/interviews`
-   `modules/projects`
-   `modules/certifications`
-   `modules/opportunities`
-   `modules/applications`
-   `modules/ai_gateway`
-   `workers/ingestion`
-   `workers/extraction`
-   `workers/analytics`
-   `packages/schemas`
-   `packages/prompts`
-   `packages/evaluation`
-   `seed`
-   `infra/docker`
-   `infra/aws`
-   `infra/apify`
-   `docs`
-   `tests/unit`
-   `tests/integration`
-   `tests/e2e`
-   `tests/evals`

## First branch

`feat/foundation-ingestion`

## Sprint 1 only

1.  repository/tooling scaffold
2.  Docker Compose: PostgreSQL + Redis + API + web
3.  FastAPI health/readiness
4.  migration framework
5.  Source table
6.  IngestionRun table
7.  RawJob immutable table
8.  source adapter protocol
9.  fixture adapter
10. idempotent ingestion
11. ingestion metrics
12. unit/integration tests
13. CI

Do not implement: - LLM extraction - roadmap - tutor - agents - voice -
vector database features

until ingestion is reproducible.

## Sprint 1 acceptance

-   fresh clone boots locally with documented commands
-   migrations apply from zero
-   fixture ingestion can run twice without duplicating jobs
-   failed records are visible
-   run counts are persisted
-   API health/readiness pass
-   tests and type/lint checks pass in CI
-   no secrets committed
-   docs explain local setup
