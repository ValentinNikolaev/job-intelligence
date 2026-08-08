# Interview Preparation

## Recruiter / HR Screening

Prepare concise answers for:

- Why a PHP product-maintenance role is relevant after recent Go work: connect it to the candidate's long PHP background and preference for production ownership.
- Exact Yii2 duration, versions, and recency: state only the prior documented exposure and do not imply four years unless independently verified.
- PHP version experience: separate general PHP depth from any exact PHP 8.2+ production work that is not in the source records.
- Rome-to-Kyiv remote arrangement, timezone overlap, legal engagement model, and occasional office expectations.
- English working level and ability to read technical documentation.
- Salary expectations, notice period, and availability; these are not in the source material and need candidate-provided answers.
- Reason for leaving the latest role and the correct end date, because source records conflict.

## Culture Fit / Behavioral Interview

Likely questions and grounded STAR sources:

1. Tell us about a difficult existing codebase you had to understand quickly — use airSlate performance investigations.
2. Describe a production incident you diagnosed — use logs, monitoring, and SRE dashboards at airSlate.
3. Give an example of improving a database under load — use the main-database workload reduction.
4. Tell us about integrating an external service — use Zendesk/Intercom orchestration at Simple.life.
5. How do you balance speed and code quality — use CI/CD improvements and release ownership.
6. Describe a time you led technical work — use the five-person PDFfiller team or airSlate delivery planning.
7. How do you review unfamiliar code safely — discuss profiling, tests, logs, and incremental changes without inventing a specific incident.
8. Tell us about a peak-load period — use the 10x BFCM traffic experience.

## Technical Interview

- **High priority — PHP and Yii2:** dependency injection, request lifecycle, Active Record trade-offs, migrations, validation, service boundaries, backward-compatible changes. Be exact about what was used personally.
- **High priority — MySQL:** indexes, composite-index order, `EXPLAIN`, transactions, isolation, locking, slow-query diagnosis, pagination, and safe schema changes.
- **High priority — existing-code work:** characterization tests, refactoring seams, observability, rollback, and reviewing side effects before changing behavior.
- **High priority — REST and integrations:** authentication, idempotency, retries, timeouts, rate limits, webhooks, and failure handling.
- **Medium priority — testing:** unit versus integration tests, database fixtures, contract tests, and preventing regressions.
- **Medium priority — frontend basics:** browser requests, HTML/CSS/Bootstrap, JavaScript event handling, Ajax, and safe backend/frontend contracts. Do not claim Node.js depth.
- **Medium priority — delivery:** Git workflows, CI/CD, containers, release checks, and production monitoring. Distinguish supported Kubernetes work from unverified Docker specifics.
- **Low priority — greenfield system design:** useful, but this vacancy is more likely to test practical work in an existing product.

## CV Deep-Dive Questions

- How was the database workload reduction measured, and what changes caused it?
- What Laravel/Symfony services did you own at airSlate?
- What failure and retry behavior did the Simple.life integrations use?
- What did “around 50 million emails per month” require from MySQL, queues, and operations?
- Which Yii2 projects did you work on, for how long, and which parts did you own?
- Why are both software-developer and technical-lead responsibilities shown at airSlate?
- Confirm the latest employment end date before the interview.

## Company-Specific Preparation

Review the service flow on the [official iPOST site](https://ipost.ua/about-us.html): customer order, courier assignment, real-time tracking, API-connected business client, and peak-load behavior. Prepare questions about the current Yii2 version, the split between backend and frontend work, database scale, release process, test coverage, and how remote engineers collaborate with the Kyiv team.

Do not assume the public courier platform and the engineering codebase have the same architecture. Treat that architecture as unknown until the team explains it.

## Preparation Plan

**Must prepare:** exact Yii2 history; PHP-version history; one MySQL optimization story; one external-integration failure story; current location and engagement constraints.

**Before the technical interview:** refresh Yii2 internals, MySQL indexing/transactions, REST failure modes, and testing a legacy PHP application. Rehearse a structured walkthrough of the airSlate database work.

**Before final/culture rounds:** confirm the product's current engineering priorities, explain motivation without disparaging Go work, and prepare examples of ownership, team support, and careful production changes.

## Questions to Ask

1. Is four years of Yii2 an absolute screen, and which Yii2 version is in production?
2. How is work divided between backend and frontend responsibilities?
3. What are the largest MySQL performance or data-consistency challenges today?
4. What automated test coverage protects the existing codebase?
5. How are deployments, rollbacks, and production incidents handled?
6. Which external services and APIs are most important to the product?
7. What does success in the first three months look like?
8. How does the remote team collaborate with colleagues in Kyiv?
