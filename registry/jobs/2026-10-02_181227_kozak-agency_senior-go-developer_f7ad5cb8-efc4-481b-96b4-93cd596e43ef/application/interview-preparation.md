# Kozak Agency — Senior Go Developer Interview Preparation

## Recruiter / HR Screening

Prepare a two-minute introduction that starts with recent Go backend ownership at Simple.life, then explains the parallel PHP consulting work at CRURATED as a separate, part-time engagement. Explain the appeal of a hands-on Senior Go role: production services, API decisions, and accountability after release. Ask who owns the product, how the team is organized, and how the engineer works with stakeholders.

Confirm the working model. The vacancy metadata says remote from European countries or Ukraine and the candidate is in Rome. Check exact core hours, any travel, contract entity, and Italy work-authorization language before making commitments. The posting says English B2–C1; the candidate records say upper-intermediate or professional working, so demonstrate technical discussion in English rather than asserting a certified CEFR level. Prepare an honest rate range and earliest start date; neither is confirmed in the current candidate profile. If asked why the CV selects roles rather than listing every job, explain that airSlate employment from 2021–2023 is real and can be discussed, while this version foregrounds stronger Go and production-architecture evidence.

## Culture Fit / Behavioral Interview

Prepare concise STAR outlines from real candidate work, not memorized invented answers. Likely questions include:

1. Describe a service you owned from design through operation. Use the Simple.life Go support platform; define personal ownership and the teams using it.
2. When did you choose a fallback rather than a full replacement? Use the categorization A/B comparison and retained in-house model.
3. Tell us about a technical decision that protected downstream users. Use CRURATED parallel event-version publication; distinguish the decision from unverified business outcomes.
4. How did you handle a reliability problem? Use the CRURATED event pipeline's verified delivery result, or a Simple.life integration issue only if its specific outcome can be explained.
5. Describe collaboration with non-engineers. Use support operations and product alignment around ticket routing or automation.
6. What did you do when a metric represented a team or platform result? Explain that the Simple.life 86% automated-handling figure was platform-wide and that you implemented many, not all, scenarios.
7. How have you reviewed a design you did not originally create? Prepare a concrete source-backed example and identify the decision you influenced.
8. What trade-off did you make under peak load? Use PDFfiller's BFCM capacity leadership only within the confirmed about-three-million ordinary monthly volume and up-to-tenfold peak scope.

For each story, separate personal contribution from team output and name the observed result.

## Technical Interview

**High priority — Go service design and ownership.** Walk through a production Go service boundary: API shape, context cancellation, timeouts, retries, error propagation, observability, and deployment. Anchor the discussion in the Simple.life platform. Do not claim a specific Go framework unless asked and directly supported.

**High priority — API and integration design.** Explain the unified API orchestration layer, source-of-truth choices, idempotency, partial failures, and backward compatibility. The posting explicitly asks for designing new APIs and maintaining production services. For a system-design exercise, sketch a support event or ticket-routing service; label any illustrative design as a proposed answer, not as a description of what was shipped.

**High priority — reliability, performance, and testing.** Discuss what would be measured first, how to reproduce a production symptom, and how to verify a fix. CRURATED provides confirmed throughput and delivery-reliability outcomes, while Simple.life supplies operational integration context. Prepare to talk about Go unit and integration tests, race checks, code review, and release safety as technical approaches; do not imply every approach appears in the candidate's past work.

**Medium priority — data and event systems.** Review PostgreSQL query design, transactions, queue delivery, schema evolution, and observability. The CV lists PostgreSQL and the CRURATED work shows event versioning and delivery; exact database isolation-level claims should be supported with a personal example before stated as experience. Explain how a schema change can be staged without silently widening the production claim.

**Medium priority — infrastructure.** Review AWS, Kubernetes, CI/CD, monitoring, and technical decisions. Identify what you personally configured versus what another team owned.

**Low priority — unnamed technologies.** Do not treat tools named in another Agency listing as requirements here.

## CV Deep-Dive Questions

Expect a question on how the Go platform connected Zendesk, Intercom, and internal services, and what part of the API orchestration layer you personally owned. Prepare the production use case and an example of a failure boundary. For the standalone support-agent service, explain the automated conversation-closure workflow without implying ownership of all LLM scenarios. For the 86% platform-wide figure, state its scope and the internal Intercom and backend-to-Grafana measurement basis; avoid the retracted 20,000-ticket claim.

For CRURATED, explain transferable architecture judgment and the measurement basis for more-than-10x throughput and above-99.9% delivery. For PDFfiller, separate team leadership and traffic scale from any unverified uptime result. Account for airSlate and Simple.life chronology if asked.

## Company-Specific Preparation

Kozak Agency's [official site](https://kozak-ag.com/) describes backend delivery from discovery through production monitoring; its [services page](https://kozak-ag.com/services) lists Go microservices. Revisit the selected [posting](https://djinni.co/jobs/851405-senior-go-developer/). Connect hands-on Go ownership to that delivery model while asking what this particular client actually uses.

## Preparation Plan

**Must prepare:** a crisp Go platform story, a qualified 86% explanation, the CRURATED architecture example, English discussion of an API decision, and exact availability/rate/work-authorization answers once the candidate confirms them. **Before technical round:** rehearse an API/system-design sketch, one diagnostic path, a safe testing plan, and a code-review example. **Before final or culture round:** connect the candidate's desire to remain hands-on with Kozak's end-to-end delivery model, and ask about project ownership, client access, and decision rights. Keep unconfirmed details as questions rather than filling them with plausible assumptions.

## Questions to Ask

1. What product and end client does this selected Senior Go vacancy serve?
2. Which Go services would I own first, and what are their current reliability or delivery challenges?
3. How are API design decisions reviewed, documented, and introduced to existing clients?
4. What tests and release checks currently protect the Go services?
5. Which observability signals matter most to the team after a release?
6. How much direct contact would I have with product stakeholders and the client team?
7. What are the expected overlap hours for someone working from Italy?
8. How do you define success for this role during its first three months?
9. What is the contract model, rate range, and expected duration for this particular project?
