# Valentin Nikolaev
Senior Go/Golang Software Engineer | Distributed Systems and Production Reliability

Rome, Italy | valeinikolaev@gmail.com | +39 351 370 1194  
LinkedIn: https://linkedin.com/in/valentinnikolaev | GitHub: https://github.com/ValentinNikolaev

## Summary

Backend engineer with more than 15 years of experience in Go and PHP production systems. I design privacy-sensitive backend systems that connect external platforms, make operational failure visible and keep data flows maintainable as they evolve. Recent work includes a PII/PHI-protected Amazon Connect platform, a multi-tenant Go integration gateway and resilience improvements for support automation. I also bring experience with event-driven PHP systems, AWS, SQL performance work and cross-service logging standards.

## Skills

**Backend and APIs:** Go, PHP, REST APIs, OpenAPI, event-driven design, distributed systems.  
**Data and integration:** PostgreSQL, MySQL, SQL performance, Snowflake, Intercom API, Zendesk API, AWS EventBridge.  
**Delivery and operations:** AWS, Amazon Connect, SQS, Kubernetes, CI/CD, monitoring, production troubleshooting.

## Experience

### Simple.life / Simple App — Software Developer
November 2023 – 2026

- Owned the architecture and backend for a health-domain Amazon Connect platform designed around PII/PHI protection: customer numbers were resolved server-side, masked in the browser and logs, and purged from Connect by TTL; it passed formal security and call-recording compliance reviews before production.
- Built backend-controlled lawful-calling safeguards for customer-timezone windows, holidays, do-not-call enforcement and opt-out withdrawal, with Amazon Connect retries set to zero so scheduled calls could not bypass those controls.
- Implemented least-privilege agent federation through Entra and AssumeRole/GetFederationToken, separating diagnostics and administration access while avoiding per-agent AWS accounts and a SAML application.
- Built a multi-tenant Go helpdesk gateway with a vendor-neutral event model, Intercom and Zendesk adapters, tenant event ingestion and SQS queues, enabling the company’s first B2B support-AI demonstration.
- Stabilized recurring Intercom search failures by tracing the timeout path and introducing partial-success reporting with time-sharded cursor scans, so incomplete processing was observable instead of aborting the run.
- Automated GDPR data exports across seven sources through a self-service administration workflow for creating, tracking and reviewing requests.

**Technologies:** Go, PHP, PostgreSQL, AWS, Amazon Connect, SQS, Kubernetes, Snowflake, Intercom API, Zendesk API

### CRURATED — PHP Software Developer, concurrent part-time consulting engagement
August 2024 – January 2026

- Designed modular event-stream architecture for a production DataLake, reducing setup of a new analytics stream from several days to under four hours.
- Maintained event delivery reliability above 99.9% through fault-tolerant routing, retries and operational monitoring.
- Designed versioned event schemas and parallel production publication so analytics consumers could evolve schemas while new events continued to be delivered.

**Technologies:** PHP, Laravel, AWS EventBridge, queues, REST APIs, event-driven architecture

### airSlate — Software Developer / Programming Team Lead
February 2021 – August 2023

- Reduced peak load on the main database by removing bottlenecks and redistributing workload, improving service stability during high-traffic periods.
- Developed a Laravel/Symfony logger package aligned with the interservice communication standard, giving teams a shared logging implementation.

**Technologies:** PHP, Laravel, Symfony, MySQL, monitoring

## Education

MSc in Computer Science, National Technical University, Kharkiv, Ukraine (2003–2008)

## Languages

Ukrainian (native), English (upper-intermediate)
