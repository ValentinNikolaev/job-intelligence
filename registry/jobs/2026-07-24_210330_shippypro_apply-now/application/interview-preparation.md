## Recruiter / HR Screening

- **Why this role?** Connect your PHP/Laravel background, high-volume backend work, integrations, automation, and reliability experience to ShippyPro's shipping platform. Do not claim prior logistics experience.
- **Why change now?** Give the factual current-status answer after confirming whether the primary CV's March 2026 end date remains correct. Avoid an answer that conflicts with LinkedIn's Present entry.
- **Location and remote work:** Confirm that you are based in Rome, Italy and can meet any occasional HQ-travel requirement before committing.
- **Salary:** The advertised EUR42,000-EUR56,000 range requires your decision. State a range only after considering employment type, benefits, and total compensation.
- **Notice period:** Confirm your availability before the call; the records do not supply it.
- **English:** Describe your working English level as supported by the primary CV: Upper-intermediate. Prepare examples of technical collaboration in English.
- **Timeline question:** Explain the Simple.life date accurately. Prepare a factual response for the overlapping CRURATED entry on LinkedIn; do not improvise or remove it during an interview.

## Culture Fit / Behavioral Interview

Prepare these as STAR stories using only the evidence named below.

1. Tell me about a system you owned end to end. Use the Simple.life support-automation platform connecting Zendesk, Intercom, and internal services.
2. Tell me about a production reliability problem. Use the message-delivery pipelines with retries, fallback logic, and monitoring.
3. Describe a hard performance problem. Use airSlate database-load reduction or API and query bottleneck work.
4. Describe a migration with operational risk. Use the ECS-to-Kubernetes migration with Helm, GitHub Actions, and ArgoCD.
5. How have you made a technical trade-off? Use a specific decision from the PDFfiller email service or Hyprr architecture only after you can describe the details accurately.
6. Tell me about leading engineers. Use the five-person PDFfiller team and explain scope, technical decisions, and BFCM preparation.
7. Describe work with product or non-engineering partners. Use Simple.life support-team automation or Hyprr work with the CTO.
8. Tell me about a failure or incident. Use an actual message-delivery or production-support example; state the context, action, and lesson without inventing incident metrics.

## Technical Interview

| Topic | Priority | Why it matters | Prepare |
| --- | --- | --- | --- |
| PHP and Laravel architecture | High | The role requires deep Laravel expertise. | Service boundaries, dependency injection, queues, testing, error handling, database access, and upgrade trade-offs. |
| Asynchronous workflows and messaging | High | ShippyPro cites distributed services and RabbitMQ. | Delivery semantics, idempotency, retries, backoff, dead-letter handling, ordering, and observability. |
| System design | High | The product handles carrier and e-commerce integrations at scale. | Design a shipment-label or tracking-update workflow with APIs, queues, state transitions, failure recovery, and monitoring. |
| Integration design | High | Carrier, ERP, WMS, OMS, and e-commerce integrations form the product core. | Webhook verification, API versioning, rate limits, retries, mapping, auditability, and partner failures. |
| Database design and performance | High | MySQL appears in the stack and the CV makes performance claims. | Indexing, query plans, contention, migrations, caching concepts, and safe changes under load. |
| Reliability and operations | High | The role owns performance and reliability. | SLIs/SLOs, structured logs, metrics, alerting, incident response, capacity planning, and rollback strategy. |
| AWS and delivery infrastructure | Medium | AWS, Docker, ECS, Lambda, and GitHub Actions appear in the vacancy. | Your supported ECS, Kubernetes, Docker, GitHub Actions, Helm, and ArgoCD experience; identify Lambda gaps openly. |
| AI workflow integration | Medium | The role includes AI and LLM workflow automation. | Explain the Simple.life triage result, evaluation, guardrails, fallback paths, and human review at the level you can support. |
| Node.js and Python | Low | The posting lists both, but candidate evidence does not. | State that your direct evidence is PHP and Go; discuss how you learn and contribute across service boundaries without claiming production experience. |
| Frontend | Low | React and TypeScript appear in the stack but the role centers backend work. | Do not claim experience. Be ready to discuss API contracts with frontend teams. |

## CV Deep-Dive Questions

- How did the PDFfiller service reach about 50 million messages per month, and which bottlenecks did the team address?
- What responsibilities did you hold while leading five backend engineers during BFCM traffic growth?
- Which database bottlenecks did you remove at airSlate, and how did you validate the improvement?
- How did the ECS-to-Kubernetes migration change deployment, rollback, monitoring, or cost decisions?
- How did your support-automation platform model tickets, routing, and external-system failures?
- How did the LLM-powered triage system reach the reported up-to-30% automated or deflected ticket result? Be precise about your own contribution.
- Which reliability signals did you use for message-delivery pipelines, and what happened when a downstream system failed?
- Why do the primary CV and LinkedIn show different Simple.life dates, and what is the accurate current status?

## Company-Specific Preparation

- Review [ShippyPro's platform overview](https://www.shippypro.com/en/) and map its shipping labels, tracking, returns, carrier choice, and automation features to the systems-design topics above.
- Study how a carrier API integration can fail: rate limits, duplicate requests, delayed callbacks, address validation, label reprints, tracking-event ordering, and provider outages.
- Prepare a short view of the trade-offs between synchronous API calls and queue-backed processing for shipment creation and notification flows.
- Note the public claim of 190+ carriers and more than 100 million shipments per year as context, not as internal architecture evidence.
- Do not claim knowledge of ShippyPro's internal AI implementation, service topology, or engineering process.

## Preparation Plan

**Must prepare:** Confirm current employment status, notice period, salary position, and the CRURATED overlap. Rehearse two-minute explanations for the Simple.life automation platform, airSlate performance work, and PDFfiller scale.

**Pre-technical:** Practice a Laravel service-design discussion, a RabbitMQ delivery-failure scenario, and a MySQL performance diagnosis. Draw a shipment-processing flow with idempotency, retries, and observability.

**Pre-final/culture:** Prepare concise STAR stories on ownership, incident response, migration, leadership, and collaboration. Re-read the CV so each metric and technology claim has a defensible example.

## Questions to Ask

1. Which backend problems would the new engineer own in the first three to six months?
2. How do teams divide ownership across Laravel services, integrations, and shared platform components?
3. Which carrier or e-commerce integration failures create the most operational risk today?
4. How do engineers define and monitor reliability for shipment creation, tracking, and notifications?
5. How does the team use RabbitMQ, EventBridge, and other asynchronous systems today?
6. What does the practical assessment evaluate: Laravel implementation, system design, debugging, or product trade-offs?
7. How do Product, Design, and Engineering collaborate before a backend workflow reaches production?
8. How does the team evaluate AI or automation features before they affect merchant workflows?
9. What are the expectations for remote work, on-call work, and occasional HQ meetings?
10. What distinguishes strong performance for this role after the first year?
