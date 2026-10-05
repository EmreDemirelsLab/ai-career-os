# Complete product contract and staged delivery

Date: 2026-10-05. Owner request: complete the AI Career OS system.
This supersedes the Sprint 1-only restriction for subsequent branches, not the quality gates.

## Release definitions

- Foundation: completed and CI-verified in PR #1.
- Personal workspace: authenticated single-owner local application with persistent profile snapshots, evidence, saved plans, structured learning/English submissions, spaced review, interview rehearsal, reviewed opportunities and application history. This branch implements this coherent workflow; it is not the full production AI product.
- Full production product: additionally requires approved live sources, empirical Phase 0 sample and benchmarks, evaluated extraction, versioned market snapshots, a prerequisite skill graph and calibrated gap scoring, an evaluated LLM tutor/interviewer, production identity, deployment, backup/restore, monitoring and a user acceptance run.

## No hidden substitutions

Manual opportunity notes are reviewer observations, not automatically extracted job-market facts. A fixed 24-week curriculum is a baseline plan, not a market-adaptive recommendation. Learning submissions and self-ratings are not verified mastery. Interview rehearsal is not automatic AI evaluation. Missing LLM/live-source connections are displayed as unavailable. Source candidates stay disabled. No fake dashboards, job probabilities, user history or generated test outcomes.

## Personal workspace acceptance

1. Unauthorized data reads/writes fail closed; token unset disables workspace API.
2. Profile versions are append-only; saved roadmap captures profile and curriculum versions.
3. Evidence stores skill, dimension, artifact, assistance and verifier; self-report never becomes externally verified.
4. A learner can save a topic submission in Turkish and English and see review dates at 3/7/14/30 days.
5. Interview responses are persisted with rubric criteria and explicitly unassessed status.
6. Opportunity eligibility separates user-reviewed hard constraints from capability evidence; unknown remains unknown. No single match percentage.
7. Application status changes append an event history and cannot reference nonexistent opportunities.
8. Export and deletion work for personal workspace data.
9. Browser login uses an HttpOnly session cookie; mutating browser requests require same origin. API key never stored in localStorage or embedded in frontend bundles.
10. Flow is tested on PostgreSQL in CI, including wrong-token denial, validation, evidence provenance, roadmap reproducibility, learning reviews, eligibility and application foreign keys.

## Production blockers and work still required

| Gate | Required before completed production claim |
| --- | --- |
| Market | Per-employer/source approval, bounded live collector, scheduling/retry, retained provenance, sampled source coverage and benchmarked dedupe/extraction |
| Adaptive plan | Versioned skill IDs/prerequisite edges, evidence rubric calibration, market/learner snapshots and deterministic scoring policy |
| AI learning/interview | Provider credentials, approved model/budget, structured gateway, prompt versions, gold cases, injection tests and expert-calibrated rubric evaluation |
| Identity | Replace single-owner shared token with production session/auth, revocation and tenant isolation before multi-user hosting |
| Deployment | Authorized hosting account, secrets, TLS/domain, restricted DB role, migrations, monitoring, tested backup/restore and deletion/retention |
| Education | Validated lesson content and independent learner assessment; seed prompts are study activities, not a complete six-month course |

No new billable cloud resources or secret credentials are created in this branch. Credentials should be entered in the deployment environment, never committed or pasted into a public issue.
