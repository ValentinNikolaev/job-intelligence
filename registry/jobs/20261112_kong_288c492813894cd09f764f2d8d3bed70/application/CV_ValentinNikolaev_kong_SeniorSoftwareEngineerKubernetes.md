# Valentin Nikolaev
Senior Software Engineer | Go, Kubernetes Delivery and API Integrations

Rome, Italy | valeinikolaev@gmail.com | +39 351 370 1194
[LinkedIn](https://linkedin.com/in/valentinnikolaev) | [GitHub](https://github.com/ValentinNikolaev)

## Summary

Backend engineer and former technical lead working on production Go services and distributed integrations. I built a gateway that gives Intercom and Zendesk a common event model while keeping webhook storage and queues scoped to each tenant. I also consolidated integrations that repeatedly read historical data, moving them to a shared delivery engine. My experience includes designing cloud service boundaries, debugging production traffic and making releases more predictable across services.

## Skills

Backend: Go, PHP, OpenAPI, REST APIs, webhooks, microservices

Infrastructure and messaging: AWS, Kubernetes, Terraform, Amazon SQS, RabbitMQ, event-driven systems

Data and operations: PostgreSQL, MySQL, Prometheus, monitoring, CI/CD

## Experience

### Simple App / Simple.life — Software Developer | November 2023 – October 2026

- Centralized vendor SDKs behind a Go gateway with OpenAPI contracts and a shared event model, allowing the support agent to work with Intercom and Zendesk through one service.

- Made data exports self-service for support administrators by building an export workflow across customer, billing and support systems.

- Brought outbound callbacks into production on Amazon Connect by owning the backend design, passing security review and enforcing call windows and opt-outs in the scheduler.

- Removed daily full-history reads from Snowflake by consolidating Intercom delivery jobs around a shared engine with pagination, throttling and retries.

- Built evaluation records for the production support agent by combining conversation text, action events and subscription snapshots at ticket open and close.

Technologies: Go, OpenAPI, AWS, Amazon SQS, Amazon Connect, Kubernetes CronJobs, Snowflake, PostgreSQL.

### CRURATED — PHP Software Developer | August 2024 – January 2026

Concurrent part-time subcontract alongside Simple App.

- Maintained reliable event delivery under production ownership of the analytics pipeline, using Grafana to monitor deliveries.

- Delivered more than one version of the analytics event contract through parallel publication in the production pipeline.

- Shortened the work of connecting additional analytics streams by dividing the production pipeline into reusable modules.

- Brought external trading account and collection operations into the product through production integration work covering authentication, data exchange and purchase verification.

Technologies: PHP, Amazon EventBridge, Amazon S3, webhooks, Grafana.

### airSlate — Technical Lead / Software Developer | February 2021 – August 2023

- Improved service stability at traffic peaks by removing database bottlenecks and moving work off the main database.

- Shortened release cycles and made deployments more consistent across services by implementing CI/CD pipelines.

- Improved backend API response times during technical leadership of the backend, with response time tracked in Prometheus.

Technologies: PHP, Laravel, RabbitMQ, Kubernetes, MySQL, Elasticsearch, Prometheus, CI/CD.

### Hyprr — Technical Lead | November 2019 – January 2021

### Sixt — Senior Software Developer | December 2018 – November 2019

### PDFfiller.com — Technical Lead | October 2016 – November 2019

## Education

MSc in Computer Science, National Technical University, Kharkiv, Ukraine

## Languages

Ukrainian (native), English (upper-intermediate), Russian (native or bilingual)
