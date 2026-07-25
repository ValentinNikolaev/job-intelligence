## Recruiter / HR Screening

- Explain interest factually: the role combines Go backend work with scalable, reliability-sensitive distributed storage products.
- Confirm Italy-based location and openness to full remote or Bologna hybrid work.
- Discuss English based on source evidence: upper-intermediate/professional working proficiency; do not overstate it.
- State compensation expectations only after reviewing the listed €45,000–€65,000 range and total package.
- Prepare a precise answer on availability and the Simple.life source-date discrepancy; do not invent a notice period.
- Explain the change motivation as seeking a senior Go/backend role with distributed-systems and infrastructure depth, if that is accurate for the candidate.

## Culture Fit / Behavioral Interview

Likely questions:

1. Describe a time you improved reliability during high load.
2. How do you approach constructive code review?
3. Tell us about turning a technical requirement into an executable plan.
4. Describe a difficult incident investigation using logs or monitoring.
5. How do you collaborate with Product and operations teams?
6. How have you handled an ambiguous architecture decision?
7. Describe a time you mentored or led engineers.
8. What do you do to maintain quality in a remote team?

Potential STAR evidence: Simple.life message-delivery pipelines and Zendesk-to-Intercom migration; airSlate ECS-to-Kubernetes migration and API/query optimization; PDFfiller peak traffic; Hyprr prototype-to-beta delivery. Verify details and personal actions before answering.

## Technical Interview

**High Priority:** Go concurrency and service design; HTTP/API design; distributed-systems failure modes; retries, idempotency, backpressure, and observability; Kubernetes delivery/operations; diagnosing latency and bottlenecks.

**High Priority:** storage-domain fundamentals to close the role gap: object versus file storage, S3 semantics, replication, consistency trade-offs, checksums, recovery, networking fundamentals, and service resilience. Study these; do not claim previous NFS/SMB experience.

**Medium Priority:** Linux process/network debugging, Docker, PostgreSQL/MySQL performance, RabbitMQ/event-driven designs, Prometheus metrics, tracing concepts, and code-review practices.

**Medium Priority:** Kubernetes operators and OpenTelemetry concepts. Frame as learning topics unless direct hands-on evidence is available.

**Low Priority:** frontend coding and unrelated product domains.

## CV Deep-Dive Questions

- Walk through the architecture and ownership boundaries of the Go support-automation platform.
- How did fallback and retry logic work in the message-delivery pipelines?
- What specific evidence led to the API/query bottleneck diagnosis at airSlate?
- What changed operationally in the ECS-to-Kubernetes migration?
- How did the PDFfiller team plan for BFCM traffic growth?
- What were your direct leadership responsibilities at Hyprr and PDFfiller?
- Reconcile Simple.life dates and any apparent concurrent roles truthfully and concisely.

## Company-Specific Preparation

Read Cubbit’s [DS3 overview](https://docs.cubbit.io/getting-started/what-is-cubbit-ds3), [technology page](https://www.cubbit.io/technology), and [DS3 Cloud page](https://www.cubbit.io/ds3-cloud). Be ready to discuss why geo-distribution, encryption, fragmentation, redundancy, S3 compatibility, and recovery affect backend design.

Prepare two thoughtful architecture observations: how tracing can reveal bottlenecks across a distributed storage request path, and how retries/timeouts should avoid amplifying failures. Present them as reasoning, not prior Cubbit knowledge.

## Preparation Plan

**Must prepare:** a two-minute Go/reliability introduction; Simple.life and airSlate STAR stories; a transparent answer on NFS/SMB, OpenTelemetry, and Kubernetes-operator gaps; date reconciliation.

**Before technical interview:** revise Go concurrency, HTTP/networking basics, distributed-systems trade-offs, S3/object storage, Linux diagnostics, Kubernetes, monitoring, tracing, and production-debugging examples.

**Before final/culture interview:** rehearse collaboration, code review, technical decomposition, remote-work communication, and questions about product reliability and team practices.

## Questions to Ask

1. Which Go services and system boundaries would this role own first?
2. How does the team use tracing and metrics to investigate production bottlenecks?
3. What are the main reliability or scale challenges in DS3 today?
4. Which distributed-systems trade-offs are most important for the team?
5. How are code reviews and technical design decisions run in the remote team?
6. How are Kubernetes, operators, and observability tooling used in practice?
7. What would success in the first six months look like?
8. How does the team support engineers learning storage-domain concepts such as S3 and NFS/SMB?
