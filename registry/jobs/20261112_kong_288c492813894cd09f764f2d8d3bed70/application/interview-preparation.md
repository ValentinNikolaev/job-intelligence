# Interview Preparation — Kong Senior Software Engineer, Kubernetes

## Recruiter / HR Screening

Start with a clear account of the production Go work. Valentin has confirmed five aggregate years building production Go systems. The most relevant recent example is a Go gateway that gives Intercom and Zendesk a shared event model while separating vendor SDKs from the consuming support agent. Describe the specific boundary and operational consequence, then say why Kong's API connectivity work interests him. Discuss the Amazon Connect platform as another example of designing an integration with security review and production controls.

Expect direct questions about location. The profile says Rome while the posting says Milan and carries a hybrid workplace marker. Ask what office attendance is required and answer with the candidate's actual availability.   Consult current candidate records before answering any unknown value.   Explain interest in service boundaries and reliability.

## Culture Fit / Behavioral Interview

Prepare concise STAR outlines from real events and leave unsupported figures out. Likely questions include: How did you decide where a vendor-specific integration should live? How did you work with support or product colleagues to settle requirements? Describe a production failure caused by a third-party API. What did you change to make partial failure visible? How did you balance privacy and ease of use in a customer callback system? Tell us about a design decision you changed after review. How did you support a colleague through a difficult delivery? How did you keep a concurrent consulting assignment separate from another role? What did you do when an operational metric was unreliable? How do you decide whether a system boundary is worth introducing?

The source-backed stories are the Simple App gateway, the Intercom scan, Amazon Connect privacy review, CRURATED parallel event versions, and airSlate delivery work.

## Technical Interview

High Priority — Go design. Review interfaces, context cancellation, concurrency, error handling, retries and testing. Connect these topics to the vendor-neutral gateway and the degraded Intercom scan. Be ready to explain when a shared event model helps, how an adapter isolates an SDK, and where tenant-specific storage and queues belong.

High Priority — Kubernetes fundamentals and controllers. Review reconciliation loops, desired versus observed state, CRDs, idempotence, leader election, rollout safety and status conditions. Distinguish study from production ownership.

High Priority — networking and API gateways. Review HTTP proxying, L4 versus L7, ingress traffic, TLS termination, service discovery, connection pooling, rate limits and failure isolation.

High Priority — distributed-system reliability. Practice a design for a control plane that applies configuration to many gateway instances. Discuss versioning, idempotent reconciliation, eventual consistency, backpressure, metrics and rollback. Ground claimed experience in CRURATED event versions and production delivery signals; treat the gateway design exercise as hypothetical.

Medium Priority — AWS and cloud integration. Use the actual Amazon Connect design to discuss federation, least privilege and secure handling of customer data. Review broad cloud-provider concepts separately.

Medium Priority — databases and messaging. Review PostgreSQL transactions, indexes, tenant isolation, SQS delivery semantics, duplicate messages and retry boundaries.

Medium Priority — observability and debugging. Explain how an incomplete scan is surfaced as an operational signal, how logs and dashboards helped diagnose problems, and what a useful alert would measure. Avoid using an unverified error-rate reduction.

Low Priority — specific Kong internals before a first interview. Read current operator and Ingress Controller documentation sufficiently to understand product vocabulary, then ask the team which components matter most.

## CV Deep-Dive Questions

Expect a request to diagram the Go helpdesk gateway. Explain its inputs, vendor-neutral event model, OpenAPI contracts, per-tenant queues and the support agent's relationship to it. Identify what shipped and which parts remained out of scope. For the Intercom scan, describe the degraded API behavior, what “incomplete” means and why partial-success reporting was safer than marking a failed scan successful. For Amazon Connect, explain what the candidate owned, what the security reviewers signed off and how call-window and opt-out rules were enforced. For Snowflake delivery, explain how shared pagination and throttling removed repeated full-history reads without claiming a measured cost saving. For CRURATED, distinguish version compatibility from a claim that all consumers migrated or remained available. For airSlate, explain the observed database stability change and CI/CD work.

 The CRURATED engagement was concurrent and part-time.  Defend numbers from the primary source and measurement method.

## Company-Specific Preparation

Read the current Kong role description and product documentation on Gateway Operator and Ingress Controller. Explain how a gateway operator might turn Kubernetes state into gateway configuration and where misconfiguration could harm traffic.  Revisit Kong's wording on open-source contribution and prepare an honest account of any public work the candidate can independently verify before applying. Check whether the role sits on controller reconciliation, gateway data plane, cloud integration or a combination.

Source facts are Kong's own posting at https://jobs.ashbyhq.com/kong/5b396e19-e312-401b-97f3-018ea6d15980 and its Gateway product page at https://www.konghq.com/products/kong-gateway.   Ask how the team measures reliability and performance. The Ashby form needs a rendered check for required fields.

## Preparation Plan

Must prepare — confirm the Milan/hybrid rule and present the real Rome location. Prepare two supported examples: the Go helpdesk gateway and the Amazon Connect backend. Know the candidate's exact employment timeline, including the concurrent CRURATED subcontract. Refresh salary and availability from current verified records before any form or screen.

Pre-technical — draw the gateway and the partial-scan failure path. Practice Go concurrency and cancellation, Kubernetes reconciliation, ingress networking, API gateway traffic flow, SQS semantics and observability. Mark which answers come from shipped systems and which are design reasoning. Recheck every quantitative statement against a source before using it.

Pre-final or culture — prepare STAR outlines for privacy review, vendor abstraction, an operational failure and cross-team delivery. Listen for the team's trade-offs around customer impact, production ownership and open-source review. Explain the transition toward this more specialized role in a direct, grounded way.

## Questions to Ask

1. Which pieces of Gateway Operator or Ingress Controller would this engineer own first?
2. How much of the role is controller reconciliation compared with gateway traffic and networking?
3. What production Kubernetes experience is mandatory on day one?
4. How does the team test configuration changes before they affect live API traffic?
5. Which signals tell you whether an operator rollout is healthy?
6. How do open-source contributions and community review fit into normal engineering work?
7. Which cloud-provider integrations are active priorities?
8. What office attendance is expected for a candidate currently based in Rome?
9. How do product and platform engineers decide which reliability issues to tackle first?
