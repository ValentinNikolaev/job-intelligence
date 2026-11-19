# Interview preparation — Sezzle Senior Software Engineer (Turkey)

## Recruiter / HR Screening

Start with the location. The employer's form asks specifically about eligible work authorisation in Turkey and the direct posting says Türkiye, Remote. Explain that the candidate is based in Rome and ask whether this requisition permits work from Italy. Do not equate Italian or EU work permission with Turkish authorisation. Turkish authorisation remains unconfirmed.

For the career introduction, distinguish more than 15 years in software development from the confirmed aggregate five years developing production Go systems. Describe recent work as backend and support automation, not seven years of full-stack work. The employer asks for full-stack duration and React. Prepare an accurate breakdown of frontend projects, contributions and dates if the candidate can substantiate them. Do not assign years from overall tenure.

For motivation, discuss the support-facing gateway and calling platform and ask about the balance between internal and customer-facing work. The source supports an MSc in Computer Science. Verify the undergraduate credential and GPA required by the form.

The job advertises USD 5,000–9,500 gross per month, but a personal expectation must follow the compensation benchmark workflow using the actual team market and employment arrangement. Confirm contract type, notice period and start date. English is professional working / upper-intermediate. Give the candidate’s own reason for leaving.

## Culture Fit / Behavioral Interview

Prepare truthful STAR outlines. These are prompts, not completed answers.

1. **Tell us about a project you took from an idea to production.** Use the Simple.life Amazon Connect calling platform. Explain the authored design, backend ownership, the three-person cross-functional delivery and security sign-off. Identify the actual constraint that mattered most.
2. **Describe a time you worked with a non-engineering stakeholder.** Consider the support platform and its collaboration with Support Ops and Product. Recall an actual request and how it changed the work before claiming a particular negotiation.
3. **Tell us about a technical disagreement.** The sources do not record a particular disagreement. Select a real event and explain the competing options, decision and your response, without inventing consensus.
4. **How have you improved reliability?** Use the support pipeline consolidation or airSlate database work. Separate observed outcomes from proposed design improvements and identify what was measured.
5. **How do you mentor or unblock teammates?** Draw on real leadership work at airSlate or PDFfiller. Prepare an actual example of feedback or help given, rather than assuming a mentoring practice from a title.
6. **Tell us about a difficult privacy decision.** The telephony backend masked customer numbers and kept them out of logs and the agent UI. Explain the security decision and its scope, while leaving legal conclusions to the review process.
7. **Describe delivering under time pressure.** Hyprr reached closed beta in under six months. Prepare the candidate's actual decisions and trade-offs without attributing the entire outcome to one person.

## Technical Interview

**High priority — Go and APIs.** Practise implementing a small HTTP service with context cancellation, validation, error handling and tests. Explain goroutines, channel ownership, cancellation and race prevention. Prepare to walk through the helpdesk gateway's vendor-neutral model, webhook ingestion and SQS queues. State actual delivery guarantees only if they can be defended from the implementation.

**High priority — distributed architecture.** Design a webhook-to-worker flow with duplicate delivery, retries and a downstream outage. Discuss idempotency, acknowledgement, dead-letter handling and monitoring as design options. Compare a transactional outbox with direct queue publishing and identify when atomicity matters. Clarify ordering and replay requirements before choosing a pattern.

**High priority — data and reliability.** Discuss query plans, indexes, transaction boundaries and how to investigate database load. Use the airSlate example to explain what the team changed and what Prometheus showed. For the Snowflake-to-Intercom consolidation, distinguish elimination of repeated reads from any unmeasured cost reduction. Review dashboard signals, alert thresholds and safe rollback.

**Medium priority — infrastructure.** Refresh Kubernetes deployments, resource limits, health checks, AWS IAM and CI/CD. Do not claim the withdrawn airSlate migration. Describe actual ownership boundaries.

**Medium priority — AI and product safety.** Discuss the LLM agent, evaluation data and human escalation. Separate product integration from personal assistant use. Frame new controls as proposals.

**Medium priority — frontend.** Review React state and API calls. Preparation is not evidence of commercial React experience. **Low priority — payments:** learn the product without implying payment-processing ownership.

## CV Deep-Dive Questions

- What did the gateway abstract, what did the vendor adapters retain, and how was the first B2B demo supported?
- How were phone numbers protected in the calling flow and which parts did the candidate own?
- Why consolidate the Snowflake pipelines, and what changed for their readers and operators?
- What did the LLM evaluation pipeline capture and how were production failures investigated?
- What did technical ownership mean for CRURATED's DataLake and parallel event versions? Which components were actually in production?
- What was the candidate's role in the airSlate database improvements and release process?
- Which parts of the Hyprr beta delivery were personally led? How did the team make technology decisions?

## Company-Specific Preparation

The employer describes interest-free instalments and a shopping product, with this role collaborating with Support and Product. Read the job's sequence: Wonderlic, recruiter screen, coding assessment, engineer interview and engineering leadership interview. Confirm whether the coding exercise is live or take-home and which tools are allowed.

## Preparation Plan

**Must prepare:** resolve geographic eligibility, Turkish authorisation, full-stack history, degree/GPA and actual AI-tool usage. Gather a clear account of notice period and preferred contract arrangement. **Before the technical stage:** practise Go coding under a time limit, a queue-based design and a database investigation. Prepare the gateway and telephony examples with ownership and limits. **Before the final stage:** rehearse one collaboration and one leadership story, then prepare questions about team priorities and working arrangements. Keep the salary answer pending a market-specific benchmark.

## Questions to Ask

1. Does this Turkey requisition permit an engineer to work from Rome, and through which employment or contractor arrangement?
2. How much of the team's work is backend Go versus React, and what frontend depth is essential on entry?
3. Which support or customer problem would the new engineer address first?
4. What are the principal reliability and consistency challenges in the event flows?
5. How do Product and Support prioritise work with engineering?
6. What does the coding assessment involve, and which tools are permitted?
7. How do engineers assess and monitor changes to LLM-supported workflows?
8. How is pay determined across the team's actual working locations and contract types?
