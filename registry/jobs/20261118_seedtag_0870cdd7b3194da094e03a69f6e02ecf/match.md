# Match Analysis

**Score:** 78/100  
**Recommendation:** Match

Strong recent production Go, event-driven integration and operational ownership suit the role. Low-latency p99 or serving-cost evidence, ad exchange experience and daily AI-tool usage remain material uncertainties. Italy is listed for remote contracts.

## Why it matches

- Five years of hands-on production Go confirmed.
- Go support-platform ownership, production incident recovery, and event-driven routing with backpressure.
- Remote contract locations include Italy.

## Gaps

- No substantiated p99 improvement or ad exchange and auction experience.
- Kafka, Google Cloud and the full set of listed resilience patterns are not established.
- Daily AI coding-tool use is not documented.

## Concerns

- Ticket volume cannot be equated to real-time bidding request rates.
- The airSlate ECS-to-Kubernetes migration attribution was withdrawn.

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| Distributed systems and backpressure | critical / stated | partial | Distributed systems: message queues, caches, data stores, and how they fail. Concurrency, consistency and backpressure. | delivery guarantees and backpressure handling. | Queue and backpressure evidence is present, but detailed cache, concurrency and consistency experience is not established. / Discuss actual event-delivery and failure choices without extrapolating. |
| Backend and recent production Go | critical / stated | strong | 5+ years building backend systems, with recent years writing Go in production. | five years of hands-on experience developing production systems in Go (Golang) | / |
| Measured p99 or serving cost in high-throughput, low-latency systems | high / stated | partial | Experience with high-throughput, low-latency services. You have measured and improved p99 latency or serving cost on a real system. | The system now supports tens of thousands of user interactions per month | P99 measurement and exchange-scale traffic are not established. / Discuss supported workload and clarify latency or serving-cost measurements. |
| Kubernetes, cloud, CI/CD and observability | high / stated | partial | Kubernetes and cloud deployments, CI/CD and production observability. | Kubernetes CronJobs | The profile lists technologies but the airSlate migration attribution was withdrawn. / Use separately supported CronJob, deployment and monitoring examples. |
| Data-driven validation | high / stated | partial | A data-driven mindset. You validate hypotheses with real data. | Grafana and operational observation | A concrete hypothesis-to-result measurement process is not fully described. / Explain an actual supported measurement and its limits. |
| Resilient low-latency service patterns | high / stated | partial | Resilient design: You have designed scalable, robust and self-healing services for high-transactional, low-latency workloads | partial-success semantics | Not all listed patterns or transactional latency requirements are evidenced. / Describe the actual scan recovery and its boundaries. |
| Production architecture and recovery | high / stated | partial | Architecture patterns in production. | Designed and owned a Go-based support automation platform | Autoscaling, sharding and canary ownership as described in the vacancy are not established. / Clarify production architecture experience using specific examples. |
| Daily AI coding tools | high / stated | unknown | AI-native workflow. You use AI coding tools daily |  | Daily use and review practices are not documented. / Confirm actual usage and frequency. |
| English communication | high / stated | partial | Clear communication with engineers, Product and non-technical stakeholders, in English. | English - Upper-intermediate | The specific cross-functional English scope is not documented. / Discuss actual communication experience. |
| End-to-end ownership | high / stated | strong | Ownership. You take a fuzzy problem to a measured outcome and keep the service healthy after launch. | Owned architecture and backend end-to-end | / |
| Remote Italy | meaningful / stated | strong | Remote contracts available in Spain, Italy, the UK, Belgium, the Netherlands, France, and Germany. | Rome, Italy | / |
| AdTech domain | preferred / stated | unknown | AdTech experience: OpenRTB, auctions, bid floors, SSP/DSP integrations or CTV |  | Direct exchange-domain experience is not established. / Treat as a learning area. |
