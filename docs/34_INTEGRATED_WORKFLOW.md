# Integrated learning-to-application workflow

2026-10-06. Extends docs21 without changing production release gates.

Learners can now open a suggested next lesson, record concept/English practice, link artifacts, rehearse an interview, review multiple job requirements, download an evidence inventory and track an application. No application is sent.

## Acceptance

- Suggestions use each lesson’s latest attempt, even outside the 50-item history. Changed content prompts refresh; incorrect checks prompt concept practice; assisted answers prompt independent practice. Self-reported independent answers still require external defense/review. No mastery or CEFR inference.
- Opportunity form records up to 20 explicit requirements with source excerpts and independent mandatory/preferred flags. Unknown eligibility stays unknown.
- Authenticated preparation endpoint includes only relevant recorded evidence, assistance, source date, requirement checks, missing links and English defense prompts. No generated achievements, CV metrics or automatic submission. Pack is computed from current records; deletion removes its source data. Previously downloaded exports are outside server deletion.
- Browser acceptance covers learning/save/reload, evidence, interview, multiple requirements, packet download, application stage, export and logout/revocation. PostgreSQL and browser checks must pass remotely.

## Validation and boundary

Local Python: 71 passed / 58 skipped (no PostgreSQL); Ruff/mypy pass; web lint/typecheck/build pass. Remote CI pending on branch. No migration or new infrastructure required.

Catalog v3 now contains 24 authored lesson units alongside the activity scaffolds; see docs35 for the small-lab and independent-validation boundary. Market sampling fixtures are synthetic; live source approval, empirical evaluation, live model evaluation, full-course independent review and deployment acceptance remain open. This workflow is a usable personal product increment, not evidence that those gates passed.
