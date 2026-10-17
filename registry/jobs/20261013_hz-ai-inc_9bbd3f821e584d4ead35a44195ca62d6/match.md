# Match Analysis

**Score:** 86/100  
**Recommendation:** Strong Match

Strong hands-on Go and distributed-backend fit with PostgreSQL, APIs, event-driven systems, idempotency, retries, Kubernetes, and observability; GPU and security specifics are gaps.

## Why it matches

- Production Go, PostgreSQL, distributed systems, APIs, retries, and operational ownership are supported.
- Kubernetes, Prometheus, and GCP-adjacent infrastructure experience is relevant.
- The candidate has fintech-related background for billing and correctness concerns.

## Gaps

- mTLS, signed credentials, GPU infrastructure, Rust, NATS, and money-movement correctness are not fully established.

## Concerns

- The role is highly correctness- and security-sensitive, so the missing specifics require technical verification.

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| Five-plus years and production Go | critical / stated | strong | 5+ years of backend engineering experience. - Strong production Go experience. | Backend engineer with 15+ years of experience building and improving production systems across **PHP** and **Go**. | / |
| PostgreSQL, distributed systems, idempotency, and retries | critical / stated | strong | Experience building distributed or event-driven systems. - Experience designing idempotent APIs and handling retries or partial failures. | Diagnosed and eliminated daily fatal failures (up to 14/day) of a cron scanning ~7,000 tickets under Intercom API degradation by introducing partial-success semantics and sharded cursor pagination, cutting full-scan time roughly 4×. | The example is support infrastructure rather than GPU marketplace infrastructure. / Translate the confirmed reliability patterns without claiming GPU or ledger experience. |
| Security-sensitive APIs and money movement | high / stated | partial | Ability to reason clearly about correctness, security, and money movement. | My background includes document automation, customer operations automation, digital products, e-commerce, fintech-related systems, and communication-heavy platforms. | Specific mTLS, cryptography, ledger, and reconciliation evidence is not present. / Verify security-sensitive API and financial transaction examples. |
