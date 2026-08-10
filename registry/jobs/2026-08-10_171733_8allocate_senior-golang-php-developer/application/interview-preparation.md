## Recruiter / HR Screening

Prepare concise, factual answers to these likely questions:

- **Why this role?** Connect deep PHP experience with recent Go ownership and the opportunity to modernize a live SaaS backend without disrupting users.
- **Why 8allocate?** Refer to its focus on client value, engineering excellence, flexibility, and direct work with client stakeholders. Do not imply prior knowledge beyond public research.
- **How many years of commercial Go do you have?** Give an exact timeline based on actual projects. Do not convert total backend tenure into Go tenure. Emphasize the depth of recent production ownership and transferable senior backend experience.
- **Are you comfortable with PHP maintenance during migration?** Use airSlate, Hyprr, PDFfiller, and the broader PHP background as evidence.
- **Location and work model?** Confirm residence in Italy and availability for full-time remote work across European time zones.
- **English level?** State the current level honestly. The source CV says Upper-intermediate while LinkedIn records professional proficiency; do not claim C1 unless independently confirmed.
- **Why did Simple App and CRURATED overlap?** Prepare the exact employment or contract arrangement and time commitment.
- **Why are you changing roles?** Use the real current situation and focus on the desired PHP-to-Go modernization scope; do not imply a reason not in the candidate evidence.
- **Salary expectations and notice period?** Both are unknown in the source material. Decide them before the recruiter call.

## Culture Fit / Behavioral Interview

Likely questions and grounded STAR material:

1. Tell me about a migration you completed without disrupting users. Use the Zendesk-to-Intercom migration or the ECS-to-Kubernetes migration.
2. Describe a production reliability problem you owned. Use resilient message delivery, retries, fallback handling, and monitoring at Simple App.
3. Give an example of improving system performance. Use the airSlate database/API bottleneck work and verified performance results.
4. Tell me about a difficult architecture decision made with stakeholders. Use Hyprr's roadmap work with the CTO or CRURATED's versioned event architecture.
5. How do you balance delivery speed and engineering quality? Use CI/CD improvements at airSlate and the modular analytics design at CRURATED.
6. Describe leading through a traffic spike or operational risk. Use PDFfiller's BFCM traffic and 50-million-email scale.
7. Tell me about a security-sensitive system. Use Sixt's GDPR and PCI DSS work.
8. How do you introduce unfamiliar tools responsibly? Explain evaluation, proof of concept, operational criteria, monitoring, rollback, and knowledge sharing; anchor the answer in a real project.

For each story, prepare Situation, Task, your personal Action, measured Result, and one lesson. Separate personal contribution from team outcomes.

## Technical Interview

**High Priority**

- **Idiomatic Go and service design:** interfaces, error handling, context cancellation, concurrency, goroutine lifecycle, testing, dependency boundaries, and graceful shutdown. The role may probe depth because the requested Go tenure exceeds the documented timeline.
- **PHP-to-Go migration strategy:** strangler pattern, contract preservation, parallel runs, data consistency, rollback, observability, and incremental traffic migration.
- **API design:** REST semantics, versioning, idempotency, pagination, authentication, error contracts, and backward compatibility. Be ready to distinguish direct REST experience from gaps in GraphQL and gRPC.
- **Kubernetes and delivery:** deployments, services, ingress, probes, resources, autoscaling, Helm, rollout/rollback, GitHub Actions, ArgoCD, and operational debugging.
- **Reliability and performance:** SLOs, metrics, tracing, retries, backoff, circuit breaking, backpressure, database bottlenecks, and load testing.
- **Messaging:** RabbitMQ concepts, delivery guarantees, ordering, duplicate handling, dead-lettering, idempotent consumers, and failure recovery.
- **MySQL and data migration:** indexes, transactions, query plans, locking, schema evolution, and zero-downtime changes.

**Medium Priority**

