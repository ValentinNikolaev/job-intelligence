# Interview Preparation

## Recruiter / HR Screening

Likely questions:

- Why are you interested in SparkFabrik and this PHP Developer role?
- Are you based in Italy, and are you comfortable with a remote Italy setup?
- What is your current availability and notice period?
- What salary range are you targeting?
- How comfortable are you working in English?
- What is your current Italian level?
- Are you open to working on Drupal-based projects?
- Do you prefer Senior Developer or Professional/Tech Lead responsibilities?

Suggested positioning:

- Motivation: "This role brings together my long PHP background, Laravel/Symfony experience, and recent cloud-native delivery work. SparkFabrik's mix of custom software, Drupal, Kubernetes, DevOps, and open source fits the kind of engineering environment where I can contribute."
- Location: "I am based near Rome and can work remotely in Italy."
- English: "I am comfortable reading, writing, and discussing technical topics in English."
- Italian: "My Italian is limited at the moment. I am improving it, and I would like to understand whether English is enough for the team and client context."
- Drupal: "I have strong PHP, Laravel, Symfony, and backend architecture experience. Drupal is not my strongest area, but I am comfortable learning it and working with specialists."
- Seniority: "I can contribute as a hands-on senior backend engineer and also support technical direction, mentoring, planning, and architecture where the team needs it."

## Culture Fit / Behavioral Interview

Likely behavioral questions:

1. Tell us about a long-running production system you owned.
2. Describe a time you improved system reliability under pressure.
3. Tell us about a performance bottleneck you diagnosed and fixed.
4. Describe your experience working with product or business stakeholders.
5. Tell us about a time you led engineers without losing hands-on contribution.
6. How do you approach code quality and maintainability?
7. How do you handle unfamiliar technology in a client project?
8. Describe a disagreement with a technical stakeholder and how you handled it.

STAR story sources from the CV:

- airSlate database load reduction and API performance work.
- airSlate migration from ECS to Kubernetes with Helm, GitHub Actions, and ArgoCD.
- PDFfiller transactional email service scaling to around 50 million emails per month.
- Hyprr prototype-to-closed-beta delivery and coordination of 10 developers.
- Simple.life Zendesk/Intercom support automation and reliable message delivery.

Behavioral themes to emphasize:

- Calm production ownership.
- Pragmatic architecture choices.
- Clear collaboration with product, support, and engineering stakeholders.
- Mentoring and technical decision-making without overstating authority.
- Learning gaps honestly, then reducing risk through collaboration and focused ramp-up.

## Technical Interview

High Priority:

- PHP backend development: OOP, Laravel, Symfony, dependency management, service boundaries, framework tradeoffs.
- REST APIs: API design, versioning, error handling, idempotency, authentication, observability.
- Databases: MySQL/PostgreSQL schema design, indexes, query optimization, transaction boundaries, load reduction.
- Cloud-native delivery: Kubernetes, containers, Helm, CI/CD, deployment safety, rollbacks.
- Production reliability: logging, monitoring, retries, queues, incident handling, performance debugging.
- Architecture: microservices, event-driven systems, distributed systems, service ownership.

Medium Priority:

- Testing: unit, functional, integration testing, pragmatic test strategy, what TDD means in real delivery.
- Git workflows: branching models, review habits, release discipline.
- Client/project communication: translating technical tradeoffs for technical and business stakeholders.
- Security/compliance: GDPR/PCI DSS exposure from Sixt, secure API and infrastructure habits.

Low Priority:

- Drupal internals: prepare an honest answer about limited direct evidence and a learning plan.
- Vue/Angular: discuss full-stack-adjacent collaboration rather than claiming current specialist depth.
- Serverless: Hyprr includes serverless architecture influence, but do not center the conversation on it unless asked.

Technical claims to defend:

- "Laravel/Symfony-based components" at airSlate: prepare concrete examples of package/service structure, dependency injection, logging, API integration, or framework conventions.
- "Reduced peak load on the main database": explain diagnosis, measurements, query/index/service changes, and production validation.
- "Migrated services from ECS to Kubernetes": explain what you owned, what the team owned, deployment pipeline details, Helm, GitHub Actions, and ArgoCD.
- "Scaled to around 50 million emails per month": explain architecture, queues, retries, deliverability, monitoring, and peak traffic handling.
- "Led backend development and coordinated 10 developers": explain planning rhythm, delegation, code review, and decision-making.

