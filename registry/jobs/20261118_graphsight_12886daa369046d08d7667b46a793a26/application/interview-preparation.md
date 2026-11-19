# Interview preparation — GraphSight Senior Backend Engineer

## Recruiter / HR Screening

The listing is offline, so these notes are preparation for a possible similar role, not an active interview or application. The archived advertisement combines Go backend services and forecasting-data pipelines with Ethereum infrastructure. It asks for practical work with clients and protocols that the candidate record does not establish. Lead with confirmed backend ownership and answer blockchain questions within the actual boundaries of the Hyprr work.

The candidate has confirmed five years of hands-on production Go in total and more than 15 years in backend engineering. The five years should not be assigned solely to Simple.life. Explain how production services were designed, operated and improved, and distinguish the CRURATED PHP subcontract from the Go work. The source describes Hyprr Ethereum-based digital asset components, but does not specify whether the candidate worked on nodes, contracts, signing or chain indexing.

## CV Deep-Dive Questions

### Story 1: a Go integration boundary

**Question:** Describe a backend service you designed and delivered.

At Simple.life, the candidate built a Go helpdesk gateway that placed Intercom and Zendesk behind a vendor-neutral event model. The source names domain models, OpenAPI contracts, webhook ingestion, tenant-specific stores and SQS queues, adapters and deployment. The gateway enabled the first B2B demonstration of the support AI product.

Start with the problem of isolating vendor-specific integrations. Explain the boundary and how events moved through the service, then give the demo as a concrete consequence. Distinguish the candidate's backend contribution from frontend and product work. If asked how duplicate webhooks, ordering or replay were handled, describe the implemented behaviour only if it can be recalled accurately. Do not assume exactly-once delivery from the presence of queues.

### Story 2: event versioning and downstream consumers

**Question:** How do you evolve an event pipeline without breaking consumers?

At CRURATED, a concurrent part-time PHP engagement, the candidate owned production DataLake and analytics work, including parallel event-version publication. The source describes versioned schemas and routing to multiple downstream destinations with backpressure and delivery guarantees.

Explain the original consumer compatibility problem, what publishing versions in parallel allowed, and how changes were coordinated. Discuss the actual guarantees and retry behaviour separately from any general design you would propose today. Candidate confirmation establishes technical ownership and production use, not sole authorship of every line. Avoid using unsupported throughput or reliability numbers unless their precise scope is clear.

### Story 3: production failure and recovery

**Question:** Tell us about a difficult production defect.

The Simple.life ticket scan could exceed its run budget when Intercom search degraded. The overall context ending bypassed per-page retry. The candidate diagnosed the interaction in logs and code, introduced partial-success behaviour and an incomplete-scan metric, and partitioned search into parallel cursor chains.

Walk through the failure signal, the root cause, the code change and how an incomplete result became visible. Explain why an exit status alone would not represent complete work. For follow-up questions about tests, state the tests actually performed if remembered. Do not claim the estimated speedup or that the change eliminated all possible failures.

### Story 4: work on Ethereum-based components

**Question:** What Ethereum work have you done?

The candidate's source CV says that at Hyprr he led backend development and worked on Ethereum-based digital asset components. It also records work with the CTO on the technology roadmap and progress from prototype to closed beta. It does not identify which Ethereum client, RPC interface, contract or signing mechanism was used, nor which components were production-operated.

Before an interview, reconstruct one actual example: the problem, the component, the candidate's contribution, interface, environment and result. If any of those details cannot be recalled, say so. Do not claim Geth, Erigon, EVM contracts, signing or event indexing merely because the posting asks for them. A candid description of limited experience lets the team judge whether general backend strengths can transfer.

## Technical Interview

**Go concurrency.** Review goroutine lifecycle, cancellation, channels, mutexes and the relationship between deadlines and cleanup. Prepare an actual production example if one exists. A design exercise can discuss bounded workers, cancellation propagation and safe channel ownership as a proposed solution without describing them as prior delivery. Explain how you would detect blocked goroutines and avoid losing work when a worker fails.

**Data ingestion.** For external forecast data, ask about timestamps, units, source revisions, missing records and freshness requirements. Consider idempotent ingestion, monitoring for delayed data and replay after a provider outage. The candidate has relevant event and integration experience, but weather feeds and forecast data are new domain examples here.

**Ethereum fundamentals.** Review the distinctions between an execution client, JSON-RPC, a transaction, a block and a log, and how a chain reorganisation affects an indexer. Discuss the security boundary around signing and key custody. These are study topics, not evidence of prior practical experience. Ask the team whether it operates infrastructure directly or consumes a managed provider.

**Performance and databases.** Be ready to explain the airSlate database-stability work and what was measured, while keeping team leadership distinct from sole implementation. For PostgreSQL, discuss actual schemas and query decisions you can substantiate. The record does not establish a time-series database or Redis implementation.

## Questions to Ask

1. How much of the role is forecasting infrastructure versus Ethereum work, and what is already in production?
2. Is hands-on Geth or Erigon experience essential on the first day, or is backend ownership the primary need?
3. How are data freshness, missing weather inputs and forecast revisions handled?
4. Does the team operate nodes and signing infrastructure, or integrate with external providers?
5. Where is the team physically based, and what contract arrangement would apply to remote work from Italy?

## Company-Specific Preparation

## Culture Fit / Behavioral Interview

Use the actual collaboration examples above and explain your contribution.

## Preparation Plan

Confirm that a current role exists and inspect its application route. Prepare a non-confidential gateway diagram and a concise event-versioning explanation. Clarify the actual Hyprr blockchain work, Go concurrency examples and availability before presenting them as facts. The archived description asks for examples of relevant projects, but does not authorize sending code or candidate information. No pay figure is suggested without a location-specific benchmark and an evidenced company pay policy.
