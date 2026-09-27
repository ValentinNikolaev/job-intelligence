# Valentin Nikolaev
Senior Backend Engineer | Go, Integrations and Service Reliability

Rome, Italy | valeinikolaev@gmail.com | +39 351 370 1194  
LinkedIn: https://linkedin.com/in/valentinnikolaev | GitHub: https://github.com/ValentinNikolaev

## Summary

Senior backend engineer with more than 15 years of experience building and operating Go and PHP services. My recent work combines domain ownership with practical system design: vendor-neutral integration APIs, secure AWS telephony and production resilience under degraded dependencies. I have also delivered event-stream architecture, database-load improvements and shared service tooling. I work as a hands-on individual contributor who can take a defined backend domain through design, delivery and operation.

## Skills

**Backend:** Go, PHP, REST APIs, OpenAPI, event-driven design, service integration.  
**Data:** PostgreSQL, MySQL, SQL performance, Snowflake, data pipelines, monitoring.  
**Delivery and operations:** AWS, Amazon Connect, SQS, Kubernetes, CI/CD, production troubleshooting.

## Experience

### Simple.life / Simple App — Software Developer
November 2023 – 2026

- Built a vendor-neutral Go gateway with Intercom and Zendesk adapters, tenant-specific event ingestion and SQS queues, enabling the company’s first B2B support-AI demonstration.
- Architected an Amazon Connect calling backend with federated agent access and customer-number masking; the design passed security sign-off and reached production without per-agent AWS accounts or SAML setup.
- Improved resilience of a ticket-processing cron during Intercom API degradation by adding partial-success reporting and parallel time-sharded cursor scans, preserving visibility of incomplete work.

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