## CV Deep-Dive Questions

Prepare concise answers for:

- Why does your recent work show more Go than PHP, and why return to a PHP-centered role?
- Which Laravel/Symfony work can you discuss in detail?
- How much Drupal have you used?
- What is your experience with Composer and PHP package design?
- How do you define a good testing strategy for a PHP service?
- What production incident taught you the most?
- How do you balance delivery speed with maintainability?
- What does "technical leadership" mean in your day-to-day work?
- Why do PDFfiller and Sixt dates overlap?
- What is your current employment status, given source records may differ?

Safe responses:

- PHP direction: "PHP has been a major part of my backend career. Recent Go work expanded my distributed-systems and reliability experience, and I see that as useful for SparkFabrik's cloud-native PHP work."
- Drupal: "I should not present myself as a Drupal specialist. My strongest value is PHP backend, Laravel/Symfony, APIs, cloud delivery, and reliability. I can ramp up on Drupal with the team."
- Italian: "My Italian is limited. I can work in English and I am improving Italian. I would rather be clear about this early."

## Company-Specific Preparation

Review before interviews:

- SparkFabrik's homepage: Cloud Native, AI, Drupal, custom development, agile methodology, senior team.
- Services page: enterprise software development, cloud engineering, DevOps, consulting, Kubernetes Certified Service Provider, CNCF and OpenSSF membership.
- Open Source page: Drupal Certified Partner Gold, CNCF, Linux Foundation Europe, OpenSSF, public Drupal contributions.
- Tech Blog: recent topics around cloud native, DevOps, AI, Drupal, security, and Kubernetes.
- Job posting: Laravel, Symfony, Drupal 7+, Angular/Vue adjacency, testing/TDD, client-facing collaboration, full remote Italy.

Company-aligned talking points:

- "My PHP background and Laravel/Symfony experience fit the backend part of the role."
- "My Kubernetes, CI/CD, AWS, monitoring, and reliability work fit SparkFabrik's cloud-native and DevOps direction."
- "I have led teams and worked with product and technical stakeholders, which fits the Professional-level expectations."
- "I am transparent about Drupal and Italian gaps and can ramp up where the team needs me."

## Preparation Plan

Must prepare:

- One clear story each for PHP/Laravel/Symfony, API performance, Kubernetes migration, and team leadership.
- A direct explanation of Drupal exposure and a practical ramp-up plan.
- A direct explanation of Italian level.
- Current availability, salary expectations, and preferred seniority track.

Before technical interview:

- Refresh Laravel/Symfony architecture concepts, Composer, dependency injection, service containers, routing/middleware, validation, queues, events, and testing.
- Prepare database optimization examples with indexes, query plans, load distribution, and production monitoring.
- Prepare CI/CD and Kubernetes details: Helm charts, GitHub Actions, ArgoCD, rollout/rollback, config/secrets handling, observability.
- Review testing strategy language: unit versus integration, contract tests, functional tests, test data, and when TDD helps.

Before final/culture interview:

- Prepare examples of mentoring, stakeholder communication, and working in distributed teams.
- Prepare questions about client context, team shape, language expectations, Drupal depth, and growth path.
- Decide how to position Senior versus Professional track.

## Questions to Ask

1. Which seniority track are you considering for this opening: Senior Developer, Professional Developer, or both?
2. How much of the role is Laravel/Symfony backend work versus Drupal-specific work?
3. Is Italian required for internal teamwork or client communication, or can the role work primarily in English?
4. What does the team consider good quality delivery on long-term client projects?
5. How are PHP developers involved in cloud-native and DevOps practices?
6. What CI/CD, testing, and observability practices are standard across projects?
7. How do frontend and backend developers collaborate on Angular/Vue-adjacent work?
8. What kind of mentoring or technical leadership would you expect from someone at my level?
9. How do you assign developers to client projects, and how stable are those assignments?
10. What would success look like in the first three to six months?
