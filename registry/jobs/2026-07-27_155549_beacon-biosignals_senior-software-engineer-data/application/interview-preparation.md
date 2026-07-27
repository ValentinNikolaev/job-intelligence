## Recruiter / HR Screening

- Explain interest factually: the role’s data infrastructure, event processing, APIs, and reliability focus aligns with supported backend work; do not claim prior clinical or EEG experience.
- Confirm whether Beacon can employ a candidate resident in Italy. The vacancy says remote anywhere in the US, while source metadata says worldwide.
- Be ready to clarify work authorization, sponsorship needs, notice period, earliest start date, and compensation expectations; each is marked TODO_CONFIRM in the application profile.
- Describe English as professional working proficiency and confirm practical overlap with Beacon’s distributed teams.
- Prepare a concise chronology explanation for the Simple.life source-date conflict and CRURATED overlap; use only the candidate’s confirmed facts.

## Culture Fit / Behavioral Interview

Prepare 5–10 answers using real experiences:

1. Describe a time you made a system more reliable under load — Simple.life message-delivery pipelines with retries, fallback logic, and monitoring.
2. Describe a cross-functional technical decision — Simple.life integrations with support operations, product, and AI teams.
3. Describe a difficult migration — Zendesk to Intercom real-time flows.
4. Describe a database-performance problem — airSlate workload redistribution and bottleneck work.
5. Describe a production incident — airSlate troubleshooting through logs, monitoring, and SRE dashboards.
6. Describe how you led technical direction — Hyprr roadmap and architecture work with the CTO.
7. Describe mentoring or leadership — PDFfiller team leadership and airSlate planning/interviews.
8. Describe a time you improved delivery practices — Kubernetes migration and CI/CD work at airSlate.

For each story, state the situation, your specific responsibility, actions, and supported outcome. Do not invent clinical impact, stakeholder approval, or numbers.

## Technical Interview

**High Priority:**

- Event-driven architecture: use the CRURATED event schema, routing, retries, downstream destinations, and observability as the anchor. Be ready to discuss idempotency, retries, backpressure, schema evolution, dead-letter handling, and delivery semantics as design considerations; distinguish general design knowledge from verified production implementation.
- PostgreSQL and SQL: explain the airSlate database-load and query-performance work, indexing and query-analysis approach only to the degree confirmed by the candidate.
- APIs and data modeling: discuss clear ownership boundaries, versioned contracts, integration patterns, data integrity, and backward-compatible changes.
- Reliability and operations: explain monitoring, logging, incident response, capacity, failure modes, and deployment safety from Simple.life and airSlate.
- Kubernetes and deployment: explain the ECS-to-Kubernetes migration, Helm, GitHub Actions, and ArgoCD experience.

**Medium Priority:**

- RabbitMQ: discuss its supported use on the CV and general messaging trade-offs without claiming Kafka experience.
- RFCs and technical design: prepare an example of clarifying a system change, evaluating trade-offs, documenting a decision, and seeking input; label it as an approach if no specific RFC artifact is available.
- Security and privacy: expect questions about data integrity and sensitive clinical data. State that direct clinical-data experience is not established, then discuss careful access control, auditability, and least-privilege principles as general engineering considerations.

**Low Priority:**

- Julia, Python, R, Kafka, Pulsar, Kinesis, Terraform, Node.js, and TypeScript. Do not claim experience. Explain the relevant adjacent background (Go, PHP, RabbitMQ, Helm, AWS) and a concrete learning approach.

## CV Deep-Dive Questions

- What did you personally own in the Go support-automation platform?
- How did fallback and retry logic work in the message-delivery pipelines?
- What changed in the Zendesk-to-Intercom migration, and how did you control risk?
- What caused airSlate database pressure, and what was your role in addressing it?
- What did the ECS-to-Kubernetes migration require from application and delivery perspectives?
- How did the CRURATED event schema support new event types and downstream consumers?
- How do you explain the Simple.life and CRURATED chronology accurately?

## Company-Specific Preparation

Read Beacon’s [platform overview](https://beacon.bio/), [careers page](https://beacon.bio/careers?trk=public_post-text), and the [Datastore role description](https://job-boards.greenhouse.io/beaconbiosignals/jobs/4273783009). Prepare to connect your experience to reliable data infrastructure while asking how the team manages scientific-data governance, schemas, lineage, and operational ownership. Beacon’s public materials emphasize documented decisions and distributed collaboration; bring an example of making technical communication explicit.

## Preparation Plan

**Must prepare:** confirm US eligibility; reconcile chronology; rehearse two backend-reliability stories and the CRURATED event-infrastructure story; review SQL/PostgreSQL fundamentals.

**Before a technical interview:** practice a data-pipeline design exercise covering ingestion, validation, versioned schemas, replay, monitoring, failure handling, and privacy boundaries; review Kubernetes, Helm, API versioning, and messaging trade-offs.

**Before a final/culture interview:** prepare examples of asynchronous communication, trade-off discussions, mentoring, and cross-functional collaboration. Be candid about the clinical domain and state how you would learn it.

## Questions to Ask

1. What are the Datastore’s most important data-integrity and reliability challenges today?
2. How do teams evolve schemas and APIs without disrupting clinical-study workflows?
3. Which event-processing and data-platform technologies are in active use?
4. How are ownership and on-call responsibilities divided across Datastore, platform, and application teams?
5. What would be the first meaningful problem for this engineer to solve in the first 90 days?
6. How are RFCs written, reviewed, and translated into implementation decisions?
7. What support exists for an engineer building clinical-domain understanding?
8. Is the role open to employment from Italy or elsewhere in the EU, and what working-hours overlap is expected?
