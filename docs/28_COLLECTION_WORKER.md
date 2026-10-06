# P3b2 — explicit collection worker and recovery

Operator command: `career-os collection-work JOB_ID` (same runtime DB configuration as schedule commands). One job per invocation. There is no resident daemon, automatic cron installation or live source approval.

## State and concurrency contract

A dedicated PostgreSQL connection owns a per-source session advisory lock across HTTP and ingestion commits. Concurrent workers return BUSY. Unlock is explicit; if unlock fails the connection is invalidated instead of pooled. PENDING/RETRY work runs only after database-clock due time. Source policy and schedule enablement are checked before attempts; the collector checks source policy again before HTTP.

The RUNNING transition and attempt number commit before HTTP. Attempt keys are `collection:JOB_ID:ATTEMPT`; maximum three attempts. Failure schedules 5, then 10 minutes of backoff; no process sleeps. Final failure does not fetch again. Provider exception text is not stored.

Recovery first looks up the prior ingestion run. COMPLETED/PARTIAL finalizes metadata without refetch. An orphaned RUNNING run is failed under the source worker lock; a job interrupted before run creation also consumes its attempt and schedules retry. Ingestion commits raw/observations atomically. PARTIAL is a terminal operator-review result, not an unbounded retry.

HTTP is not exactly-once: death after downloading but before durable ingestion can cause a later refetch. Immutable revision identity prevents duplicate raw revisions. Session lock safety assumes a live PostgreSQL session; network partition/fencing across lost database sessions is not a distributed exactly-once guarantee. Manual collector operations do not participate in this worker lock; operators must not reuse the reserved collection key prefix or concurrently run manual collection for scheduled sources.

## Acceptance

Disposable PostgreSQL tests cover two workers/one request, crash after ingestion commit/no refetch, crash before ingestion/recovery, due time/retry cap, source/schedule disable/no request. All HTTP is mocked with synthetic source records. Local lint/types passing is insufficient; PostgreSQL CI and existing Compose/browser/restore regression gates must pass.

No real collection or external API call was made during implementation. Periodic operation, monitoring, metadata retention for growing job history, live-source policy review and the real market benchmark remain open.
