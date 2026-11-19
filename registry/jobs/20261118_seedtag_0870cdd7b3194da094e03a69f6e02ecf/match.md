# Match Analysis

**Score:** 77/100  
**Recommendation:** Match

Good match for senior Go backend ownership: the profile supports resilient event-driven services, production Go, queues, observability, and Kubernetes-related delivery. The main risks are unproven five-plus years of Go, p99 low-latency measurement, Kafka/GCP, ad-tech auction mechanics, and daily AI coding-tool use.

## Why it matches

- Recent production Go ownership for a support automation platform serving tens of thousands of interactions per month.
- Event-driven systems using queues and EventBridge, with backpressure handling, retries, observability, and 99.9% delivery reliability.
- Backend architecture, CI/CD, Kubernetes-related infrastructure, and measurable performance and cost improvements.
- Remote contract coverage explicitly includes Italy.

## Gaps

- No direct AdTech, OpenRTB, auction, bid-floor, SSP/DSP, or CTV experience is established.
- Kafka, Google Cloud, and p99 latency measurement are not evidenced in the sealed candidate profile.
- The profile does not establish five-plus years writing Go in production or daily AI coding-tool usage.

## Concerns

- The candidate profile contains conflicting historical role dates and a boundary against reusing an unconfirmed ECS-to-Kubernetes attribution; the result relies on the explicit technology and experience evidence only.
- The role's real-time bidding and auction domain is materially different from the candidate's confirmed support and analytics domains.

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| 5+ years building backend systems with recent years writing Go in production | critical / stated | partial | 5+ years building backend systems, with recent years writing Go in production. | backend in Go. | Recent production Go is evidenced, but the sealed profile does not establish five-plus years of Go specifically. / Present the confirmed Go scope and quantify the relevant production period without extending it. |
| Distributed systems, queues, caches, data stores, concurrency, consistency, and backpressure | critical / stated | strong | Distributed systems: message queues, caches, data stores, and how they fail. Concurrency, consistency and backpressure. | backpressure handling. | The profile does not specifically evidence cache or concurrency choices. / Anchor the assessment in queues, routing, delivery guarantees, backpressure, and retries. |
| High-throughput, low-latency services with measured p99 latency or serving cost | high / stated | partial | Experience with high-throughput, low-latency services. You have measured and improved p99 latency or serving cost on a real system. | The system now supports tens of thousands of user interactions per month | Scale and reliability are evidenced, but p99 latency measurement and ad-request millisecond workloads are not. / Do not claim p99 or bidding performance; use verified throughput and reliability outcomes. |
| Kubernetes, cloud deployments, CI/CD, and production observability | high / stated | partial | Kubernetes and cloud deployments, CI/CD and production observability. | Kubernetes | The profile supports these technologies, but the exact cloud/platform scope for this role is not fully detailed. / Describe only the explicit Kubernetes, CI/CD, monitoring, and logging evidence. |
| Resilient self-healing design with retries, graceful degradation, fallback paths, and idempotent processing | high / stated | partial | Resilient design: You have designed scalable, robust and self-healing services for high-transactional, low-latency workloads and applied the patterns on real systems: circuit breakers, timeouts, retries with backoff and jitter, bulkheads, load shedding, graceful degradation and fallback paths, idempotent event processing and caching strategies. | fallback logic, retries, and | Fallbacks, retries, and monitoring are evidenced; the full list of self-healing patterns and low-latency transaction scale is not. / Claim only the confirmed resilience patterns and measured disruption reduction. |
| Remote contract available in Italy | meaningful / stated | strong | Remote contracts available in Spain, Italy, the UK, Belgium, the Netherlands, France, and Germany. | Fiumicino, Latium, Italy | / |
| AdTech experience such as OpenRTB, auctions, bid floors, SSP/DSP integrations or CTV | preferred / stated | missing | AdTech experience: OpenRTB, auctions, bid floors, SSP/DSP integrations or CTV |  | No direct AdTech evidence appears in the sealed candidate profile. / Treat the domain as a learning gap and do not imply prior auction or exchange experience. |
