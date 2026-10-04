# 03 --- Data Model and Skill Graph

## 1. Design principles

-   Raw data is immutable.
-   Normalized data is reproducible from raw data plus processor
    versions.
-   Market state is temporal.
-   Taxonomy is versioned.
-   Learner mastery is multidimensional.
-   Evidence is first-class.
-   Every recommendation is reproducible from a market snapshot +
    taxonomy version + learner snapshot + scoring version.

## 2. Core entities

### Source

`id, name, type, geography, collection_method, terms_review_status, robots_review_status, enabled, rate_policy, notes`

### IngestionRun

`id, source_id, started_at, completed_at, status, actor_or_adapter_version, parameters, fetched_count, accepted_count, rejected_count, cost, error_summary`

### RawJob

`id, source_id, source_job_id, source_url, payload, description_raw, fetched_at, published_at, content_hash, ingestion_run_id`

### JobCluster

Represents deduplicated logical job.
`id, canonical_company, canonical_title, location, first_seen, last_seen, duplicate_confidence`

### NormalizedJob

`id, job_cluster_id, role_id, seniority, country, city, remote_type, employment_type, salary_min, salary_max, currency, description_clean, language, published_at, last_seen`

### JobRequirement

`job_id, requirement_type, canonical_entity_id, requiredness, years_min, confidence, evidence_span`

Requirement types: - skill - education - certification - language -
experience - domain - responsibility

### Role

Versioned canonical role taxonomy.

### Skill

Fields: - canonical_name - category - description - skill_type -
lifecycle_status - first_seen/last_seen - ontology_version

### SkillAlias

Maps text variants to canonical skill.

### SkillEdge

Types: - prerequisite_of - part_of - related_to - often_cooccurs_with -
alternative_to - builds_on

Edges have provenance and confidence.

### MarketSnapshot

`id, geography, role_scope, window_start, window_end, generated_at, source_set_version, taxonomy_version, unique_job_count, quality_score`

### SkillMarketMetric

Per snapshot: - job_count - share - growth - persistence - cooccurrence
metrics - seniority distribution - required/preferred split

## 3. Learner model

### LearnerGoal

-   target roles
-   target geographies
-   target date
-   weekly hours
-   language target
-   certification targets

### LearnerSkillState

A single percentage is prohibited as the only representation.

Dimensions: - conceptual - mathematical - implementation - debugging -
production - system_design - explanation - interview

Each dimension stores: - score - uncertainty - last_assessed_at -
evidence_count - decay/review_due

### LanguageState

-   general_reading
-   technical_reading
-   listening
-   sentence_parsing
-   speaking
-   technical_explanation
-   interview_communication
-   translation_dependency

### Evidence

Types: - assessment - coding task - project - production artifact -
certification - interview - code review - deployment - documentation -
prior work

Evidence fields:
`skill_id, dimension, strength, verifier, artifact_uri, rubric_version, score, created_at, expires_or_decay_policy`

Self-report is allowed but receives low evidence weight.

## 4. Roadmap entities

### RoadmapVersion

Stores: - market_snapshot_id - learner_snapshot_id - taxonomy_version -
scoring_version - generated_at - target role - constraints

### RoadmapItem

-   skill
-   order
-   status
-   priority components
-   prerequisite status
-   expected hours
-   learning template
-   required evidence
-   English objective
-   assessment gate
-   explanation

## 5. Learning entities

### LearningUnit

-   skill
-   level
-   objectives
-   prerequisites
-   stages
-   source references
-   content version

### Assessment

-   skill/dimension
-   difficulty
-   format
-   rubric
-   expected concepts
-   evaluator version

### Attempt

-   response/code/audio reference
-   score
-   rubric breakdown
-   feedback
-   evaluator/model version

### ReviewSchedule

-   skill/dimension
-   due_at
-   interval
-   retention estimate

## 6. Interview entities

### InterviewQuestion

-   role
-   skills
-   level
-   question_type
-   rubric
-   followups
-   source/provenance where relevant

### InterviewSession

-   target role
-   difficulty
-   questions
-   transcript
-   technical evaluation
-   language evaluation
-   structured feedback

## 7. Applications

### Opportunity

Normalized job + computed learner fit.

### Application

-   opportunity
-   applied_at
-   CV version
-   cover letter version
-   stage
-   outcome
-   interview stages
-   feedback

## 8. Canonical skill rules

Do not create a new canonical skill from one LLM extraction
automatically.

Pipeline: 1. exact alias match, 2. normalized lexical match, 3. semantic
candidate retrieval, 4. LLM candidate classification, 5. confidence
threshold, 6. unknown/review queue, 7. human approval for canonical
addition.

## 9. Taxonomy versioning

Changes that require a new ontology version: - skill merge/split -
prerequisite edge change - role mapping change - category change
affecting analytics

Historical snapshots retain the taxonomy version used when calculated.

## 10. Temporal truth

Never overwrite market history.

A job can: - first appear, - remain active, - disappear, - reappear.

Store observations so duration and persistence can be estimated.

## 11. Provenance

Every extracted requirement stores the supporting source text span or
structured source field where legally/technically possible.

Every aggregate metric must be drillable to:
`metric -> snapshot -> normalized jobs -> raw source records`.

## 12. Readiness model

Readiness is role-specific and multidimensional.

Example conceptual formula:

`Readiness = Σ(skill_importance × evidence_adjusted_mastery × coverage) - critical_gap_penalties`

Do not publish a readiness percentage until: - weighting is versioned, -
critical skills are defined, - uncertainty is represented, - score
explanation is available.
