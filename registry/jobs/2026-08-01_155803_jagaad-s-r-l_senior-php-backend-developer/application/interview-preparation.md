# Interview Preparation

## Recruiter / HR Screening

Likely questions:

- Why are you interested in Jagaad and this Senior PHP Backend Developer role?
- Are you comfortable with a fully remote contractor role?
- Where are you based, and which timezone do you usually work in?
- What is your current employment status and notice period?
- Do you need visa sponsorship or any special work authorization support?
- What salary or contractor rate are you targeting?
- How fluent is your English for daily engineering communication?
- Your recent work looks Go-heavy. How current is your PHP and Symfony experience?
- Have you worked in remote international teams?
- Can you share examples of owning API or platform work from design through production?

Suggested positioning:

- Motivation: "The role matches the kind of work I do best: backend APIs, PHP/Symfony, performance, Kubernetes, and technical ownership in a remote team."
- Remote work: "I am based in Rome and comfortable working around CET hours. I work well with explicit communication, written decisions, code review, and async handoffs."
- PHP recency: "My recent work broadened into Go, but I have a long PHP background across Laravel and Symfony-based systems, API performance, MySQL, and production services."
- Contractor terms: confirm before interview. Do not guess salary, availability, sponsorship, or invoicing details.

Must confirm before screening:

- Current employment status and whether Simple.life ended in March 2026 or continued after that date.
- How CRURATED overlapped with Simple.life, if it should be mentioned at all.
- Notice period and earliest start date.
- Work authorization wording for Italy/EU and whether sponsorship is needed.
- Target salary or contractor rate.

## Culture Fit / Behavioral Interview

Likely behavioral questions:

- Tell me about a time you led a complicated technical project.
- Describe a time you improved system performance under production pressure.
- How do you review pull requests constructively?
- How do you balance best practices with pragmatic delivery?
- Tell me about a disagreement with a stakeholder or another engineer.
- How do you communicate progress and risks in a remote team?
- Describe a time you helped a teammate improve.
- Tell me about a system you owned after production release.
- How do you break down a large technical project into deliverables?
- What kind of feedback helps you work better?

STAR stories to prepare:

- airSlate Kubernetes migration: situation around ECS services, task to prepare Kubernetes runtime, actions with Helm/GitHub Actions/ArgoCD, result in deployment consistency, cost/performance improvements if comfortable using LinkedIn metrics.
- airSlate database/API performance: situation around peak database load and bottlenecks, task to stabilize service, actions around query/API optimization and workload redistribution, result in improved stability.
- PDFfiller transactional email service: situation around high-volume messaging, task to scale and lead the backend team, actions around architecture, DNS/DKIM/SPF/DMARC, reliability, and team coordination, result around 50 million emails per month and BFCM traffic.
- Hyprr prototype-to-beta delivery: situation around early product, task to establish backend direction, actions around architecture, roadmap, CI/CD, and team leadership, result of closed beta in under 6 months.
- Simple.life support automation: situation around support scale, task to connect Zendesk, Intercom, and internal systems, actions around API orchestration, routing, fallback, retries, and monitoring, result in operational responsiveness.

## Technical Interview

High Priority:

- Modern PHP and Symfony: dependency injection, services, controllers, validation, console commands, Doctrine patterns if relevant, configuration, testing approach, and maintainable service structure.
- REST API design: resource modeling, versioning, pagination, idempotency, error handling, authentication, rate limits, backwards compatibility, and API documentation.
- MySQL performance: indexing, query plans, slow query analysis, transactions, locking, schema design, migrations, and high-load troubleshooting.
- Kubernetes and Docker: containerization, deployments, service configuration, health checks, rollout/rollback, logs, resource limits, Helm, and production debugging.
- System design for scalable APIs: decomposition, queues, caching, observability, failure modes, backpressure, retries, and tradeoffs.
- Code review and design discussion: how to review for correctness, maintainability, security, performance, testability, and shared understanding.

Medium Priority:

- Testing strategy: unit, integration, and functional tests; test boundaries; fixtures; CI quality gates; when to mock external services.
- CI/CD: GitHub Actions, ArgoCD, release safety, deployment consistency, and rollback practices.
- Microservices: service ownership, API contracts, observability, data consistency, queues, and operational complexity.
- Linux operations: logs, processes, networking basics, file permissions, service debugging, and shell-based production investigation.
- Go as bonus: how Go experience improved backend design, concurrency thinking, and service reliability without distracting from PHP.

Low Priority:

- MongoDB: prepare only a high-level comparison if no production evidence exists. Emphasize MySQL/PostgreSQL evidence.
- Frontend/mobile: understand API consumers, but do not position as a frontend developer.
- Jagaad internal products: useful for questions, but the role appears broader across client and platform work.

Questions to defend CV claims:

