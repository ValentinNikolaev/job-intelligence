# PraxisConcierge — Interview Preparation

## Recruiter / HR Screening

Prepare a direct answer for why a hands-on product and integrations role fits a senior backend engineer. Confirm Rome location, CET working hours, remote expectations and any Berlin visits against the employer's actual policy. Confirm notice period and earliest start date from the candidate rather than guessing. A salary answer needs the vacancy-specific compensation benchmark workflow and the team's physical market before a figure is supplied. Most importantly, ask the candidate for an honest German proficiency statement. The ad explicitly requires secure spoken and written German, while the current profile establishes English, Ukrainian and Russian only. Ask whether the employer allows English in engineering and Customer Success collaboration. Have the CV and contact details ready for the Arbeitnow form.

## Culture Fit / Behavioral Interview

Use real stories and keep each answer focused on a decision, contribution and result. Likely questions include: How did you learn what Support needed before building an integration? What happened when an upstream service degraded? How did you decide between a quick workaround and a durable fix? How did you communicate a technical cause to a non-engineer? Describe a privacy concern that changed implementation. Tell us about an ambiguous product request and how you narrowed it. How do you handle feedback after release? What did you do when a migration affected existing customer workflows? Why move from a broader technical-lead background to this role? How do you learn a new language or domain quickly? Build STAR notes from the verified Simple App gateway, Amazon Connect calling controls, Intercom scan repair and GDPR export workflow. The problem and observed result must come from candidate sources. Do not add an invented incident, customer quote or quantified result.

## Technical Interview

**High priority — external integrations.** Explain the Go helpdesk gateway's vendor-neutral event contract, inbound webhook handling, per-tenant queueing and Intercom/Zendesk adapters. Discuss authentication boundaries, webhook replay, error classification, retry caps and idempotency as design questions. Separate practices actually implemented from proposals. A likely whiteboard task is to synchronize appointments or patient status between a PVS and the product while preserving ordering and auditability. Use a hypothetical design and mark it as such.

**High priority — telephony, privacy and consent.** Walk through the Amazon Connect outbound scheduler. The verified source includes calling windows across time zones and holidays, do-not-call checks, queued-callback withdrawal, backend-owned retries, phone masking and recording outcomes in existing Intercom tickets. Be ready to state which controls were implemented and which were operational policy.

**High priority — failure diagnosis.** Reconstruct the Intercom degradation case. Source evidence says the scan had many pages and exceeded its run budget when search slowed. Describe the logs used, the partial-success model, incomplete-scan metric and sharded cursor chains. Avoid quoting counts without a measurement ledger. Explain what would alert the team if a scan remains incomplete for too long.

**Medium priority — data model and operations.** Review relational schema design, indexes for incremental synchronization, transactional outbox alternatives, and how a webhook consumer resumes after a crash. Know the candidate's actual PostgreSQL and MySQL examples. Explain how AWS, SQS, Kubernetes, CI/CD and monitoring were used in sourced work. The job names Git and Linux, so be ready with ordinary development and troubleshooting habits.

**Medium priority — domain standards.** Learn the purposes of PVS, HL7, FHIR and GDT enough to ask precise questions. Review DSGVO data minimization, access logging and deletion workflows. BSI C5 is mentioned in the vacancy, but do not present a certification or audit contribution without evidence.

**Low priority — unrelated AI depth.** The product uses an AI telephone assistant, yet this role emphasizes product features and integrations. Prepare to discuss integration with AI services if asked. Avoid centering the interview on model behavior unless the employer does.

## CV Deep-Dive Questions

Why did the Go gateway put vendor SDKs behind one service? Which contracts were stable and which needed adapter-specific handling? What tenant boundaries were present in storage and queues? What made the first B2B demo possible? For telephony, who authored the backend design and security controls, and what had actually reached production? How were opt-outs reconciled with queued callbacks? For GDPR exports, which systems did the workflow touch and how did administrators track status? In the Snowflake-to-Intercom consolidation, what behavior was preserved and how were retries and throttling tested? Explain why Simple App ended in October 2026, and describe the concurrent part-time CRURATED period clearly. A reviewer may ask why Hyprr, Sixt and PDFfiller are dated headings with no bullets. Explain the deliberate short career presentation rather than improvising new achievements.

## Company-Specific Preparation

Read the current job page and product information shortly before any interview. The stored posting says PraxisConcierge serves German practices through AI telephone assistance and patient communication and connects with more than 50 PVS systems. Treat these as employer statements. Ask which part of the interface estate is most fragile, how Customer Success reports integration defects, and whether practitioners can see synchronization failures. Check whether the role is expected to join client calls in German. Ask which PVS vendors are currently in scope and how API changes are communicated to the integration team.

## Preparation Plan

**Must prepare:** confirm German level, working-language policy, notice period and remote/travel expectations. Prepare two source-grounded STAR stories, one for the helpdesk gateway and one for the telephony platform or degraded Intercom scan. Check the final submitted CV against these stories.

**Before technical interview:** sketch a PVS integration with consent, authentication, idempotent webhook handling, reconciliation and failure recovery. Review REST error handling, relational indexing, SQS queue semantics and privacy-by-design. Distinguish actual prior implementation from a proposed architecture.

**Before final or culture interview:** connect motivation to product feedback and patient-communication reliability. Prepare questions about ownership, Customer Success collaboration, privacy review and engineering standards. Confirm the company's application and interview language.

## Questions to Ask

1. Which PVS integrations create the most support work today?
2. How do Customer Success and engineering decide which integration failures to fix first?
3. What is the expected German level for day-to-day engineering and customer discussions?
4. Which patient data moves through the interfaces, and who owns retention and deletion policy?
5. How do you detect and recover from missed webhooks or partial synchronization?
6. What would success in this role look like after the first three months?
7. Which decisions can the engineer make directly about API contracts and reliability?
8. How do you review privacy and BSI C5-related changes before release?
9. How often does the remote team meet in Berlin?
