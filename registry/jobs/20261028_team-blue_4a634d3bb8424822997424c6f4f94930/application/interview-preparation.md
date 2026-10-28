# Interview preparation — team.blue, PHP (Symfony) Software Engineer

## Recruiter / HR Screening

Explain the fit through PHP backend delivery, production event systems and the narrower Symfony experience shown in the CV. The role's Platforms PHP team works on hosting automation and internal APIs. Its extensive-Symfony requirement is a screening risk: the airSlate logger is verified, but years of Symfony-led product work are not. State precisely what you built and for how long.

Simple.life was a Go-focused role ending in August 2026; CRURATED was concurrent part-time PHP consulting ending in January 2026. Do not transfer PHP delivery to Simple.life. The role is remote and lists Florence, while the candidate is Rome-based. Confirm Rome eligibility, meeting frequency and language expectations.

Before form answers, confirm Italian work right, sponsorship category, gross salary, start, notice, PHP and Symfony tenure, and location choice. The employer cannot sponsor visas or relocation. Do not guess the permit category.

## Culture Fit / Behavioral Interview

Build STAR outlines from firsthand memory, covering contribution, decision, outcome and learning without invented metrics.

- When did you own a production system? Use CRURATED's DataLake and event analytics work.
- How did you change an event model? Use parallel event versions and the versioned schema.
- Which cross-service integration did you deliver? Use CRURATED's account-linking and purchase-verification work.
- When did you address a bottleneck? Use airSlate's peak-load work; distinguish team leadership from personal implementation.
- How did you improve delivery? Use airSlate's CI/CD work and release consistency.
- How did you collaborate across teams? Use the Go gateway, distinguishing backend from product decisions.
- How did you handle privacy? Use the security-reviewed calling platform and server-side phone-data design.
- How do you learn a new tool? Propose a method for hosting tools without claiming Ansible or API Platform experience.

## Technical Interview

**High priority — PHP and Symfony depth.** Review the Symfony components actually used: dependency injection, configuration, controllers, testing and package design. The airSlate logger is evidenced, but its adoption is unverified. Explain your contribution and limits. Do not attribute Symfony to CRURATED without source support.

Prepare a small code-review exercise around a Symfony service that calls a slow hosting API. Look for timeout handling, dependency boundaries, error propagation and tests that cover failed provisioning. Describe what you would change and why, then distinguish those proposals from the airSlate work actually in the record.

**High priority — API and architecture.** Design an idempotent hosting-provisioning API with state transitions, retries and partial-failure recovery. Cover validation, permissions, versioning and observability. Ground transferable choices in real integrations while labelling hosting design hypothetical.

**High priority — SQL and data changes.** Review transactions, indexes, query plans, migrations and locking. Explain airSlate's database work, measurement and team contribution. Avoid the withdrawn ECS migration and unsupported cost claims.

**Medium priority — infrastructure and delivery.** Review Linux, containers, deployment, health checks and rollback. Distinguish verified AWS/Kubernetes/CI-CD experience from unverified Ansible or GitLab depth. **Medium — AI-assisted coding:** explain review and testing. **Low — hosting products:** learn Managed WordPress and WooCommerce basics without claiming prior hosting work.

## CV Deep-Dive Questions

Separate recent PHP consulting at CRURATED from Go systems at Simple.life and explain the part-time overlap. For Symfony depth, describe the airSlate logger and only other work you can substantiate. CRURATED's DataLake and analytics work ran in production under technical ownership and supported reporting; do not invent adoption or revenue. AirSlate database and API results were team-led with Prometheus measurement. The calling platform shows privacy architecture, not PHP delivery.

## Company-Specific Preparation

Reread the [official role](https://careers.team.blue/jobs/8585325-php-symfony-software-engineer) before interview. It concerns internal APIs and automation for a European cloud and hosting platform. Prepare a question about shared contracts and ownership. Do not claim product use. Recheck the live form before answering it.

## Preparation Plan

**Must prepare now:** confirm work authorisation and sponsorship wording, Florence/Rome remote eligibility, salary, start date, notice period and the precise Symfony history. Prepare one sentence on why the hosting-platform role is interesting without claiming prior product use. Check the candidate's current CV dates and the concurrent consulting label.

**Before the technical round:** rehearse a PHP/Symfony implementation walkthrough, the production CRURATED event system and one API design exercise. Practise a SQL query-plan investigation and explain how you would deploy a change with rollback and observability. Mark unverified tools as learning areas, not résumé claims.

Write down the exact Symfony packages, versions and duration you can defend from firsthand experience. The application asks for this explicitly; a vague framework label will not answer it. If the honest answer is narrower than the employer expects, address that directly and show the adjacent PHP, API and production ownership evidence.

**Before the final or culture round:** turn the behavioral prompts into brief candidate-verified stories. Ask about team boundaries, service ownership, support rotation and the amount of hands-on PHP work. Decide whether the actual work model and Symfony depth make the role a good fit.

## Questions to Ask

- Which services does the Platforms PHP team own directly, and which are shared with infrastructure or product teams?
- What portion of the work is Symfony feature development versus platform integration or legacy maintenance?
- Which Symfony components and versions matter most in the current codebase?
- How are internal API contracts reviewed and rolled out across brands?
- What does a successful first production contribution look like in this role?
- How are hosting automation changes tested before they affect customer environments?
- How do engineers diagnose and resolve an incident that spans PHP services and infrastructure?
- How much design authority does an engineer have from requirement analysis through implementation?
- Is Rome-based remote work accepted under the Florence listing, and when does the team meet on-site?