- How did you reduce peak database load at airSlate?
- Which Symfony components or patterns did you use?
- What did the Laravel/Symfony logger package do?
- How did the ECS-to-Kubernetes migration work?
- What problems did Helm, GitHub Actions, and ArgoCD solve?
- How did you scale the PDFfiller email service?
- What monitoring signals did you use during incidents?
- How did you lead code reviews and technical decisions without slowing delivery?
- What tradeoffs did you make in Hyprr's prototype-to-beta architecture?

## CV Deep-Dive Questions

Simple.life:

- Explain the support automation platform architecture.
- Which internal services did the platform connect?
- How did retries, fallback logic, and monitoring work?
- How did you collaborate with Support Ops, Product, and AI teams?
- Which parts were API orchestration versus business workflow logic?

airSlate:

- Describe the PHP backend services you worked on.
- Explain your Symfony/Laravel experience with concrete examples.
- How did you identify API and query bottlenecks?
- What changed during the ECS-to-Kubernetes migration?
- How did you improve release consistency with CI/CD?
- What technical leadership responsibilities did you have?

Hyprr:

- What did you build between prototype and closed beta?
- How did you define the technical roadmap with the CTO?
- What microservice or serverless decisions did you make?
- How did you coach or lead the team?

PDFfiller:

- How did the transactional email service scale to 50 million emails per month?
- What reliability issues appear in high-volume email systems?
- How did DNS, DKIM, SPF, DMARC, and feedback loops affect backend design?
- How did you prepare for BFCM traffic?

Timeline:

- Be ready to explain the Simple.life / CRURATED overlap if asked. Use factual wording only after confirming the correct chronology.

## Company-Specific Preparation

Know these verified Jagaad facts:

- Jagaad is fully remote and office-less.
- The role is contractor and fully remote.
- The role page says Jagaad builds cloud-based applications and scalable, performant microservices that often integrate with APIs.
- Jagaad works with clients in Energy, Travel, E-commerce, and Retail.
- The company emphasizes transparency, autonomy, feedback, continuous improvement, and remote collaboration.
- Public services include web and mobile development, custom API integrations, cloud architectures, microservices/DevOps, e-commerce, automated monitoring, and AI.
- Public technology cues include PHP, Go, Node, Vue, React, AWS, Docker/cloud topics, and backend work.

Translate experience to Jagaad:

- API integrations: Simple.life, airSlate, PDFfiller.
- Scalable microservices: Hyprr, airSlate, PDFfiller.
- Cloud/Kubernetes: airSlate and Hyprr.
- Performance optimization: airSlate database/API work, PDFfiller traffic peaks.
- Remote autonomy: Rome/CET remote collaboration, explicit communication, code review, written technical decisions.
- Team improvement: PR reviews, mentoring, design discussions, technical interviews, planning.

Avoid unsupported claims:

- Do not claim direct Jagaad product familiarity beyond public pages.
- Do not claim MongoDB, GitLab, Python, or billions-of-data-points experience unless the candidate confirms it.
- Do not imply native/fluent English beyond the documented professional working / upper-intermediate level.

## Preparation Plan

Must prepare before recruiter call:

- Confirm current work status, Simple.life dates, and CRURATED overlap.
- Confirm contractor setup, notice period, earliest start date, and salary/rate.
- Prepare a 60-second answer on why this role and why Jagaad.
- Prepare a concise PHP recency answer.

Before technical interview:

- Refresh Symfony service architecture, dependency injection, Doctrine patterns, validation, console commands, and testing conventions.
- Prepare one REST API design walkthrough, including versioning, idempotency, pagination, error handling, observability, and deployment concerns.
- Prepare one MySQL performance story with indexes, query plans, bottleneck diagnosis, and production validation.
- Prepare Kubernetes migration details from airSlate: deployment, Helm, GitHub Actions, ArgoCD, rollout safety, monitoring, and debugging.
- Prepare code review principles with examples of constructive feedback.

Before final or culture interview:

- Prepare examples for autonomy, transparency, feedback, remote collaboration, and stakeholder alignment.
- Prepare questions about team structure, roadmap ownership, review culture, and contractor expectations.
- Decide how to discuss long-term interest in PHP while acknowledging recent Go work.

## Questions to Ask

- Which product or client domain would this PHP backend role support first?
- How much of the backend stack is Symfony today, and where are the main modernization priorities?
- What are the biggest performance or reliability challenges the team wants this person to help solve?
- How does Jagaad structure code review and design discussions in a fully remote team?
- What does successful technical leadership look like for this role after 3 and 6 months?
- How are roadmap priorities agreed between engineers, product stakeholders, and clients?
- What testing practices and CI quality gates does the team expect for PHP services?
- How are Kubernetes deployments, observability, and incident response handled today?
- What contractor setup and working-hours overlap do you expect from someone based in Italy?
