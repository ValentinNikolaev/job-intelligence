## Recruiter / HR Screening

Prepare short, factual answers for:

- **Current status:** reconcile the March 2026 Simple.life end date with the LinkedIn export that says Present.
- **Concurrent work:** explain the August 2024–January 2026 CRURATED overlap without guessing at an engagement type.
- **Location and working model:** based in Rome, comfortable with CET-compatible remote work and occasional company meetups; confirm any travel expectations to Kyiv or another office.
- **Work authorization:** confirm the exact Italy/EU work-authorization wording and whether sponsorship is required.
- **Availability:** confirm notice period and earliest start date.
- **Compensation:** decide on a gross annual range and whether it changes by employment or contractor arrangement.
- **English:** be ready to conduct the discussion in English at the stated professional working / upper-intermediate level.
- **Motivation:** focus on hands-on Go backend work, high-load services, architecture participation, and mentoring. Do not claim a prior personal commitment to iGaming.
- **Background check:** ensure employment dates, titles, and concurrent roles can be documented consistently.

## Culture Fit / Behavioral Interview

Use real experiences as STAR material; do not memorize invented answers.

1. **Tell us about a service you owned in production.** Use the Simple.life Go automation platform: integrations, operational responsibility, retries, fallback logic, and monitoring.
2. **Describe a serious performance or capacity problem.** Use the airSlate database peak-load work or API/query bottleneck investigation.
3. **When did you improve a system without a full rewrite?** Use the Zendesk-to-Intercom migration or the airSlate ECS-to-Kubernetes transition.
4. **Tell us about an architecture decision with trade-offs.** Use CRURATED's versioned event schema, multiple downstreams, backpressure, and delivery guarantees.
5. **How have you handled peak traffic or incidents?** Use PDFfiller's Black Friday/Cyber Monday periods with more than 10x traffic.
6. **How do you review code and mentor others?** Use leadership of five backend engineers at PDFfiller, direct management of ten developers at Hyprr, and airSlate technical interviews.
7. **Describe a disagreement with Product or another team.** Choose a real Simple.life, CRURATED, or airSlate example and document the participants, constraint, decision, and outcome before the interview.
8. **How do you introduce standards across services?** Use the airSlate logger package, CI/CD pipelines, or CRURATED's versioned schema only if you can explain your exact contribution.
9. **Tell us about a mistake or failed approach.** Prepare one genuine example with detection, correction, and changed practice; none is documented in the source records.
10. **How do you stay hands-on while leading?** Connect architecture reviews, task planning, code contribution, incident work, and mentoring from Hyprr, airSlate, and PDFfiller.

## Technical Interview

**High Priority — Go service design.** Review HTTP service structure, dependency boundaries, error handling, interfaces, testing strategy, graceful shutdown, and production diagnostics. Prepare one precise walkthrough of the Simple.life Go platform without disclosing confidential details.

**High Priority — Concurrency and context.** Expect goroutines, channels, cancellation, deadlines, worker pools, fan-in/fan-out, synchronization, race detection, leak prevention, and backpressure. The CV does not prove these explicitly, so prepare only examples you personally implemented.

**High Priority — SQL consistency and performance.** Review indexes, query plans, transactions, isolation levels, locks, deadlocks, replication trade-offs, schema design, and high-load connection management. Tie answers to MySQL/PostgreSQL and airSlate performance work.

**High Priority — Messaging and event-driven systems.** Compare RabbitMQ and Kafka, delivery semantics, acknowledgements, retries, dead-letter queues, ordering, idempotency, deduplication, poison messages, and consumer backpressure. Use CRURATED and Simple.life as evidence; label Kafka knowledge separately from production experience.

**High Priority — Microservice reliability.** Cover timeouts, retries with jitter, circuit breakers, bulkheads, observability, SLOs, alert quality, deployment safety, and incident response. Be ready to explain when retries make an outage worse.

**High Priority — System design.** Practice designing a high-volume transaction or player-event service across API, validation, persistence, queues, consumers, idempotency, observability, retention, and failure recovery. Include consistency and regulatory/audit concerns without claiming iGaming expertise.

**Medium Priority — MongoDB and Redis.** Review document modeling, indexes, consistency, TTLs, cache invalidation, eviction, distributed locks, and failure modes. State clearly that production depth is not established in the source CV.

**Medium Priority — REST API design.** Review pagination, idempotency keys, versioning, validation, status codes, authentication/authorization boundaries, and backward compatibility.

