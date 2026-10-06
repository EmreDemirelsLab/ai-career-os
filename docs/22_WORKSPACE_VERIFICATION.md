# Personal workspace acceptance — 2026-10-05

Scope: extends the completed foundation slice; does not declare the entire AI Career OS complete. The completion contract is [docs/21](21_COMPLETE_PRODUCT_CONTRACT.md). Foundation-only exclusions in docs/16–20 describe the earlier slice.

## Implemented behavior

- Single-owner bearer access, disabled without a configured >=32-character key; browser session is HttpOnly/SameSite Strict. Mutations require same origin. Local loopback deployment only.
- Profile snapshots and saved baseline roadmap snapshots; later profile edits do not rewrite earlier plans.
- 24 authored activity scaffolds with official source starting points. This is not a validated full course or a market-adaptive prerequisite planner.
- Persisted concept/English submissions, 3/7/14/30-day review queues, duplicate and early-review rejection. No submission certifies mastery.
- Canonical skill evidence with assistance and review provenance; external review links remain user-entered assertions.
- English interview rehearsal with separate technical/English rubric dimensions; assessment remains unavailable.
- Manually sourced opportunities, explicit requirement evidence and conservative eligibility; no missing requirement is inferred from ad language. UI supports one requirement per opportunity; API supports multiple.
- Application and stage-event history, JSON export, explicitly confirmed personal-data deletion. Ingestion records are outside the deletion scope.
- Explicit migration 0002 with foreign keys and unique recall intervals; package-contained curriculum/taxonomy.

## Checks

Local: Ruff lint/format and mypy pass; pytest **24 passed, 17 skipped** (PostgreSQL unavailable). Web lint, TypeScript and production build passed. Chromium download failed in this environment; local browser verification is not claimed.

CI gates configured: SQLite + PostgreSQL tests, migration roundtrip/metadata drift, frontend build, Docker Compose boot and fixture idempotency, Playwright real-browser login/profile/roadmap/learning/persistence/export/logout test. CI on 2026-10-05 confirmed **39 passed, 2 skipped** (the two SQLite variants of PostgreSQL-only concurrency tests), web lint/typecheck/build and Compose startup/ingestion. [Initial run](https://github.com/EmreDemirelsLab/ai-career-os/actions/runs/37298775549) found a browser container-origin mismatch; it was corrected to use the explicit browser origin. Browser acceptance must pass on the final PR head before this slice is accepted; see the PR checks for the authoritative current result.

## Operation and limitations

Run `python3 scripts/init_workspace.py` once before Compose; existing .env is never overwritten. Read the key locally, never publish it. Browser mutations use the explicit `WORKSPACE_ORIGIN` (default `http://localhost:3000`), not the container-internal hostname or untrusted forwarding headers. Set it to the exact browser origin when changing the local address. For native Next.js, export it into the web process environment. Restart API after rotating the key; old sessions then fail verification. Export personal data before destructive resets. Database volume persistence is not a backup strategy.

This local token is not multi-user identity or production session management. Public hosting, managed auth, TLS configuration, rate limits, background retention, encrypted backups and restore drills remain release gates. All workspace records are loaded together: pagination and large-volume benchmarks remain open. API-created profile/roadmap versions are preserved by behavior; database administrators can still alter them.

Live-source ingestion adapters, extraction evaluation/gold set, market snapshots, adaptive planning, calibrated mastery assessment, LLM tutor/interview evaluation and production deployment remain **unimplemented**. Provider credentials alone will not complete these engines. See docs/21 for the required subsequent acceptance gates.
