# Interview Preparation — KITRUM

## Recruiter / HR Screening

Position the candidate as a Go/PHP backend engineer with technical lead experience and production ownership. Recent Go work covers telephony, helpdesk integration, privacy workflows and an LLM support agent. Describe delivery boundaries before technologies.

Confirm the potential six-month duration, expected weekly workload, contract form and extension possibilities. The role is remote on EU hours and the official location includes Europe, but that does not establish the legal engagement route for an Italy-based candidate. Ask who contracts with the engineer and whether the client imposes a country restriction. Give current notice, start-date and compensation answers only after the candidate confirms them. The application form requires notice and English level. Supported English wording is upper-intermediate.

The five-year requirement concerns backend development, which the chronology supports. Do not describe it as five years of professional Go or invent a continuous Go timeline. Explain that CRURATED was concurrent part-time PHP consulting. Keep Simple App as completed employment and use the latest candidate-confirmed end date. A September project milestone is a project fact, not an employment-date extension.

## Culture Fit / Behavioral Interview

Prepare concrete answers to these questions, separating personal decisions, shared decisions and unknowns:

1. How did you turn the telephony need into an architecture and design document, and who approved its scope?
2. Which privacy decisions were yours, and what changed after security and call-recording review?
3. How did you coordinate backend, frontend and SRE work before production release?
4. What did the vendor-neutral helpdesk model change for the support-AI demonstration, and which boundaries did you choose?
5. How did you agree CRURATED event contracts with other teams and handle changes to them?
6. How did you direct airSlate's backend performance work while crediting the team's implementation?
7. What responsibility did you retain after rollout, and how did operational evidence inform a later change?
8. What actual onboarding or knowledge-sharing example can you explain without inventing a promotion or retention result?

Use the confirmed design, security, launch and demonstration boundaries. airSlate establishes backend direction and team outcomes measured through Prometheus. Do not claim product-strategy authority, sole implementation or an unsupported conflict story. Explain any percentage before using it.

## Technical Interview

**High priority:** Go service design, DDD/domain boundaries, relational data and automated tests. **Medium priority:** CI/CD, cloud operation, event messaging and observability. **Low priority:** unverified optional GraphQL/gRPC, CQRS/BFF and frontend patterns.

For Go, review cancellation, deadlines, concurrency limits, error propagation and service lifecycle in the context of actual delivered services. A useful design exercise is a workflow API with asynchronous work, duplicate requests and a downstream outage. Explain where state lives, how operations become idempotent, what the user sees and how incomplete work is observed. Separate a proposed design from an account of past implementation. Do not claim the source establishes every mechanism in that exercise.

For domain modelling, explain the helpdesk gateway's vendor-neutral events and API contracts. Identify which concepts belonged to the business and which belonged to vendor adapters. Discuss why SDKs were isolated and what the candidate actually delivered. Then map those experiences cautiously to DDD concepts. Formal aggregates, bounded contexts, repositories and ubiquitous language should be explained as technical knowledge unless the candidate can identify their actual use. The CV deliberately does not declare DDD expertise.

For event systems, prepare CRURATED's analytics infrastructure and versioned contracts. Explain the production ownership, how different event types were integrated and how contract consistency helped teams. If discussing parallel versions, describe only the confirmed publication work. Do not invent a zero-downtime consumer migration or incident reduction. The confirmed throughput improvement is scoped to DataLake/event processing, not company revenue or a general availability promise.

For data and operations, connect airSlate's database bottleneck removal and workload redistribution to peak service stability. Explain API measurement and team contribution. Review SQL indexes, query plans, transactions and contention using examples the candidate can defend. Docker and comprehensive unit/integration testing are explicit screens, so prepare concrete hands-on examples and acknowledge any thin area. Kubernetes familiarity does not automatically establish Docker build expertise.

## CV Deep-Dive Questions

Expect: “What did you own in telephony?”, “What changed because of the gateway?”, “Which GDPR flows reached users?”, “What did consolidating pipelines improve?” and “What did you personally build in the LLM agent?” Answer each with problem, contribution, boundary and outcome. Telephony's verified outcome is production launch following security and call-recording reviews. The gateway enabled the support-AI product's first business demonstration. GDPR automation delivered a self-service admin workflow. Consolidation eliminated full-history rereads without changing interfaces or causing downtime.

The LLM agent included tools and evaluation data, but the candidate did not implement all automation scenarios. Do not attribute platform-wide automation rates solely to him. Keep unmeasured onboarding, cost and turnaround estimates out of spoken achievement claims unless clarified. Explain why the CV uses qualitative outcomes instead of reviving the retracted ticket calculation or earlier inflated email-volume number.

## Company-Specific Preparation

The [official role](https://kitrum.com/career/senior-software-engineer-golang/) describes an unnamed Belgian client with a cloud QMS for pharmaceutical, biotechnology and medical technology businesses. It is transitioning toward Go and stresses end-to-end product ownership. Those facts justify interest in service boundaries and controlled change. They do not establish the client's architecture, regulatory standard or validation procedure.

Prepare a direct statement about adjacent experience: privacy-sensitive health-related telephony and GDPR work are relevant, while pharmaceutical QMS validation is a new domain. Ask how engineers learn the business rules and which reviewers approve changes. Explain AI product integration separately from daily AI-assisted coding. The latter is a requirement needing a real workflow example, including how generated code is reviewed and tested.

## Preparation Plan

First, select telephony and the gateway as the principal architecture examples and rehearse clear ownership boundaries. Second, review CRURATED event contracts and one airSlate performance result with its measurement context. Third, practise a short Go/service-design exercise and actual testing examples. Fourth, confirm contract duration, availability, compensation and Italy eligibility. Keep answers conversational and grounded.

## Questions to Ask

Ask which business subdomain the engineer would own, how Product participates in modelling, and how DDD is applied in practice. Ask which services are moving to Go and how correctness is checked across the transition. Clarify release validation, on-call responsibilities, available observability, coding-assistant policy and expectations for mentoring. Finally, ask what successful delivery during the possible six-month engagement looks like and how extension decisions are made.
