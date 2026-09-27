# Valentin Nikolaev
Senior Backend Engineer | Go, Integrations and Service Reliability

Rome, Italy | valeinikolaev@gmail.com | +39 351 370 1194  
LinkedIn: https://linkedin.com/in/valentinnikolaev | GitHub: https://github.com/ValentinNikolaev

## Summary

Backend engineer with more than 15 years in Go and PHP production systems. I design privacy-sensitive integrations and operational services, with recent ownership of a PII/PHI-protected health-domain calling platform, a vendor-neutral Go helpdesk gateway and resilient support automation. I bring hands-on architecture, AWS delivery, SQL performance work and event-driven PHP experience.

## Skills

**Backend:** Go, PHP, REST APIs, OpenAPI, event-driven design, service integration.  
**Data:** PostgreSQL, MySQL, SQL performance, Snowflake, data pipelines, monitoring.  
**Delivery and operations:** AWS, Amazon Connect, SQS, Kubernetes, CI/CD, production troubleshooting.

## Experience

### Simple.life / Simple App — Software Developer
November 2023 – 2026

- Architected the health-domain Amazon Connect platform around PII/PHI protection: phone numbers were server-resolved, masked in UI and logs, and purged by TTL; formal security and call-recording compliance reviews cleared the production release.
- Put lawful calling under backend control through customer-timezone windows, holidays, do-not-call enforcement and opt-out withdrawal, with Amazon Connect retries disabled to prevent bypasses.
- Implemented least-privilege agent federation and lazy Connect-user lifecycle management, separating call access from diagnostics and administration without per-agent AWS accounts or a SAML application.
- Built a multi-tenant Go helpdesk gateway with vendor-neutral events, Intercom and Zendesk adapters and SQS queues, enabling the company’s first B2B support-AI demonstration.
- Stabilized Intercom search failures with partial-success reporting and time-sharded cursor scans, making incomplete processing observable instead of failing the run.

**Technologies:** Go, PHP, PostgreSQL, AWS, Amazon Connect, SQS, Kubernetes, Intercom API, Zendesk API

### CRURATED — PHP Software Developer, concurrent part-time consulting engagement
August 2024 – January 2026

- Reworked modular stream design for production analytics, cutting setup of a new analytics stream from several days to under four hours.
- Kept production event delivery above 99.9% through fault-tolerant routing, retries and observability.
- Implemented versioned event schemas with parallel publication in production, allowing consumers to transition between schema versions while new events were delivered.

**Technologies:** PHP, Laravel, AWS EventBridge, queues, REST APIs, event-driven architecture

### airSlate — Software Developer / Programming Team Lead
February 2021 – August 2023

- Reduced peak pressure on the main database by finding bottlenecks and redistributing workload, improving stability during busy periods.
- Created a Laravel/Symfony logging package that conformed to the interservice communication standard and gave teams a shared implementation.

**Technologies:** PHP, Laravel, Symfony, MySQL, monitoring

## Education

MSc in Computer Science, National Technical University, Kharkiv, Ukraine (2003–2008)

## Languages

Ukrainian (native), English (professional working)
