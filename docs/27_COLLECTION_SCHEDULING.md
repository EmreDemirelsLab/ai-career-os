# P3b1 — bounded collection scheduling

This slice queues metadata only. No worker, cron installation or external HTTP request is introduced. PostgreSQL is required; SQLite fails closed.

## Contract and acceptance

- Operator `schedule-source SOURCE --interval-minutes 1440 --state enable` requires an enabled, reviewed, approved Greenhouse board. Intervals are 60–10080 minutes. Reconfiguration preserves the due time.
- `schedule-tick --limit 25` processes at most 100 due schedules using database time and row locks with SKIP LOCKED. Concurrent ticks cannot enqueue the same cycle twice.
- One outstanding PENDING/RUNNING/RETRY job per source is maintained by scheduler serialization. Missed periods coalesce; there is no historical backfill flood.
- Source policy is checked again at enqueue. Revocation disables the schedule. The future worker must also check immediately before HTTP.
- `schedule-status SOURCE` shows at most 50 recent metadata records. Job records contain no fetched content.
- Migration 0005 has explicit upgrade/downgrade. Existing retention rules remain unchanged.

Tests cover parallel ticks, repeated ticks, active backlog, completed-job progression, source disable, due-time preservation and bounds. PostgreSQL CI is required for acceptance; local SQLite results do not establish locking behavior.

## P3b2 next: worker/recovery

Use a per-source session advisory lock spanning collection; release explicitly before returning a pooled connection. Persist attempt identity before I/O, cap attempts at three and schedule backoff rather than sleeping. Before refetch, inspect the durable ingestion run: completed/partial runs finalize the job; abandoned RUNNING runs require recovery. Test two workers/one request, crash after ingestion commit/no refetch, disabled source/no HTTP and retry exhaustion. Do not claim orchestration complete until these gates pass.

Actual periodic execution, source-specific approval and live collection remain separate release gates. All tests use synthetic sources.
