# Interview Preparation

## Recruiter / HR Screening

Open with a concise position statement: you are based in Rome, have 15+ years of backend experience across PHP and Go, and are applying because the role’s PHP, database, API and production-delivery responsibilities match documented work. State that English is professional working level; do not claim Italian. Explain the chronology before being asked: Simple.life was the primary role from November 2023 to July 2026, while CRURATED was a concurrent part-time PHP subcontract from August 2024 to January 2026. Ask about contract type, hybrid or remote expectations, working language and the expected split between backend and frontend work.

## Culture Fit / Behavioral Interview

Prepare a STAR response on ownership from Simple.life. Situation: support operations needed reliable connections among Zendesk, Intercom and internal services. Task: own the backend automation platform and delivery behaviour. Action: designed the integration layer, built fallbacks, retries and monitoring, and worked with Support Ops, Product and AI teams. Result: do not invent a team-level metric; describe the documented reliability and operational intent. A second story can cover airSlate leadership: plan work, distribute assignments, support release plans and conduct technical interviews. Emphasise how you make decisions visible, bring operational evidence to discussions and ask for feedback early.

Useful behavioural questions to rehearse: (1) Tell us about a production failure you helped resolve. Use airSlate logs, monitoring and SRE dashboards. (2) How do you handle conflicting delivery priorities? Use airSlate planning and release support. (3) Describe mentoring or leadership. Use the 20+ technical interviews and Hyprr’s ten-developer management. (4) How do you work with non-engineers? Use Simple.life’s cross-functional collaboration. (5) What did you learn from a difficult system migration? Use ECS to Kubernetes. (6) How do you communicate a limitation? Use the honest frontend-scope discussion.

## Technical Interview

Review PHP service design through the airSlate work: separate responsibilities, keep API contracts explicit, observe production behaviour and profile bottlenecks before optimising. Explain Laravel and Symfony only from the documented logger-package context; do not claim CodeIgniter. For SQL, discuss query patterns, indexes, execution plans and safe rollout steps, then anchor the answer in the airSlate database-load reduction and API bottleneck work. For integrations, explain idempotency, retries, timeouts, recovery paths and monitoring using CRURATED’s webhooks/S3 routing and Simple.life’s delivery pipelines.

For infrastructure, describe the ECS-to-Kubernetes migration: Helm charts, GitHub Actions and ArgoCD prepared the runtime and deployment path, producing a reported 30% cost reduction and more than 20% performance improvement. Do not overstate web-server administration. For security, mention Sixt’s GDPR and PCI DSS context, assessments and vulnerability scans; do not claim a certification or formal compliance ownership. Discuss clean code through responsibility boundaries, documented interfaces, review, observability and careful rollout. If asked about frontend technologies, state that evidence is backend-first and invite clarification on the required depth.

## CV Deep-Dive Questions

Expect the following technical probes. First: what caused the airSlate API and query bottlenecks, what data did you inspect, and how did you validate the 30% response-time improvement? Keep the answer to recorded facts and explain your diagnostic method separately as an approach. Second: why was a product-wide Laravel/Symfony logger package needed, and how did an interservice standard help troubleshooting? Third: what changed when services moved from ECS to Kubernetes, and how did Helm, GitHub Actions and ArgoCD fit together? Fourth: at CRURATED, why use versioned event schemas, and how did backpressure, retries and observability protect webhook/S3 delivery? Fifth: how did new streams move to under four hours without compromising schema consistency? Sixth: how did the PDFfiller team operate a service around 50 million emails per month and prepare for BFCM traffic growth?

For each answer, use context, your role, action, documented outcome and one lesson. Do not blur the CRURATED subcontract into Simple.life or recast PDFfiller messaging expertise as web-server administration. If a metric cannot be explained confidently, acknowledge the recorded result and focus on your work.

## Company-Specific Preparation

Use only verified company context: Web To Emotions is an independent sustainable digital agency and software house, founded in 2000 and certified as a B Corp. The vacancy asks the team to convert creative concepts into secure, performance-optimised applications. Your motivation is dependable engineering in a collaborative agency/software-house setting, not prior knowledge of clients or products. Prepare a 30-second statement connecting that need to API performance, database work, observability and practical delivery. Ask which framework is central and how design, frontend and backend responsibilities meet.

## Preparation Plan

Before the interview, rehearse three two-minute technical stories: airSlate API/database performance work; CRURATED event-routing reliability; and the ECS-to-Kubernetes migration. Prepare a one-minute chronology covering Simple.life, CRURATED’s concurrent part-time scope, airSlate, Hyprr, Sixt and PDFfiller. Revisit PHP/Laravel/Symfony fundamentals, SQL indexing, API idempotency, queue backpressure, monitoring and safe deployment. Draft no claims for JavaScript, jQuery, HTML/CSS, React, Vue, Angular, WordPress, Italian, open-source contributions or web-server administration.

Bring a short risk discussion rather than defensiveness: your evidence is strongest for backend PHP systems; if sustained frontend work is essential, you need to understand the expected technologies and support. Bring questions on code review, testing, deployment ownership, security review, on-call expectations and remote collaboration. Confirm the company’s use of flexible hours and possible remote work without assuming a fully remote contract. Finally, review the CV line by line so dates, metrics and the part-time subcontract label can be explained consistently.

## Questions to Ask

Ask: (1) Which PHP framework is central to current projects? (2) What proportion of a typical week is frontend versus backend? (3) Are HTML/CSS, JavaScript and jQuery maintenance requirements or core delivery responsibilities? (4) Who owns deployments and web-server operations? (5) What database and API reliability issues are most pressing? (6) How are code reviews, testing and security checks handled? (7) How do developers collaborate with design and client-facing colleagues? (8) Is Italian required for internal or client communication? (9) What does the flexible/remote arrangement mean in practice? (10) What would success look like in the first three months?
