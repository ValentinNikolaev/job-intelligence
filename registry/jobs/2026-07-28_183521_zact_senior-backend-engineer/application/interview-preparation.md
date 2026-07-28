## Recruiter / HR Screening

- Give a concise overview: 15+ years in backend engineering, recent Go/PHP platform work, APIs, event-driven systems, production reliability, and technical leadership.
- Be direct that Java/Spring is not in the supplied CV evidence. Explain the adjacent experience—REST APIs, SQL databases, messaging, Kubernetes, operational troubleshooting—without presenting it as Java experience.
- Confirm remote availability around European time zones. Clarify Italy/EU work authorization, sponsorship needs, notice period, earliest start date, and salary expectations before final interviews; these are open candidate questions.
- Expect “Why change roles?” and “Why Zact?” Answer with supported interest in hands-on backend ownership, reliable integrations, and fintech operations; do not invent product familiarity.

## Culture Fit / Behavioral Interview

Prepare STAR stories from real CV evidence for:

1. A production incident or reliability issue: Simple.life delivery pipelines with fallbacks, retries, and monitoring.
2. Improving a high-load system: airSlate database-load reduction and API/query performance work.
3. Making an architectural decision: CRURATED’s versioned events and multi-downstream routing.
4. Working across functions: Simple.life collaboration with support, product, and AI teams.
5. Mentoring or raising quality: airSlate planning/interviews or PDFfiller team leadership.
6. Handling peak demand: PDFfiller BFCM traffic growth.
7. Delivering quickly under ambiguity: Hyprr’s prototype-to-closed-beta work.
8. Disagreeing constructively on technical direction: use a specific, factual instance only if the candidate can supply it.

## Technical Interview

| Topic | Priority | Why |
| --- | --- | --- |
| Java 8+, Spring Boot, Spring Security, Spring Data JPA | High | Core stated stack and the largest evidence gap. Study honestly; do not represent study as production experience. |
| REST API design and API security | High | Direct responsibility; review versioning, error handling, authentication, authorization, and auditability. |
| OAuth 2.0, JWT, RBAC | High | Explicit requirement; be ready to explain concepts and distinguish them from documented experience. |
| SQL, PostgreSQL/MySQL, transactions and performance | High | Strong candidate evidence and likely fintech relevance. |
| Enterprise integrations, Apache Camel, ETL patterns | High | Named preferred area; map conceptually to documented event routing and integrations, then state missing tool experience. |
| Distributed systems, queues, idempotency, retries, backpressure | High | Strong CRURATED/Simple.life overlap and likely payments relevance. |
| Kubernetes and container operations | Medium | Supported experience, but Docker is not explicitly evidenced. |
| Kafka/RabbitMQ | Medium | RabbitMQ is supported; Kafka is not. Explain message-broker principles without claiming Kafka use. |
| JUnit/Mockito and testing strategy | Medium | Required tools are unsupported; review unit/integration testing fundamentals and state the gap. |
| Algorithms/coding exercises | Medium | Senior backend screens may include them; practice clean Java solutions if pursuing the role. |

## CV Deep-Dive Questions

- How did the Simple.life platform coordinate Zendesk, Intercom, and internal services?
- What delivery failures did fallback logic and retries address, and how was success monitored?
- How did CRURATED’s event schema and routing handle new event types and downstream consumers?
- What changes reduced airSlate’s database load and API response times?
- What did the ECS-to-Kubernetes transition require across Helm, GitHub Actions, and ArgoCD?
- How did you lead technical decisions and mentor engineers at Hyprr and PDFfiller?
- How should the overlapping Simple.life and CRURATED timeline be explained accurately?

## Company-Specific Preparation

Read Zact’s job page and prepare a concise explanation of why dependable APIs, reconciliation-oriented integrations, and secure access control matter in an expense/payment-management product. Verify current team, legal hiring location, and application route before interviewing. Do not imply knowledge beyond the public posting.

## Preparation Plan

**Must prepare:** an honest Java/Spring gap statement; API-security concepts; OAuth 2.0/JWT/RBAC; a concise experience narrative; Italy/EU work authorization, availability, and salary answers.  
**Pre-technical:** refresh SQL transactions and query-performance examples; review Java/Spring fundamentals; rehearse design of a reliable payment/integration API with retries, idempotency, authorization, audit trails, and monitoring.  
**Pre-final/culture:** prepare the eight behavioral stories above, an accurate explanation of overlapping work dates, and questions about the team’s engineering and remote practices.

## Questions to Ask

1. Which Java and Spring components are most central to the services this role will own?
2. How strict is the requirement for prior production Java/Spring versus senior experience in comparable backend stacks?
3. Which integrations and reconciliation flows create the highest operational risk today?
4. How are API authorization, auditability, and security reviews handled?
5. What are the main data stores and message brokers in production?
6. How does the team test integrations and protect releases?
7. What would success in the first 90 days look like?
8. How do the US, Europe, and India teams collaborate across time zones?
9. Is Italy-based remote employment supported for this role?
