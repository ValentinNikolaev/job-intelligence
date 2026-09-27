# Valentin Nikolaev
Backend Developer | PHP, Go and Production Integrations

Rome, Italy | valeinikolaev@gmail.com | +39 351 370 1194  
LinkedIn: https://linkedin.com/in/valentinnikolaev | GitHub: https://github.com/ValentinNikolaev

## Summary

Backend developer with more than 15 years in Go and PHP production systems. I build privacy-sensitive backend services, integrations and operational workflows with a focus on clear system boundaries and reliable delivery. Recent work includes a PII/PHI-protected Amazon Connect platform, a multi-tenant Go gateway, event-driven PHP systems and SQL performance improvements.

## Skills

**Languages and frameworks:** PHP, Laravel, Symfony, Go.  
**Data and integration:** MySQL, PostgreSQL, REST APIs, EventBridge, queues, event-driven architecture, Intercom API, Zendesk API.  
**Delivery and operations:** AWS, Kubernetes, CI/CD, monitoring, production troubleshooting, SQS.

## Experience

### Simple.life / Simple App — Software Developer
November 2023 – 2026

- Architected a health-domain Amazon Connect platform with PII/PHI protection as its starting point: phone numbers were server-resolved, masked in UI and logs, passed only as transient contact attributes and purged by TTL; formal security and recording-compliance reviews preceded production.
- Implemented backend-owned contact controls for timezones, holidays, do-not-call rules and opt-outs, setting Amazon Connect retries to zero so repeat calls could not bypass those safeguards.
- Implemented least-privilege Entra federation and lazy Connect-user lifecycle management, separating call access from diagnostics and administration without individual AWS accounts or a SAML application.
- Built a Go helpdesk gateway with vendor-neutral events, Intercom and Zendesk adapters and SQS queues, enabling the support-AI product’s first B2B demonstration.
- Made Intercom ticket processing resilient with partial-success reporting and sharded cursor scans, retaining visibility of incomplete work during dependency degradation.
- Delivered self-service GDPR exports across seven data sources with request creation, status tracking and review.

**Technologies:** Go, PHP, PostgreSQL, AWS, Amazon Connect, SQS, Intercom API, Zendesk API, REST APIs

### CRURATED — PHP Software Developer, concurrent part-time consulting engagement
August 2024 – January 2026

- Built modular event-stream architecture for production analytics, reducing the setup of a new stream from several days to under four hours.
- Maintained event delivery above 99.9% through retry design, fault-tolerant routing and operational monitoring.
- Designed versioned event contracts and parallel publication so consumers could migrate without preventing delivery of new event data.
- Owned a production partner integration covering authentication, OTP, account linking and request/response logging.

**Technologies:** PHP, Laravel, AWS EventBridge, queues, REST APIs, event-driven architecture

### airSlate — Software Developer / Programming Team Lead
February 2021 – August 2023

- Removed database bottlenecks and redistributed workload, reducing peak pressure on the main database and improving service stability during heavy traffic.
- Introduced a Laravel/Symfony logger package aligned with the product’s interservice communication standard, creating a shared service-level logging component.

**Technologies:** PHP, Laravel, Symfony, MySQL, monitoring

## Education

MSc in Computer Science, National Technical University, Kharkiv, Ukraine (2003–2008)

## Languages

Ukrainian (native), English (upper-intermediate), Italian (learning)
