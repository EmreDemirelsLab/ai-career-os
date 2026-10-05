> Workspace extension: see docs/21 and docs/22. The foundation-only interface inventory below predates authenticated personal workspace routes. Single-owner access uses a local bearer token and HttpOnly same-origin browser session; this is not production identity management.

# Operations, security and learner defense

Date: 2026-10-05. Scope: trusted local development, not hosted production.

## Safety boundaries

Only `/health` and `/ready` are exposed. No public source mutation, raw payload, user profile or ingestion endpoint. Operator CLI inherits the caller's DB credentials and must remain trusted. API/web/PostgreSQL host ports bind loopback. Redis has no host port. Containers run app processes as non-root. No live source is enabled and fixture URLs are never fetched, avoiding a network/SSRF entry point in this slice. Credentials are supplied via environment; local example passwords are not production secrets.

Validated payloads may still contain hostile text. They are stored as data, never evaluated, rendered as HTML or sent to an LLM here. Logs contain run IDs/counters and safe error codes only. Invalid content is represented by hash and field/code errors; the input fixture remains the replay artifact. This minimal quarantine does not yet support arbitrary production raw-payload recovery.

## Run state and failure recovery

RUNNING is committed before iteration. The batch writes raw revisions, observations, rejections and final counters atomically. Failure rolls back that transaction and writes FAILED with `batch_failed`, zero committed counters. Thus failed-run counters describe committed records, not partially attempted work. Inspect the source fixture in the trusted operator environment to diagnose; exception text is intentionally not published.

Same request key + fingerprint returns the existing run (including RUNNING/FAILED) and never starts a second batch. Distinct keys add observations but reuse unchanged raw revisions. Changed content adds a revision. Hashing excludes envelope fetched_at but includes the adapter payload; future adapters must remove volatile transport fields from payload according to a versioned contract.

Abrupt process termination can leave RUNNING. Verify the worker is dead and the DB transaction is rolled back before `career-os fail-run <id>`, then retry with a NEW request key. No automatic recovery lease, heartbeat or retry queue is claimed. DB row locking prevents recovery from racing an active committed run in PostgreSQL.

Source disable prevents new runs; it does not cancel a batch already authorized. Enabling a live source requires a reviewed policy migration/change containing method, policy reference, reviewer, retention days and a real adapter. Generic ATS registry rows do not approve every employer.

## Data and migrations

Raw UPDATE/DELETE is prohibited by DB triggers. Observation history captures sightings; absent jobs are not inferred closed from one incomplete source run. Retention limits are policy metadata only in Sprint 1; no external personal data is collected. Before live ingestion, implement authorized retention/deletion with separate maintenance privileges and reconcile immutability with minimization.

Initial migration downgrade destroys foundation tables: only use on disposable development/test databases. Back up real data before future schema changes. No backup/restore SLO, production IAM/RBAC or deployment is implemented yet. Database owner credentials can change triggers; production must use a restricted application role.

## Independent learning gate (not yet assessed)

1. Explain in Turkish why a content revision differs from a sighting.
2. Implement or debug a changed-description test without an assistant writing the solution.
3. Explain in English: “An idempotency key identifies an operation; a content hash identifies a revision.”
4. Defend ON CONFLICT, source scoping, transaction boundaries and rejected-record visibility in a three-minute recording.
5. Answer: What happens if the process dies after creating the run? Why is SQLite insufficient evidence for PostgreSQL concurrency?
6. Repeat the explanation after 3 and 14 days. Store future evidence with artifact commit, assistance level, rubric version and separate technical/English scores; never publish private recordings by default.
