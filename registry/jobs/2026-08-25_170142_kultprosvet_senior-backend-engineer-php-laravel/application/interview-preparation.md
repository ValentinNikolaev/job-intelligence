# Interview preparation — Kultprosvet / Senior Backend Engineer (PHP/Laravel)

## Recruiter / HR Screening

Position the candidacy as a hands-on backend engineer and technical lead who has stayed close to production systems while taking ownership of delivery and reliability. Connect the role to PHP/Laravel work at airSlate, Hyprr, and PDFfiller, while being precise that the most recent primary position at Simple.life was Go-focused. Mention the concurrent, part-time PHP consulting engagement at CRURATED without obscuring the overlap.

Explain interest through mature-platform improvement, integration reliability, performance, and mentoring. The gifting domain is new; say so. The role's investigation-to-monitoring ownership matches documented production work.

Clarify remote logistics early. The candidate is based in Rome, Italy; the vacancy is remote or Dnipro-based. `TODO_CONFIRM`: work authorization/contract arrangement, travel, notice period, start date, compensation, and employment type. Do not state these before confirmation.

For Node.js and AI tooling, answer candidly. There is no verified production Node.js experience or use of AI coding assistants. Describe PHP/Go work, then willingness to learn Node.js. `TODO_CONFIRM`: current AI-assisted tooling and a truthful example.

## Culture Fit / Behavioral Interview

Prepare three structured stories using situation, task, action, and outcome. First, at Simple.life, describe a Go-based support-automation platform integrating Zendesk, Intercom, and internal services. Focus on routing, lifecycle tracking, retries, fallback logic, and monitoring. The documented result is that automation handled or deflected up to 30% of inbound tickets; avoid adding unrecorded timelines, incident details, or team structure.

Second, use the CRURATED event-analytics work to demonstrate architectural judgment. Discuss versioned schemas, modular streams, downstream routing, backpressure, retries, and observability. Ground impact in more-than-10x DataLake throughput, new streams shrinking from days to under four hours, and delivery reliability above 99.9%. Distinguish personal work from team-owned work.

Third, use airSlate for incremental improvement in a mature system: database bottlenecks, API/query investigation, production troubleshooting, and deployment migration from ECS to Kubernetes. State only that peak main-database load was reduced and stability improved; `TODO_CONFIRM` a specific incident, the candidate’s exact diagnostic steps, and a concrete prevention change before telling this story.

For mentoring and disagreements, draw on the documented technical-lead role at Hyprr and leading five backend engineers at PDFfiller. Avoid inventing a conflict narrative. Prepare a real example of feedback, a technical trade-off, or a decision process only after confirming facts and outcomes.

## Technical Interview

For a slow Laravel/MySQL endpoint, use a method: characterize the issue, use logs and metrics, inspect query behavior and access patterns, identify the largest bottleneck, make the smallest safe change, and monitor rollout. The candidate has MySQL and query-performance evidence, but should not claim schema-design, transaction, migration, index, or profiling-tool detail without a real example. Separate principles from past experience.

For the gifting lifecycle, reason from the role rather than claim prior gifting experience: define explicit states and ownership, make external effects idempotent, use asynchronous work where appropriate, record failures, retry safely, expose operational signals, and provide reconciliation paths. Relate this to documented retry, fallback, event-routing, and monitoring experience, not to a Laravel queue implementation unless confirmed.

For API design, discuss clear contracts, integration boundaries, observability, compatibility planning, and failure behavior. REST APIs and backend integrations are supported. `TODO_CONFIRM`: concrete experience with authentication, GraphQL, API versioning, and frontend API-contract collaboration. If asked about tests, code review, migrations, or transactions, answer with supported high-level engineering practice and say where detailed recent evidence needs verification.

## CV Deep-Dive Questions

Expect questions about the overlap between Simple.life and CRURATED. Explain accurately: CRURATED was a part-time subcontract/consulting engagement from August 2024 to January 2026, concurrent with Simple.life. Do not minimize the distinction or imply both were full-time roles.

Be ready to compare the Go-focused Simple.life work with PHP/Laravel experience from airSlate, Hyprr, PDFfiller, and CRURATED. The technical throughline is production ownership: integrations, reliability, API work, performance investigation, observability, and delivery. Avoid claiming CRURATED used Laravel; its verified technology is PHP with AWS EventBridge, queues, webhooks, S3, and observability.

At PDFfiller, discuss leadership of five backend engineers and a transactional email service handling around 50 million emails monthly, including BFCM periods with over 10x traffic growth. Keep DNS/DKIM/SPF/DMARC/FBL details factual and do not turn them into unsupported claims about SaaS availability or on-call processes.

## Company-Specific Preparation

Kultprosvet describes a gifting SaaS for sending gifts at scale. The posting emphasizes PHP/Laravel, MySQL, APIs, safe deployments, background work, reliability, and gradual Node.js exposure. Its public site lists PHP/Laravel, Node.js, React, and Vue.js; prepare for cross-functional collaboration without claiming Vue.js or frontend architecture experience.

Clarify whether this is a Kultprosvet product or a client engagement, the Laravel/Node.js boundary, operational ownership, team topology, and current modernization priorities. These are unknowns, not facts about the company.

## Preparation Plan

Before the interview, rehearse a 90-second introduction and the three grounded stories. Make a one-page evidence sheet with dates, role scope, technologies, and verified results. Confirm all `TODO_CONFIRM` items, especially remote-work eligibility, start date, compensation, AI-assisted tooling, Node.js learning position, and recent examples of migrations, schema work, transactions, testing, reviews, and frontend collaboration.

Practice a whiteboard-level design for an integration-driven lifecycle: states, idempotency, retries, failure visibility, reconciliation, and rollout metrics. Practice explaining how an incremental change would be released and monitored in a mature PHP/Laravel system. Label any hypothetical design clearly. Finally, prepare concise examples of ownership and mentoring from Hyprr and PDFfiller only after validating the detail the candidate can personally defend.

## Questions to Ask

- Which product domain would this role own first, and what outcome would define a successful first 90 days?
- Is the gifting platform a Kultprosvet product or a client engagement, and how is the delivery team structured?
- How are PHP/Laravel and Node.js responsibilities divided today, and what learning support is expected for Node.js work?
- What reliability, performance, or modernization problem is currently most urgent?
- How do engineering teams handle deployment ownership, incidents, code review, testing, and cross-functional API contracts?
- What are the remote-work, contract, travel, and work-authorization expectations for a candidate based in Italy?
