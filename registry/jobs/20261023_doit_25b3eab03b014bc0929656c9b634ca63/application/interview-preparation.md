## Recruiter / HR Screening

Prepare a brief introduction centred on Go services, API integration and production responsibility. Explain that this is a backend-focused application to a role with substantial frontend scope. Do not present React or TypeScript as a strength without additional direct evidence. The retained match score is 73, but it is an internal analysis result and does not belong in a recruiter pitch.

Clarify Italy-based eligibility first. The posting names specific employee countries and allows contractors in Eastern Europe and Portugal. Rome is not explicitly covered. Ask which contract or employment arrangement could apply without assuming EU residence settles the issue. Work authorization, sponsorship, notice period and salary expectations remain unconfirmed in the general profile. Do not reuse a notice answer given for another employer. Give a current answer before submission.

## Culture Fit / Behavioral Interview

Prepare six real stories around these questions. Use the source-backed situation and personal contribution, then explain the result without inventing a conflict, decision or measurement.

- When did you turn unclear integration needs into a workable service boundary? Use the multi-tenant gateway, distinguishing technical design from customer discovery.
- How did you protect users during a production change? Use Snowflake consolidation and its no-downtime outcome.
- How did you handle security input before launch? Use the outbound telephony design and sign-off.
- When did you choose a fallback rather than an immediate replacement? Use the categorization comparison and retained earlier model.
- How have you helped others deliver? Use airSlate backend-lead coordination and team feature delivery.
- When did you make a technical direction decision jointly? Use the Hyprr roadmap with the CTO, preserving the shared authority.

Prepare concise STAR outlines. Where the source does not explain disagreement, alternatives or lessons, supply a truthful recollection rather than a rehearsed invention.

## Technical Interview

**High Priority — Go and API design.** Practise defining an ingestion service with a clear domain model, provider adapters, validation and APIs. Explain tenant isolation and how retries avoid duplicate effects. Discuss concurrency, cancellation, resource limits and failure handling in Go. These are likely interview topics, not claims that every mechanism appeared in the gateway.

**High Priority — data correctness.** Design a small provider-usage ingestion flow. Consider late data, corrections, duplicate records, currency and time boundaries, and changing provider schemas. Ask what the product treats as authoritative. Discuss how to expose incomplete or stale data so a customer does not mistake a pipeline delay for lower spending. Keep illustrative design choices conditional.

**High Priority — production change.** Explain how the Snowflake pipelines were consolidated and how service continuity was preserved. Be ready to separate mechanisms actually used from safeguards proposed for a new system. Prepare to explain rollback and verification without inventing an automated parity framework.

**High Priority — frontend gap.** Review the expected React/TypeScript workflow and be ready for a practical assessment. Do not promise immediate independent interface ownership based on backend work or collaboration with a frontend engineer.

**Medium Priority — cloud and SQL.** Review AWS operating decisions, SQL aggregation and query costs. Snowflake pipeline experience is supported. BigQuery and GCP proficiency are not established. Learn their vocabulary for the interview while keeping learning separate from past experience.

**Medium Priority — AI-assisted engineering.** Bring factual examples of coding-tool use, review practices and failures if available. Building LLM applications is a different claim. Explain where human checks remain necessary.

**Low Priority — unrelated language breadth.** The role names Go and TypeScript. Additional languages matter only when they support a concrete system question.

## CV Deep-Dive Questions

The gateway enabled a demo of the support-AI product. Be ready to explain which contracts and adapters you personally designed, what the demo demonstrated, and which later adoption outcomes are unknown. Do not convert a demo into a customer rollout.

For the Snowflake change, describe the previous repeated reads, the consolidation decision and the source-backed continuity outcome. Do not lead with code-size or test-count statistics. For telephony, explain your architecture and security responsibilities without exposing internal identifiers or detailed customer-data mechanics.

For CRURATED, explain production DataLake ownership, schema consistency and faster stream integration. Preserve the concurrent consulting arrangement. For airSlate, distinguish database stability, API responsiveness, delivery-cycle improvements and team delivery as separate results. Be explicit that leadership contribution does not mean sole implementation.

## Company-Specific Preparation

Read the supplied posting alongside the [official GenAI Intelligence documentation](https://help.doit.com/docs/dashboards/genai). The verified product problem is combining AI cost and usage data across providers and allocating it to projects and teams. This preparation already captured the primary source, so another broad research pass is unnecessary.

Prepare a reason for applying that connects this task with hands-on backend ownership. Avoid claiming prior DoiT use or FinOps expertise. Be able to explain the difference between building a reliable data service and knowing whether a cost allocation helps a customer make a decision. The latter requires domain learning and user context.

## Preparation Plan

**Must prepare before recruiter contact:** confirm location, authorization, notice and salary wording. Decide how to describe frontend depth plainly. Build a short introduction and choose the six source-backed behavioral outlines above.

**Before the technical interview:** draw the gateway and pipeline boundaries, practise a Go ingestion exercise, and prepare a data-correctness design discussion. Review SQL and the unfamiliar cloud vocabulary without adding it to the CV. Gather truthful AI-coding examples if the candidate can provide them.

**Before a final or culture interview:** clarify how the team discovers customer problems, defines feature success and shares responsibility after release. Rehearse discussing a real limit without either hiding it or dismissing relevant strengths.

## Questions to Ask

1. Can DoiT engage someone based in Italy for this role?
2. How much independent React/TypeScript delivery is expected immediately?
3. Which analytical store and SQL tasks dominate the backend work?
4. How do engineers learn from FinOps practitioners using the product?
5. How are incomplete provider data and retrospective corrections represented?
6. What does ownership after release include for this team?
7. How do you assess useful AI-assisted engineering rather than tool usage alone?
