## Recruiter / HR Screening

Prepare brief factual answers on motivation, Rome location, remote work, some overlap with U.S. hours, salary expectations, availability, work authorization or contract arrangement, and English. Explain that the role is relevant because it combines production APIs, integrations, data-heavy reliability, and incremental architecture change. Do not claim real-estate product use, Domain-Driven Design, Laravel 12, Docker, Redis, or a confirmed ability to work any specific U.S. schedule. Explain that Simple.life ended in July 2026 according to the user-confirmed clarification. If CRURATED is discussed, describe it as a concurrent part-time PHP consulting engagement, not a second full-time role.

## Culture Fit / Behavioral Interview

Likely questions and truthful STAR sources:

1. Describe a backend system you owned. Use the Simple.life support-automation platform.
2. How have you reduced production risk? Use the airSlate database-stability example.
3. Tell us about a difficult system change. Use the ECS-to-Kubernetes migration.
4. How do you make architectural choices visible? Use Hyprr roadmap work with the CTO.
5. How do you work with ambiguity? Use the prototype-to-closed-beta Hyprr story.
6. Describe reliable automation. Use the verified auto-triage workflow.
7. How have you supported a team? Use leading five backend engineers at PDFfiller.
8. How do you respond when a requirement is unclear? Prepare a truthful personal example rather than inventing one.

For each answer, state the context, personal action, verified result, and what you would do differently. Do not assign team outcomes exclusively to yourself.

## Technical Interview

**High Priority:** PHP/Laravel service design, external REST API contracts, authentication and validation, backward-compatible changes, webhooks, legacy-code investigation, incremental refactoring, data integrity, database bottlenecks, and production observability. These topics map directly to the API-only backend and its migration from classic Laravel patterns.

**High Priority:** design an idempotent queued workflow for a payment or alert event. Discuss duplicate delivery, retries, dead-letter handling, transactional boundaries, monitoring, and safe rollouts. The candidate has transferable queue and integration evidence, but should say when a named Redis or Docker implementation is unfamiliar.

**Medium Priority:** PostgreSQL indexing, query plans, live schema migrations, report/export performance, DDD boundaries, strict types, static analysis, and test strategy. Research these concepts and reason from first principles; do not claim prior live PostgreSQL migrations, DDD practice, or Laravel testing conventions without evidence.

**Medium Priority:** AWS deployment trade-offs, ECS and Kubernetes, CI/CD controls, logging, Prometheus, and incident investigation. Tie answers to the verified migration and database-reliability evidence. Explain scope clearly: migration work is documented; every operational detail is not.

**Low Priority:** PostGIS, React, exact Laravel 12 changes, Redis-specific tuning, payment-provider semantics, and the company’s internal agent workflow. Learn vocabulary and prepare questions, but keep direct claims limited to evidence.

## CV Deep-Dive Questions

Expect “What did you own?” for the support automation platform; state the platform’s integration scope. Expect follow-up on the 30% auto-triage metric; quote it accurately and explain only recorded flow ownership. For airSlate, be ready to explain the bottleneck-removal and ECS-to-Kubernetes entries without adding undocumented implementation detail. For Hyprr, distinguish roadmap contribution, backend leadership, and team results. For PDFfiller, state the verified team-of-five and service-scale facts. Explain the Simple.life date reconciliation directly and do not describe omitted consulting work as a chronology gap.

## Company-Specific Preparation

Study the stated product context: a marketplace backend handling leads, properties, alerts, payments, in-house consumers, and external partners. Practice how you would understand an unfamiliar legacy Laravel flow before changing it: trace behavior, identify contracts, add targeted tests, make a small reversible change, observe production, and document decisions. The posting’s central architecture question is how to introduce domain boundaries while old and new patterns coexist. Prepare a conservative migration plan and ask how the team measures behavior preservation, data correctness, and API compatibility.

## Preparation Plan

**Must prepare:** two STAR stories, one on Simple.life integration automation and one on airSlate production reliability; a concise explanation of timeline, location, and contract eligibility; a direct answer on DDD/Docker/Redis gaps.

**Before technical interview:** rehearse a Laravel API design, a webhook/idempotency discussion, a data-heavy query investigation, a backwards-compatible API change, and a small safe legacy-refactor plan. Practice marking assumptions and discussing alternatives.

**Before final/culture stage:** articulate why maintainable backend systems and measured production changes are relevant to your experience. Reread each claim ledger entry so employer, role, action, and result are precise. If asked about a missing tool, acknowledge it, state the closest verified experience, and explain a practical learning plan.

## Questions to Ask

1. Which API or webhook contracts are hardest to change safely today?
2. How are domain boundaries chosen during the Laravel-to-DDD migration?
3. Which PostgreSQL tables or reports most constrain product development?
4. How are queue failures, retries, and idempotency monitored?
5. What testing practices are expected before changing revenue-critical logic?
6. How does the team use AI coding tools while reviewing generated changes?
7. What U.S.-hours overlap is expected for a Rome-based engineer?
8. What does successful delivery in the first six months look like?

Before the technical round, practice a structured answer for a legacy change: first identify stakeholders and API consumers; then trace current behavior, data constraints, and failure modes; next propose a narrow backward-compatible change with tests and monitoring; finally explain rollout, rollback, and documentation. This is a method answer, not a claim about a named tool. Practice a second system-design answer for an asynchronous alert or payment workflow: define the event contract, idempotency key, retry policy, observability, and ownership when a downstream system is unavailable. State where the explanation is general engineering reasoning rather than prior Redis or Docker experience.

Also prepare a short written explanation of a data-heavy performance investigation. Start with the user-visible symptom, collect measurements, narrow the likely query or workload concern, make a focused change, and compare observable behavior. Connect this method only to the verified airSlate database-stability result when describing past experience. For every answer, avoid adding unrecorded metrics, dates, employer tools, or team scope. The goal is to show rigorous thinking while keeping the candidate evidence accurate.
