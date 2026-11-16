# Binariks interview preparation

## Recruiter / HR Screening

Expect questions on why this eQMS role appeals, how the PHP and Go work fits together, location in Rome, remote work, contract expectations, English and availability. Explain the appeal of improving a regulated document workflow through a staged backend rewrite, using the privacy and audit decisions from Simple App as a related example. The CRURATED assignment overlapped Simple App as part-time consulting. Confirm work authorization and notice period from current candidate facts before giving a precise answer. For salary, use the vacancy-specific compensation benchmark workflow before stating an expectation.

## Culture Fit / Behavioral Interview

Prepare short, sourced STAR outlines rather than memorized claims. Likely questions include how you handled a disagreement over a service boundary, how you responded to an incident involving external APIs, how you chose a privacy control, how you worked with security reviewers, how you brought an ambiguous change to production, how you explained a tradeoff to a nontechnical stakeholder, how you mentored engineers, and how you handled a migration with a moving legacy system. Use the Simple App gateway and callback platform, CRURATED event versioning, and airSlate database/release work as distinct stories. Distinguish personal decisions, team contributions and measured outcomes.

## Technical Interview

High Priority. Design a Go service for regulated documents with a stable REST contract, authorization, immutable audit trail, idempotent writes and explicit failure states. Explain database transactions, schema evolution and coexistence with an authoritative PHP service. High Priority. Go concurrency, context cancellation, tests and error handling for a service that processes messages. High Priority. SQL indexing and query plans, plus how to use outbox or idempotency controls across a message boundary. Medium Priority. CI/CD gates, container delivery, rollback and operational signals. Medium Priority. Compare RabbitMQ and SQS with the employer's Kafka/MQTT examples, avoiding claims of hands-on use where absent. Medium Priority. DDD vocabulary and bounded contexts as design reasoning. Lower Priority. GraphQL, gRPC, BFF and CQRS, because the posting lists these as pluses.

Practice extracting a single read path from the PHP service. Keep writes with the current owner while shadowing reads in Go. Compare identifiers, version numbers, permission decisions and audit entries on sampled records. Then describe a rollback trigger and who can flip it. Explain how to handle records changed during reconciliation and how to distinguish a contract bug from a migration lag. For a write path, explain when to rely on a transaction plus outbox and how to deduplicate downstream deliveries.

## CV Deep-Dive Questions

Be ready to describe the Go gateway's exact vendor boundary and why it used a common event model, without claiming it was a general API gateway product. Explain what the Amazon Connect security sign-off covered and who approved it. Clarify how phone masking and ticket-linked call outcomes worked at the boundary. Describe the GDPR export and cancellation flow, which parts you owned, and what remained with other teams. For CRURATED, explain the versioned analytics contract and its PHP implementation. For airSlate, describe the database-load intervention and the production metric that showed an improvement. Do not volunteer the unconfirmed ECS migration.

## Company-Specific Preparation

Review the Binariks eQMS workflow around documents, training and audits. Ask how electronic records are versioned, what audit evidence customers require and whether the Go services will coexist with PHP during migration. Prepare a candid answer on the difference between health-data privacy experience and formal GxP. The company may ask about daily AI-assisted development, but current candidate records do not verify that habit.

## Preparation Plan

Must prepare: one architecture drawing of document versioning and an audit trail, plus a grounded narrative of the Simple App privacy design. Before the technical interview, rehearse Go coding, SQL, queue delivery and a staged migration plan. Before the final or culture interview, choose two stakeholder stories and check how to describe contract and availability facts accurately.

Prepare a separate example for sensitive values in logs. Draw the boundary between operational traces, customer-visible activity and a durable audit trail. Explain what each needs to retain, which roles can read it and how clock skew affects incident reconstruction. Ask how the client handles corrections to records while keeping an intact history. Review the terms the team uses for validation evidence and release approval so that questions during the interview are specific.

Draw the migration sequence before the interview and identify which steps require approval from the client or QA.

## Questions to Ask

1. Which PHP component remains the system of record during the rewrite?
2. What audit history must survive migration unchanged?
3. Which GxP or customer controls govern release approval?
4. How are document and training records versioned?
5. What are the team's incident response and on-call expectations?
6. Which queues or streams are used in the actual product?
7. How are service boundaries decided with PMs and client stakeholders?
8. How is AI-assisted quality work validated before production?
