# P4a — foundation lesson and practice pilot

2026-10-06. Four authored lessons align with baseline weeks 1–4: Python input contract, SQL integrity, API validation and idempotent data flow. This is a usable foundation pilot, not a validated 24-week course or a mastery/CEFR classifier.

## User flow

Authenticated **Temel alıştırmalar** tab provides why → concept → worked example → local exercise → debugging prompt → technical English defense. Each lesson has two objective questions and separate technical/English review criteria. Sources were opened on 2026-10-06: Python errors tutorial, PostgreSQL17 constraints and FastAPI request-body documentation (exact links in the catalog). Lesson prose/examples are authored; source pages are reading references, not copied course content.

`labs/foundation/exercises.py` contains intentionally failing starter functions. `uv run python labs/foundation/check.py --week N` runs local checks. The reference implementation passes all five checks and is available only as an assisted learning aid; CI validates the reference and confirms the starter fails. SQLite lab tests do not replace PostgreSQL concurrency/permission checks. No uploaded code is executed by the API.

The learner submits question choices, technical explanation, English defense, assistance level and optional artifact URL. Only choice correctness is automatically checked. Technical implementation and English quality remain unassessed; even full marks do not create EvidenceRecord, mastery or CEFR status. External independent debugging/defense review remains necessary. Repeated submissions are separate practice attempts; no paid request or hidden retry occurs.

## Persistence and integration

Routes `/workspace/lessons` GET and `/workspace/lessons/attempts` POST reuse existing bearer/session authorization. GET omits correct-choice keys and feedback until submission; these authored questions are not secret exams. POST requires current catalog version, exact question IDs, integer choices, bounded answers and explicit assistance. Historical records store content fingerprint/version, question prompts, selected answers and feedback.

Attempts use the existing LearningAttempt table, so 3/7/14/30-day recall, workspace export and confirmed personal deletion apply without a migration. Latest 50 lesson attempts appear in the lesson tab. Learning text is never evaluated as code. Existing baseline 24-week activity scaffold remains unchanged; lessons are an added layer for weeks 1–4 only.

## Acceptance

- Catalog skill/week alignment, invalid/versioned input, unauthorized denial and answer-key stripping.
- Objective score stays separate from mastery, implementation and English assessment, including generated assistance.
- Persist/reload/export/recall/delete integration on SQLite and PostgreSQL.
- Local reference lab succeeds; unimplemented starter fails as documented.
- Frontend lint/type/build and browser lesson submission/reload/export scenario.
- Existing Compose, hosted configuration and backup/restore regression gates.

## Next P4 slices

Expand executable data/ML exercises and independent-review rubrics after the foundation flow passes. Add diagnosis-driven recommendations with explicit uncertainty rather than interpreting two questions as mastery. Real learner baseline, independent assessor validation, lessons 5–24, spoken English assessment and live-model quality remain open. P3 empirical market and human annotation gates also remain open while education implementation continues.
