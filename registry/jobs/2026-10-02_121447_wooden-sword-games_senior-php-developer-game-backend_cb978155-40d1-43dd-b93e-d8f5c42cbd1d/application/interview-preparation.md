# Interview Preparation

## Recruiter / HR Screening

Prepare a concise motivation statement: this is a PHP-primary backend role where the candidate can bring API, Laravel, production ownership, and event-driven delivery while learning the game runtime honestly. Confirm remote employment mechanics from Rome, overlap hours with Dnipro, contract type, compensation range, notice period, interview language, and whether Ukrainian is expected. Explain the concurrent CRURATED engagement directly: it was a part-time subcontract/consulting assignment from August 2024 to January 2026, alongside Simple.life. Do not describe it as a second full-time role. For job change, say that the candidate is seeking a hands-on PHP backend role with clear product impact and a new live-service domain.

## Culture Fit / Behavioral Interview

Prepare 7 questions and grounded STAR anchors:

1. Describe a time you owned a system under sustained load. Use the Simple.life platform handling at least 20,000 tickets per ordinary month and up to three times more in peak season.
2. Describe a difficult production design decision. Use CRURATED's production event-version publication, focusing on compatibility rather than an invented business result.
3. How do you work across teams? Use the CRURATED integration scope and discuss the concrete backend responsibility, avoiding claims of management.
4. Tell us about an experiment that changed a technical direction. Use the A/B test of in-house categorization and Intercom Fin, then the migration with ML fallback.
5. How do you handle sensitive automation? Use the public-review keyword guardrails and human escalation.
6. Describe a peak-period reliability challenge. Use the PDFfiller service through BFCM traffic up to 10x ordinary volume.
7. How do you approach an unfamiliar domain? Be explicit that Nakama and game-server TypeScript are new, then describe how you begin with contracts, existing tests, deployment safeguards, and targeted questions.

## Technical Interview

**High priority:** PHP/Laravel API design, REST contracts, error handling, validation, migrations, Eloquent, controllers, Artisan commands, SQL query design, PostgreSQL transactions and locking, unit tests, code review, profiling, and cache or queue behavior. The vacancy names these directly. Review current Laravel practices, but do not claim prior use of a named component unless you can explain a real example.

**High priority:** TypeScript typing, async/await, promises, error propagation, race conditions in a single-threaded runtime, and how RPC handlers should be profiled. These are direct role requirements and the main technical gap.

**Medium priority:** Nakama concepts, authoritative versus client state, RPC contracts, storage schemas, idempotency, rate limits, and concurrency around player actions. Prepare as learning material, not past experience.

**Medium priority:** A/B test instrumentation and event contracts. Use the supported Intercom Fin A/B-test story to explain hypothesis, routing, fallback, and safe migration, then ask how game experiments are instrumented.

**Low priority:** push notifications and mobile-client specifics. Know the conceptual boundary but do not imply OneSignal or Firebase implementation experience.

## CV Deep-Dive Questions

Expect close questions on every selected bullet. For the 20,000-ticket platform, explain the candidate's operational ownership and distinguish platform volume from individual feature impact. For up to 86% automation, say that it is a platform-wide result from Intercom and backend metrics and that the candidate implemented many, not all, scenarios. For CRURATED, define technical ownership precisely: production DataLake/event analytics, versioned events, and the listed integration capabilities; do not claim sole authorship, revenue impact, or reliability figures not in the CV. For PDFfiller, explain that ordinary volume was about 3 million emails and BFCM could reach 10x; do not reuse the earlier incorrect 50-million figure.

## Company-Specific Preparation

Read the vacancy again before the interview and prepare questions about the division between Laravel and Nakama. Ask which RPC handlers are hot paths, how public contracts and storage schemas evolve, and what test and review gates protect player-facing changes. The DOU profile says Wooden Sword Games develops mobile games through a full cycle; connect this to an interest in production systems affecting a live product, without claiming personal game experience. The specific RPG title, traffic, player geography, deployment path, and on-call expectations remain unknown.

## Preparation Plan

**Must prepare:** a one-minute explanation of the PHP background, the CRURATED PHP production examples, and the honest TypeScript/Nakama gap. Rehearse the Simple.life load and automation stories with exact attribution. Review Laravel migrations, Eloquent, controllers, Artisan, PostgreSQL transactions, locks, and SQL plans so you can distinguish current knowledge from a documented past project.

**Before technical interview:** build a small TypeScript async example; study Nakama authoritative RPC and storage documentation; practice explaining idempotent handlers, error paths, and tests. Prepare a simple system design for a player inventory update with transaction and concurrency considerations, clearly labelled as an interview exercise rather than prior delivery.

**Before final or culture discussion:** confirm remote logistics, desired collaboration style, how the studio handles code review and learning new domain concepts, and why a full-cycle mobile-game studio is a coherent next step.

## Questions to Ask

1. How is responsibility divided between the Laravel API and Nakama runtime?
2. Which player-facing RPC paths currently need the most profiling or optimization?
3. How do you evolve RPC contracts and storage schemas without breaking live clients?
4. What PostgreSQL transaction and locking problems occur most often in this backend?
5. What unit and integration tests are required before a game-server feature is released?
6. How are A/B tests or feature flags implemented and observed in the live game?
7. What does the first 90 days look like for an engineer ramping up on Nakama?
8. Which production metrics best represent a healthy backend for this game?
9. How are code reviews shared between Laravel and TypeScript contributors?
10. What remote overlap hours and employment arrangement does the team expect?
