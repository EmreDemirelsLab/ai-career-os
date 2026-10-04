# AI Career OS --- Engineering Blueprint

**Version:** 1.0\
**Date:** 2026-10-04\
**Status:** Architecture baseline; implementation-ready after Phase 0
source validation.

## Mission

Build a market-driven adaptive AI/ML career platform that continuously:

1.  observes the job market,
2.  normalizes roles and skills into a versioned skill graph,
3.  maintains an evidence-backed learner/career profile,
4.  calculates role-specific skill gaps,
5.  generates a dependency-aware learning roadmap,
6.  teaches difficult concepts first for understanding and then in
    technical English,
7.  verifies learning through recall, coding, projects and interviews,
8.  tracks certifications and portfolio evidence,
9.  learns from real application/interview outcomes,
10. updates recommendations without allowing an LLM to invent market
    facts.

The first user is Emre and the first target market is Germany/EU AI/ML
engineering. The architecture must remain multi-user and multi-market
capable.

## Product thesis

The platform is not a course catalog. Its core object is a **versioned
skill/evidence graph** connected to real market demand.

Core loop:

`Market -> Skill Graph -> Gap -> Roadmap -> Learn -> Build -> Explain -> Interview -> Apply -> Outcome -> Roadmap`

## Non-negotiable principles

-   Database computes; AI interprets.
-   Market facts must be traceable to source records and collection
    timestamps.
-   Trend is not the same as importance.
-   Skill claims require evidence.
-   Learning completion is not mastery.
-   Curriculum respects prerequisites.
-   LLM output never silently mutates canonical taxonomy or roadmap.
-   English is embedded into technical learning, not treated as an
    unrelated course.
-   Production integrations use APIs/webhooks/queues; MCP is primarily
    an agent/developer interface.
-   Start as a modular monolith; split services only when operational
    evidence justifies it.
-   Every AI feature must have an evaluation dataset and regression
    criteria.
-   Every external source must have an explicit collection policy and
    provenance record.

## Document map

-   `01_PRODUCT_SPEC.md` --- users, jobs-to-be-done, flows, screens,
    requirements, MVP.
-   `02_SYSTEM_ARCHITECTURE.md` --- components, runtime, boundaries,
    integrations, deployment.
-   `03_DATA_MODEL_AND_SKILL_GRAPH.md` --- canonical entities, ontology,
    evidence and temporal model.
-   `04_MARKET_INTELLIGENCE_AND_INGESTION.md` --- collection,
    deduplication, extraction, provenance, analytics.
-   `05_LEARNING_ENGLISH_INTERVIEW_ENGINE.md` --- adaptive pedagogy,
    English transition, assessment, interviews.
-   `06_EVALUATION_SECURITY_GOVERNANCE.md` --- evals, privacy, security,
    AI governance, cost and reliability.
-   `07_DELIVERY_PLAN_AND_ACCEPTANCE.md` --- milestones, tests,
    acceptance criteria and Definition of Done.
-   `08_ADR_BASELINE.md` --- architecture decision records.
-   `09_MASTER_BUILD_PROMPT.md` --- operating prompt for Cursor/Claude
    Code implementation.
-   `10_INITIAL_BACKLOG.md` --- ordered implementation backlog.

## Current external architecture assumptions

Apify Actors can be invoked programmatically, scheduled, and return
structured datasets; production ingestion should therefore use Apify
API/schedules/webhooks rather than treating MCP as the runtime data
plane.

AWS MLA-C02 is relevant to the curriculum because the updated exam
covers traditional ML plus GenAI, RAG, agentic AI, foundation
models/LLMs, deployment, monitoring and security. Certification content
must be mapped into the same skill graph as job-market requirements
rather than maintained as a separate syllabus.

## Success condition

The first release is successful when the system can ingest a defensible
sample of Germany/EU AI/ML jobs, produce reproducible role/skill
statistics, create an explainable personalized gap analysis, and
generate a prerequisite-aware 24-week roadmap whose recommendations can
be traced to market evidence and learner evidence.

## Expansion documents

-   `11_SIX_MONTH_EMPLOYABILITY_SYSTEM.md` --- 24-week employability
    operating system.
-   `12_OPPORTUNITY_AND_ELIGIBILITY_ENGINE.md` --- separates technical
    fit from hard eligibility constraints.
-   `13_PORTFOLIO_AND_FLAGSHIP_PROJECT_STRATEGY.md` --- production-grade
    portfolio evidence strategy.
