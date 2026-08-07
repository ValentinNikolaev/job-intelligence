## Recruiter / HR Screening

### Likely questions and safe talking points

1. **Why are you interested in this work?** Focus on the combination of Laravel, integrations, operational workflows, production problem-solving, and a product whose reliability affects residents and service teams. Avoid claiming prior housing-sector experience.
2. **How much PHP and Laravel experience do you have?** Explain the supported work at airSlate, Hyprr, and PDFfiller, the kinds of services built, and where you made technical decisions. Separate general PHP tenure from framework-specific experience.
3. **How much commercial Vue.js experience do you have?** Give an exact, factual answer. The current candidate files do not document a year of Vue.js. If there is relevant experience, add concrete project, dates, responsibilities, and version details to the canonical evidence before using it.
4. **Why has your recent work focused on Go?** Present Go as a widening of backend experience across APIs, integrations, event systems, and reliability. Then connect those practices to Laravel service design and production support.
5. **Why are you changing roles?** Prepare a concise answer based on the real reason. Do not invent a project ending, redundancy, or growth story.
6. **Can you work remotely from the EU and overlap with the team?** State that you are based in Rome and work in the Europe/Rome time zone. Confirm work authorization and any required UK or client overlap before the call.
7. **What is your English level?** The candidate records support upper-intermediate / professional working proficiency. Prepare a two-minute project explanation in English.
8. **Why do Simple.life and CRURATED overlap?** Explain the actual arrangement, workload, and boundaries. Do not label either role part-time, contract, or freelance unless accurate.
9. **What are your salary expectations?** The posting gives no range. Prepare a gross annual or daily-rate range after confirming the employment model, country of contract, benefits, and currency.
10. **When can you start?** Confirm notice period and earliest start date before the screening call.

### Facts to confirm before speaking with a recruiter

- Italy/EU work authorization and whether sponsorship is required.
- Notice period and earliest start date.
- Expected compensation and whether the role is employment or contracting.
- Correct Simple.life end date.
- The working arrangement behind the Simple.life and CRURATED overlap.
- Correct PDFfiller title and end date.
- Any real commercial Vue.js or JavaScript evidence that is missing from the candidate registry.

## Culture Fit / Behavioral Interview

Prepare concise STAR stories for these likely questions:

1. **Tell me about a difficult production defect you diagnosed.** Use the airSlate database/API bottleneck or a Simple.life message-delivery incident. Explain signals, investigation, trade-offs, fix, and verification.
2. **Describe a technical decision that affected several teams.** Use the airSlate interservice logging component or CRURATED's versioned event schema.
3. **Tell me about a client or stakeholder request that required deeper product knowledge.** Use collaboration with Support Operations and Product at Simple.life or roadmap work at airSlate. Keep the story within the documented facts.
4. **How have you shared knowledge or raised team capability?** Use airSlate planning and mentoring, Hyprr team leadership, or PDFfiller coaching and performance metrics.
5. **Describe a time you modernised an established system.** Use the ECS-to-Kubernetes migration, delivery automation, or the Zendesk-to-Intercom flow migration.
6. **Tell me about balancing feature delivery and reliability.** Use PDFfiller's high-volume email system during traffic peaks or CRURATED's event delivery guarantees.
7. **Describe a disagreement over architecture or priorities.** Prepare a real example involving Product Management, the CTO, or engineering leadership. Do not manufacture conflict.
8. **How do you onboard into a mature product?** Describe how you map domain flows, read logs and metrics, trace integrations, review tests, ask product questions, and ship a bounded first change.

For each story, prepare the situation in two sentences, your personal responsibility, two or three actions, one supported result, and one lesson relevant to client delivery.

## Technical Interview

### High Priority

- **PHP and Laravel service design:** service container and dependency injection, validation, middleware, Eloquent trade-offs, transactions, queues, jobs, events, exception handling, API resources, authorization, and modular boundaries. The role screens directly for senior Laravel depth.
- **Laravel performance and defect investigation:** N+1 queries, indexing, query plans, caching, queue failures, timeouts, logs, traces, reproducible debugging, safe production fixes, and regression tests. The vacancy explicitly spans defects across backend and integrations.
- **REST APIs and integrations:** idempotency, retries, backoff, rate limits, webhooks, authentication, schema changes, reconciliation, partial failure, and observability. Client-specific implementations and property-management integrations make this central.
- **Vue.js fundamentals:** components, Composition API, props and events, reactivity, state management, routing, forms, validation, API calls, error states, component tests, and accessibility. This is the biggest evidence gap, so prepare for both conceptual and coding questions without overstating experience.
- **Dynamic administration interfaces:** modelling diagnostic questions, categories, problem types, conditional flows, content versioning, audit history, permissions, and safe publishing. The administration panel appears central to the team.
- **Database design:** relational modelling, migrations, indexes, transactions, concurrency, data integrity, query optimisation, and rollback plans for schema changes.
- **System design:** design a repair-diagnostics flow that collects resident answers, selects a problem category, creates a work order, integrates with a property-management system, and supports retries, auditability, and reporting.

### Medium Priority

- **Testing strategy:** PHPUnit concepts, feature versus unit tests, API contract tests, Vue component tests, integration tests, fixtures, and regression coverage for diagnostic rules. Specific tools are not listed, so ask what the team uses.
- **Queues and event-driven work:** RabbitMQ concepts, delivery semantics, dead-letter queues, duplicate handling, backpressure, ordering, and monitoring. Candidate evidence is strong and can differentiate the interview.
- **Security and compliance:** authorization, tenant isolation, personal data, audit trails, secure integrations, GDPR, and safe handling of resident information.
- **CI/CD and operational readiness:** GitHub Actions, deployment checks, migrations, health checks, rollback, monitoring, and incident response.
- **Accessibility:** semantic forms, keyboard navigation, focus management, labels, validation messages, screen-reader behavior, and automated/manual testing. The posting lists accessibility as an opportunity, not a proven candidate strength.

