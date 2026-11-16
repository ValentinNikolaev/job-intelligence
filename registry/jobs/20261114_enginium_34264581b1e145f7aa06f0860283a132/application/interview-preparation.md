# Enginium — Interview Preparation

## Recruiter / HR Screening

Prepare a short explanation of five aggregate years of production Go, keeping that duration separate from any individual employer period. Explain why the candidate wants hands-on backend ownership within a consultancy and how client-facing collaboration would work. Ask about the client project and whether the posted requirements are a single mandatory stack or a composite across possible projects. State Rome location, remote/CET availability and any travel limits accurately. Confirm actual notice period and start date with the candidate. Before discussing a number, follow the vacancy-specific compensation benchmark workflow and confirm contract context. Ask for an honest Italian level and whether fluent Italian is required on the assigned project. The current record does not prove it. Enginium’s Allibo form accepts an uploaded CV.

## Culture Fit / Behavioral Interview

Prepare eight source-grounded STAR stories or concise answers. Why did you choose a shared vendor boundary in the Simple App gateway? How did you keep tenant data separate while handling webhook events? Describe a production failure caused by an external API and how you diagnosed it. Tell us about an architecture change that simplified repeated scheduled jobs. What did you do when priorities changed across product and support teams? How have you explained tradeoffs to a non-engineer? Describe a time you owned an AWS deployment or security review. How did you organize work during a delivery under time pressure? Use the verified gateway, Intercom scan, Amazon Connect backend, Snowflake job consolidation and CRURATED event pipeline. For airSlate, use supported planning-through-release responsibilities without inventing an individual outcome. Avoid presenting team figures as personal measurements.

## Technical Interview

**High priority — Go distributed-system design.** Walk through the Simple App gateway's vendor-neutral contracts, inbound webhooks, tenant-scoped stores and SQS queues. Be ready to draw ingestion, queue processing, adapter calls and error paths. The source supports those components, but does not prove a particular idempotency key or isolation mechanism. If asked to design one, use a hypothetical design and mark it as such. Discuss duplicate events, ordering, poison messages, retries, dead-letter queues and tenant-specific authorization checks.

**High priority — AWS operational ownership.** Explain the Amazon Connect production backend and federated agent access. The candidate source says backend-owned provisioning avoided a per-agent AWS account. Discuss the security review, IAM boundary and deployment responsibility with precision. For ECS, Kubernetes and SQS, use the candidate's actual examples. Step Functions, VPC and Lambda operational depth require confirmation; prepare to say what has and has not been used.

**High priority — observability.** Reconstruct the degraded Intercom scan diagnosis. The source describes repeated fatal runs, an upstream slowdown, partial-success behavior, an incomplete-scan metric and smaller cursor searches. Explain the alerts and logs that would let operators distinguish incomplete work from success. The posting specifically asks for OpenTelemetry correlation of logs, traces and metrics. The candidate record does not establish native use, so prepare a conceptual explanation without claiming past implementation.

**High priority — PostgreSQL and tenant safety.** Review execution plans, selectivity, index design, transaction boundaries and connection-pool effects. Practice a tenant-scoped query and show how code and schema prevent missing tenant predicates. Discuss tests that fail on cross-tenant access. Ask for candidate examples of PostgreSQL tuning, pgx and sqlc before claiming them.

**Medium priority — event delivery and integrations.** Use CRURATED production analytics to explain versioned event contracts, downstream routing, retries and backpressure. Ask what was observed and how reliability was evaluated. Sketch a third-party API contract test and an ADR for a change in event schema. The posting lists contract testing and ADRs as bonuses; do not present them as prior practice without evidence.

**Low priority — unrelated frontend technologies.** The position concentrates on backend systems. Review enough frontend/API collaboration to explain contracts, while keeping technical preparation focused on Go, AWS, data boundaries and operations.

## CV Deep-Dive Questions

Why was the helpdesk vendor SDK code isolated in one service? Which tenant boundaries were implemented in storage and queues? What exactly enabled the support product demo? How did the Amazon Connect federation and provisioning work, and what was security's role? What failure mode caused Intercom scan runs to terminate? What did partial-success reporting change for downstream operators? In the Snowflake consolidation, how were full-history reads removed and retry behavior preserved? Which parts of the CRURATED pipeline did the candidate own, and how were contracts versioned in parallel? At airSlate, what belonged to the candidate versus the team? Why does the CV list Simple App and the concurrent CRURATED subcontract separately? What is the evidence for five aggregate production-Go years? A precise answer is better than an embellished one.

## Company-Specific Preparation

Enginium presents itself as a Gi Group Holding technology consultancy. The stored role description spans client projects, a Technical Direction function, career paths and formal HR follow-up. Ask which client or business unit owns this particular Go vacancy and whether the stack requirements are tied to a live production architecture. Clarify who manages AWS accounts and incident response on the project. The posting says interview order can vary, with Talent Acquisition screening followed by technical discussion with the Business area. Prepare for both. Ask how much ownership the engineer retains after the client project goes live.

## Preparation Plan

**Must prepare:** answer Italian and English proficiency honestly, confirm notice period and contract expectations, and bring two concrete Go/AWS stories. Prepare a clear account of the Simple App and CRURATED overlap.

**Before technical interview:** draw the helpdesk gateway, an idempotent SQS consumer, a tenant-safe storage boundary and an external API failure path. Review PostgreSQL plans/indexes and OpenTelemetry architecture, marking unknown past experience clearly. Revisit AWS service responsibilities and any direct Step Functions, VPC, Lambda, pgx or sqlc evidence.

**Before final or culture interview:** connect motivation to production backend ownership and consultancy delivery. Ask which of the role's strict requirements are non-negotiable for the actual project. Review the posted compensation and any client-facing Italian expectations.

## Questions to Ask

1. Is this opening for a specific client or a pool of possible projects?
2. Which listed AWS services are used in the team's production path today?
3. What does tenant isolation rely on in storage and authorization?
4. How are idempotency and replay handled in the event pipeline?
5. Which OpenTelemetry instrumentation already exists, and who owns it?
6. How frequently does the role communicate with clients in Italian?
7. What PostgreSQL performance problems are most pressing?
8. Who handles incidents and on-call for this service?
9. Which technical decisions can the engineer make independently?
10. How is the advertised salary range applied to seniority and project responsibility?
