# Valentin Nikolaev
PHP Developer | Support Integrations and Production Troubleshooting

Rome, Italy | valeinikolaev@gmail.com | +39 351 370 1194  
LinkedIn: https://linkedin.com/in/valentinnikolaev | GitHub: https://github.com/ValentinNikolaev

## Summary

Senior backend developer with 15+ years in PHP and Go systems. I build support and integration services where privacy, operational visibility and dependable customer contact matter. Recent work includes PII/PHI-protected health-domain telephony, resilient ticket processing, GDPR automation and event-driven PHP delivery for customer-facing production data services across multiple integrations.

## Skills

**Languages and frameworks:** PHP, Laravel, Symfony, Go.  
**Integration and data:** REST APIs, PostgreSQL, MySQL, AWS EventBridge, queues, event-driven systems, Intercom API, Zendesk API.  
**Operations:** logging, monitoring, production troubleshooting, AWS, Kubernetes, CI/CD, SQL performance.

## Experience

### Simple.life / Simple App — Software Developer
November 2023 – 2026

- Owned the health-domain Amazon Connect backend with privacy by design: customer numbers remained server-side, masked in UI and logs, and transient in Connect; formal security and call-recording compliance reviews approved its production release.
- Implemented backend-enforced call windows, holidays, do-not-call rules and opt-out withdrawal, with zero Amazon Connect retries so repeat calls could not bypass customer-contact controls.
- Built least-privilege agent federation through Entra and lazy Connect-user lifecycle management, separating support-call access from diagnostics and administration without individual AWS accounts or SAML.
- Built the multi-tenant helpdesk gateway with Intercom and Zendesk adapters, tenant event ingestion and SQS queues, enabling the first B2B support-AI demonstration.
- Made Intercom ticket processing observable during API degradation through partial-success handling and sharded cursor searches.
- Built self-service GDPR exports across seven sources, centralizing request creation, tracking and review for administrators.

**Technologies:** Go, PHP, PostgreSQL, Intercom API, Zendesk API, SQS, REST APIs, monitoring

### CRURATED — PHP Software Developer, concurrent part-time consulting engagement
August 2024 – January 2026

- Delivered a production partner integration for authentication and OTP, account linking, collection exchange, purchase-ownership verification and request/response logging.
- Reduced setup of a new analytics stream from several days to under four hours by applying modular stream design.
- Kept event delivery reliability above 99.9% through fault-tolerant routing, retries and observability in the production pipeline.
- Defined versioned event contracts with parallel publication, allowing analytics consumers to move between versions while new events were delivered.

**Technologies:** PHP, Laravel, AWS EventBridge, queues, REST APIs, event-driven architecture

### airSlate — Software Developer / Programming Team Lead
February 2021 – August 2023

- Reduced peak database load through bottleneck analysis and workload redistribution, improving stability during high-traffic periods.
- Developed a shared Laravel/Symfony logger package aligned with the interservice communication standard.

**Technologies:** PHP, Laravel, Symfony, MySQL, monitoring

## Education

MSc in Computer Science, National Technical University, Kharkiv, Ukraine (2003–2008)

## Languages

Ukrainian (native), English (upper-intermediate)
