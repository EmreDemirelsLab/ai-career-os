# 07 --- Delivery Plan and Acceptance Criteria

## Phase 0 --- Research and contracts

Deliverables: - source registry - role taxonomy v0.1 - skill taxonomy
v0.1 - data contracts - 500--1,000 job research sample - dedupe
benchmark - extraction gold set - ADR baseline

Exit criteria: - at least 3 viable source types or a documented reason
for fewer - every source has a collection policy - raw schema stable
enough for migration - 100+ manually reviewed extraction examples -
duplicate benchmark exists

## Phase 1 --- Market Intelligence MVP

Build: - ingestion runs - raw storage - dedupe - normalization -
extraction - taxonomy mapping - market snapshots - dashboard

Acceptance: - rerunning the same ingestion is idempotent - aggregates
are traceable to source jobs - duplicate benchmark reaches agreed
threshold - extraction metrics visible - dashboard always shows sample
size/date/source coverage - no LLM-generated percentage without SQL
evidence

## Phase 2 --- Learner and Evidence Graph

Build: - goals - learner skill dimensions - evidence - manual override -
uncertainty

Acceptance: - a skill can hold different
conceptual/coding/production/interview scores - every non-self-reported
score links to evidence - history is preserved

## Phase 3 --- Gap and Roadmap Engine

Build: - role profile - deterministic priority formula - prerequisite
resolver - roadmap versioning - explanation layer

Acceptance: - same inputs/version produce same roadmap - every item
explains why it is prioritized - blocked prerequisites are visible -
low-quality market snapshot cannot trigger large automatic reorder

## Phase 4 --- Learning Engine

Build: - learning units - Turkish conceptual scaffolding - English
bridge - assessments - spaced review

Acceptance: - completion does not equal mastery - delayed recall is
scheduled - mastery changes only through defined evidence rules - lesson
can explain its target skill and roadmap reason

## Phase 5 --- Interview and Projects

Build: - question bank - rubrics - text interview - project generator -
portfolio evidence

Acceptance: - technical and English evaluation are separate - feedback
cites rubric dimensions - project maps to market skills and evidence
requirements

## Phase 6 --- Certifications

Build: - objective mapping - AWS MLA-C02 track - vendor-neutral
certification model - practice attempts

Acceptance: - certification objectives map to canonical skills -
certification progress does not inflate unrelated skill mastery

## Phase 7 --- Applications

Build: - opportunity fit - application tracking - outcome feedback

Acceptance: - fit explanation separates hard vs preferred requirements -
application outcomes can influence recommendations only through a
versioned policy

## Phase 8 --- Voice and advanced adaptation

Only after text interview/evaluation is reliable.

## Engineering Definition of Done

A feature is done only if: - requirement/acceptance criteria exist -
schema/migration included - unit tests pass - integration tests pass
where relevant - security implications reviewed - observability added -
error states handled - docs updated - AI feature has eval coverage - no
secret committed - rollback/migration impact understood

## Release discipline

Use: - short-lived branches - pull requests - CI - migration checks -
staging - release notes - ADR for architecture changes
