## Recruiter / HR Screening

- **Why this role?** Focus on the documented overlap: PHP, Go, APIs, microservices, payment-provider integrations, and dependable services. Do not claim a personal connection to Nord Security’s mission beyond the cover letter’s factual relevance.
- **Why a change?** Give only the candidate’s truthful current reason; the source record does not supply one, so prepare a concise personal answer rather than inventing it here.
- **Location and working model:** The role is listed remote in Poland while the candidate record lists Fiumicino, Italy. Confirm work authorization, residence, travel, and remote-location feasibility directly with the recruiter.
- **Salary and notice period:** These are not in the candidate record. Prepare truthful current expectations and availability.
- **Language:** English evidence conflicts between Professional Working and Full Professional. State the level accurately and be prepared to demonstrate it in the interview.
- **Payments relevance:** Describe the CoinsBank/bit-x work precisely: exchange-core features involving fiat money and integrations with Stripe, PayPal, and Skrill.

## Culture Fit / Behavioral Interview

Prepare 5–10 concise STAR stories using only documented experiences:

1. Leading a 10-engineer Hyprr team from prototype to closed beta in under six months.
2. Coordinating delivery planning and assignments at airSlate, including a documented 20% feature-delivery increase.
3. Coaching and interviewing engineers at airSlate and PDFfiller.com.
4. Handling Black Friday/Cyber Monday traffic at PDFfiller.com, where traffic exceeded normal volume by more than 10x.
5. Migrating services from ECS to Kubernetes at airSlate.
6. Improving message-delivery resilience at Simple App with fallback logic, retries, and monitoring.
7. Working with Product, Support Operations, and AI teams at Simple App.
8. Designing event analytics infrastructure and a versioned event schema at CRURATED.

Likely questions: Describe a difficult stakeholder alignment; a production incident; a technical decision you owned; feedback or mentoring you provided; a mistake and learning; how you work independently; and how you prioritize reliability against delivery speed. Nord Security publicly presents values of self-movers, team players, future shapers, and restless achievers; connect answers to factual examples, not slogans.

## Technical Interview

### High Priority

- **PHP and OOP/code design:** explain supported Laravel/Symfony work, PHP frameworks (Mezzio/Phalcon), logger-package design, testability, and trade-offs.
- **Go backend services:** be ready to discuss the Simple App Go platform, API orchestration, retries, monitoring, and the boundaries of services you own.
- **Payment integrations:** explain provider integration design, failure handling, idempotency considerations, callback/webhook validation, reconciliation concepts, and security considerations as technical reasoning. Distinguish general design knowledge from the documented Stripe/PayPal/Skrill implementation details.
- **Microservices and APIs:** prepare service boundaries, versioning, backward compatibility, error handling, observability, and performance examples.
- **Databases:** discuss documented PostgreSQL, schema/database normalization, query optimization, and production workload reduction. Be explicit that MySQL-specific experience is not documented.
- **Reliability under load:** cover retries, backpressure, delivery guarantees, monitoring, and the PDFfiller.com and Simple App scale examples.

### Medium Priority

- **Kubernetes and delivery:** explain the ECS-to-Kubernetes work, Helm, GitHub Actions, and ArgoCD from airSlate.
- **Event-driven architecture:** discuss queues/AWS EventBridge, versioned schemas, downstream routing, and operational visibility from CRURATED.
- **Security:** discuss PCI DSS/GDPR-related work at Sixt as documented. Do not present this as cybersecurity-product experience.
- **System design:** sketch a payment-service integration with clear APIs, state transitions, failure modes, observability, and operational ownership.

### Low Priority

- **RabbitMQ, Redis/KeyDB, Debezium, OpenSearch/Elasticsearch:** the vacancy lists these, but the candidate record does not support direct experience. Review concepts before the interview and state the gap candidly.

## CV Deep-Dive Questions

- How did the Simple App platform integrate Zendesk, Intercom, and internal services, and what did you personally own?
- What concrete design decisions enabled the documented reduction in incident-related disruptions?
- How did the CRURATED event schema and routing handle multiple downstreams and backpressure?
- What was your role in the airSlate ECS-to-Kubernetes migration and ArgoCD setup?
- What did the CoinsBank/bit-x payment-provider integrations involve, and how were failures handled?
- How did you lead the PDFfiller.com service through high-traffic BFCM periods?
- Explain the overlapping Simple App and CRURATED dates accurately.
- Explain the broad Upwork freelance period with a specific, truthful example relevant to backend or payments work.

## Company-Specific Preparation

- Review Nord Security’s public product portfolio and mission around security, privacy, and user control: [Nord Security](https://nordsecurity.com/).
- Review the published careers values and prepare factual examples that show initiative, collaboration, learning, and problem solving: [Careers](https://nordsecurity.com/careers).
- Read the role again and map each responsibility to one supported example, especially API/service design, provider integrations, standards, QA/DevOps/security collaboration, and mentoring.
- Prepare questions to clarify the payments domain, compliance expectations, provider landscape, production ownership, and the Poland-based remote policy.

## Preparation Plan

**Must prepare:** PHP/OOP, Go service ownership, API and microservice design, payment-provider integrations, database optimization, and candid MySQL/queue/cache-tool positioning.

**Before a technical interview:** rehearse a payment-integration system design; review idempotency, retries, reconciliation, observability, and failure handling; prepare an accurate Kubernetes/ArgoCD explanation and two production reliability stories.

**Before a final/culture interview:** prepare STAR examples for initiative, mentorship, cross-functional work, a difficult delivery, and high-load operations. Confirm practical questions about location, compensation, notice period, and working arrangement.

## Questions to Ask

1. Which payment methods and provider-integration patterns are most important for this team in the next six to twelve months?
2. How are payment services divided into ownership boundaries, and how does the team manage cross-service changes?
3. What are the most important reliability, latency, or correctness concerns for the Payments infrastructure?
4. How does the team approach idempotency, reconciliation, and incident response for provider-facing workflows?
5. Which parts of the listed stack are most actively used by this team today?
6. What would success look like for this role after the first 90 days?
7. How do Backend, QA, DevOps, and security teams collaborate on releases and operational issues?
8. What mentorship or technical-guidance expectations come with this mid–senior position?
9. What is the practical remote-work arrangement for someone currently based in Italy for a Poland-listed role?
10. What are the next stages of the interview process and the technical areas each stage will assess?
