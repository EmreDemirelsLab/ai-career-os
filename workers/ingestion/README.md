# Ingestion entry point

`career-os ingest-fixture --key demo-1` executes the application service in a local process. It is not a durable queue worker. Redis dispatch, leases, retry/backoff and dead-letter delivery are deferred to C8; a future worker calls the same service.
