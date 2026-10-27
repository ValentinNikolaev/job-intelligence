# Match Analysis

**Score:** 78/100  
**Recommendation:** Match

Strong backend and Go fit for a remote high-load role, with relevant PostgreSQL, RabbitMQ, AWS, Kubernetes, event-driven, and performance experience. Direct evidence for 10k+ RPS, Redis, Node.js-to-Go migration, and iGaming mechanics is not present.

## Why it matches

- 15+ years of backend engineering experience and recent ownership of a Go support-automation platform.
- Relevant PostgreSQL, RabbitMQ, AWS, Kubernetes, event-driven, message-delivery, and performance work.
- Remote EU location and experience with architectural decisions and technical leadership.

## Gaps

- Redis, ClickHouse, Node.js migration, iGaming slot mechanics, RNG, RTP, and payout logic are not established in the profile.
- The profile does not establish prior operation at the stated 10k+ RPS level.

## Concerns

- The role is explicitly senior and concurrency-heavy, while the profile gives strong adjacent evidence but no direct concurrency or 10k+ RPS example.
- ACID and complex transaction expertise is not stated directly.

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| Go expertise | critical / stated | partial | Strong expertise in Go and deep understanding of concurrency and performance | Go-based support automation platform | The profile confirms substantial recent Go ownership but does not directly document deep concurrency work. / Validate concurrency and performance depth through technical discussion and a system-design example. |
| High-load distributed systems | critical / stated | partial | Experience working with high-load distributed systems | resilient message delivery pipelines | The supplied profile does not establish the vacancy's 10k+ RPS scale. / Ask for a concrete throughput, latency, and failure-mode example. |
| Backend development experience | critical / stated | strong | 5+ years of backend development experience | 15+ years of experience | / |
| PostgreSQL, complex transactions, and optimization | high / stated | partial | Experience with PostgreSQL, including complex transactions and optimization | PostgreSQL | PostgreSQL is listed, but complex transaction work is not described directly in the sealed profile. / Confirm transaction design and query-optimization examples. |
| Redis and message brokers | high / stated | partial | Experience with Redis and message brokers (RabbitMQ or similar) | RabbitMQ | RabbitMQ is evidenced, while Redis is not present in the profile. / Confirm Redis state-management experience or treat it as a ramp-up item. |
| ACID and data consistency | high / stated | partial | Strong understanding of ACID principles and data consistency | versioned event schema | Data consistency is evidenced, but ACID principles are not named directly. / Probe transaction and consistency guarantees in the interview. |
| Legacy refactoring | high / stated | unknown | Experience working with legacy systems and refactoring is a strong advantage |  | Legacy-system and refactoring depth is not established, which may affect the migration portion of the role. / Ask for a concrete legacy refactoring or migration example. |
| Independent remote work | high / stated | partial | Ability to work independently in a remote environment | Fiumicino, Latium, Italy | The location is compatible with the EU remote format, but independent remote-work evidence is not explicit in the profile. / Confirm remote collaboration context and working arrangements. |
