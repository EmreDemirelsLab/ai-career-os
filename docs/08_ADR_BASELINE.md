# 08 --- Architecture Decision Records: Baseline

## ADR-001 --- Modular monolith first

**Decision:** Use one FastAPI backend with explicit domain modules and
workers.\
**Reason:** Lower operational complexity while boundaries are evolving.\
**Revisit when:** independent scaling/deployment/security/team ownership
demands it.

## ADR-002 --- PostgreSQL as system of record

**Decision:** PostgreSQL stores normalized domain state and temporal
snapshots.\
**Reason:** relational integrity, analytics capability, mature
operations.\
**Vector:** pgvector only for justified semantic use cases.

## ADR-003 --- Raw job data is immutable

**Decision:** Preserve raw payloads with hashes and processor versions.\
**Reason:** reproducibility and reprocessing.

## ADR-004 --- Deterministic scoring, LLM explanation

**Decision:** Market/readiness/roadmap scores are computed by versioned
code/SQL.\
**Reason:** prevent hallucinated or irreproducible career
recommendations.

## ADR-005 --- Versioned ontology

**Decision:** Skills/roles/edges are versioned.\
**Reason:** market history must remain interpretable after taxonomy
changes.

## ADR-006 --- Evidence-backed mastery

**Decision:** Skill mastery is multidimensional and evidence-linked.\
**Reason:** course completion and self-report are insufficient.

## ADR-007 --- API/webhook production integrations

**Decision:** Use Apify API/schedules/webhooks for runtime ingestion.
MCP is an agent/developer interface.\
**Reason:** clearer operational contracts and observability.

## ADR-008 --- Provider-agnostic LLM gateway

**Decision:** Domain modules depend on an internal gateway, not vendor
SDKs directly.\
**Reason:** cost, reliability and model evolution.

## ADR-009 --- Evaluation before autonomous behavior

**Decision:** No autonomous roadmap mutation/application action without
benchmarked evaluation and explicit policy.\
**Reason:** career-impacting errors are costly.

## ADR-010 --- English embedded in technical curriculum

**Decision:** Technical English is taught on the same concept graph.\
**Reason:** target outcome is workplace comprehension/explanation, not
detached language completion.

## ADR-011 --- Source governance before scale

**Decision:** Every source needs a collection-policy record before
production dependency.\
**Reason:** technical scrapeability is not sufficient.

## ADR-012 --- No premature microservices

**Decision:** Do not split by fashionable architecture.\
**Reason:** optimize for learning speed, correctness and maintainability
first.