### Low Priority

- **Cloud platform specifics:** AWS and Kubernetes are relevant transferable skills, but the vacancy does not name its infrastructure.
- **Algorithm puzzles:** possible in a general engineering screen, though the work description points more strongly to product code, debugging, and system integration.
- **Advanced PropTech regulation:** understand the business context and data sensitivity, but deep housing-law expertise is unlikely to be the first technical screen.

### Coding exercises to rehearse

- Build a Laravel endpoint that validates diagnostic answers, resolves a problem category, stores an auditable result, and returns clear validation errors.
- Process a webhook idempotently with retries and a dead-letter path.
- Diagnose and fix an N+1 query in an administration list.
- Implement a small Vue form with dependent questions, server-side validation errors, loading states, and accessible labels.
- Write tests for a rule change that must not alter existing diagnostic outcomes.

## CV Deep-Dive Questions

- What Laravel/Symfony backend components did you build at airSlate, and why was shared logging needed?
- How did you measure the 30% API response-time reduction and the database-load improvement?
- Which production incidents did you investigate, and what monitoring signals led to the fix?
- What parts of the ECS-to-Kubernetes migration did you personally own?
- How did the Simple.life integration layer coordinate Zendesk, Intercom, and internal services?
- How were retries, fallbacks, and monitoring designed in the message-delivery pipeline?
- What changed to produce the 10-times throughput increase at CRURATED?
- How did you guarantee event compatibility and delivery above 99.9%?
- What technical decisions allowed the PDFfiller email service to handle around 50 million messages per month and traffic spikes above 10 times normal?
- How did you manage ten developers at Hyprr while staying involved in technical decisions?
- Why do the candidate records differ on Simple.life and PDFfiller dates and titles?
- Which parts of your prior PHP work map most directly to modern Laravel practices today?

Prepare evidence, measurement method, personal contribution, constraints, and trade-offs for every quantified claim.

## Company-Specific Preparation

- Review Digis's delivery model. Expect questions about joining an established client team, learning a client's domain, communicating across organisational boundaries, and supporting client-specific implementations.
- Treat Plentific as an informed hypothesis, not a confirmed client. Its public platform description matches the vacancy's scale and capabilities. Review the product areas: resident experience, repair diagnostics, work orders, contractor management, compliance, analytics, APIs, and property-management integrations.
- Trace one end-to-end workflow before the interview: a resident reports a fault, diagnostic questions classify it, the platform creates and routes a work order, a contractor updates progress, and the housing provider receives status and reporting data.
- Prepare examples of product judgment. The team may value an engineer who can distinguish a code defect from a rule/content issue, integration inconsistency, permissions problem, or client configuration difference.
- Expect a client interview in addition to the Digis screening. Keep explanations clear for engineers, product staff, and operational stakeholders.

Research sources: [Digis overview](https://digiscorp.com/about-us/), [property operations platform](https://www.plentific.com/property-operations-platform/), [repair and maintenance integrations](https://www.plentific.com/partners/partner-network/microsoft-dynamics-365/), and [award announcement](https://www.plentific.com/resource-center/newsroom/plentific-wins-technology-partner-of-the-year-at-the-northern-housing-awards-2025/).

## Preparation Plan

### Must prepare before recruiter screening

- Confirm Vue.js experience, work authorization, compensation range, notice period, and earliest start date.
- Reconcile the Simple.life, CRURATED, and PDFfiller timeline details.
- Practice a 60-second introduction focused on PHP/Laravel, integrations, production troubleshooting, and team contribution.
- Prepare a direct answer to the Vue.js gap and a realistic learning/update plan.

### Before the technical interview

- Refresh modern Laravel architecture, Eloquent performance, queues, events, testing, authorization, and API patterns.
- Build or review one small Vue.js form with dependent questions and server validation.
- Rehearse the repair-diagnostics system-design exercise and integration failure modes.
- Prepare four metric-backed stories: airSlate performance, Simple.life integrations, CRURATED event pipelines, and PDFfiller scale.

### Before the final or culture interview

- Prepare examples of mentoring, code review, stakeholder communication, and technical disagreement.
- Explain how you learn an unfamiliar domain and support a client team without becoming a bottleneck.
- Review the product's resident, contractor, housing-provider, and compliance perspectives.
- Decide which employment, team, and growth conditions you need before accepting an offer.

## Questions to Ask

1. How much of the role is Laravel backend work versus Vue.js feature development in a typical sprint?
2. Is commercial Vue.js experience a strict entry requirement, or can deep Laravel experience offset a shorter Vue background?
3. Which workflows and services does the Diagnostics team own from end to end?
4. How are diagnostic questions, categories, and problem types modelled, versioned, tested, and published?
5. What are the most common defects across the frontend, backend, and integration boundaries?
6. How does the team separate core-product changes from client-specific implementations?
7. What does the current Laravel and Vue.js architecture look like, and which parts are being modernised?
8. Which tests and release checks protect changes that affect repair classification or work-order creation?
9. How do Digis engineers work with the client's product, design, QA, and engineering leaders?
10. What would successful delivery look like after the first 30, 60, and 90 days?
