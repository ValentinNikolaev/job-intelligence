# Valentin Nikolaev
Senior Go/Golang Software Engineer | Backend Architecture and Production Reliability

Rome, Italy | valeinikolaev@gmail.com | +39 351 370 1194  
[LinkedIn](https://linkedin.com/in/valentinnikolaev) | [GitHub](https://github.com/ValentinNikolaev)

## Summary

Backend engineer and technical lead with more than 15 years building production systems in Go and PHP. Recent work includes architecture and operational ownership of Go services for support automation, vendor integrations and AWS telephony. I have simplified data pipelines, addressed failures in production batch processing and reduced database load in earlier SaaS work. My contribution spans design, delivery and diagnosis, with experience explaining technical choices to product and engineering colleagues. I bring this mix of hands-on Go engineering, SQL performance work and accountable system design to complex backend platforms.

## Skills

**Backend and architecture:** Go, PHP, REST APIs, OpenAPI, event-driven systems; **Data:** SQL, PostgreSQL, MySQL, Snowflake, Elasticsearch, database performance; **Cloud and operations:** AWS, Amazon Connect, SQS, Kubernetes, CI/CD, monitoring, Prometheus

## Experience

### Simple.life / Simple App — Software Developer
November 2023–2026

- Architected an Amazon Connect outbound-calling backend with federated agent access, removing per-agent AWS accounts and SAML setup; it passed security sign-off and entered production.
- Replaced three duplicated Snowflake-to-Intercom pipelines with one two-phase engine, reducing the implementation from 1,670 to 800 lines, expanding process test coverage from one to three and removing a 100-item daily cap.
- Diagnosed fatal cron runs during Intercom API degradation and introduced partial-success reporting plus parallel, time-sharded cursor scans so incomplete work was visible without failing the entire run.
- Designed and operated a Go support platform connecting Zendesk, Intercom and internal services, handling at least 20,000 tickets in an ordinary month and up to three times that volume during the US peak season.
- Built a vendor-neutral Go helpdesk gateway with Intercom and Zendesk adapters, tenant-specific event ingestion and SQS queues, enabling the company's first B2B support-AI demo.

Technologies: Go, PHP, PostgreSQL, AWS, Amazon Connect, SQS, Kubernetes, Snowflake, Intercom, Zendesk, REST APIs

### CRURATED — PHP Software Developer, concurrent part-time consulting engagement
August 2024–January 2026

- Owned the production DataLake and event analytics work as throughput grew by more than tenfold, with Grafana and operational observation used to assess the increase.
- Delivered parallel publication of event versions in production under full technical ownership.
- Owned the production Crutrade integration covering authentication and OTP, account linking, collection import and export, purchase-ownership verification and request/response logging.

Technologies: PHP, event analytics, DataLake, EventBridge, REST APIs

### airSlate — Software Developer / Programming Team Lead
February 2021–August 2023

- Reduced peak load on the main database by removing bottlenecks and redistributing work, improving service stability during high-traffic periods.
- Delivered production fixes after tracing failures through logs, monitoring and SRE dashboards, strengthening day-to-day service operation.
- Developed a Laravel/Symfony logger package to the company's interservice communication standard, giving teams a shared logging implementation.

Technologies: PHP, Laravel, Symfony, MySQL, Elasticsearch, RabbitMQ, AWS, Prometheus, CI/CD

### Hyprr — Technical Lead
November 2019–January 2021

- Helped bring the creator platform from prototype to closed beta in less than six months through technical leadership and backend delivery.
- Defined the technology roadmap with the CTO and helped establish the core product stack, including microservice and serverless design considerations.

Technologies: Go, PHP, Laravel, MySQL, AWS, Kubernetes, microservices, CI/CD

## Education

MSc in Computer Science, National Technical University, Kharkiv, Ukraine (2003–2008)

## Languages

Ukrainian (native) | English (professional working)
