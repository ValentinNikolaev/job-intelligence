# Interview preparation: Giraffe Software Senior Golang Developer

## Recruiter / HR Screening

Expect a concise account of the candidate's backend career, five aggregate years of production Go, the end of Simple.life work in September 2026 and the concurrent part-time CRURATED engagement. Explain that the overlap was a subcontract, not two undisclosed full-time roles. The source does not establish a reason for leaving or a notice period; prepare truthful current answers rather than inventing one. English is recorded at upper-intermediate level, and the final client meeting is in English, so practise the examples aloud in that language.

The role is remote under a private-entrepreneur arrangement. The candidate has a registered B2B entity, but its jurisdiction and company acceptance are unconfirmed. Ask whether Italy and this entity are eligible. The form requires a USD salary expectation: complete the separate compensation benchmark before entering a figure. Ask about working hours and time-zone overlap.

## Culture Fit / Behavioral Interview

Prepare examples with situation, responsibility, action and consequence. Keep team outcomes distinct from personal work.

1. **Tell us about a design you owned end to end.** Use the telephony backend: explain the security constraints, architecture decisions, review and collaboration with frontend and SRE.
2. **Describe a time you made integration easier.** Use the helpdesk gateway's vendor-neutral model and adapters; explain why separating provider SDKs mattered.
3. **How did you handle a difficult privacy decision?** Discuss the server-side handling and masking of phone numbers and what the approved security controls actually covered.
4. **How do you work with people outside engineering?** Discuss support and product collaboration on the automation platform, with a specific true example ready.
5. **Tell us about simplifying a complex system.** Explain the consolidation of Snowflake-to-Intercom pipelines and the removal of repeated full-history reads without claiming unmeasured savings.
6. **Describe a delivery involving another team or client.** Use the helpdesk gateway and the first B2B demo, distinguishing the candidate's backend work from the wider demo.
7. **How do you prioritise tradeoffs under load?** Discuss the airSlate database reliability work; prepare the actual diagnosis and shared team contribution.
8. **Tell us about a leadership responsibility.** Discuss planning and delivery at airSlate, clearly distinguishing technical lead work from direct implementation.

## Technical Interview

**High priority — Go:** concurrency and goroutine lifecycle, channels versus locks, contexts and cancellation, race detection, interfaces, error propagation, testing and profiling. Practise implementing a bounded worker pool with cancellation and explaining how failures and shutdown are handled. Be explicit about real commercial Go experience and avoid attributing the entire five years to Simple.life.

**High priority — distributed systems and REST:** design a multi-tenant event ingestion API; discuss authentication, tenant isolation, idempotency, ordering, retries, dead-letter handling and eventual consistency. Explain versioning and compatibility for schemas and APIs. Use the gateway as a real example, but distinguish its actual implementation from hypothetical alternatives. Consider how resource assignments avoid concurrent double allocation and how the UI observes changes; the vacancy does not specify an existing design.

**High priority — PostgreSQL:** review transactions and isolation, indexes, EXPLAIN plans, query patterns and concurrency. Prepare a real example of the candidate's own schema or tuning work if available. Explain the airSlate database result without implying it necessarily used PostgreSQL. Review how to enforce allocation constraints safely under simultaneous updates.

**High priority — Redis, React and MongoDB:** the vacancy explicitly asks for them; source evidence is insufficient to claim hands-on use. Review background-job patterns and Redis failure behaviour, React's state and data-flow basics, and MongoDB document models. Separate preparation from production experience and explain transferable concepts honestly. Ask whether frontend work means small integrations or independent feature ownership.

**Medium priority — infrastructure and delivery:** revisit AWS SQS, Lambda, Kubernetes and CI/CD using actual work examples. Discuss backpressure, observability, deployment rollback and access controls. Docker and individual Terraform contributions need confirmation before claiming them. For the telephony platform, rehearse the security sign-off and limited exposure of phone data without claiming every log in the system was covered.

**Medium priority — search and messaging:** Elasticsearch and RabbitMQ appear in the source skill records. Prepare a concrete example if one can be substantiated, including index design or message delivery semantics; otherwise state the limit. Compare SQS and Redis queues on retry and delivery behaviour without claiming identical operational guarantees.

## CV Deep-Dive Questions

- What did the gateway own, and how were tenant boundaries and vendor adapters represented?
- What was the first B2B demo able to show after gateway delivery? Which parts belonged to others?
- Which phone data were masked or withheld, where were controls enforced, and what did the security review cover?
- Why were the Snowflake pipelines consolidated, and how did the change preserve the public interface?
- What specific decisions drove CRURATED's analytics and event routing, and how was production ownership shared?
- What caused the airSlate database peak, and which changes improved stability? What were the boundaries of the candidate's contribution?
- Which CI/CD steps changed and how was the shorter release cycle observed?

## Company-Specific Preparation

Review the [vacancy](https://giraffesoftware.hurma.work/public-vacancies/78): its client is unnamed. Giraffe describes dedicated development on its [website](https://giraffesoftware.com/). Explain how the gateway and analytics experience could transfer to resource allocation, without claiming direct domain experience. Practise in English.

## Preparation Plan

**Must prepare:** confirm actual React, Redis, MongoDB, Docker and AI assistant usage; clarify contracting eligibility from Italy; prepare the separate compensation benchmark. Choose gateway and telephony examples with clear ownership and limits.

**Before the technical interview:** practise Go concurrency and cancellation, a tenant-aware API with reliable background work, PostgreSQL transaction design, and a defensible search or messaging example. Review the project's privacy controls and rehearse tradeoffs without inventing incidents.

**Before the client meeting:** prepare a short English explanation of the resource-allocation design and a specific collaboration story. Ask about the team, decision-making and success measures rather than assuming the client's organisation.

## Questions to Ask

1. How much of the role involves React feature work versus API integration and backend development?
2. How are Redis and MongoDB used, and what depth of prior experience is essential at the start?
3. What are the hardest consistency or scaling problems in resource allocation today?
4. How do the team handle event retries, ordering and duplicate delivery?
5. What are the team's physical working locations and expected time-zone overlap?
6. Can the engagement be performed from Italy through an existing registered B2B entity?
7. How are technical decisions and priorities shared between Giraffe and the client?
8. What would a successful first three months look like?
