# Interview Preparation

## Recruiter / HR Screening

Likely questions:

- Why are you interested in Faria and the Atlas product?
- Are you comfortable with a remote B2B contract with the US LLC?
- What is your current location and availability for UTC+1/UTC+2 collaboration?
- Can you coordinate occasionally with China and US West Coast business hours?
- What is your English level for daily written and spoken communication?
- What is your notice period and earliest start date?
- What compensation range are you targeting?
- Do you have a valid international passport?
- Have you worked with PHP 8 and Laravel 12?
- How do you use AI during development?
- Can you explain the overlap between Simple.life and CRURATED?
- Are you comfortable with safer recruitment checks if required?

Suggested positioning:

- Motivation: focus on product engineering, PHP/Laravel backend ownership, API/database performance, CI/CD, and Atlas's education impact.
- Remote: Rome, Italy, CET-compatible; clarify acceptable overlap for China and US West Coast.
- Contract: confirm B2B details, payment currency, invoicing, and whether US LLC contract terms work for you.
- Salary: use the reusable answer only after confirming range: "Given the role scope and leadership expectations, I would like to discuss the upper part of the published range, depending on the full package, responsibilities, and growth path."
- AI: cite Simple.life AI-powered triage and support automation; add current AI-assisted coding workflow only if true.

## Culture Fit / Behavioral Interview

Prepare STAR stories from real CV evidence:

- End-to-end ownership: Hyprr prototype to closed beta in under 6 months.
- Cross-functional collaboration: Simple.life work with Support Ops, Product, and AI teams.
- Performance optimization: airSlate database load reduction and API/query bottleneck work.
- CI/CD improvement: airSlate ECS to Kubernetes migration with Helm, GitHub Actions, and ArgoCD.
- AI in product workflows: Simple.life auto-triage and LLM-assisted support workflows.
- Mentoring/code review: PDFfiller team of 5 backend engineers.
- Reliability under scale: PDFfiller transactional email system at around 50 million emails/month.
- Security/compliance: SIXT GDPR and PCI DSS-related backend work.

Likely behavioral questions:

- Tell us about a time you owned a backend feature or project end-to-end.
- How do you scope and estimate work with product managers and designers?
- How do you keep remote communication reliable across time zones?
- Tell us about a time you improved an API or database performance issue.
- How do you balance feature delivery with technical debt?
- How do you use AI tools without reducing code quality?
- Tell us about a time you improved CI/CD or developer experience.
- How do you approach secure development when requirements are still changing?
- How do you handle code review feedback?
- How do you help a team improve its SDLC?

## Technical Interview

High Priority:

- PHP/Laravel architecture: service boundaries, controllers, validation, jobs/queues, events, dependency injection, Eloquent trade-offs, migrations, and configuration.
- OOP principles: encapsulation, SOLID, composition over inheritance, domain services, interfaces, and pragmatic refactoring.
- REST API design and performance: pagination, filtering, idempotency, error handling, versioning, rate limits, caching, and request tracing.
- Database optimization: query plans, indexes, N+1 queries, transaction boundaries, locking, schema design, and migration safety.
- Testing: unit tests, feature tests, mocking, fixtures, integration boundaries, and regression coverage. Be ready for PHPUnit questions even if not highlighted in the CV.
- CI/CD and build tooling: GitHub Actions, pipeline design, linting/static analysis, quality gates, deployment safety, rollbacks, and developer feedback loops.
- Security-conscious development: input validation, authorization, secrets, dependency risks, data protection, audit trails, and privacy-aware engineering for school data.
- AI-assisted development: where AI helps, where it is risky, and how to verify generated code, tests, refactors, and documentation.

Medium Priority:

- Vue.js collaboration: component/API contracts, frontend-backend handoff, migration awareness from Vue 2 to Vue 3, and debugging collaboration.
- Third-party integrations: retries, rate limits, webhooks, idempotency, auth, observability, and failure handling.
- Kubernetes/AWS: useful supporting evidence, but this role appears more Laravel/product-engineering focused than infrastructure-heavy.
- Static analysis and profiling: prepare tools and examples even if source evidence is not tool-specific.
- Atlassian/Jira workflow: show practical delivery discipline and priority sequencing.

Low Priority:

- MS SQL Server specifics: vacancy says MS SQL Server or similar relational database; MySQL/PostgreSQL evidence is enough, but review basic SQL Server differences.
- EdTech domain depth: learn the product/user context, but avoid pretending prior EdTech specialization.

Technical exercises to rehearse:

