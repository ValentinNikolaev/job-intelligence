# Valentin Nikolaev
Senior Go Backend Engineer | AWS and Multi-Tenant Services

Rome, Italy | valeinikolaev@gmail.com | +39 351 370 1194
[LinkedIn](https://linkedin.com/in/valentinnikolaev) | [GitHub](https://github.com/ValentinNikolaev)

## Summary

Backend engineer and former technical lead building production services in Go. I designed a vendor-neutral helpdesk service with tenant-scoped webhook storage and queues. I also owned an AWS telephony backend through security review and production release. Much of my work has been at the point where an external API starts affecting our own reliability, including removing repeated reads and consolidating retry behavior across scheduled jobs.

## Skills

Backend: Go, PHP, REST APIs, OpenAPI, webhooks, microservices

Cloud and messaging: AWS, Amazon SQS, Amazon Connect, Terraform, Kubernetes, RabbitMQ

Data and operations: PostgreSQL, MySQL, Prometheus, monitoring, CI/CD

## Experience

### Simple App / Simple.life — Software Developer | November 2023 – October 2026

- Enabled a support product demo for business customers by building a Go integration service with tenant-scoped webhook storage and queues, OpenAPI contracts and separate vendor adapters.

- Released an Amazon Connect backend with federated agent access and backend-owned provisioning, removing the need to set up an AWS account for each support agent.

- Made support-agent evaluations use conversation text, action events and subscription state together by building an evaluation pipeline around ticket open and close.

- Replaced redundant Snowflake ingestion jobs with a common engine that paginates, throttles and retries delivery, eliminating daily reads of the full event history.

- Made personal data export available through a self-service support workflow that collects records from connected systems and exposes request status.

Technologies: Go, PostgreSQL, OpenAPI, Amazon SQS, Amazon Connect, AWS IAM, Kubernetes CronJobs, Snowflake.

### CRURATED — PHP Software Developer | August 2024 – January 2026

Concurrent part-time subcontract alongside Simple App.

- Improved production analytics throughput under technical ownership of the DataLake, using Grafana and operational observation to follow the change.

- Maintained consistent event contracts for teams integrating new event types by defining a versioned schema and owning parallel publication in production.

- Made additional analytics streams faster to bring online by designing modular parts of the production pipeline.

- Routed events to destinations such as webhooks and Amazon S3, with delivery controls and backpressure for downstream processing.

Technologies: PHP, Amazon EventBridge, Amazon S3, webhooks, Grafana.

### airSlate — Technical Lead / Software Developer | February 2021 – August 2023

- Stabilized services at peak traffic by removing primary database bottlenecks and redistributing workload.

- Improved the consistency and speed of releases across services by implementing CI/CD pipelines.

- Improved backend API response times as backend lead and tracked the result through Prometheus metrics.

Technologies: PHP, Laravel, MySQL, Elasticsearch, RabbitMQ, Kubernetes, Prometheus, CI/CD.

### Hyprr — Technical Lead | November 2019 – January 2021

### Sixt — Senior Software Developer | December 2018 – November 2019

### PDFfiller.com — Technical Lead | October 2016 – November 2019

## Education

MSc in Computer Science, National Technical University, Kharkiv, Ukraine

## Languages

Ukrainian (native), English (upper-intermediate), Russian (native or bilingual)
