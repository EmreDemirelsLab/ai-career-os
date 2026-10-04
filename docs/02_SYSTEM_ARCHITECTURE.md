# 02 --- System Architecture

## 1. Architecture style

Start with a **modular monolith** plus background workers.

Why: - one primary developer, - domain boundaries are still evolving, -
transactional consistency matters, - operational complexity of
microservices is not yet justified, - modules can later be extracted
behind stable interfaces.

## 2. Technology baseline

Frontend: - Next.js - TypeScript - Tailwind - server components where
useful - charting library selected after dashboard prototype

Backend: - Python - FastAPI - Pydantic - SQLAlchemy/Alembic or
equivalent migration stack

Persistence: - PostgreSQL - pgvector only where semantic retrieval is
justified - object storage for large artifacts/raw snapshots if needed

Background processing: - Redis + worker queue initially - idempotent
jobs - dead-letter handling - retry policy with backoff

AI/ML: - scikit-learn - PyTorch - provider-agnostic LLM gateway -
structured outputs with schema validation

Collection: - Apify API/Actors - schedules/webhooks - source-specific
adapters - Playwright/Crawlee only where justified and permitted -
official feeds/APIs preferred

Infrastructure: - Docker - AWS - GitHub Actions - managed PostgreSQL -
secrets manager - centralized logs/metrics/traces

## 3. Runtime modules

### market

Sources, ingestion runs, raw jobs, normalized jobs, dedupe, extraction,
snapshots, trend analytics.

### taxonomy

Skills, aliases, role taxonomy, prerequisite graph, ontology versions,
review queue.

### learner

Learner profile, goals, evidence, mastery states, language states.

### roadmap

Priority scoring, dependency checks, scheduling, roadmap versions,
recommendation explanations.

### learning

Learning units, content templates, assessments, spaced repetition,
mastery updates.

### english

Technical chunks, sentence parsing tasks, listening tasks,
translation-dependency state.

### interviews

Question bank, rubrics, sessions, evaluations, role simulations.

### projects

Project templates, milestones, skill coverage, artifacts, deployment
evidence.

### certifications

Certification objectives, mappings, practice attempts, access/status.

### opportunities

Job-fit scoring and explanation.

### applications

Application funnel and outcome feedback.

### ai_gateway

Provider abstraction, prompt registry, structured output, token/cost
tracking, retry/fallback.

### audit

Decision provenance, human overrides, model versions, taxonomy versions.

## 4. Data flow --- job ingestion

`Scheduler -> Source Adapter/Apify -> Raw Payload -> Validation -> Raw Job -> Dedupe -> Normalization -> Extraction -> Taxonomy Mapping -> Normalized Job -> Snapshot Analytics`

Every stage records: - input version/hash - processor version - output -
confidence - timestamp - failure/retry state

## 5. Data flow --- roadmap

`Target Role + Market Snapshot + Skill Graph + Learner Evidence -> Deterministic Priority Engine -> Dependency Resolver -> Roadmap Version -> LLM Explanation`

The LLM explains the computed recommendation. It does not own the score.

## 6. Data flow --- learning

`Roadmap Item -> Learner State -> Lesson Template -> Tutor -> Assessment -> Evaluator -> Evidence -> Mastery Update -> Spaced Review Queue`

Mastery updates must be based on assessment/evidence rules, not
conversational praise.

## 7. LLM gateway

Interface: - `generate_text` - `generate_structured` - `classify` -
`extract` - `evaluate_against_rubric` - `tool_call` - optional `embed`

Provider adapters: - Claude - OpenAI - AWS Bedrock - local/open model
later

All calls record: - provider/model - prompt version - schema version -
token usage - cost - latency - result status - evaluation tags

## 8. MCP boundary

MCP is useful for: - developer/agent access to Apify Actors, - repo
tooling, - interactive data exploration, - controlled agent tools.

MCP is not the default production event bus or ingestion transport.

Production uses stable APIs, webhooks and queues.

## 9. Reliability

Required: - idempotency key per source/job/run - retries with
exponential backoff - dead-letter queue - resumable ingestion - run
status dashboard - source circuit breaker - rate-limit handling - schema
drift detection - alert on sudden record-count or extraction-quality
changes

## 10. Observability

Three layers: - infrastructure: CPU/memory/queue/database - application:
latency/errors/job counts - AI: model/prompt version, cost,
structured-output failures, eval regressions

Market pipeline must expose: - fetched - parsed - rejected -
duplicated - normalized - extraction-failed - taxonomy-unmapped

## 11. Deployment environments

-   local
-   dev
-   staging
-   production

No production secret may be used in local/dev.

Database migrations must be forward/reversible where practical.

## 12. Repository

ai-career-os/ - apps/web - apps/api - modules/market -
modules/taxonomy - modules/learner - modules/roadmap -
modules/learning - modules/english - modules/interviews -
modules/projects - modules/certifications - modules/opportunities -
modules/applications - modules/ai_gateway - workers/ingestion -
workers/extraction - workers/analytics - packages/schemas -
packages/prompts - packages/evaluation - packages/taxonomy -
infra/docker - infra/aws - infra/apify - docs - tests/unit -
tests/integration - tests/e2e - tests/evals

## 13. Scaling rule

Do not extract a microservice until at least one is true: - independent
scaling is materially required, - independent deployment is materially
required, - failure isolation is materially required, - security
boundary requires it, - ownership/team boundary requires it.

Architecture decisions are recorded as ADRs.
