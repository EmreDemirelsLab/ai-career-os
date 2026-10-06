# Ingestion entry points

`career-os ingest-fixture --key demo-1` runs a local synthetic ingestion batch.

PostgreSQL operator orchestration:

1. Review/register an exact Greenhouse board and explicitly enable its source.
2. `career-os schedule-source SOURCE --interval-minutes 1440 --state enable`
3. `career-os schedule-tick --limit 25` creates bounded durable job metadata without HTTP.
4. `career-os schedule-status SOURCE` shows recent job IDs.
5. `career-os collection-work JOB_ID` executes one due job, with source locking, capped retries and crash recovery. Terminal FAILED returns exit code 1; RETRY persists a later due time.

No cron/daemon is installed. Do not run manual collectors concurrently for scheduled sources or reuse the reserved `collection:` request-key prefix. See docs/27_COLLECTION_SCHEDULING.md and docs/28_COLLECTION_WORKER.md for exact behavior and limitations. These commands do not grant source approval. All verification so far uses synthetic/mocked HTTP data.
