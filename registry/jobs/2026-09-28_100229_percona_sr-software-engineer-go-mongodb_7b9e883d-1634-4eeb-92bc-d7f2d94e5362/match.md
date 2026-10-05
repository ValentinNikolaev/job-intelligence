# Match Analysis

**Score:** 78/100
**Recommendation:** Match

Good remote Go tooling fit through backend, reliability, APIs, and observability evidence; MongoDB replication internals and open-source depth are not established.

## Why it matches

- Production Go
- Event-driven reliability work
- APIs and monitoring
- Italy included in remote metadata

## Gaps

- Change streams
- oplog
- sharding
- backup/restore
- and open-source contribution are not explicit

## Concerns

- Concurrency and database-internals bar is high

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| Production Go concurrency | critical / stated | partial | Strong Go experience in production, **with real fluency in concurrency: goroutines, channels, context cancellation, worker pools, and backpressure. You have debugged a race condition that only showed up under load, and you know how you found it. | - Build resilient message delivery pipelines with fallback logic, retries, and | Explicit goroutine and race-debugging evidence is absent. / Verify concurrency depth. |
| MongoDB replication internals | critical / stated | unknown | Hands-on MongoDB knowledge: **change streams, the oplog, resume tokens, replica sets, and sharding. You do not need to have built replication before, but you should understand why it is hard. |  | MongoDB internals are not established. / Confirm hands-on MongoDB scope. |
| APIs and operational metrics | high / stated | partial | Comfort building and operating command-line tools and HTTP APIs, **and instrumenting them with metrics and structured logs. | - Engineer a unified API orchestration layer to streamline ticket routing, | CLI and structured-log details are not explicit. / Verify operational tooling examples. |
