# Interview Preparation

## Recruiter / HR Screening

Prepare short answers for:

- Motivation: "I am looking for a hands-on senior backend role where I can own architecture and code, improve reliability, and mentor engineers. Solidgate's Taxes module fits because it combines Go backend ownership, billing reliability, and a path toward technical leadership."
- Location: "I am based in Rome, Italy and work well with CET-compatible teams. I need to confirm whether this role supports remote work from Italy because Ashby lists Warsaw and DOU listed remote."
- Work authorization: Confirm exact Italy/EU wording before submission.
- Visa sponsorship: Confirm whether sponsorship is needed before submission.
- Notice period: Confirm before submission.
- Salary: The posting does not show a range. Prepare a flexible answer based on senior Go backend scope, leadership expectations, and total package.
- English: Explain that English is professional working / upper-intermediate, with daily remote collaboration experience.
- Timeline: Prepare a clear explanation for the Simple.life and CRURATED overlap in source records.

## Culture Fit / Behavioral Interview

Likely questions:

- Tell me about a backend system you owned from design to production.
- Describe a time you improved reliability for a high-load service.
- Tell me about a production incident and how you handled it.
- How do you make architecture decisions when requirements are still changing?
- How do you mentor junior or mid-level engineers while staying hands-on?
- Describe a disagreement with Product or another engineer and how you resolved it.
- How do you balance speed with testing and operational safety?
- Tell me about a time you reduced database or infrastructure load.

STAR stories to prepare:

- Simple.life: Go support automation platform, Zendesk/Intercom integrations, retries, fallback logic, and monitoring.
- CRURATED: Event analytics infrastructure, routing to downstream systems, delivery guarantees, and observability.
- airSlate: Database load reduction, ECS-to-Kubernetes migration, CI/CD, and production troubleshooting.
- PDFfiller: Transactional email service, 50 million emails per month, and BFCM traffic peaks.
- Hyprr: Prototype to closed beta in under 6 months and leadership of a 10-person team.

## Technical Interview

**High Priority:**

- Go service design, API design, concurrency basics, error handling, context cancellation, retries, idempotency, and observability.
- High-load system design for billing/tax calculation, including correctness, auditability, retries, eventual consistency, and failure isolation.
- PostgreSQL schema design, indexing, query analysis, transactions, migrations, and data consistency.
- Queues and event-driven architecture, including RabbitMQ experience, backpressure, dead-letter handling, retry policy, ordering, and delivery guarantees.
- Testing strategy across unit, integration, functional, and end-to-end tests.
- Production reliability: metrics, logs, alerts, SLO-style thinking, incident response, and rollback.

**Medium Priority:**

- AWS services and Kubernetes delivery, including Helm, GitHub Actions, ArgoCD, deployment health, and operational tradeoffs.
- Fintech/payment systems, PCI DSS context, provider integrations, reconciliation, and financial data integrity.
- Team leadership: architecture reviews, mentoring, technical interviews, and planning.

**Low Priority:**

- Kafka specifics, unless Valentin has production experience to confirm before the interview.
- Kotlin/Java implementation details, because the strongest evidence is Go/PHP.
- Tax law details. Prepare product and data-model questions, but do not claim tax expertise.

## CV Deep-Dive Questions

- Simple.life: How did the Go automation platform integrate Zendesk, Intercom, and internal services?
- Simple.life: How did retries and fallback logic work during incidents?
- CRURATED: How did the event schema versioning work?
- CRURATED: How did you handle backpressure and failed downstream delivery?
- airSlate: How did you reduce database load and prove the improvement?
- airSlate: What changed during the ECS-to-Kubernetes migration?
- Hyprr: What architecture decisions did you own, and how did you manage the team?
- PDFfiller: How did the email service scale to 50 million messages per month?
- Sixt: What did PCI DSS context mean for your backend work?

## Company-Specific Preparation

Review:

- Solidgate payment orchestration, billing, subscriptions, chargebacks, fraud prevention, and indirect tax positioning.
- The Taxes module scope from the posting: tax calculation, reporting, third-party providers, resilience, uptime, and architecture.
- Solidgate's public tech page before the technical interview: [Solidgate Tech](https://solidgate-tech.github.io/).
- Tax concepts at a system-design level: VAT, GST, Sales Tax, nexus/location rules, provider integration failure modes, audit logs, recalculation, refunds, and reporting.

Positioning:

- Lead with Go backend ownership and event-driven reliability.
- Connect airSlate database/load work and PDFfiller peak traffic to Solidgate's high-load requirement.
- Connect Sixt PCI DSS and older payment provider integrations to fintech/payments context without overstating tax expertise.
- Explain that Kafka is not listed as hands-on experience, but queue-based design and RabbitMQ production work are supported.

## Preparation Plan

**Must prepare before submitting:**

- Confirm remote-from-Italy eligibility.
- Confirm work authorization and sponsorship wording.
- Confirm current role dates and CRURATED/Simple.life overlap.
- Confirm notice period and salary expectations.

**Before technical interview:**

- Prepare one system design for a tax calculation and reporting service.
- Prepare examples for idempotent provider integration, retries, audit trails, and data correction.
- Review PostgreSQL transaction and indexing examples from prior work.
- Prepare a comparison between RabbitMQ experience and Kafka concepts without claiming Kafka production usage.

**Before final/culture interview:**

- Prepare leadership examples around mentoring, code reviews, architecture decisions, and handling ambiguity.
- Prepare questions about the path to Lead, team growth, and ownership boundaries.

## Questions to Ask

- Is this role open to remote work from Italy, or is Warsaw presence required?
- Which parts of the Taxes module are already in production, and which parts need new architecture?
- Which third-party tax providers do you integrate with or plan to integrate with?
- How do you handle tax calculation correctness, auditability, refunds, and recalculation?
- What are the main reliability or uptime risks in the Billing team today?
- Which queues or streaming tools does the team use in production?
- How do engineers balance automated testing with delivery speed?
- What does the path to Lead look like for this role?
- How large do you expect the Taxes team to become?
- What would success look like after the first three months?