- Design a Laravel API feature with request validation, database schema changes, tests, and background jobs.
- Diagnose a slow Laravel endpoint backed by a relational database.
- Add a third-party integration with retries, idempotency, logging, and failure recovery.
- Refactor a legacy Laravel service while protecting behavior with tests.
- Design CI quality gates for static analysis, tests, and deployment checks.
- Explain how to use AI to draft tests or refactoring options, then verify correctness.

## CV Deep-Dive Questions

Prepare concise answers for:

- Simple.life: What did the Zendesk/Intercom automation platform do? What APIs and services did it connect?
- Simple.life: How did the AI-powered triage work, and how was 30% automation or deflection measured?
- Simple.life: How did fallback logic and retries improve reliability?
- CRURATED: Why was event-driven analytics needed? What changed to increase throughput by over 10x?
- airSlate: What Laravel/Symfony backend components did you build?
- airSlate: How did you reduce database load and optimize API/query performance?
- airSlate: What did GitHub Actions, Helm, and ArgoCD do in your delivery pipeline?
- Hyprr: What architecture choices helped move from prototype to closed beta?
- PDFfiller: How did the transactional email service scale to around 50 million emails/month?
- SIXT: What did security/compliance-sensitive backend development look like in practice?

Important timeline defense:

- Confirm and rehearse the Simple.life / CRURATED overlap. If CRURATED was contract, parallel, part-time, or consulting, say so clearly. Do not improvise.

## Company-Specific Preparation

Facts to know:

- Faria is an EdTech company serving millions of learners and more than 10,000 schools.
- Atlas is Faria's curriculum planning / curriculum management platform trusted by over 6,000 schools and districts.
- Atlas supports curriculum development, lesson planning, analytics, standards alignment, integrations, and collaboration for teachers and administrators.
- Public Atlas material mentions Atlas AI and 50+ integrations.
- Atlas public material emphasizes global hosting, ISO/IEC 27001:2013 compliance, GDPR compliance, and safeguarding.
- Faria careers material lists 370+ people globally, 31 nationalities, and hubs including Krakow and Ivano-Frankivsk.

How to connect your experience:

- Atlas API performance and scale: airSlate database/API optimization and PDFfiller high-volume systems.
- AI-native engineering: Simple.life AI triage and automation workflows.
- Integrations: Simple.life Zendesk/Intercom/internal services; CRURATED Webhook/S3 downstreams; older payment integrations if asked, but do not overemphasize older dated work in the CV.
- Security: SIXT GDPR/PCI DSS-related backend work and general secure development discipline.
- Remote collaboration: cross-functional Simple.life and airSlate product/engineering collaboration.

Topics to research before final interviews:

- Atlas core user workflows: curriculum mapping, unit planning, standards alignment, reports, and integrations.
- Basic student-data privacy concerns: GDPR, safeguarding, least-privilege access, audit trails, secure integration design.
- Laravel 12 and PHP 8 features if your recent production stack used older versions.
- PHPUnit feature testing patterns in Laravel.
- Vue 2 to Vue 3 migration basics so you can collaborate fluently with frontend engineers.

## Preparation Plan

Must-prepare:

- Confirm notice period, earliest start date, salary expectations, work authorization, B2B readiness, and valid passport status.
- Resolve the Simple.life / CRURATED timeline explanation.
- Prepare exact current experience with PHP 8, Laravel 12, PHPUnit, Vue.js, and AI development tools.
- Prepare one strong Laravel API/database performance story from airSlate.

Pre-technical:

- Review Laravel 12 conventions, PHP 8 language features, Eloquent performance, migrations, service classes, queues, events, and feature tests.
- Rehearse CI/CD examples with GitHub Actions and quality gates.
- Prepare examples for third-party API integration, retries, idempotency, and observability.
- Prepare secure-development examples tied to validation, authorization, secrets, and data privacy.

Pre-final/culture:

- Read Atlas product pages and Faria careers page.
- Prepare a thoughtful answer on why EdTech product work is credible and attractive.
- Prepare questions about team ownership, AI-native practices, SDLC improvements, and backend quality standards.

## Questions to Ask

- What are the first backend projects this role would own on Atlas?
- Which parts of the Atlas application need the most performance or maintainability work?
- What database engine powers Atlas today, and where are the largest query or scaling challenges?
- How does the team use PHPUnit, static analysis, and profiling in daily development?
- What does "AI-native team" mean in Faria's engineering practice right now?
- How do backend engineers collaborate with the Vue frontend team during the Vue 2 to Vue 3 transition?
- What CI/CD and build-tooling improvements are most important this year?
- How much overlap is expected with China and US West Coast colleagues?
- What security or safeguarding requirements most affect backend development?
- How does Faria measure success for a senior engineer in the first 3 to 6 months?
