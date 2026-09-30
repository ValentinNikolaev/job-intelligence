# Interview Preparation

## Recruiter / HR Screening

Prepare answers for:

- Italy-based eligibility for a Europe-remote role and quarterly European offsites.
- Why early-stage cloud security is relevant: connect production reliability, Go, event streams, regulated systems, and ownership without claiming cloud-security specialization.
- Exact Terraform/Pulumi exposure. If none, state it and describe a concrete ramp-up plan.
- Use of AI coding tools. Separate coding-agent workflow from supported OpenAI API integration.
- Expected level, compensation range, equity, notice period, and availability.
- Comfort with changing priorities, direct customer contact, and broad ownership.
- Overlapping Simple.life/CRURATED dates and the correct latest-role end date.

## Culture Fit / Behavioral Interview

1. Describe owning a system end to end — use the Simple.life automation platform.
2. Tell us about an ambiguous problem you simplified — use support workflow orchestration or Hyprr product planning.
3. Describe a failure-mode decision — use retries/backpressure in the CRURATED pipeline.
4. Give an example of operating under peak load — use PDFfiller BFCM.
5. Tell us about a security or compliance constraint — use Sixt GDPR/PCI work.
6. Describe working directly with product stakeholders — use Simple.life or airSlate.
7. How do you decide what not to build — prepare a real roadmap or architecture example.
8. Describe a production issue you followed through — use airSlate monitoring and fixes.

## Technical Interview

- **High priority — Go services:** concurrency, context cancellation, interfaces, error handling, testing, profiling, and predictable shutdown/failure behavior.
- **High priority — SQL policy evaluation:** schema design for resources and relationships, temporal state, query planning, indexing, correctness, auditability, and safe rule evolution.
- **High priority — event streams:** ordering, deduplication, idempotency, retries, replay, backpressure, eventual consistency, and exactly-once myths.
- **High priority — cloud control plane:** IAM concepts, network/security groups, resource graphs, audit events, API calls, drift, and control-plane versus data-plane boundaries.
- **High priority — enforcement design:** simulation, block/allow decisions, remediation safety, race conditions, bypass prevention, and fail-open versus fail-closed choices.
- **Medium priority — Terraform/Pulumi:** state, plans, providers, drift, imports, modules, dependency graphs, and failure recovery. Build hands-on examples before interview.
- **Medium priority — Kubernetes:** admission controls, RBAC, operators/controllers, deployment safety, observability, and production cluster failure modes.
- **Medium priority — security:** least privilege, threat modeling, policy audit trails, PCI/GDPR distinctions, secrets, and incident response.
- **Medium priority — AI coding tools:** prepare an honest view based on actual usage; do not convert AI API work into coding-agent experience.

## CV Deep-Dive Questions

- How did the CRURATED event system handle ordering, retries, backpressure, and multiple destinations?
- What did 99.9% delivery reliability measure?
- What did you own in the ECS-to-Kubernetes migration?
- Describe the airSlate database workload reduction and evidence.
- What security assessments did you perform at Sixt?
- Which Go services did you design at Simple.life?
- What was your direct technical contribution versus leadership at Hyprr?
- Explain overlapping recent roles and confirm dates.

## Company-Specific Preparation

Study the [official product description](https://linro.io/) and be ready to distinguish detection, simulation, blocking, remediation, and drift reversal. Sketch a resource graph and SQL-based rule for a concrete cloud misconfiguration, then discuss event arrival, historical/current/future state, latency, false positives, audit logs, and rollback.

Research Terraform state and AWS control-plane events hands-on before the interview. Prepare a view on how a policy system should handle unavailable dependencies and ambiguous resource state.

## Preparation Plan

**Must prepare:** Terraform/Pulumi truth and ramp-up plan; one event-stream design; one SQL performance story; one regulated-system story; location and chronology answers.

**Before the technical interview:** build a small Go service that consumes infrastructure-change events, stores versioned relational state, evaluates a SQL-backed rule, and emits an auditable decision. Add replay and duplicate-event tests.

**Before final/culture rounds:** review early-stage risk, equity terms, founder expectations, customer contact, offsites, decision authority, and on-call responsibilities.

## Questions to Ask

1. Which cloud and resource types does the current platform support?
2. How is infrastructure state represented for SQL policy evaluation?
3. What latency and correctness targets govern enforcement decisions?
4. How do simulation, blocking, and remediation differ operationally?
5. Which parts of the platform would this engineer own first?
6. How mature are the product, customer base, and on-call practices?
7. Is Italy-based employment compatible with the Europe-remote policy?
8. How are equity, runway, and role scope discussed with early engineers?
