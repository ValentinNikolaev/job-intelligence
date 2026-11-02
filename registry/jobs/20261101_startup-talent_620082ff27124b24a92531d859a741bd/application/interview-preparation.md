# Interview Preparation — Startup Talents / unnamed client

## Recruiter / HR Screening

Present the candidate as a senior backend engineer with Go/PHP, production integrations, event systems and technical-lead responsibility. Ask for the client’s name and whether the vacancy remains live before treating the package as ready for submission. The source describes a crypto financial-management product, but no specific brand is verified. Confirm the hiring entity, employment arrangement for Italy, compensation currency, benefit eligibility and timezone expectations. The advertised range is employer information, not a candidate acceptance. Current availability and exact work-authorisation wording need confirmation.

Resolve the Go/Python balance early. The evidence establishes Go engineering and does not establish production Python or every listed database. Ask which skills are immediate requirements and which can be learned with the team. Explain CRURATED as a parallel part-time consulting assignment and Simple.life as completed employment. Keep the current CV’s end-year rendering separate from a claim of later employment; a supported September project milestone does not extend the employment period. Do not use a dated availability response as current.

## Culture Fit / Behavioral Interview

- Describe taking backend architecture into production. Use the telephony platform, your design ownership, security review and collaboration with frontend and SRE.
- Tell us about a service boundary you chose. Use the vendor-neutral Go gateway and why adapters and a shared event model were useful; separate supported facts from retrospective opinion.
- Describe full technical ownership in a consulting engagement. Use CRURATED’s production event analytics or external integration, without claiming sole code authorship.
- Tell us about simplifying a system. Use the unified analytics-to-support delivery engine and the removed operating restriction, rather than leading with code-size statistics.
- Describe coordinating a release. Use airSlate planning and production-delivery responsibilities and identify the decisions you influenced versus made independently.
- How would you approach a required technology you have not used professionally? Discuss an explicit learning and verification plan; do not invent a past Python project.
- Tell us about startup delivery. Hyprr’s progression from prototype to closed beta is supported; avoid adding adoption, funding or revenue claims.

Prepare STAR outlines with the real contribution and consequence; unknown metrics or commercial outcomes can remain unknown.

## Technical Interview

High Priority: Go, concurrency, context cancellation, error handling, data structures and testable service design. Practise a bounded worker pipeline with cancellation, backpressure and a failing dependency. Explain what happens when shutdown overlaps an external request. Discuss the design before naming libraries. Distinguish a code exercise from previous production ownership, and show which assumptions you would confirm before choosing a persistence or queue strategy.

High Priority: event processing and data correctness. Rehearse idempotency, duplicates, ordering, schema versions and retry boundaries using the gateway and CRURATED evidence. A hypothetical portfolio system may ingest late or repeated exchange events. Explain how you would preserve source identity, event time, correction history and uncertainty about an external operation. This is system-design preparation, not a claim that you built this client’s product. Be careful with exactly-once language and describe where deduplication or reconciliation would actually occur.

High Priority: databases, bottlenecks and observability. PostgreSQL, MySQL and Prometheus have evidence; MongoDB, Cassandra and Sentry do not. Be ready to explain relational indexes, query plans, transactions, contention and how workload redistribution improved airSlate service stability. Ask which access patterns drive the NoSQL choices. For unfamiliar stores, describe a learning plan rather than claiming operational expertise.

High Priority as a fit check: Python usage and container responsibilities. Clarify whether Python is for core services, ingestion, scripts or data work. The user has confirmed practical Docker use in the current conversation, but no employer-specific Docker outcome is inferred from it. Kubernetes and AWS should be discussed within supported scope. Never reuse the withdrawn airSlate migration. Medium Priority: financial-data consistency, wallet/exchange integrations and permission boundaries. Prepare questions about whether the product is read-only, executes transactions or handles custody, because the anonymised description does not settle those risks.

Medium Priority: blockchain concepts and the Hyprr digital-asset work. Explain what the candidate actually built around Ethereum components. Do not claim smart-contract audits, active dApp usage or conference participation. Low Priority: ClickHouse, TimescaleDB and detailed time-series tuning until the client confirms they matter to the role. Those are bonus or adjacent topics, not justification for unsupported CV keywords.

## CV Deep-Dive Questions

For each recent bullet, identify the personal contribution, system boundary and actual consequence. For the gateway, explain tenancy, event contracts and the demonstrated product use. For telephony, distinguish architecture ownership from independent security approval and discuss privacy controls at a useful level. For GDPR workflows, explain creation, status and deletion cancellation without exposing internal identifiers. For the evaluation pipeline, describe how conversation, action and subscription state were assembled and what remained outside your work.

For CRURATED, explain the production status of DataLake, parallel event versions and the account/collection integration. For airSlate, prepare the database bottleneck and CI/CD changes; use qualitative outcomes unless the confirmed measurement context is clear. For Hyprr, explain backend development and the CTO roadmap without enlarging your authority. Older dated headings preserve chronology and do not need invented achievements to fill a discussion.

## Company-Specific Preparation

[Startup Talents’ official site](https://www.startuptalents.tech/) verifies recruitment context, while the recorded posting describes the anonymous product. Treat recruiter and client as different organisations. Ask for an official client product or careers page before preparing company-specific motivation. Do not identify the business by matching a generic crypto-portfolio description to a familiar brand. The direct posting was unavailable during this pass, so the interview process and application fields remain unknown.

## Preparation Plan

Must prepare: concise backend introduction, the client-identity question, Go/Python boundary, current logistics and one production architecture example. Before a technical stage, practise Go failure handling, database analysis, event-version evolution and a hypothetical ingestion design. Study the actual required unfamiliar tools after the recruiter clarifies scope. Before a final discussion, clarify shared decisions and production responsibility. Keep delivered work, proposals and personal ownership distinct.

## Questions to Ask

- Who is the client and where is the official vacancy?
- What is the actual Go/Python split?
- Which databases require immediate operational experience?
- Does the product read data, execute trades or handle custody?
- How are exchange failures and corrected historical data handled?
- What responsibility continues after a service reaches production?
- Which employment arrangements are available from Italy?
- How are the assessment and first deliverable defined?
