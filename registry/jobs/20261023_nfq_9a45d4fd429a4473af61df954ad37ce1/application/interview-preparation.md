# NFQ / HomeToGo interview preparation

## Recruiter / HR Screening

Prepare a short introduction centred on hands-on PHP and Go backend work, production integrations and technical leadership. State that the target is a senior engineering role with responsibility for design and delivery, rather than assume a management position. Explain why the Checkout remit is relevant without claiming travel-industry experience. The published role combines customer-facing workflows with ownership through production, which is a concrete discussion point.

Confirm the location arrangement first. The candidate lives in Rome, while the posting refers to teams in Poland and Lithuania. Ask whether Italy residence is compatible with employment or contracting and what office attendance is expected. Do not infer work authorisation, sponsorship needs, notice period, start date or salary expectations. The posting offers permanent and business-contract options, but the candidate's acceptable terms remain unconfirmed. Prepare a compensation answer only after choosing a defensible range.

Explain CRURATED as concurrent part-time consulting. Use the completed Simple App role and its conservative end-year chronology consistently. Prepare an honest explanation of the transition after that role without inventing a reason for departure. English is supported at upper-intermediate level, and should be demonstrated through a clear technical walkthrough.

## Culture Fit / Behavioral Interview

Prepare concise STAR notes for these seven likely questions. Fill missing situation, alternatives and outcomes from recollection before interviewing.

- When did you take responsibility for a feature beyond its initial implementation? Use the calling platform's design, security review and production release.
- How did you keep an integration change manageable? Use the gateway's vendor boundary and API contracts.
- How did you handle evolving contracts across teams? Use production parallel event-version publication at CRURATED.
- How did you decide what to simplify? Use duplicated data pipelines and the supported consequence of removing full-history reads.
- How did you work with business or operational stakeholders? Use actual support-platform collaboration, distinguishing agreed requirements from personal product authority.
- How did you improve team delivery? Use airSlate's engineering metrics and planning-to-production work, distinguishing team outcomes from sole implementation.
- What would you do differently after delivering an AI feature? Use a real support-agent example and identify an actual learning before claiming one.

Avoid supplying a fictional disagreement, failure or coaching success merely because the question asks for one. The employment letter supports mentoring, onboarding and technical interviewing, but the precise stories must come from actual memory.

## Technical Interview

**High Priority — PHP and Symfony.** Expect code structure, dependency injection, services, validation, database access and testing questions. Refresh with a small practical exercise and explain design choices plainly. General Symfony knowledge is supported, but deep recent Symfony work is not established. Do not borrow details from an excluded older employer to fill that gap.

**High Priority — APIs and integration design.** Practise contract evolution, idempotency, retries, timeouts, error classification and observability. Use the gateway for boundaries and the Crutrade integration for concrete production scope. Distinguish an implemented mechanism from a reasonable design you would propose today.

**High Priority — databases and performance.** Be ready to interpret a query plan, discuss indexes, transactions, contention and workload redistribution. Explain how the airSlate team observed bottlenecks and checked results. Prometheus measurement is supported, but a missing baseline or query example should be acknowledged rather than reconstructed.

**High Priority — architecture and system design.** Sketch a booking-related workflow as a hypothetical design. Identify states, dependencies, failure recovery and the boundary between checkout and later customer operations. Ask for constraints before choosing synchronous or asynchronous communication.

**Medium Priority — coding.** Practise a small PHP service or API exercise with readable tests. Prefer an explicit contract and clear failure behaviour over pattern-heavy abstractions. Discuss trade-offs as choices for the exercise, not historical achievements.

**Medium Priority — infrastructure.** Review AWS, Kubernetes, RabbitMQ and SQS operating concepts. The gateway specifically supports SQS usage. Explain delivery guarantees and visibility into failures without claiming every named tool was used in the same system.

**Medium Priority — LLM engineering.** Prepare actions, evaluation, escalation and failure handling from the support agent. Keep product AI experience separate from unconfirmed personal coding-agent workflows. **Low Priority — travel-specific vocabulary:** learn the basic booking lifecycle, while asking the team about its actual domain model.

## CV Deep-Dive Questions

Defend the gateway's precise personal contribution and why a vendor-neutral model mattered. Explain what the business-demo result does and does not establish. For the calling platform, identify which architecture and security decisions were personally owned and how the production release was coordinated. Avoid turning the cross-functional team into a line-management claim.

For CRURATED, distinguish analytics ownership, schema design, version publication and the Crutrade integration. Explain the boundaries of production responsibility and downstream ownership. For airSlate, separate database stability, API response times, release pipelines and team feature-delivery rate. These are distinct claims, and each needs its own account. The CV intentionally avoids numerical achievements, so do not add a percentage during interview unless its scope and basis can be defended.

## Company-Specific Preparation

Reuse the verified research: NFQ is HomeToGo's technology partner, and this role concerns checkout and post-booking. Treat the team arrangement and internal architecture as questions. Explain why ongoing ownership of customer-facing backend features interests you, grounded in the configured hands-on role preference. Do not imply that you have used HomeToGo or followed its product history.

## Preparation Plan

**Must prepare:** location eligibility, current PHP/Symfony calibration, an accurate career introduction and gateway evidence. **Before the technical round:** rehearse database diagnosis, event compatibility and a booking-workflow design, then review the actual support-agent implementation. **Before the final or culture round:** prepare real stakeholder, mentoring and delivery examples, compensation expectations and the questions that remain unanswered. Keep a short evidence sheet with contribution, system scope and consequence for every chosen story.

## Questions to Ask

- Can the role support an engineer resident in Italy, and under which contract arrangement?
- What does the Checkout team own after a booking completes?
- Which PHP and Symfony versions and architectural conventions are in active use?
- How are responsibilities divided between this team, architects and product stakeholders?
- What reliability signals guide changes to booking flows?
- Where do external integrations create the most engineering work today?
- What would useful progress look like during the initial period in the team?
