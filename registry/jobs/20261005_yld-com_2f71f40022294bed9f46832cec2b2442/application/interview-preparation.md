# Interview Preparation — YLD Contract Golang Software Engineer

## Recruiter / HR Screening

Introduce production Go platform ownership at Simple.life, concurrent part-time CRURATED consulting, and airSlate backend leadership. The CV lists English as upper-intermediate; practice explaining architecture in spoken English. Confirm daily GMT overlap, Italy-based contracting eligibility, engagement structure, six-month availability, start date, rate and currency; none is agreed yet. Ask about client-team onboarding and extension criteria. If asked about the Simple.life end date, the CV says 2026 because source records disagree on the month. Explain CRURATED as concurrent part-time work, not a second full-time job.

## Culture Fit / Behavioral Interview

Prepare truthful STAR outlines: **situation**, **task**, personal **actions**, and a properly scoped **result**. Do not invent dialogue or motives.

1. **How did you make a complex system understandable to a non-engineering partner?** Simple.life calling platform: describe the privacy and compliance need, the authored design, decisions communicated to frontend and SRE, and the production outcome. Name the stakeholder and feedback only if personally recalled.
2. **Tell us about an outage or degraded dependency.** Simple.life’s Intercom-related cron failures: establish the observed failure and run budget, explain partial-success semantics and sharded search, then state the verified operational result without inventing an uptime figure.
3. **When did you trade an ideal design for a practical delivery?** The multi-tenant Go helpdesk gateway: explain why vendor-neutral contracts and adapters mattered for the first B2B support-AI demo. Distinguish delivered scope from future plans.
4. **How did you influence a team without doing every task yourself?** At airSlate, explain backend leadership, CI/CD and API performance work; distinguish decisions and coordination from teammates’ implementation. The approximately 20% feature-delivery-rate improvement was a team-level result.
5. **How did you protect users while shipping quickly?** For the Amazon Connect platform, discuss masked customer numbers, calling windows and security review, plus how the three-person team coordinated. Avoid disclosing internal controls beyond the CV’s public level.
6. **How did you handle competing work?** CRURATED was concurrent part-time consulting. Use a remembered scheduling example; the overlap alone does not prove how priorities were managed.

## Technical Interview

**High priority — Go services and API design.** YLD names Go and backend SaaS APIs as core skills. Draw the Simple.life helpdesk gateway: vendor-neutral event model, OpenAPI contract, webhooks, tenant separation, SQS, adapters and errors. Explain idempotency, retries and observability, distinguishing delivered features from design alternatives.

**High priority — resilience and performance.** YLD stresses fault tolerance. Explain Intercom degradation, run-budget constraints, sharded searches and partial-success reporting. At airSlate, approximately 30% lower average API response time was Prometheus-measured under backend leadership, not sole implementation. CRURATED’s over 10x DataLake throughput, under-four-hour stream setup and above-99.9% event delivery reliability belong to that analytics system; explain their baselines and monitoring scope.

**High priority — testing.** YLD explicitly mentions TDD. The CV establishes an LLM evaluation pipeline; evidence also records expanded tests for three Snowflake-to-Intercom processes and telephony QA. These do not prove named TDD practice. Find a real test-first example, or explain candidly how tests guided a change.

**Medium priority — cloud and delivery.** Explain AWS, SQS, Kubernetes and CI/CD. AirSlate’s release cycle shortened about 11 minutes, approximately 70%, under backend leadership; team delivery rate rose about 20%. Direct Docker use is unverified; confirm hands-on tasks. Omit the withdrawn ECS-to-Kubernetes account.

**Medium priority — AI judgment.** Simple.life production LLM actions and evaluation demonstrate AI product engineering. They do not establish the candidate’s use of AI tools to write code, which YLD explicitly asks about. Prepare a real personal development-workflow example only after confirming one.

**Low priority — other clouds.** The CV supports AWS. State when Azure or Google Cloud experience is unknown.

## CV Deep-Dive Questions

Expect “What did you personally build?” for the Simple.life Go platform: 377,251 **closed conversations passed through the Go service in Q2 2026**; this is throughput of closed conversations, not all incoming tickets or individual automations. The up-to-86% fully automated handling figure is platform-wide; the candidate implemented many, not all, scenarios. Expect follow-ups on tenancy boundaries, the B2B demo, the LLM evaluation dataset and privacy review. For CRURATED, distinguish full technical ownership of production analytics from business-wide outcomes, and explain Grafana or operational measurement behind each metric. For airSlate, describe the role as Software Developer with backend leadership, explain the approximately 30% API response improvement, 11-minute release-cycle gain and 20% team-level delivery-rate gain in their separate scopes. Hyprr and Sixt have dates and titles only in this CV; give further examples only from separately confirmed evidence, not inferred achievements.

## Company-Specific Preparation

YLD presents itself as a remote-first consultancy working inside client teams. Its published energy-supplier case describes splitting a monolithic finance application into smaller cloud-native Kubernetes services and improving delivery and observability. This is an example of YLD’s work, not evidence that the unnamed client for this opening uses that stack. Prepare a short reason for interest grounded in the posting: Go backend engineering, pragmatic service resilience and collaborative client delivery. The listed sequence is a Talent Partner call, a 90-minute senior-developer technical interview and a Client Partner conversation. Ask each interviewer about the stage they own.

## Preparation Plan

Must prepare: confirm the contract answers and precise Simple.life chronology. Before the technical interview, rehearse the gateway architecture, an incident narrative, and real testing, Docker and AI-assisted coding examples. Before the final Client Partner discussion, rehearse the six behavioral outlines aloud, each with one personal decision and a scoped result, focusing on business-facing explanations. Keep a one-page metric key covering Q2 closed conversations through Go, platform-wide automation, CRURATED analytics and the separate airSlate measurements.

## Questions to Ask

1. What is the client product, and what would success look like by the end of six months?
2. Which parts of the Go service architecture would this engineer own directly?
3. What reliability or performance problem is currently most costly to the client?
4. How are tests, TDD and performance checks used in the team’s actual review and release process?
5. Which Docker and Kubernetes responsibilities are hands-on in this role?
6. How do YLD engineers and client engineers share design decisions and feedback?
7. What GMT overlap is required, and how is it handled for engineers based in Italy?
8. What contracting structure, rate process and extension criteria apply to this opening?
