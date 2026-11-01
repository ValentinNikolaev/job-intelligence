# Match Analysis

**Score:** 61/100  
**Recommendation:** Possible Match

Possible fit for Go fintech/crypto backend work because the profile contains cryptocurrency, payment integrations, event-driven systems, reliability, and Go. The vacancy requires deep money-operation, Kafka, and financial-consistency expertise that is not sufficiently explicit in the profile.

## Why it matches

- Go backend and event-driven architecture are supported.
- The profile includes cryptocurrency and integrations with Stripe, PayPal, and Skrill.
- Reliability, monitoring, and production troubleshooting evidence is relevant.

## Gaps

- Kafka, gRPC, and the specific Saga/outbox/idempotent-consumer patterns are not documented.
- Detailed money-operation lifecycle and reconciliation experience is not explicit.

## Concerns

- The vacancy makes financial consistency and Kafka production depth central requirements.

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| Production money operations in fintech or crypto | critical / stated | partial | Production experience with money operations in fintech or crypto: holds, debits, credits, balances, transaction lifecycle, and reconciliation | My background spans various domains | The specific money-operation lifecycle is not detailed. / Require a concrete transaction/reconciliation example. |
| Go, PostgreSQL, gRPC/REST, and Kafka | critical / stated | partial | Strong production experience with Go, PostgreSQL, gRPC / REST, and Kafka | Go | Kafka and gRPC are not documented. / Confirm both technologies with production examples. |
| Financial microservice patterns | critical / stated | unknown | Real experience applying microservice patterns to financial systems: Saga, compensation, distributed transactions, outbox, idempotent consumers, and reconciliation loops | Microservices | The named financial patterns are not established. / Treat as a major technical-screen risk. |
| External payment-provider integration | high / stated | partial | Experience integrating external providers via REST, including timeouts, provider-side statuses, delayed reversals, and our side / their side reconciliation | Develop integration with Stripe/PayPal/Skrill payment gateway providers. | Timeout, reversal, and reconciliation handling are not stated. / Clarify provider-state and reconciliation design. |
