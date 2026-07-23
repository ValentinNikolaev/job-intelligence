## Recruiter / HR Screening

- **Why this role?** Ground the answer in senior backend work for a consumer financial platform and the candidate’s experience with reliable, user-facing integrations; do not claim a personal connection to Satispay.
- **Location and working model:** The listing is in Provincia di Milano; candidate sources list Rome/Fiumicino. Clarify actual willingness and availability before the screen rather than implying relocation or remote eligibility.
- **Current status and dates:** Explain the Simple.life CV date (ending March 2026) versus the LinkedIn “Present” entry truthfully, including the overlapping CRURATED engagement if applicable. Update the public profile once the correct explanation is confirmed.
- **Salary and notice period:** Prepare truthful expectations; neither source provides them.
- **Language:** Be prepared to discuss English communication. Sources list upper-intermediate/professional-working English; do not overstate Italian or other language ability.
- **Job change:** Focus on seeking a senior backend role where ownership of reliable consumer-facing systems, integrations, and product collaboration is useful.

## Culture Fit / Behavioral Interview

Prepare concise STAR stories from documented experience. Do not invent the Situation, Task, Action, or Result; use the source records to refresh specifics.

1. Describe owning the Go support-automation platform at Simple.life.
2. Describe integrating or migrating critical flows from Zendesk to Intercom.
3. Describe a reliability incident or peak-load challenge involving fallback logic, retries, or monitoring.
4. Describe designing CRURATED’s versioned event schema and gaining cross-team consistency.
5. Describe managing downstream routing, backpressure, or delivery guarantees in event analytics.
6. Describe reducing database pressure or API latency at airSlate.
7. Describe a Kubernetes migration and the deployment/CI/CD choices involved.
8. Describe collaborating with product, support operations, or engineering leadership.
9. Describe technical-roadmap work with the CTO at Hyprr.
10. Describe leading a team through a high-volume BFCM period at PDFfiller.

## Technical Interview

- **High priority — Go backend design:** be ready to describe service boundaries, API orchestration, error handling, retries, idempotency, and testing around the Simple.life platform.
- **High priority — event-driven architecture:** defend event schemas, versioning, queues/EventBridge, downstream routing, delivery guarantees, retry behavior, backpressure, and observability from CRURATED.
- **High priority — reliability and operations:** prepare examples of monitoring, logging, production troubleshooting, incident resilience, and trade-offs between availability, consistency, and operational cost.
- **High priority — system design:** practice designing a user-facing backend integration with scale, failure modes, data flow, metrics, and rollout/rollback plans. Tie principles to documented work, not Satispay’s unknown stack.
- **Medium priority — databases/performance:** explain airSlate database-load reduction, API/query investigation, indexing/query reasoning where factual, and how performance is measured.
- **Medium priority — cloud and delivery:** review AWS, Kubernetes, Helm, GitHub Actions, and ArgoCD experience, including ECS-to-Kubernetes migration decisions.
- **Medium priority — consumer financial domain:** review the candidate’s payment-gateway integrations and PCI DSS-related work at Sixt, while distinguishing them from direct Satispay domain experience.
- **Medium priority — coding:** rehearse idiomatic Go and PHP problem solving, API design, concurrency/error handling concepts, and data-structure fundamentals. The exact language is unknown.
- **Low priority — company-specific stack:** do not guess frameworks, languages, or tooling not present in the truncated vacancy.

## CV Deep-Dive Questions

- What was the architecture of the Go support-automation platform and what did “owned” mean in practice?
- How was the 30% automation/deflection figure measured?
- What changed operationally during the Zendesk-to-Intercom migration?
- How did the CRURATED event schema evolve without breaking downstream consumers?
- What mechanism provided delivery reliability above 99.9%, and over what measurement period?
- What were the key causes of database load at airSlate and how were they addressed?
- What did the ECS-to-Kubernetes migration require across deployment, observability, and release operations?
- How did you lead five engineers and prepare for BFCM traffic at PDFfiller?
- How do you reconcile the Simple.life and CRURATED dates in the CV and LinkedIn source records?

## Company-Specific Preparation

Review Satispay’s public description of its payment app and consumer financial services, including payments, money exchange, savings, and investments, and its stated focus on user impact. [Product overview](https://www.satispay.com/en-it/) Review its recent public expansion into welfare and other services. [Company newsroom](https://www.satispay.com/it-it/newsroom/satispay-be-comics-be-games-festival-padova/)

Prepare questions about Consumer Growth’s customer outcomes, service ownership, backend architecture, team interfaces, reliability targets, experimentation practices, and working model. Do not assume these details from public material.

## Preparation Plan

**Must prepare:** location/availability decision; truthful chronology explanation; Go platform architecture; CRURATED event system; two reliability stories; and an outcome-focused answer about user-facing backend work.

**Before technical interview:** rehearse an end-to-end event-driven system design, an API integration failure-mode discussion, database/performance troubleshooting, and Kubernetes/CI/CD fundamentals.

**Before final/culture stage:** connect documented ownership, cross-functional collaboration, and technical-lead experience to Satispay’s stated user-impact focus; ask for clarity on the Consumer Growth mandate and ways of working.

## Questions to Ask

1. What user or business outcomes does the Consumer Growth team own?
2. Which backend services and integrations would this role be responsible for in the first six months?
3. How does the team define and observe reliability for user-facing flows?
4. What are the main technical challenges as the consumer platform expands?
5. How are product, data, and engineering partners involved in prioritizing work?
6. What approach does the team use for safe rollouts, experimentation, and incident learning?
7. Which languages, platforms, and observability tools are most important in the current backend stack?
8. How is technical ownership balanced with team collaboration and review?
9. What does success look like after 90 days?
10. What is the expected working model for a role listed in Provincia di Milano?
