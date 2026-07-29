## Recruiter / HR Screening

- Motivation: position the role around PHP platform stability, production debugging, payment-adjacent systems, and gradual modernization.
- Location: candidate is based in Rome/Fiumicino, Italy. Confirm whether this role accepts candidates outside the U.S. or LATAM.
- Working model: public sources describe remote work, but mirrors differ on geography. Ask about timezone overlap and employment/contract arrangement.
- Language: English is upper-intermediate/professional working proficiency in the source records. Prepare examples of technical written communication.
- Rust: state clearly that production Rust is not evidenced yet. Frame it as a ramp-up area backed by Go, backend systems, testing, and migration experience.
- Notice/current status: reconcile Simple.life and CRURATED timelines before recruiter calls.
- Salary: prepare a range for senior PHP/backend remote work and a separate expectation if the role is U.S.-market contract.

## Culture Fit / Behavioral Interview

Likely behavioral questions:

1. Tell us about a long-lived backend system you improved without disrupting users.
2. Describe a production debugging case involving APIs, queries, or database load.
3. How do you approach migration work when the existing platform still handles critical traffic?
4. Tell us about a time you improved release discipline or CI/CD.
5. How do you work with a legacy codebase when documentation is incomplete?
6. Describe a time you balanced technical debt with product delivery.
7. How do you ramp up on a new language such as Rust?
8. Tell us about a high-pressure production reliability issue.
9. How do you communicate risks during a payment or financial workflow change?

STAR stories to prepare:

- airSlate PHP/MySQL performance work: API/query bottlenecks, database load reduction, logs, monitoring, and production fixes.
- airSlate ECS-to-Kubernetes migration: service migration, Helm, GitHub Actions, ArgoCD, CI/CD, cost and performance improvements from LinkedIn evidence.
- Simple.life Zendesk-to-Intercom migration: critical workflow migration, routing speed, consistency, and operational responsiveness.
- CRURATED event analytics infrastructure: delivery guarantees, Webhook/S3 routing, backpressure, retries, observability, and 99.9% reliability.
- Older CoinsBank payment integrations: Stripe, PayPal, Skrill, exchange-core work, real-time notifications, and performance profiling. Use as older context, not recent CV experience.

## Technical Interview

**High Priority - PHP backend maintenance.** Review Laravel, Symfony, service boundaries, dependency management, logging, error handling, test strategy, and refactoring in long-lived codebases.

**High Priority - MySQL and relational debugging.** Prepare examples around indexes, query plans, slow queries, locks, transactions, load reduction, and safe schema changes.

**High Priority - Production troubleshooting.** Prepare a debugging workflow: reproduce, inspect logs/metrics, isolate service versus database symptoms, mitigate, patch, monitor, and document.

**High Priority - Migration strategy.** Practice explaining how to migrate from PHP to Rust incrementally: identify bounded contexts, add contract tests, create adapters, preserve interfaces, dual-run critical paths, measure behavior, and roll back safely.

**Medium Priority - Rust ramp-up.** Study Rust basics before interviews: ownership, borrowing, lifetimes, Result/Option, error handling, async runtime concepts, crates, cargo, testing, and FFI/API boundary considerations.

**Medium Priority - Payments and financial workflows.** Review idempotency keys, retries, reconciliation, settlement, audit logs, transaction state machines, duplicate prevention, and failure handling.

**Medium Priority - Unix/Linux.** Prepare practical examples of log inspection, process/service checks, file permissions, networking basics, shell tooling, and deployment troubleshooting.

**Medium Priority - CI/CD and releases.** Prepare airSlate examples around GitHub Actions, Helm, ArgoCD, release consistency, and deployment safety.

**Low Priority - Frontend/product UI.** The role is backend-focused; discuss frontend only if asked about cross-functional work.

## CV Deep-Dive Questions

- Which PHP services did you build or maintain at airSlate?
- How did the Laravel/Symfony logging package work?
- How did you identify and fix API or query bottlenecks?
- What caused the main database load reduction?
- What production dashboards or logs did you use for troubleshooting?
- How did the Zendesk-to-Intercom migration avoid disrupting support workflows?
- What did backpressure mean in the CRURATED event pipeline?
- What payment systems did you work with before 2016, and how current is that knowledge?
- Have you written production Rust?
- How would you start migrating a PHP payment workflow to Rust safely?

## Company-Specific Preparation

- Read South Geeks' site and LinkedIn profile to understand the nearshore/client-partner model.
- Review the Ashby posting and job mirrors before applying because the local Jooble text is truncated.
- Prepare questions that distinguish South Geeks employment terms from the client's day-to-day engineering expectations.
- Study payment platform migration risks: idempotency, data consistency, auditability, compliance-adjacent logging, rollback, and release windows.
- Prepare a clear Rust-learning plan: one small service, tests first, code review with Rust engineers, then production-adjacent tasks before ownership.

## Preparation Plan

**Must prepare before recruiter screen:** location eligibility, contract/employment setup, timezone overlap, Rust honesty, payment-platform experience framing, and salary range.

**Before technical interview:** practice a system design for migrating a PHP payment authorization or reconciliation workflow to Rust while keeping the PHP system live.

**Before final/culture interview:** prepare stories around legacy modernization, production responsibility, debugging under pressure, client communication, and incremental delivery.

## Questions to Ask

1. Is this role open to Italy-based candidates, or is U.S./LATAM residency required?
2. How much production Rust is expected on day one?
3. Which parts of the PHP payment platform are first candidates for Rust migration?
4. What is the current test coverage around payment workflows?
5. How do releases work, and what rollback options exist?
6. What production incidents or bottlenecks pushed the migration decision?
7. How are payment workflow correctness and auditability validated?
8. What observability stack does the team use?
9. Will I work as part of a South Geeks team or directly embedded with the client team?
10. What would success look like after the first 90 days?
