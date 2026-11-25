# Interview preparation: Payward Go Developer

## Recruiter / HR Screening

Lead with a production Go integration: the candidate built a Go gateway that isolates helpdesk vendors behind an event model. Explain the problem, the boundaries chosen, the webhook and queue flow, and how the gateway enabled a product demonstration. This is a real support-platform example; do not present it as a payment gateway. The relevant lesson is how to keep provider-specific behavior behind a stable interface while retaining enough information to diagnose failures.

For a security example, discuss the outbound calling platform. Describe the candidate's backend architecture and security sign-off, the cross-functional delivery, and the choice to mask customer phone numbers and limit retention. Avoid claiming ownership of the frontend or a compliance certification. CRURATED's production analytics and event versioning provide a separate example of data movement and compatibility. State what was personally owned and what remains a team result.

The CV deliberately leaves out earlier employers outside the agreed career window. If asked about prior payment work, describe it with the correct employer and period, and distinguish integration experience from direct operation of the payment core described in this vacancy. The exact depth of recent payment-state design is not established. It is better to name that gap and reason through a scenario than to imply the support gateway handled money.

## Culture Fit / Behavioral Interview

**Question:** A provider request times out after a merchant asks to charge a card. How do you avoid charging twice?

Start by distinguishing a timeout from a confirmed failure: the provider might have completed the payment even though the response was lost. Persist a stable operation identity and the intended state before sending. Use provider-supported idempotency keys when available and retain the mapping between the merchant request and provider reference. On timeout, mark the outcome as unknown and query or reconcile before issuing a new charge. A retry must reuse the same logical identity rather than create a new operation.

Explain that a local transaction cannot atomically commit the provider's external action. State transitions should reject invalid or stale updates, while callbacks and polling may arrive in either order. Escalate unresolved states according to an agreed operational policy. This is an interview design proposal, not a claim that the candidate has implemented this exact flow.

**Follow-up:** What does exactly-once mean here? Separate delivery from effect: a broker can redeliver, and a handler may run more than once. Aim for an effectively once business effect through deduplication, durable state and the provider's idempotency contract. Check how long the provider retains keys and how reconciliation detects discrepancies outside that window.

## CV Deep-Dive Questions

**Question:** How would an outbox help?

Write the business update and an outgoing event into the same database transaction. A separate publisher sends pending records and marks them delivered; it may publish twice if it crashes after sending but before recording success. Consumers therefore need idempotent processing. Discuss ordering, poison messages, monitoring backlog age and safe replay. This does not make the remote provider part of the database transaction. Ask about failure recovery and whether the team needs per-payment ordering or broader ordering.

**Question:** How do you handle callbacks out of order? Authenticate the sender, retain a provider event ID where available, deduplicate, and compare the event against the current version and allowed state transitions. Preserve raw evidence according to privacy and retention rules. Do not assume timestamps alone establish order; provider semantics and a recovery query matter. Explain what operators see when an event conflicts with current state.

## Technical Interview

Be ready to explain goroutine lifetime, cancellation with context, bounded concurrency, channel ownership, mutex protection and data races. Use an example from actual work if one can be described accurately; otherwise say how a proposed worker pool would stop accepting new work, wait for in-flight tasks and surface errors. Discuss a race detector as a diagnostic aid, not proof of absence of races. Explain why retries need a timeout and backoff, and why a retry policy depends on idempotency.

Review transaction isolation using a concrete concurrent update: two handlers try to transition the same payment. Explain a conditional update or row lock, how to detect a stale version, and how to test competing requests. Discuss indexes from query patterns and actual plans rather than claiming a specific optimization without evidence. Clarify the difference between a unique constraint that protects a local key and a guarantee about an external payment.

## Company-Specific Preparation

Describe a test matrix for successful responses, provider timeout before and after processing, duplicate callbacks, out-of-order events, crashes between commit and publish, and replay. Integration tests should exercise actual transaction and constraint behavior; provider simulations can reproduce failure modes that are hard to trigger safely. Explain which tests were actually written only when a candidate source or memory supports the example.

For observability, propose a correlation ID connecting merchant request, internal transaction and provider reference without logging card data. Useful measures include unknown-state age, callback backlog and reconciliation discrepancies, alongside latency and failure rates. Alerts should point operators to a next action. Ask who owns the incident and what recovery tools exist. Avoid presenting these proposed measures as an existing Payward implementation.

## Questions to Ask

1. Which provider guarantees are available for idempotency and transaction lookup, and how are ambiguous outcomes reconciled?
2. How are state transitions and event replay tested across provider-specific adapters?
3. What is the on-call rotation, escalation support and incident-review process?
4. Which parts of settlement and PCI-scoped infrastructure would this role own directly?
5. Where is the team based, which legal entity contracts with an engineer in Italy, and what working hours are expected?

Before the interview, confirm which Go concurrency, PostgreSQL, testing and payment examples the candidate can personally explain. Keep unknown implementation details open rather than filling them with generic claims.

## Preparation Plan

Review the supported gateway example and rehearse the failure scenarios above; identify where the candidate is describing a proposal rather than a past implementation.
