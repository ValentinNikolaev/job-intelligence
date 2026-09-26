# Valentin Nikolaev
Senior PHP Developer

Rome, Italy | valeinikolaev@gmail.com | +39 351 370 1194  
LinkedIn: https://linkedin.com/in/valentinnikolaev | GitHub: https://github.com/ValentinNikolaev

## Summary

Senior backend engineer with 15+ years of experience across PHP and Go production systems. At CRURATED, owned a PHP event analytics platform whose DataLake throughput increased more than tenfold while event delivery reliability exceeded 99.9%. Earlier PHP work includes a Laravel/Symfony logger used across airSlate services and database load reduction during peak traffic. Brings hands-on architecture, release and operational ownership, plus experience defining a product technology roadmap with a CTO.

## Skills

**PHP and architecture:** PHP, Laravel, Symfony, REST APIs, event-driven architecture, microservices; **Data and messaging:** PostgreSQL, MySQL, queues, AWS EventBridge; **Delivery and operations:** Docker, Kubernetes, CI/CD, GitHub Actions, ArgoCD, Helm, production monitoring

## Experience

### Simple App (Simple.life) — Software Developer
November 2023 – 2026

- Architected and released an outbound telephony backend on Amazon Connect after security sign-off, using agent federation to avoid individual AWS accounts while keeping customer phone numbers masked and out of logs.
- Built a multi-tenant Go helpdesk gateway with vendor-neutral events and Intercom/Zendesk adapters, enabling the first B2B demo of the support AI product.
- Consolidated three Snowflake-to-Intercom pipelines into one engine, reducing code from 1,670 to 800 lines, testing all three processes and removing a 100-item-per-day cap.
- Resolved recurring fatal cron runs under Intercom API degradation by introducing partial-success handling and sharded cursor searches for a backlog of about 7,000 tickets.
- Automated GDPR data exports across seven sources through a self-service admin workflow, replacing manual coordination for request creation and status tracking.

**Technologies:** Go, PHP, PostgreSQL, AWS, Kubernetes, Snowflake, Intercom, Zendesk

### CRURATED — PHP Software Developer (concurrent part-time subcontract)
August 2024 – January 2026

- Architected an event-driven analytics pipeline with queues and AWS EventBridge; DataLake throughput increased by more than 10x under full technical ownership.
- Kept event delivery reliability above 99.9% through retry and observability work on the production analytics pipeline.
- Designed versioned event schemas and owned parallel event-version publication in production, allowing analytics consumers to move between schemas without blocking new events.
- Owned the production Crutrade integration, including authentication and OTP, account linking, collection exchange and purchase-ownership verification.
- Reduced setup time for new analytics streams from several days to under four hours through modular design.

**Technologies:** PHP, Laravel, AWS EventBridge, queues, REST APIs

### airSlate — Senior Software Developer
February 2021 – August 2023

- Reduced peak load on the main database by finding bottlenecks and redistributing workload, improving stability during high-traffic periods.
- Built a Laravel/Symfony logger package used across services and aligned it with the interservice communication standard.
- Diagnosed production issues with logs, monitoring and SRE dashboards, then delivered fixes and operational improvements.

**Technologies:** PHP, Laravel, Symfony, MySQL, monitoring

### Hyprr — Technical Lead
November 2019 – January 2021

- Defined the technology roadmap with the CTO and established the PHP, Go, AWS and Kubernetes stack for product delivery.
- Led backend development on Ethereum-based digital asset components as the platform advanced from prototype to closed beta in under six months.

**Technologies:** PHP, Go, Laravel, AWS, Kubernetes

## Education

MSc in Computer Science, National Technical University, Kharkiv, Ukraine (2003–2008)

## Languages

Ukrainian (native), English (upper-intermediate)
