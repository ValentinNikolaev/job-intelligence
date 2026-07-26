## Recruiter / HR Screening

- **Why this role?** Focus on the supported preference for a hands-on technical-lead role, backend architecture, reliable systems, product ownership, and mentoring.
- **Why ShippyPro?** Reference the role’s ownership of order management and label generation plus ShippyPro’s shipping automation platform. Do not claim prior logistics expertise.
- **Location and working model:** Rome, Italy; compatible with CET; remote work preferred; willing to visit HQ for meetups.
- **Salary:** The role publishes €52,000–€72,000. State that the upper part of the range depends on the total package, scope, and growth path.
- **Work authorization:** Confirm Italy/EU authorization and sponsorship needs before the call.
- **Notice period and start date:** Confirm before the call; neither source record supplies them.
- **English:** Describe English as professional working / upper-intermediate, consistent with the candidate record.
- **Job change and timeline:** Prepare a concise explanation of Simple.life’s current status and the CRURATED overlap; confirm facts before answering.

## Culture Fit / Behavioral Interview

Prepare STAR stories from verified experience for these likely questions:

1. Tell me about leading engineers through an operationally demanding period. Use the five-engineer PDFfiller team and BFCM traffic growth.
2. Describe a technical decision you made with incomplete information. Use Hyprr’s roadmap and stack work with the CTO.
3. How do you raise the technical bar without becoming a bottleneck? Use supported mentoring, code-review, architecture, and delivery evidence.
4. Tell me about a system reliability issue you improved. Use Simple.life retries, fallback logic, and monitoring.
5. Describe a performance bottleneck you investigated. Use airSlate’s database and API work.
6. Explain a migration that required delivery coordination. Use ECS-to-Kubernetes work at airSlate.
7. How do you balance shipping with architecture? Use the prototype-to-closed-beta experience at Hyprr.
8. How do you collaborate with product or business stakeholders? Use Hyprr planning with the CTO and Simple.life cross-functional work.

Avoid invented people-management methods, logistics knowledge, or claims about target-stack experience.

## Technical Interview

| Topic | Priority | Why |
| --- | --- | --- |
| Backend system design | High | The role owns core fulfillment services and expects architectural judgment. |
| Scalability and reliability | High | The posting stresses high-volume shipment processing; candidate has relevant production evidence. |
| PHP and service architecture | High | PHP is a stated backend language and a strong candidate skill. |
| AWS and cloud-native operations | High | The posting lists AWS ECS/Lambda; candidate can discuss ECS, Kubernetes, Helm, CI/CD, and monitoring. |
| Data modeling and MySQL/PostgreSQL | High | The stack lists MySQL and PostgreSQL; candidate has both. |
| API integration and asynchronous workflows | High | Carrier, order, and label systems depend on integrations; candidate can discuss REST APIs, RabbitMQ, retries, and fallbacks. |
| Team technical leadership | High | The position leads a pod while remaining hands-on. |
| Docker | Medium | It is in the posting but not supported by source evidence; acknowledge the gap and discuss adjacent deployment experience only. |
| NodeJS and Python | Medium | The stack includes both; prepare a frank transferability answer without claiming production use. |
| DynamoDB | Medium | Listed in the stack but unsupported by the candidate record. Review concepts without claiming experience. |
| React, TypeScript, Tailwind | Low | The role’s focus is backend leadership; no candidate evidence supports these tools. |
| Logistics domain | Medium | The product domain matters, but the posting does not require prior logistics experience. Learn order, label, carrier, tracking, and returns flows from public product material. |

Likely deep-dive questions: explain the 50-million-email service’s architecture and failure modes; describe retry and fallback choices for message pipelines; defend the ECS-to-Kubernetes migration; explain database load reduction; describe the 30% ticket-deflection measure; explain how a pod should manage technical debt while shipping.

## CV Deep-Dive Questions

- What was your formal responsibility when leading five backend engineers at PDFfiller?
- How did the email service handle peak traffic and delivery failures?
- What drove the ECS-to-Kubernetes migration and how did you measure its effects?
- How did you identify and remove airSlate database bottlenecks?
- What did you personally own in the Go automation platform?
- How did the Zendesk-to-Intercom migration change routing and operations?
- What did the prototype-to-closed-beta timeline require from you at Hyprr?
- Can you clarify the Simple.life end date and the CRURATED overlap shown in candidate records?

## Company-Specific Preparation

Read ShippyPro’s [about page](https://www.shippypro.com/en/about-us), [careers page](https://www.shippypro.com/en/work-with-us), and the [role posting](https://shippypro.factorialhr.com/job_posting/software-engineering-team-lead-311256). Be ready to discuss how reliable APIs, durable delivery workflows, monitoring, and pragmatic architecture matter for order management, carrier integration, labels, tracking, and returns.

Distinguish verified facts from assumptions. ShippyPro publicly describes multi-carrier shipping automation; do not claim knowledge of the Fulfillment Pod’s internal architecture or incident process.

## Preparation Plan

**Must prepare:** Confirm work authorization, notice period, current employment status, and the CRURATED overlap. Rehearse two leadership STAR stories and two reliability/performance stories grounded in the CV.

**Before the technical interview:** Refresh PHP service design, relational data modeling, API reliability, retries and idempotency, queues, observability, ECS/Kubernetes deployment trade-offs, and order/label lifecycle concepts. Prepare candid answers for NodeJS, Python, Docker, DynamoDB, and logistics gaps.

**Before the final / culture interview:** Prepare examples of mentoring, stakeholder trade-offs, feedback, and making progress amid changing priorities. Tie them to the company’s published emphasis on ownership, learning, and transparent feedback without adopting unsupported slogans.

## Questions to Ask

1. How many engineers are in the Fulfillment Pod, and what roles make up the team?
2. Which outcomes define success for the pod in the first six months?
3. How do order management and label-generation services handle peak periods and carrier failures today?
4. What architecture decisions will the new lead own directly?
5. How much hands-on coding does the role involve in a typical month?
6. How do the COO, Product, Design, and pod make delivery and technical-debt trade-offs?
7. What engineering practices exist for incident review, observability, and reliability work?
8. Which parts of the move toward Python, TypeScript, and cloud-native architecture are active priorities?
9. How does ShippyPro support technical growth and mentoring within engineering?
