# Match Analysis

**Score:** 56/100  
**Recommendation:** Possible Match

Backend, payments-adjacent, PostgreSQL, event-driven, reliability, and API evidence is relevant, but the role centers on ledger correctness, reconciliation, concurrency, and DDD that the profile does not directly demonstrate.

## Why it matches

- More than five years of backend production experience with PostgreSQL and financial-domain exposure.
- Strong distributed-systems, event-driven, API, reliability, and production troubleshooting background.
- Go and cloud/Kubernetes experience align with the stated modern backend stack.

## Gaps

- No direct evidence of a double-entry ledger, settlement/reconciliation ownership, or accounting correctness.
- TDD-first practice, DDD, transaction isolation depth, Terraform/CloudFormation, and KYC/AML are not confirmed.

## Concerns

- The central money-movement correctness requirement may be materially deeper than the candidate's documented payment-gateway and exchange experience.

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| Double-entry ledger and money-movement correctness | critical / stated | partial | Demonstrated money-movement correctness experience: you've built a ledger, settlement system, payments core, or transaction-processing system | Designed and implemented large scope of new features in exchange core component | Exchange-core work is relevant but does not establish double-entry ledger or reconciliation ownership. / Verify transaction-model, settlement, and reconciliation responsibilities before advancing. |
| Concurrency, idempotency, partial failure, and replay | critical / stated | partial | Guarantee financial correctness under concurrency: idempotent operations, transactional integrity, and reconciliation that ties out to the cent | Build resilient message delivery pipelines with fallback logic, retries, and | Messaging resilience is adjacent but not proof of financial concurrency correctness. / Test with a detailed race-condition and replay example. |
| 5+ years backend production experience | critical / stated | strong | 5+ years of backend development on production systems | I'm a highly experienced developer with over 15 years of expertise. | / |
| PostgreSQL schemas, transactions, and optimization | high / stated | partial | Deep **PostgreSQL** knowledge: schema design, transactions, isolation levels, optimization | Normalized database tables and performed extensive query optimization. | Isolation levels and PostgreSQL-specific depth are not explicit. / Confirm transaction and locking experience. |
| Go or modern backend stack | high / stated | strong | Strong in a modern backend stack: we work in TypeScript/Node.js, Go and on the JVM ecosystem | Designed and owned a Go-based support automation platform connecting **Zendesk** | / |
