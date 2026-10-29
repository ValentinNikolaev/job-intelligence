# Jobtome interview preparation

## Recruiter / HR Screening

Prepare a short introduction centred on backend engineering, Go services and responsibility from design to production. Start with the helpdesk gateway or production telephony architecture, then explain the connection to Jobtome's service ownership. Keep historical titles accurate. The final CV uses Software Developer for Simple App and airSlate while describing supported technical leadership in the work itself.

The first screening question to settle is the exact duration of hands-on production Go. Build a factual project timeline with dates, the work personally done and whether Go was a primary language. Do not add whole job durations merely because Go appears in a technology list. The posting treats five years as a non-negotiable, so an honest answer matters more than polished phrasing.

State Rome, Italy as the location and discuss the advertised European timezone range. Confirm actual core hours and how summer-time changes are handled. Reconfirm notice period, earliest start, acceptable compensation and contractual arrangement before providing figures. Describe English as upper-intermediate, consistent with the CV, and practise explaining a design choice aloud. Clarify the completed Simple App employment and concurrent part-time CRURATED engagement without suggesting two standard full-time roles.

## Culture Fit / Behavioral Interview

Prepare six real stories, each with the problem, personal responsibility, decision, collaboration and observed consequence. Use source facts to build answers rather than memorising invented STAR scripts.

- When did you define an approach without complete specifications? Use telephony epic and design-document ownership, distinguishing decisions you made from constraints supplied by security and operations.
- How did you coordinate across disciplines? Explain the backend, frontend and SRE contributions to the telephony release and how formal review affected delivery.
- When did you simplify a system? Use the Snowflake processing consolidation and explain the consequences of removing repeated history reads.
- How did you balance delivery and maintainability? Use the vendor-neutral helpdesk boundary and explain what belonged in adapters versus the common model.
- How did you improve team outcomes? Use airSlate's delivery leadership, distinguishing team results from your individual code contributions.
- When did you own an integration after release? Use CRURATED's production DataLake or Crutrade integration and describe only operations and follow-up responsibilities you can substantiate.

Do not invent disagreement, failure, persuasion or customer feedback just to complete a story. If a question needs a real incident, select one the candidate remembers and verify its details before rehearsal.

## Technical Interview

High priority: production Go. Practise context propagation, cancellation, error wrapping, concurrency ownership, data races, bounded parallelism and interfaces. Explain where cancellation ends a request and where background work needs separate lifecycle handling. A small coding exercise should show readable control flow, meaningful tests and explicit error behaviour. Do not claim that these exact tasks are part of Jobtome's interview.

High priority: API and service design. Sketch the Go helpdesk gateway, including tenant isolation, provider adapters, webhook ingestion, queue boundaries and versioned contracts. Discuss duplicate events, out-of-order delivery, idempotency, retries and dead-letter handling as design questions. Separate the system's actual decisions from alternatives you would consider now. REST is supported experience. Explain what would need learning for GraphQL rather than presenting it as delivered history.

High priority: relational data and performance. Review indexes, query plans, transaction isolation, locks, pagination and connection pools. Use the airSlate database and API work to explain how bottlenecks were identified and assessed. Prometheus is the stated measurement basis. Do not assign a specific database engine to a result when its source does not identify one.

High priority: distributed architecture and operations. Explain the CRURATED event platform, delivery guarantees, backpressure, event-version changes and monitoring. Discuss how a service behaves when a downstream provider degrades. Use Snowflake consolidation to explain the operational consequence of avoiding repeated full-history reads, without inventing a financial saving.

Medium priority: Kubernetes, AWS and CI/CD. Review deployment readiness, resource limits, rollout safety, secrets, service identities, logs and metrics. Describe actual runtime and delivery experience. Do not use the withdrawn airSlate migration as an example. Prepare the difference between deployment, release and feature exposure.

Medium priority: observability and testing. Explain which metrics answer user-impact questions, how to avoid noisy alerts and how integration tests exercise real boundaries. Low priority: Python, Protobuf and gRPC, because the posting treats them as extras. BigQuery and GCP deserve a conceptual overview, but do not crowd out the core Go screen or imply production experience.

## CV Deep-Dive Questions

For the gateway, expect “What did vendor neutrality change, which contracts did you own, and how did it enable the first B2B demonstration?” Be precise about delivered components and avoid assigning commercial results to a demonstration.

For telephony, expect “Which security decisions were yours and what happened before release?” Explain the privacy objective, formal review and production responsibility without getting lost in internal identifiers. The employment end remains August 2026, while the candidate separately permitted later project material as past experience. Explain this distinction plainly if asked.

For CRURATED, defend throughput improvement and shorter stream setup qualitatively before discussing numbers. If giving a metric orally, preserve its measure, monitoring source and personal technical-ownership scope. For airSlate, distinguish backend-team leadership from sole implementation, and describe the four distinct consequences rather than repeating a general performance claim.

## Company-Specific Preparation

Read the supplied vacancy and the already verified official company pages. Jobtome operates employer-facing Hirematic and a job-search product. Connect the role to reliable workflows, integration boundaries and data-driven services. Do not assume personal product use, undisclosed traffic, or a specific architecture. Prepare one explanation of why a backend change matters to a recruiter or job seeker, clearly framed as a hypothetical product consequence.

## Preparation Plan

Must prepare before screening: the production-Go timeline, concise introduction, chronology, location, availability and compensation boundaries. Before the technical stage: rehearse the gateway diagram, one database investigation, event delivery and one Go exercise. Before the final or culture stage: rehearse the six grounded behavioural stories and how responsibility was shared. Confirm the employer form before deciding whether a letter is required.

## Questions to Ask

1. How do you calculate the five-year production-Go requirement for mixed-language roles?
2. Which services and product workflows would this role own first?
3. Where do teams currently struggle with integration boundaries or data consistency?
4. How are architectural decisions reviewed and recorded?
5. Which reliability measures guide engineering priorities?
6. What are the actual core hours and Italy contracting options?
7. What would successful ownership look like after the first few months?
