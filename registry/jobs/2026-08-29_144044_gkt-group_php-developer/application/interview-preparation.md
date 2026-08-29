## Recruiter / HR Screening

Prepare short, factual answers about location, working model, salary expectations, notice period, language level, and reason for interest. The candidate is based in Rome; the posting is listed in Alba, and the source does not confirm remote or hybrid work. Say that the expected arrangement needs discussion rather than volunteering an unsupported commitment. English is recorded as upper-intermediate / professional working. Do not claim Italian ability. Employment type and salary are unknown, so prepare preferences only from the candidate's own current information.

Explain the timeline clearly: Simple.life ran from November 2023 to July 2026 according to the candidate clarification. CRURATED ran from August 2024 to January 2026 as a concurrent part-time subcontract/consulting engagement, not a second full-time job. A concise explanation is: “Alongside my primary role, I took a defined part-time PHP consulting engagement focused on event analytics infrastructure.” Expect a question about the move from Go-focused recent work to a PHP role; answer with the documented PHP foundation at airSlate, PDFfiller, Hyprr, and CRURATED, and an interest in a role whose stated stack directly uses PHP frameworks and MySQL.

## Culture Fit / Behavioral Interview

Prepare six STAR stories, keeping ownership accurate.

1. **Independent diagnosis:** At airSlate, investigate API and query bottlenecks, identify where database load was concentrated, and describe the resulting operational improvement. Do not claim sole ownership of team outcomes.
2. **Reliability under pressure:** At PDFfiller, explain leading five backend engineers on a transactional-email service during BFCM growth. Focus on technical decisions, communication, and preparation.
3. **Platform ownership:** At Simple.life, describe designing and owning a support-automation platform integrating Zendesk, Intercom, and internal services.
4. **Delivery from ambiguity:** At Hyprr, explain contributing to a product that progressed from prototype to closed beta in under six months, including planning with the CTO.
5. **Cross-team delivery:** At airSlate or Simple.life, describe working with product, support operations, or other engineering teams around a shared system.
6. **Learning a domain:** Use the CRURATED analytics infrastructure story to show how versioned schemas, routing, and observability were introduced without pretending to know GKT's domain.

Likely behavioral questions: How do you solve an unfamiliar production problem? How do you decide when to refactor? How do you handle differing technical opinions? What did you learn from a difficult incident? How do you balance speed and reliability? How do you mentor or review work? How would you clarify a vague client requirement? What attracts you to custom software work? How do you communicate risk? How do you prioritize technical debt?

## Technical Interview

**High Priority — PHP and frameworks.** Review PHP language fundamentals, modern object-oriented design, dependency injection, error handling, logging, testing approach, and safe upgrade considerations. Be ready to discuss Laravel and Symfony only from documented use: airSlate used Laravel/Symfony; PDFfiller and Hyprr used Laravel. Do not claim current GKT version knowledge.

**High Priority — MySQL and performance.** Prepare to reason through slow queries, indexes, query plans, transaction boundaries, schema trade-offs, pagination, locks, caching choices, and diagnosing a database under load. Tie answers to airSlate's supported database and API bottleneck work without adding metrics beyond the source.

**High Priority — APIs and debugging.** Review REST API design, validation, authentication/authorization concepts, idempotency, error responses, backwards compatibility, observability, and incident triage. Explain the factual workflow used at airSlate: logs, monitoring, SRE dashboards, fixes, and operational improvements.

**Medium Priority — architecture and reliability.** Be able to discuss queues, retries, fallback logic, backpressure, delivery guarantees, and versioned events. CRURATED offers the strongest direct example: queue/event routing, downstreams such as webhooks and S3, retries, and observability. Simple.life supports message delivery with fallback logic and monitoring.

**Medium Priority — deployment and operations.** Review the ECS-to-Kubernetes migration, Helm charts, GitHub Actions, ArgoCD, monitoring, and production release discipline from airSlate. Clarify personal contribution accurately: the source says the candidate migrated services and prepared infrastructure for Kubernetes deployments.

**Low Priority — ERP/CRM, mobile, frontend.** These are company-scope terms, not published role requirements. Ask before preparing deeply. If asked, state that the source record establishes backend and web-service experience, not direct ERP/CRM or mobile implementation.

## CV Deep-Dive Questions

Expect detailed questions on the airSlate logger package, API and query bottlenecks, Kubernetes migration, CI/CD, and database load. Prepare a clear distinction between engineering action, team context, and recorded outcome. Expect a scale question on PDFfiller's approximately 50-million-email monthly service: explain transactional email, queues, DNS/DKIM/SPF/DMARC knowledge, team leadership, and peak periods, without revealing confidential implementation details.

For Simple.life, expect questions about Zendesk-to-Intercom migration, retry behavior, monitoring, and ownership boundaries. For CRURATED, prepare why versioned schemas help teams, how routing handles multiple downstreams, and why the engagement was concurrent. For Hyprr, be ready to describe technology planning, backend leadership, and prototype-to-beta work without overstating direct management scope beyond the source.

## Company-Specific Preparation

Re-read the supplied GKT company and vacancy pages. The confirmed facts are its custom web services, tailored software, websites, mobile applications, and ERP/CRM systems; PHP with Laravel or Symfony; MySQL; autonomous problem solving; and an Alba location. Do not rehearse assumptions about customers, products, culture, benefits, remote work, or technical stack. Prepare a concise motivation: the candidate has experience in PHP platforms, APIs, reliability, and product delivery, and wants to understand how that can support tailored software projects.

## Preparation Plan

**Must prepare:** the timeline explanation; two PHP/MySQL stories from airSlate and PDFfiller; one independent troubleshooting story; one architecture/reliability story; and a factual statement of unknown GKT requirements. **Before technical stage:** refresh PHP OOP, Laravel/Symfony patterns, MySQL indexes/query plans, REST design, debugging, queues, retries, Git, and CI/CD concepts. **Before final or culture stage:** prepare location/working-model questions, a collaboration story, and examples of technical decisions communicated to non-specialists. Do not prepare an Italian-language answer unless the candidate confirms it separately.

## Questions to Ask

- Which PHP version and which Laravel or Symfony versions are currently in production?
- What proportion of this role is new custom software, maintenance, and client-specific web services?
- Which projects are most relevant: websites, ERP/CRM systems, or other applications?
- What MySQL scale or performance problems are most urgent?
- How are code review, testing, and release ownership handled?
- Is the expected working arrangement on-site in Alba, hybrid, or remote?
- Are there client-facing or Italian-language requirements?
- What would success in the first three and six months look like?
- How is engineering work coordinated with product, design, or client teams?
- Which opportunities for professional growth are most concrete for this role?
