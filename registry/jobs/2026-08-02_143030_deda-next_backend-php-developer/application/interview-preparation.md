# Interview Preparation

## Recruiter / HR Screening

Prepare concise answers for:

- Why this role: It uses PHP, Laravel/Symfony, REST APIs, relational databases, integrations, logging, monitoring, and maintainable backend services.
- Why Deda.Next: The company works on digital transformation for public administrations and public-service companies, with backend systems that need reliable APIs, data quality, permissions, and long-term maintainability.
- Location: Rome, Italy. The role lists Pisa and Rome.
- Working model: The posting says Hybrid. Ask for Rome office frequency and whether project teams support flexible remote work.
- Salary: Published range is EUR 30,000-35,000. Ask whether the range changes for a candidate with senior/technical-lead experience, as the posting says seniority evaluation can affect salary range.
- Work authorization: Confirm exact Italy/EU wording before screening.
- Notice period: TODO_CONFIRM.
- Earliest start date: TODO_CONFIRM.
- Language: English is professional working / upper-intermediate. Italian is not documented; ask whether Italian is required for public-sector stakeholders.
- Job change: Emphasize hands-on backend work, maintainable services, and cross-functional delivery.

## Culture Fit / Behavioral Interview

Likely questions:

- Tell me about a backend service you maintained and improved over time.
- Describe a difficult API or database performance problem.
- Tell me about a time you worked with frontend, DevOps, product, or functional stakeholders.
- How do you approach code review for backend services?
- How do you balance speed with maintainability?
- Tell me about a production issue you investigated using logs or monitoring.
- Describe your experience mentoring or leading other backend engineers.
- How do you document API behavior and integration assumptions?
- How do you handle unclear requirements from non-technical stakeholders?
- Why are you interested in public-administration or public-service digital projects?

STAR story candidates:

- airSlate database load reduction to 65% and API response-time optimization.
- airSlate Laravel/Symfony logger package and interservice communication standards.
- airSlate ECS to Kubernetes migration with Helm, GitHub Actions, and ArgoCD.
- Hyprr prototype to closed beta in under 6 months.
- PDFfiller transactional email service scaling to around 50 million emails per month.
- Simple.life Zendesk/Intercom support automation and monitoring.
- CRURATED event analytics infrastructure and reliability.

## Technical Interview

**High Priority:** PHP, Laravel, Symfony, REST API design, MySQL, PostgreSQL, ORM patterns, data modeling, query optimization, external-service integration, logging, monitoring, testing, code review, backend maintainability.

Why: These are central to the posting and strongly supported by the candidate record.

**High Priority:** Authentication and authorization concepts, JWT, OAuth2, OpenID Connect, permissions, application security, GDPR/PCI DSS-aware backend work.

Why: The vacancy explicitly names OAuth2, OIDC, JWT, permissions, and security logic. Candidate evidence supports security-aware backend work through Sixt and API/integration experience, but direct OAuth2/OIDC/JWT claims should be confirmed before interviews.

**Medium Priority:** Kubernetes, AWS, CI/CD, Helm, GitHub Actions, ArgoCD, Prometheus, RabbitMQ, Elasticsearch, event-driven systems.

Why: These support DevOps collaboration, observability, and scalable backend service operation.

**Medium Priority:** Digital content workflows, metadata, publishing processes, cataloging/search platforms.

Why: The domain is central to the role, but candidate evidence is adjacent through document automation, digital products, analytics, and platform services rather than direct digital heritage work.

**Low Priority:** Go, OpenAI automation, email infrastructure, blockchain/NFT.

Why: These show breadth but should stay secondary unless Deda asks about broader backend experience.

Technical questions to prepare:

- How do you design a secure REST API for frontend and third-party integrations?
- How do you structure a Laravel or Symfony service for maintainability?
- How do you handle authentication and authorization in backend APIs?
- What is your experience with OAuth2, OIDC, and JWT? Be precise and do not overclaim.
- How do you model relational data and optimize slow queries?
- How do you use logging and monitoring to troubleshoot production issues?
- How do you write tests for API behavior and integrations?
- How do you review code for reliability and maintainability?
- How would you design metadata and permissions for digital assets?
- How do you plan backward-compatible changes in a service consumed by multiple systems?

## CV Deep-Dive Questions

Prepare to defend:

- Simple.life: Zendesk/Intercom integration architecture, API orchestration, monitoring, and 30% automation/deflection claim.
- CRURATED: role scope, overlap with Simple.life, event schema, queue/EventBridge design, and 99.9% delivery reliability claim.
- airSlate: Laravel/Symfony logger package, database load reduction, API/query performance, ECS-to-Kubernetes migration, and production troubleshooting.
- Hyprr: backend stack, roadmap ownership, direct leadership of 10 developers, and prototype-to-closed-beta delivery.
- Sixt: GDPR/PCI DSS microservices, backend security constraints, and technical viability assessments.
- PDFfiller: transactional email architecture, team leadership, scale to 50 million emails per month, and BFCM readiness.

## Company-Specific Preparation

Review these sources:

- Deda Backend PHP Developer posting: https://careers.deda.com/jobs/7926763-backend-php-developer
- Deda public services page: https://www.deda.com/markets-solutions/markets/public-services-en
- Deda Next history page: https://www.deda.com/group/history/deda-next-is-born

Prepare talking points:

- Deda.Next works in public administration and public-service digital transformation.
- The role supports cataloging, search, and digital heritage platforms, so data quality, metadata, permissions, and maintainability matter.
- Your strongest technical overlap is PHP/Laravel/Symfony, REST APIs, database performance, logging, monitoring, integrations, and reliable backend operation.
- Confirm Italian-language expectations and office rhythm early.
- Treat the salary and seniority mismatch professionally: ask whether the posted range changes after seniority evaluation.

## Preparation Plan

Must-prepare:

- One PHP/Laravel/Symfony service story from airSlate.
- One REST API and integration story.
- One database performance story.
- One logging/monitoring troubleshooting story.
- One code review or maintainability story.
- Precise work authorization, notice period, salary, and office-frequency answers.

Before technical interview:

- Refresh PHP 8.x features, Laravel/Symfony architecture, dependency injection, routing, validation, queues, middleware, and testing.
- Review REST API design, OpenAPI-style documentation, error handling, versioning, pagination, idempotency, and security.
- Review OAuth2, OIDC, JWT, RBAC/ABAC, permissions, session security, and token lifecycle concepts.
- Review MySQL/PostgreSQL indexing, query plans, transactions, locks, migrations, and data modeling.
- Prepare a simple design for digital asset metadata, permissions, workflow states, and publishing processes.

Before final or culture interview:

- Prepare a short explanation of why a senior candidate is interested in a medium-seniority hands-on role.
- Prepare a direct answer on hybrid work in Rome.
- Prepare examples of working with product, functional, frontend, UX, and DevOps teams.
- Prepare questions about Deda.Next's public-sector delivery process and technical standards.

## Questions to Ask

- How many days per week are expected in the Rome office?
- Is Italian required for daily work, documentation, or client meetings?
- Which PHP framework does the project use, Laravel, Symfony, or both?
- What PHP version and database stack are used?
- How mature are the current tests, logging, and monitoring?
- What authentication and authorization model does the platform use?
- How are metadata, permissions, and publishing workflows modeled today?
- Does the salary range adjust for seniority beyond the "Media" level?
- What would success look like in the first 90 days?
- How do frontend, UX, DevOps, and functional teams collaborate on this platform?
