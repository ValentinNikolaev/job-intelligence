# Valentin Nikolaev
Backend Developer | PHP, Go and Production Integrations

Rome, Italy | valeinikolaev@gmail.com | +39 351 370 1194  
LinkedIn: https://linkedin.com/in/valentinnikolaev | GitHub: https://github.com/ValentinNikolaev

## Summary

Backend developer with 15+ years of experience across PHP and Go services. I work on integrations and data flows that must remain understandable and dependable in production: external APIs, event pipelines, operational tooling and database performance. Recent work spans secure AWS telephony, a vendor-neutral helpdesk gateway and PHP event analytics, alongside pragmatic improvements to service resilience, release operations and cross-service maintainability. I favour explicit service boundaries and observable production behaviour.

## Skills

**Languages and frameworks:** PHP, Laravel, Symfony, Go.  
**Data and integration:** MySQL, PostgreSQL, REST APIs, EventBridge, queues, event-driven architecture, Intercom API, Zendesk API.  
**Delivery and operations:** AWS, Kubernetes, CI/CD, monitoring, production troubleshooting, SQS.

## Experience

### Simple.life / Simple App — Software Developer
November 2023 – 2026

- Released an Amazon Connect outbound-calling platform with federated agent access and customer-number masking, satisfying security requirements without individual AWS accounts.
- Built a Go helpdesk gateway that abstracts Intercom and Zendesk behind a vendor-neutral event model, enabling the company’s first B2B support-AI demo.
- Changed degraded Intercom searches from fatal cron failures to tracked partial results through sharded cursor scans and explicit incomplete-scan reporting.
- Delivered self-service GDPR export automation across seven sources, providing a single administration flow for request creation, status and review.

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
