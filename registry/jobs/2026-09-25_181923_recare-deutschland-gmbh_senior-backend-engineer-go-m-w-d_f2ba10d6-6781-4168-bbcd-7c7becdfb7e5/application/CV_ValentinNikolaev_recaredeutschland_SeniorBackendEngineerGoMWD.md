# Valentin Nikolaev
Senior Backend Engineer — Go

Rome, Italy | valeinikolaev@gmail.com | +39 351 370 1194  
[LinkedIn](https://linkedin.com/in/valentinnikolaev) | [GitHub](https://github.com/ValentinNikolaev)

## Summary

Backend engineer and technical lead with more than 15 years in production Go and PHP systems. I design, deliver and operate backend services, including a Go support platform with direct operational ownership at peak demand. Recent work has covered AWS telephony, helpdesk integrations and simplification of data pipelines; earlier work includes database performance, service reliability and technical leadership. I am comfortable owning a defined system, making architecture decisions with colleagues and following the work through to production. My experience fits a senior individual contributor role centered on Go, code quality and practical engineering judgment.

## Skills

**Backend:** Go, PHP, REST APIs, OpenAPI, event-driven design; **Data:** PostgreSQL, SQL, MySQL, Snowflake, Elasticsearch, database performance; **Delivery and operations:** AWS, Amazon Connect, SQS, Kubernetes, CI/CD, GitHub Actions, monitoring

## Experience

### Simple.life / Simple App — Software Developer
November 2023–2026

- Designed and operated a Go support automation platform connecting helpdesk and internal services, handling at least 20,000 tickets in an ordinary month and up to three times that volume during the US peak season.
- Built a vendor-neutral Go gateway with Intercom and Zendesk adapters, tenant-specific event ingestion and SQS queues, enabling the company's first B2B support-AI demo.
- Architected an outbound-calling backend on Amazon Connect with federated agent access, removing per-agent AWS accounts and SAML setup; it passed security sign-off and entered production.
- Consolidated three duplicated Snowflake-to-Intercom pipelines into one two-phase engine, reducing code from 1,670 to 800 lines, expanding process test coverage from one to three and removing a 100-item daily cap.
- Investigated fatal cron runs during Intercom API degradation and introduced partial-success reporting and parallel, time-sharded cursor scans so incomplete work could be tracked without aborting the whole run.

Technologies: Go, PHP, PostgreSQL, AWS, Amazon Connect, SQS, Kubernetes, Snowflake, Intercom, Zendesk

### CRURATED — PHP Software Developer, concurrent part-time consulting engagement
August 2024–January 2026

- Owned production DataLake and event analytics as throughput grew by more than tenfold, with Grafana and operational observation used to assess the increase.
- Delivered parallel publication of event versions in production under full technical ownership.
- Owned the production Crutrade integration for authentication and OTP, account linking, collection transfer, purchase-ownership checks and request/response logging.

Technologies: PHP, DataLake, event analytics, EventBridge, REST APIs

### airSlate — Software Developer / Programming Team Lead
February 2021–August 2023

- Reduced peak load on the main database by removing bottlenecks and redistributing work, improving stability during high-traffic periods.
- Delivered production fixes after tracing issues through logs, monitoring and SRE dashboards.
- Developed a Laravel/Symfony logger package to the company's interservice communication standard, giving teams a shared logging implementation.

Technologies: PHP, Laravel, Symfony, MySQL, Elasticsearch, RabbitMQ, AWS, Prometheus, CI/CD

### Hyprr — Technical Lead
November 2019–January 2021

- Helped take the creator platform from prototype to closed beta in less than six months through technical leadership and backend delivery.
- Defined the technology roadmap with the CTO and helped establish the core stack for product delivery, including microservice and serverless design.

Technologies: Go, PHP, Laravel, MySQL, AWS, Kubernetes, microservices

## Education

MSc in Computer Science, National Technical University, Kharkiv, Ukraine (2003–2008)

## Languages

Ukrainian (native) | English (professional working)
