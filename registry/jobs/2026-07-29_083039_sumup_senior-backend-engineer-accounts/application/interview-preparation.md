## Recruiter / HR Screening

- Motivation: connect the role to merchant-facing financial infrastructure, event-driven reliability, global scale, and backend platform ownership.
- Location: candidate is based in Rome/Fiumicino, Italy. Confirm whether the Berlin role requires relocation, hybrid office attendance, or can support remote work from Italy.
- Working model: SumUp mentions Extreme Programming, small iterations, daily deliveries, and deep problem understanding. Prepare examples of iterative delivery and technical design discussions.
- Language: English is upper-intermediate/professional working proficiency in source records. Prepare examples of written technical communication with distributed teams.
- Kotlin: be direct that production Kotlin is not evidenced. Emphasize Go/PHP backend depth and a concrete Kotlin ramp-up plan.
- Kafka: state that candidate has event-driven systems, queues, EventBridge, RabbitMQ, backpressure, and delivery guarantees, but no explicit Kafka production evidence.
- Salary: prepare a Berlin senior backend range and decide whether relocation, hybrid policy, and VSOP matter.
- Notice/current status: reconcile Simple.life and CRURATED dates before recruiter contact.

## Culture Fit / Behavioral Interview

Likely behavioral questions:

1. Tell us about a backend system you owned from design to production.
2. Describe a time you migrated a critical workflow without disrupting users.
3. How do you design event-driven systems that degrade safely?
4. Tell us about a production incident where monitoring or retries helped.
5. How do you handle regulatory or compliance-driven requirements?
6. Describe a time you improved database or API performance.
7. How do you work in small iterations while preserving design quality?
8. Tell us about a time you supported teammates' growth.
9. How would you ramp into Kotlin and Kafka in a banking team?

STAR stories to prepare:

- Simple.life Go automation platform: ownership, API orchestration, Zendesk/Intercom integrations, retries, monitoring, and 30% ticket deflection.
- Simple.life Zendesk-to-Intercom migration: critical workflow migration, routing speed, consistency, and operational responsiveness.
- CRURATED event analytics infrastructure: versioned event schema, Webhook/S3 downstreams, delivery guarantees, backpressure, and 99.9% reliability.
- airSlate Kubernetes migration: ECS to Kubernetes, Helm, GitHub Actions, ArgoCD, cost/performance improvements from LinkedIn evidence.
- airSlate performance work: API response time reduction, database load reduction, logs, monitoring, and SRE dashboards.
- PDFfiller messaging platform: 50 million emails/month and BFCM 10x traffic surge.

## Technical Interview

**High Priority - Event-driven architecture.** Prepare concepts around producers, consumers, schema evolution, idempotency, ordering, retries, dead-letter handling, backpressure, replay, duplicate handling, and failure isolation. Map examples to CRURATED and Simple.life.

**High Priority - Distributed systems and account-state consistency.** Review consistency models, transaction boundaries, eventual consistency, sagas, outbox pattern, exactly-once versus at-least-once delivery, and reconciliation.

**High Priority - Kotlin/JVM ramp-up.** Study Kotlin syntax, null safety, data classes, sealed classes, coroutines, functional style, JVM basics, Gradle, testing, and Spring/Ktor patterns if relevant. Be clear that this is preparation, not source-backed experience.

**High Priority - Kafka.** Study partitions, consumer groups, offsets, retention, compaction, schema registry, ordering constraints, delivery guarantees, retries, poison messages, and observability. Compare conceptually with RabbitMQ/EventBridge experience.

**Medium Priority - Cloud-native infrastructure.** Prepare AWS, Kubernetes, Helm, CI/CD, service deployment, rollout/rollback, scaling, health checks, and runtime observability stories from airSlate.

**Medium Priority - Databases and data modeling.** Review PostgreSQL, relational modeling for accounts, indexes, transactions, constraints, migrations, query plans, and performance monitoring.

**Medium Priority - Compliance-aware design.** Review KYC, KYB, AML basics, regional rules, audit logs, data retention, GDPR, PCI-adjacent concerns, access control, and traceability. Keep claims at study/preparation level unless using Sixt compliance evidence.

**Medium Priority - Observability.** Prepare Prometheus, logs, dashboards, SLOs, Honeycomb-style tracing concepts, event lag, retry rates, queue depth, error budgets, and account-platform health signals.

**Low Priority - Elixir and Java.** Know why they may appear in the stack, but do not claim experience.

## CV Deep-Dive Questions

- What did the Go support automation platform own end to end?
- How did API orchestration work across Zendesk, Intercom, and internal services?
- How did you design retries and fallback logic?
- What guarantees did the CRURATED event pipeline provide?
- How did backpressure work in the analytics pipeline?
- How did you monitor 99.9% event delivery reliability?
- What did the ECS-to-Kubernetes migration involve?
- How did you reduce database load at airSlate?
- What payment or fintech-related work have you done, and how recent is it?
- Have you worked with Kotlin, Kafka, account ledgers, or KYC systems directly?

## Company-Specific Preparation

- Read SumUp's Global Bank Tribe page and prepare why account infrastructure for small merchants is relevant to your backend interests.
- Review SumUp's merchant ecosystem: payments, business accounts, point of sale, invoicing, and broader financial partner positioning.
- Study the role's XP language: small iterations, daily deliveries, pair/mob programming possibility, refactoring, tests, and design quality.
- Prepare one system design: global merchant account platform with region-specific compliance, event-driven workflows, internal self-service APIs, and failure isolation.
- Prepare another system design: account verification workflow with event ingestion, status state machine, audit logs, retries, and regional policy rules.

## Preparation Plan

**Must prepare before recruiter screen:** Berlin/remote expectations, current employment timeline, Kotlin/Kafka honesty, salary range, and concise motivation for SumUp's Global Bank tribe.

**Before technical interview:** practice event-driven account-system design with Kafka concepts, PostgreSQL modeling, idempotency, reconciliation, and observability. Prepare side-by-side examples from CRURATED, Simple.life, and airSlate.

**Before final/culture interview:** prepare stories around ownership, respectful collaboration, mentoring, technical design quality, incremental delivery, and learning a domain with compliance constraints.

## Questions to Ask

1. Is this Berlin role hybrid, onsite, or open to remote work from Italy?
2. How much Kotlin experience do you expect on day one?
3. Which parts of the accounts platform are being built from scratch versus migrated?
4. How does the team model account state across regions?
5. What Kafka patterns does the team rely on most?
6. How do you handle regional compliance differences in the platform design?
7. What observability signals matter most for account-platform health?
8. How do internal teams use the self-service platform?
9. How does Extreme Programming work day to day in the Global Accounts team?
10. What would make a senior backend engineer successful in the first 90 days?
