# Architecture review v1.3

Decision date: 2026-10-05 (Europe/Istanbul). Status: accepted for this foundation branch.
Source: repository owner's request, the 2026-10-04 Repo Ready Pack v1.2 and dated employer observations in [market evidence](17_MARKET_EVIDENCE_2026-10-05.md).
This document overrides conflicting baseline instructions in docs/00–15. Those files preserve the original design; they do not certify completed implementation.

## Decisions and rationale

| Area | Review | v1.3 decision |
| --- | --- | --- |
| Architecture | Modular monolith fits a single developer and shared transactions | Keep FastAPI, SQLAlchemy/Alembic, PostgreSQL, minimal Next.js/TypeScript shell |
| Phase 0 | Full research exit contradicts fixture-first Sprint 1 | Separate foundation gate (synthetic fixture, contracts, tests) from empirical market gate (500–1,000 reviewed-scope records, 100+ extraction examples, dedupe benchmark, viable approved sources). Foundation can pass while market gate remains OPEN |
| Sprint scope | C7 quarantine was excluded despite required visibility of invalid records | Include minimal C7 (ordinal + validation codes + payload hash; no unsafe raw content in logs). C8 queues/retries remain deferred |
| Identity | Per-run identity would duplicate raw jobs on every rerun | Raw revision key is (source_id, source_job_id, content_hash); observations link each run to each revision, preserving repeated sightings |
| Hashing | Timestamp-inclusive hashes make identical records appear new | Hash content, source URL and payload, excluding fetched_at and adapter version; adapter version belongs to run provenance |
| Immutability | A comment is insufficient protection | DB triggers reject raw UPDATE/DELETE. Future authorized retention uses a separately reviewed migration/maintenance role; no deletion endpoint now |
| Idempotency | Read-then-insert alone races | Unique constraints and dialect-specific INSERT ON CONFLICT; run request key is unique per source; changed input under same key is a conflict |
| Failure state | Partial writes and pending runs obscure metrics | One persisted RUNNING run, one atomic batch transaction, FAILED after rollback, PARTIAL with structured rejections. Interrupted RUNNING runs require explicit operator recovery; no automatic rerun lease yet |
| Source governance | Generic ATS labels are not approved employers/endpoints | Import all original candidates disabled. Only local synthetic fixture is enabled. Enabling needs reviewed policy, method, reference, reviewer and retention limit |
| Graph | Many named engines risk premature platforms | Skill/evidence graph remains a relational model; no graph DB or vector extension in Sprint 1. Original taxonomy stays v0.1 seed, not an implemented prerequisite graph |
| Redis | Required stack component but no queue workload in fixture CLI | Supply optional Compose `queue` profile; API readiness checks only DB and migration revision; queue adoption needs retry/lease ADR |
| Eligibility | English text does not imply English-only work; remote does not imply anywhere | Retain separate PASS/UNCERTAIN/FAIL and evidence spans; unknown remains unknown. Degree preferred is not mandatory; years experience is reviewed rather than invented |
| Public portfolio | Learner history and complete employer text do not belong in a public seed | Synthetic fixtures only; publish concise sourced research notes, never private CV/interview data |
| 24-week plan | Three flagship products plus all tools can dilute learning | AI Career OS is flagship; ML service and RAG slice are focused evidence projects. Fine-tuning/Kubernetes optional until core gates pass; certifications secondary |
| Skill evidence | AI-generated code does not prove independent learner skill | Track assisted construction separately; mastery requires independent debugging, implementation and English defense against rubric |
| Certification | Baseline treats MLA-C02 as a settled fixed track | Version exam metadata with source + checked date; September 2026 AWS announcement describes MLA-C02 beta registration. Recheck before booking |

## Delivery boundary

Sprint 1: A1–A8, B1–B3, C1–C2, C4–C7, C9. B3 uses a local operator CLI, not a public unauthenticated admin API. Web is an honest foundation shell, without invented metrics. No live collection, extraction, LLM, tutor, roadmap computation, agents or automatic applications.

Module layout is executable Python packages under `apps/api/career_os`; future modules are documented, not empty implementations. `workers/ingestion` documents the CLI entry point. This replaces the ambiguous duplicate root `modules/*` import layout.

## Six-month operating plan

Preserve weeks 1–4 foundation, 5–8 classical ML, 9–12 PyTorch + serving, 13–16 RAG/evaluation, 17–20 applied AI reliability, 21–24 hiring/production hardening. Begin selective calibration applications in weeks 8–10, then increase only with evidence gates. This is a capability target, not a job offer or C1 guarantee. Weekly hours and diagnostic scores are not known; do not silently schedule a full-time workload.

Every week produces one linked evidence record: technical objective, code/experiment artifact, independent debugging gate, delayed recall, English source comprehension, three-minute explanation, and one interview defense. Use Turkish scaffolding only as needed; score technical correctness separately from English clarity. Each milestone can move based on assessment rather than calendar completion. The app need not be complete before learning begins.

## Definition of Done

See [Sprint 1 acceptance](18_SPRINT1_ACCEPTANCE.md). Never mark PostgreSQL or Docker verification passed from SQLite tests. Remote PR/CI status must be separately verified. Phase 0 empirical research remains incomplete.
