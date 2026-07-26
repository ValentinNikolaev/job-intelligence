## Recruiter / HR Screening

- **Why this role?** Focus on hands-on backend ownership, architecture, reliable delivery, and product-facing collaboration; do not claim prior logistics expertise.
- **Why ShippyPro?** Refer to the publicly described multi-carrier shipping platform and the role’s backend integration and reliability challenges.
- **Location and remote work:** Rome, Italy; comfortable with CET collaboration and occasional HQ meetups.
- **Salary:** the vacancy states EUR 42,000–56,000; use the candidate’s approved salary answer only after reconciling the profile’s inconsistent ShippyPro range.
- **Notice period / start date / work authorization:** confirm with the candidate before answering. The profile intentionally marks these as open questions.
- **English:** state professional working / upper-intermediate proficiency, not native fluency.
- **Job change and chronology:** prepare a factual explanation of Simple.life and CRURATED dates; do not improvise an explanation.

## Culture Fit / Behavioral Interview

Prepare STAR stories from real evidence for:

1. A production incident or peak-load problem addressed through monitoring and fixes (airSlate or Simple.life).
2. A difficult architecture trade-off in service migration to Kubernetes (airSlate).
3. Building a resilient integration or delivery pipeline with retries and fallbacks (Simple.life).
4. Improving a database or API bottleneck (airSlate).
5. Leading delivery planning and prioritization (airSlate Technical Lead).
6. A technical disagreement resolved with evidence and collaboration (use a real incident or architecture discussion only).
7. Scaling a service through extraordinary traffic (PDFfiller BFCM).
8. Mentoring or interviewing engineers (airSlate or PDFfiller).

For each story, name the situation, your specific responsibility, the decision made, the outcome, and what you would change. Do not manufacture missing details.

## Technical Interview

**High Priority**

- PHP/Laravel: service boundaries, dependency design, error handling, queues, and maintaining production code.
- Distributed systems and async workflows: idempotency, retries, dead-letter handling, ordering, backpressure, observability, and failure isolation.
- System design: design a carrier-integration or label-generation service handling high request volume and partial failures.
- MySQL and performance: index selection, query diagnosis, connection/load risks, and evidence-based optimization.
- Reliability: monitoring, SLO thinking, incident triage, safe rollout, and resilient message delivery.
- AWS and delivery: explain ECS-to-Kubernetes migration evidence, CI/CD with GitHub Actions, Helm, and ArgoCD.

**Medium Priority**

- RabbitMQ: delivery semantics, retry strategy, consumer failures, and operational monitoring.
- Microservice trade-offs: when not to split services, API compatibility, and schema evolution.
- AI workflow integration: describe the supported auto-triage and LLM-assisted automation experience, including reliability and guardrails; do not claim stack tools not evidenced.
- Security and integration boundaries: credentials, webhooks, rate limits, auditability, and GDPR-aware engineering based on prior work.

**Low Priority**

- NodeJS, Python, DynamoDB, Docker, React, TypeScript, Tailwind, PHPUnit, Jest, and Cypress. Acknowledge absence of direct source-backed experience; explain how you would ramp up without overstating proficiency.
- Logistics domain specifics. Learn basic carrier API, label, tracking, and returns concepts from ShippyPro public materials before the interview.

## CV Deep-Dive Questions

- How did the Simple.life platform connect Zendesk, Intercom, and internal services?
- What made the message-delivery pipelines resilient, and how were they monitored?
- Which ECS-to-Kubernetes migration risks did you personally own at airSlate?
- How were API and database bottlenecks diagnosed and validated?
- What did the Laravel/Symfony logger package standardize?
- How did the transactional-email system scale to around 50 million messages per month?
- What were your direct leadership responsibilities at airSlate and PDFfiller?
- Clarify the source-record chronology between Simple.life and CRURATED before any interview.

## Company-Specific Preparation

Review ShippyPro’s [platform overview](https://www.shippypro.com/en/) and [original job posting](https://shippypro.factorialhr.com/job_posting/senior-software-engineer-309743). Be ready to discuss a conceptual design for multi-carrier integrations: normalization, rate limits, asynchronous status updates, retries, idempotency, observability, and merchant-facing failures. Treat the company’s claims as context, not personal experience.

## Preparation Plan

**Must prepare:** truthful chronology and availability answers; PHP/Laravel deep dive; a system-design story on integrations and asynchronous reliability; the exact scope of AI automation work.

**Before technical interview:** rehearse two production-performance stories, the ECS-to-Kubernetes migration, message reliability, RabbitMQ concepts, MySQL diagnosis, and trade-offs in microservice boundaries.

**Before final/culture interview:** prepare collaboration, ownership, mentoring, ambiguity, and Product/Design partnership examples; formulate questions about engineering autonomy, on-call expectations, and remote work.

## Questions to Ask

1. Which backend domains and services would this role own in the first six months?
2. What are the most important current reliability or scalability challenges?
3. How are carrier-specific failures, rate limits, and data inconsistencies handled today?
4. What does the microservices evolution mean in practice: new extraction, consolidation, or operational hardening?
5. What is the team’s approach to architecture decisions and technical debt?
6. How are Product and Design involved from discovery through delivery?
7. What are the expectations for testing, code review, observability, and incident response?
8. Which AI-enabled workflows are in production, and what engineering safeguards govern them?
9. How do remote engineers collaborate, and how often are HQ meetups expected?
10. What would distinguish a strong first-year outcome for this hire?