**Medium Priority — Cloud and delivery.** Prepare AWS, Kubernetes, Helm, GitHub Actions, ArgoCD, rollout/rollback, health probes, autoscaling, and production-debugging examples.

**Medium Priority — Coding exercise.** Practice an idiomatic Go service or data-processing task with table-driven tests, race-safe concurrency, clear error handling, and complexity analysis.

**Low Priority — Frontend.** The vacancy is backend-focused and does not request frontend delivery.

## CV Deep-Dive Questions

- What parts of the Simple.life platform did you design and code personally?
- What does “handled or deflected up to 30%” measure, over what period, and how was it validated?
- Which failure modes required fallback logic, and how were retries bounded and observed?
- How was the CRURATED throughput increase measured, and what was the baseline bottleneck?
- What guaranteed the reported above-99.9% event-delivery reliability?
- What exactly overlapped between Simple.life and CRURATED, and under what arrangement?
- Which airSlate changes reduced database pressure, and how did you rule out regressions?
- How did the ECS-to-Kubernetes migration change cost, performance, deployment, and operational risk?
- What Go services did you build at Hyprr, and how much code did you personally own?
- How was the PDFfiller 50-million-messages-per-month volume measured, and what broke first during 10x peaks?
- What did code review and mentoring look like in practice for the teams of five and ten?

Prepare supporting details, but remove any metric from the spoken story if you cannot defend its definition and source.

## Company-Specific Preparation

GameInspire publicly presents a B2B iGaming platform spanning games, betting, payments, KYC/anti-fraud, responsible gaming, reporting, affiliate management, and CRM. The official site publishes 6M+ monthly active players, 250+ casinos, and 100+ payment methods. The company and vacancy describe more than 200 services or modules and 24/7 operation. Review the [official platform overview](https://gameinspire.com/en), [DOU company profile](https://jobs.dou.ua/companies/gameinspire/), and [LinkedIn company page](https://www.linkedin.com/company/gameinspire).

Prepare for domain questions around transaction integrity, payment-provider failures, player-event volume, auditability, KYC boundaries, fraud signals, responsible-gaming controls, and zero-downtime change. Treat these as likely platform concerns, not as confirmed ownership of the vacancy's team.

The vacancy describes open management, initiative, architecture discussion, production alerts, and mentoring. Prepare examples where you proposed a change, documented trade-offs, accepted review, and remained accountable after deployment.

## Preparation Plan

**Must prepare before recruiter call**

- Reconcile Simple.life status and the CRURATED overlap.
- Confirm work authorization, sponsorship needs, notice period, earliest start, and compensation range.
- Prepare a 60-second summary focused on Go, production ownership, event-driven systems, databases, high load, and mentoring.
- Decide how to discuss the iGaming domain neutrally and credibly.

**Before the technical interview**

- Build one detailed architecture diagram from a real Go system you owned.
- Rehearse Go concurrency/context, SQL isolation/locking, RabbitMQ delivery semantics, and high-load failure scenarios.
- Prepare measurable definitions for the 30%, 10x, 99.9%, 50-million, and peak-traffic claims.
- Practice one Go coding task with tests and one distributed-system design exercise.
- Review MongoDB, Redis, and Kafka fundamentals while separating study knowledge from production experience.

**Before the final or culture interview**

- Prepare three STAR stories: production incident, architecture trade-off, and mentoring or disagreement.
- Review the company's platform modules and choose two areas where your payments, communication, event, or reliability background is most relevant.
- Prepare a transparent answer about background checks and concurrent employment dates.
- Identify what you need to learn about team ownership, on-call, remote collaboration, and growth expectations.

## Questions to Ask

1. Which platform domain and services would this engineer own first?
2. How are the 200+ services divided among teams, and where are the main coupling or ownership problems today?
3. Which databases and messaging systems are used by this team, and what are the most important consistency guarantees?
4. What production incidents or scaling limits are driving the current hiring need?
5. How is on-call organized, and what authority does the responding engineer have to mitigate or roll back changes?
6. What does strong performance in the first 90 days look like for a senior contributor?
7. How are architecture decisions proposed, documented, reviewed, and revisited?
8. How much time is spent on new features, reliability work, and modernization of existing services?
9. What mentoring or code-review responsibilities are expected without formal people management?
10. How does remote collaboration work across locations, and are there required office visits or fixed overlap hours?
