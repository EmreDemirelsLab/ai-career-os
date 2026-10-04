# 04 --- Market Intelligence and Ingestion

## 1. Objective

Produce defensible, reproducible labor-market intelligence rather than a
scraped pile of job descriptions.

## 2. Source strategy

For each source define: - legal/terms review status - official API/feed
availability - permitted collection method - robots/rate constraints
where relevant - geographic coverage - freshness - data fields -
reliability - cost - duplicate tendency

Preferred order: 1. official API/feed/export, 2. public company career
endpoints, 3. approved Apify Actor/source adapter, 4. custom browser
automation only when justified and permitted.

Do not assume that a technically scrapable page is automatically an
approved production source.

## 3. Apify usage

Use Apify for: - source-specific Actors, - scheduling, - proxy/browser
infrastructure where needed, - datasets, - run monitoring, - webhooks.

Use scoped credentials and least privilege.

MCP is used for interactive development/agent access; production backend
uses Apify REST/client APIs and webhooks.

## 4. Ingestion contract

Every adapter emits a common envelope:

-   source
-   source_job_id
-   source_url
-   fetched_at
-   published_at if available
-   title
-   company
-   location
-   description
-   raw payload
-   adapter version

Validation failures go to quarantine, not silent deletion.

## 5. Deduplication

Stages: 1. deterministic exact keys, 2. normalized
company/title/location, 3. content hash, 4. fuzzy similarity, 5.
semantic similarity for unresolved cases.

Maintain duplicate clusters and confidence.

Build a manually labeled duplicate benchmark before tuning thresholds.

## 6. Extraction

Extract: - canonical role - seniority - skills - required/preferred
status - years of experience - education - language - certifications -
cloud/framework/tool requirements - responsibilities - domain/industry -
salary where available

Every extraction uses a strict schema.

## 7. Extraction evaluation

Create a gold set stratified by: - source - role - language -
seniority - country

Measure: - precision - recall - F1 - exact match for structured fields -
calibration by confidence band

No production market statistic should depend on an extractor whose
quality is unknown.

## 8. Market metrics

For each skill/role/geography/time window compute: - unique job count -
share of jobs - required share - preferred share - seniority
distribution - median/available salary association - co-occurrence -
persistence - growth - source concentration

## 9. Source-bias controls

A skill can appear inflated because one source or one company posts many
similar jobs.

Therefore calculate: - raw job share - company-normalized share -
source-normalized share - unique-company count

Display sample size.

## 10. Trend classification

Suggested classes: - foundational - mainstream - accelerating -
emerging - niche - insufficient-data

Do not classify "declining" without sufficient longitudinal history and
confidence.

## 11. Market snapshot quality score

Factors: - unique jobs - source diversity - company diversity -
freshness - duplicate confidence - extraction quality - taxonomy mapping
rate

Low-quality snapshots must display a warning and must not drive
aggressive roadmap changes.

## 12. Roadmap change policy

Market change alone does not immediately reorder curriculum.

A change proposal must consider: - magnitude - persistence - target-role
relevance - prerequisite readiness - learner gap - switching cost

Use hysteresis/cooldown to prevent weekly roadmap thrashing.

## 13. Data retention

Raw source content retention must be configurable per source policy.
Aggregated derived statistics can have different retention rules. Store
only what is necessary for the product purpose.

## 14. Phase-0 research output

Before production collection: - source registry - collection policy per
source - initial 500--1,000 job research sample - first role taxonomy -
first skill taxonomy - duplicate benchmark - extraction gold set -
baseline market snapshot
