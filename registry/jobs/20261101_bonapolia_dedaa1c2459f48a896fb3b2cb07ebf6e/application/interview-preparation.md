# Interview preparation — Bonapolia Senior Go Engineer

## Recruiter / HR Screening

Present a backend profile centred on Go services, integration contracts and production responsibility. The client is unnamed, so describe the advertised mobility problem without guessing the company. Explain that your strongest recent examples come from support systems, privacy-sensitive infrastructure and production event analytics. Domain transfer should be explicit rather than hidden behind a broad senior title.

The advertised stages include an English check, internal technical interview, client interview, live coding and cultural fit. Rehearse concise English explanations of cancellation, unknown outcomes and service ownership. English remains upper-intermediate in the source record.

Confirm actual contract dates behind the relative duration wording, start date, expected hours, rate, currency and payment deadline. The candidate has confirmed B2B willingness, but that is not a rate agreement or acceptance of unknown terms. Ask how extensions and early termination work and whether payment depends on client collection. Rome fits CET and the EU location wording. The application modal's fields remain unknown, and no mandatory letter was established. Nothing was submitted or sent.

## Culture Fit / Behavioral Interview

### Go delivery story

The candidate built a Go helpdesk gateway with vendor-neutral contracts, tenant-isolated webhook ingestion and asynchronous queues, enabling a business-to-business support-product demonstration. Explain the service boundary, the contract between producers and adapters and where tenant data is isolated. Distinguish the delivered architecture from a generic microservices diagram.

Prepare for questions about cancellation, retries, duplicate events and shutdown. Use actual implementation details you remember, and mark a proposed alternative as hypothetical. The source proves delivery and its demonstration outcome, but does not establish that every requested Go pattern was used. Do not add an internal incident or throughput benchmark to make the story more dramatic.

Explain how you would know an adapter has completed work when a process receives a shutdown signal. Identify who owns the queue acknowledgement and what happens if cancellation arrives between persistence and acknowledgement. Discuss how to keep goroutines bounded and how to propagate a context without hiding independent background work. These are rehearsal topics, not automatic claims about the historical gateway.

### Architecture and responsibility

The candidate owned architecture and backend delivery of a privacy-sensitive platform through formal review into production. Use telephony as an example of responsibility before coding: authored design, security decisions and collaboration with frontend and SRE. Explain why personal-data boundaries affected the architecture and how review established readiness for release.

The candidate's role did not imply line management of the cross-functional team or independent legal approval. Keep those boundaries clear. If asked about service operation after launch, use only recorded facts. Do not confuse designed capacity with observed production load. Internal identifiers and permission names are implementation details unless the interviewer specifically needs them.

Pipeline consolidation is a separate example of investigating an existing codebase and changing shared behaviour without public-interface changes or downtime. Describe how you separated repeated mechanics from the business-specific parts. The outcome is simpler operating behaviour and eliminated full-history reads, not a claim of company-wide adoption or a new platform strategy.

Likely behavioral questions for source-backed STAR outlines:

- How did you take a design through review and production? Use the telephony story.
- How did you make integrations easier to change? Use the gateway boundary.
- How did you preserve compatibility? Use versioned CRURATED events.
- How did you improve an existing system? Use the pipeline consolidation.
- How did you work with other disciplines? Use actual backend, frontend and SRE responsibilities.

## Technical Interview

High Priority: core service design, correctness and the vacancy-specific gaps below. Medium Priority: supporting cloud and delivery tools. Low Priority: unrelated domains before the actual work is clarified.

### Live coding rehearsal

Practise a bounded worker pool that accepts jobs, propagates cancellation and exits cleanly. Discuss queue capacity, ownership of channel closure, error propagation and backpressure. Add a test that would detect a leaked goroutine or unfinished task only when the exercise supports a reliable observation. Avoid sleep-based reasoning where synchronisation can express the condition.

For a gRPC question, separate transport features from business guarantees. Ask about deadlines, retry policy, idempotency and the point at which an operation becomes durable. Production gRPC depth is unconfirmed, so explain what you know and what you would verify. A confident design discussion does not require pretending to have operated the exact stack.

### SQL and observability

Use the airSlate database example to discuss removing bottlenecks and redistributing load. The grounded consequence is improved stability during high traffic. Additional API performance improvements are candidate-confirmed. Explain how observations informed the change without inventing query plans, replication topology or a benchmark period that is not in the source.

Review joins, composite indexes, transaction boundaries and query plans. Then distinguish replication, partitioning and sharding: each changes different failure and operating boundaries. Ask what the client actually uses before recommending a design. PostgreSQL and MySQL appear in your supported skills, but they do not establish experience with every advanced topology.

## CV Deep-Dive Questions

The role expects ambiguity clarification and technical trade-offs. Prepare a real example from your memory in which you clarified a requirement before implementation. The evidence supports design ownership but does not provide a complete interpersonal anecdote. Do not invent stakeholder objections. Explain which information you requested, which choice you owned and what other teams decided.

Ask what the first delivery should be, how success is measured, who reviews architecture changes and whether the engineer joins on-call. Discuss how the team handles handover if the engagement ends on schedule. A short contract makes scope and continuity important practical questions, without proving that the client has a current handover problem.

Defend the contribution, system boundary and actual consequence of each recent CV claim. Distinguish technical ownership from sole implementation and a project milestone from employment dates.

## Company-Specific Preparation

The live official posting matches the unnamed mobility engagement and B2B terms. Ask about the actual service and contract dates. Do not infer a client identity from the fare-negotiation description.

## Preparation Plan

Must prepare: current logistics and the strongest ownership story. Before technical: rehearse the core coding and failure cases above. Before final/culture: prepare one real collaborative decision and resolve the remaining scope questions.

## Questions to Ask

- Which service and first delivery would I own?
- What are the actual engagement dates?
- What Redis and gRPC depth is immediate?
- Which Go lifecycle cases enter live coding?
- How are on-call and handover divided?
- What payment deadline and extension terms apply?
