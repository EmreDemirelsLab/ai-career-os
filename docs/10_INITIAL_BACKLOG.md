# 10 --- Initial Backlog

## Epic A --- Repository foundation

A1. Initialize monorepo structure.\
A2. Configure Python/Node tooling.\
A3. Docker Compose: API, web, PostgreSQL, Redis.\
A4. Environment validation.\
A5. CI: lint, type, unit tests.\
A6. Health/readiness endpoints.\
A7. Migration framework.\
A8. Structured logging.

## Epic B --- Source governance

B1. Source registry schema.\
B2. Collection-policy fields.\
B3. Admin source enable/disable.\
B4. Source rate/cost configuration.\
B5. Phase-0 source review document.

## Epic C --- Ingestion

C1. Adapter protocol.\
C2. Demo fixture adapter.\
C3. Apify adapter.\
C4. IngestionRun lifecycle.\
C5. RawJob immutable persistence.\
C6. Idempotency.\
C7. Quarantine invalid records.\
C8. Retry/dead-letter behavior.\
C9. Run metrics.

## Epic D --- Deduplication

D1. Normalization utilities.\
D2. Exact/hash dedupe.\
D3. Fuzzy candidate generation.\
D4. Semantic fallback experiment.\
D5. Gold duplicate dataset.\
D6. Precision/recall report.

## Epic E --- Taxonomy

E1. Role taxonomy v0.1.\
E2. Skill taxonomy v0.1.\
E3. Alias table.\
E4. Skill edges.\
E5. Taxonomy versioning.\
E6. Unknown/review queue.

## Epic F --- Extraction

F1. Extraction schema.\
F2. Prompt registry.\
F3. AI gateway.\
F4. Structured extractor.\
F5. Evidence-span capture.\
F6. Gold extraction set.\
F7. Eval runner.\
F8. Confidence/review routing.

## Epic G --- Market analytics

G1. Normalized jobs.\
G2. Market snapshots.\
G3. Skill counts/shares.\
G4. required/preferred split.\
G5. source/company-normalized metrics.\
G6. co-occurrence.\
G7. persistence/growth.\
G8. snapshot quality score.

## Epic H --- Market UI

H1. Dashboard shell.\
H2. filters.\
H3. sample-size/source banner.\
H4. role chart.\
H5. skill chart.\
H6. skill drill-down.\
H7. source provenance view.

## Epic I --- Learner/evidence

I1. learner goals.\
I2. multidimensional skill state.\
I3. evidence records.\
I4. self-assessment import.\
I5. manual override.\
I6. uncertainty/history.

## Epic J --- Roadmap

J1. role skill profile.\
J2. scoring v1.\
J3. prerequisite resolver.\
J4. roadmap version.\
J5. explanation payload.\
J6. roadmap UI.\
J7. anti-thrashing policy.

## Epic K --- Learning

K1. learning unit schema.\
K2. Turkish conceptual template.\
K3. English bridge template.\
K4. sentence parsing tasks.\
K5. assessments.\
K6. mastery rules.\
K7. spaced review.

## Epic L --- Interviews/projects

L1. question schema.\
L2. rubrics.\
L3. text interview.\
L4. evaluator benchmark.\
L5. project template.\
L6. evidence mapping.\
L7. portfolio story.

## Epic M --- Certification

M1. certification schema.\
M2. AWS MLA-C02 objective map.\
M3. practice attempts.\
M4. readiness view.\
M5. other certification adapters.

## Epic N --- Applications

N1. opportunity fit.\
N2. hard/preferred separation.\
N3. application funnel.\
N4. outcome feedback.\
N5. policy-controlled roadmap influence.

## Recommended first sprint

Do only: A1-A8, B1-B3, C1-C2, C4-C6, C9.

Goal: prove that the system can ingest reproducibly before adding
scraping complexity or LLM extraction.
