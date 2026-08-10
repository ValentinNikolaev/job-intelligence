## Recruiter / HR Screening

- **Why WhiteTech and this role?** Explain the connection between PHP backend work, payment-related systems, third-party integrations, and WhiteTech’s modular fintech platform. Do not claim personal use of WhiteTech products.
- **Where are you based and can you work CET hours?** Rome, Italy; the posting’s European/CET model is compatible.
- **What is your availability?** Confirm the current notice period before the call; it is not in the supplied evidence.
- **What salary do you expect?** Prepare a gross monthly EUR range and clarify whether it assumes employment or contracting. The application form requires a number.
- **Do you speak Ukrainian or Russian?** Ukrainian is documented as native. Russian appears in the LinkedIn source but is not confirmed in the primary CV; answer the form accurately.
- **Why are you considering a change?** Keep the answer forward-looking: seek a role where PHP backend engineering, APIs, reliability, and complex fintech workflows are central.
- **What is your Symfony experience?** Cite the airSlate PHP/Laravel/Symfony backend work and avoid claiming unsupported Doctrine depth.
- **What is your DDD experience?** Be direct that advanced DDD concepts are not explicitly documented in the supplied CV; relate only the supported microservice, event-driven, and architecture work.

## Culture Fit / Behavioral Interview

Prepare 5–10 STAR stories from verified experience:

1. **Ownership:** owning the Simple.life support automation platform across integrations and operational reliability.
2. **Performance:** investigating API and query bottlenecks at airSlate and reducing peak database load.
3. **Delivery:** migrating services from ECS to Kubernetes with Helm, GitHub Actions, and ArgoCD.
4. **Reliability:** building message-delivery fallback, retry, and monitoring behavior at Simple.life.
5. **Scale:** leading the PDFfiller transactional email service at approximately 50M emails/month.
6. **Peak incident pressure:** leading BFCM readiness through more than 10x traffic growth.
7. **Architecture:** taking Hyprr from prototype to closed beta in under six months and shaping its microservice/serverless direction.
8. **Collaboration:** coordinating with Support Ops, Product, and AI teams on automation flows.

Likely questions: a time a production issue was difficult to diagnose; a trade-off between speed and maintainability; how you handle disagreement about architecture; how you mentor or distribute work; a change that failed and what you learned; how you document decisions; how you work with frontend and product colleagues; and how you prioritize reliability work against feature delivery.

## Technical Interview

**High Priority**

- PHP backend and Symfony fundamentals: request lifecycle, dependency injection, validation, error handling, API boundaries, and maintainability.
- REST API design: versioning, idempotency, authentication, retries, rate limits, and third-party payment integration failure modes.
- PostgreSQL and SQL performance: indexes, query plans, normalization, transactions, locking, and safe schema changes.
- Microservices and production reliability: service boundaries, queues, retries, dead-letter handling, observability, and operational ownership.
- Kubernetes and delivery: deployments, configuration, health probes, rollout safety, Helm, CI/CD, and incident diagnosis.

**Medium Priority**

- SOLID, GRASP, and common design patterns with examples from supported PHP/backend work.
- Event-driven systems and asynchronous processing, clearly distinguishing this from claiming CQRS or Event Sourcing expertise.
- Testing strategy: unit, integration, contract, and environment setup; be explicit about which named libraries you have and have not used.
- Payment systems: gateway integrations, idempotency, reconciliation concepts, monitoring, and security-sensitive data handling.

**Low Priority / Gap Validation**

- Doctrine ORM, Jenkins, Docker Swarm, Codeception/Behat, DDD Bounded Contexts, CQRS, and Event Sourcing. Prepare honest definitions and transferable experience, but do not present them as production experience without evidence.

## CV Deep-Dive Questions

- What was your personal scope in the airSlate database and API performance work?
- Which Symfony components and architectural boundaries did you work with?
- How did you measure or observe the result of the Kubernetes migration?
- What failure modes did the Simple.life message-delivery pipeline handle?
- How did the PDFfiller service behave during 10x BFCM traffic growth?
- What design decisions made the transactional email system reliable at 50M messages/month?
- What did “prototype to closed beta in under six months” involve at Hyprr?
- Which payment gateway integrations did you build in earlier work, and what responsibilities did you own?
- How do you distinguish a microservice boundary from a module or queue consumer?
- Which timeline applies to the CRURATED and Simple.life overlap? Confirm before the interview.

## Company-Specific Preparation

- Review WhiteTech’s modular fintech platform, PSP and payment-orchestration pages, and the official job posting.
- Be ready to connect the role’s provider integrations, monitoring, reporting, reconciliation, and production support to your API, messaging, reliability, and payment-related experience.
- Review the company’s public claims about 50+ modules, 500+ integrations, and 24/7 production support; treat these as company-published facts, not assumptions about the team’s internal implementation.
- Ask which parts of the role are new product development versus support and modernization, and which advanced architecture patterns are actually used.

## Preparation Plan

**Must prepare:**

- A two-minute introduction focused on PHP/Symfony, APIs, PostgreSQL, Kubernetes, reliability, and fintech-related systems.
- Two STAR stories: airSlate performance/Kubernetes delivery and PDFfiller scale/reliability.
- A truthful DDD/CQRS/Event Sourcing answer that separates direct evidence from adjacent experience.
- A salary expectation, notice period, and confirmation of the Simple.life/CRURATED dates.

**Before the technical interview:**

- Rehearse PostgreSQL query-plan and indexing explanations, REST idempotency, payment integration failure handling, and Kubernetes rollout troubleshooting.
- Refresh Symfony dependency injection, service boundaries, validation, and testing strategy.

**Before the final/culture interview:**

- Prepare why a fintech platform role is attractive without claiming product use.
- Prepare examples of architecture communication, cross-functional collaboration, and production ownership.

## Questions to Ask

1. Which parts of the platform would this role own during the first six months?
2. How much of the work is new development, modernization, and production support?
3. Which Symfony and PHP versions are currently in production?
4. How are Doctrine, testing libraries, CI/CD, and Jenkins used in the team today?
5. Which DDD, CQRS, or Event Sourcing patterns are genuinely in use, and what depth is expected from this role?
6. How are payment-provider integrations isolated, tested, monitored, and reconciled?
7. What are the main PostgreSQL performance or scalability challenges on the platform?
8. How does the team handle incidents and on-call or production-support responsibilities?
9. How is success measured for the first 90 days and first year?
10. What are the contract model, salary range, and practical expectations around CET working hours?
