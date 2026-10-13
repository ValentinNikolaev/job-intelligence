# Match Analysis

**Score:** 87/100  
**Recommendation:** Strong Match

Strong fit for a remote senior Go backend role centered on distributed services, event-driven processing, PostgreSQL-backed reliability, idempotent recovery, APIs, observability, and production ownership. The main uncertainties are direct GPU marketplace and prepaid-ledger experience plus several stack specifics.

## Why it matches

- Production Go ownership of a support automation platform and backend integrations.
- Event-driven architecture, queues, retries, backpressure, and delivery reliability above 99.9% are directly evidenced.
- Strong production operations background across PostgreSQL, Kubernetes, AWS, monitoring, CI/CD, and incident diagnosis.
- Remote worldwide location is compatible with the candidate's Italy-based profile.

## Gaps

- Direct GPU-compute marketplace, provider-node placement, and Rust-agent experience are not established.
- NATS/JetStream, Redis, GCP, mTLS, and signed short-lived credentials are not explicitly evidenced.
- Prepaid billing, settlement, ledger reconciliation, and marketplace accounting are not directly established, although payment integrations are documented.

## Concerns

- The role is correctness-critical and money-moving; the candidate's profile shows payment gateways and fintech-related systems but not a complete billing ledger or reconciliation system.
- PostgreSQL is evidenced, but the sealed profile does not provide a detailed example of transaction locking and migration ownership for this exact domain.

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| Strong PostgreSQL experience, including transactions, indexes, migrations, and query analysis | critical / stated | partial | Strong PostgreSQL experience, including transactions, indexes, migrations, and query analysis. | Normalized database tables and performed extensive query optimization. | The sealed profile supports PostgreSQL and query optimization but does not explicitly evidence every listed transaction, index, and migration responsibility. / Verify concrete transaction, locking, index, and migration examples before preparation or interview discussion. |
| Strong production Go experience | critical / stated | strong | Strong production Go experience. | support automation platform that connects Zendesk, Intercom, and | / |
| Experience building distributed or event-driven systems | critical / stated | strong | Experience building distributed or event-driven systems. | event-driven system using queues and EventBridge, increasing | / |
| Experience designing idempotent APIs and handling retries or partial failures | critical / stated | strong | Experience designing idempotent APIs and handling retries or partial failures. | resilient message delivery pipelines with fallback logic, retries, and | / |
| Strong testing discipline, including integration tests | high / stated | partial | Strong testing discipline, including integration tests. | 30-scenario telephony QA checklist with run journal; 4 documented runs | The profile shows structured QA and increased unit-test coverage, but does not explicitly establish integration-test depth for Go services. / Confirm representative integration-test ownership and failure-case coverage. |
| Experience with Redis, message queues, or NATS | high / stated | partial | Experience with Redis, message queues, or NATS. | event-driven system using queues and EventBridge, increasing | Message queues are evidenced, while Redis and NATS are not explicitly established. / Position queue and EventBridge experience as transferable and verify any direct Redis or NATS work. |
| Ability to reason clearly about correctness, security, and money movement | high / stated | partial | Ability to reason clearly about correctness, security, and money movement. | strict compliance with the PCI DSS | Security and payment-related evidence is strong, but end-to-end correctness of a prepaid compute ledger is not directly documented. / Use PCI DSS, payment gateway, audit, retry, and delivery-guarantee examples while clearly separating them from ledger experience. |
| Clear written communication and ownership from design through production support | high / stated | strong | Clear written communication and ownership from design through production support. | event analytics | / |
| Payments, billing, ledger, marketplace, fintech, or accounting-system experience | meaningful / stated | partial | Payments, billing, ledger, marketplace, fintech, or accounting-system experience. | Develop integration with Stripe/PayPal/Skrill payment gateway providers. | Payment integrations and fintech-related systems are documented, but ledger, settlement, and reconciliation ownership is not. / Present the verified payment integration experience and avoid implying accounting-ledger ownership. |
| Kubernetes, GCP, and production observability experience | preferred / stated | partial | Kubernetes, Prometheus, Grafana, and GCP. | Migrated managed services from ECS to Kubernetes. Prepared infrastructure for | Kubernetes and Prometheus are evidenced; GCP and Grafana are not explicitly established. / Emphasize transferable cloud and observability ownership without claiming GCP experience. |
| mTLS, cryptography, signed credentials, or security-sensitive APIs | preferred / stated | partial | mTLS, cryptography, signed credentials, or security-sensitive APIs. | security assessments, and vulnerability scans | Security-sensitive and compliance work is evidenced, but mTLS, cryptography, and signed credentials are not explicit. / Use GDPR, PCI DSS, security assessment, and audit evidence; verify any direct credential or mTLS implementation before claiming it. |
| Rust, Linux, GPU infrastructure, or distributed-systems operations | preferred / stated | partial | Rust, Linux, GPU infrastructure, or distributed-systems operations. | Troubleshot production issues by analyzing logs, monitoring system performance, SRE | Distributed production operations are evidenced, but Rust, GPU, and Linux-host agent experience are not explicit. / Lead with distributed backend and operational reliability experience and treat GPU-agent ramp-up as a learning area. |