- **Cloud architecture:** AWS services actually used, availability, cost/performance tradeoffs, and the ECS-to-Kubernetes migration.
- **Security:** secure coding, secrets, authentication/authorization, dependency risks, GDPR, PCI DSS, and auditability.
- **Caching:** principles, invalidation, consistency, and failure modes. Redis is required but not explicitly supported by the CV, so distinguish conceptual knowledge from production experience.
- **Load balancing:** health checks, routing, timeouts, connection handling, and failure scenarios. Do not claim HAProxy experience without evidence.
- **GraphQL and gRPC:** prepare fundamentals, tradeoffs, and an honest account of any actual exposure not captured in the source records.

**Low Priority**

- **Frontend development:** not central to the vacancy.
- **Advanced domain-specific fitness workflows:** useful context, but the role is primarily backend modernization. Focus on booking concurrency, payments, schedules, cancellations, and notification reliability at a conceptual level.

Possible system-design exercise: migrate booking and payment-related endpoints from a PHP monolith to Go services while preserving API contracts, preventing double bookings, keeping payment operations idempotent, and providing rollback and observability.

## CV Deep-Dive Questions

- What parts of the Simple App platform were personally designed and implemented?
- What Go concurrency, data, and deployment patterns were used there?
- How were the 35% first-response and 28% resolution improvements measured?
- What caused incident-related disruptions, and how did retries and fallback logic reduce them?
- How was the CRURATED 10x throughput increase measured, and what were the bottlenecks?
- What delivery guarantees were implemented for webhooks and S3?
- What specific services moved from ECS to Kubernetes at airSlate, and what produced the cost and performance improvements?
- How were the 30% API response-time improvement and database workload reduction validated?
- What PHP and Go components did you personally own at Hyprr?
- What architecture decisions enabled PDFfiller to handle approximately 50 million emails per month?

Reconcile before interviewing: Simple App end date, the Simple App/CRURATED overlap, and PDFfiller title and end date.

## Company-Specific Preparation

- Review the current [8allocate website](https://8allocate.com/) and be ready to connect client value, excellence, flexibility, and integrity to specific working practices.
- Re-read the [Djinni vacancy](https://djinni.co/jobs/842095-senior-golang-php-developer/) and identify which requirements are direct matches, transferable matches, and gaps.
- Prepare a two-minute modernization proposal: discovery and observability baseline, API contract inventory, migration slice selection, parallel validation, incremental traffic shift, rollback, and decommissioning.
- Prepare domain risks for a fitness/booking SaaS platform: double booking, schedules and time zones, cancellations, payment idempotency, peak demand, notifications, and multi-tenant data boundaries.
- Research the end client only if its name is disclosed later; do not guess its identity from the description.

## Preparation Plan

**Must prepare before recruiter screen**

- Exact commercial Go timeline and strongest production examples.
- Honest English level, salary expectation, notice period, and work authorization/location details.
- Explanation of overlapping Simple App and CRURATED dates.
- Correct official dates and title for PDFfiller.

**Before technical interview**

- Rehearse the PHP-to-Go migration design and one Go service deep dive.
- Review Kubernetes, Helm, RabbitMQ, MySQL, API versioning, reliability, and secure coding.
- Prepare truthful gap statements for GraphQL, gRPC, Redis, Docker, HAProxy, Doctrine, and Codeception.
- Practice one coding exercise in Go involving concurrency, cancellation, error propagation, and tests.

**Before final or culture interview**

- Prepare three concise STAR stories covering ownership, stakeholder collaboration, and a difficult production problem.
- Refine questions about the client, migration stage, decision authority, delivery expectations, and engineering culture.
- Confirm that motivation remains specific to the role without claiming knowledge of the unnamed client.

## Questions to Ask

1. What percentage of the backend is currently PHP versus Go, and which migration stage is the team in?
2. How do you decide service boundaries and validate parity while moving functionality from PHP to Go?
3. What are the main reliability or performance problems the new engineer should address first?
4. How are responsibilities divided between 8allocate engineers and the client's internal team?
5. Which API styles are used in production today: REST, GraphQL, and gRPC, and for which workloads?
6. What does the deployment stack look like around Kubernetes, Helm, observability, and rollback?
7. How do you measure success during the first three and six months?
8. Which parts of the role require direct client communication, architecture ownership, or DevOps work?
9. How does the team approach testing and safe changes in the existing PHP codebase?
10. Is the five-year Go requirement a strict screen, or can extensive senior backend and migration experience compensate for a shorter Go timeline?
