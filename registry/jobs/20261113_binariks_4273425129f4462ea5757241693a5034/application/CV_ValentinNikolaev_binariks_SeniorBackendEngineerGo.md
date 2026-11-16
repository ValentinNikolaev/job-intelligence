# Valentin Nikolaev
Senior Backend Engineer | Go and PHP

Rome, Italy | valeinikolaev@gmail.com | +39 351 370 1194
[LinkedIn](https://linkedin.com/in/valentinnikolaev) | [GitHub](https://github.com/ValentinNikolaev)

## Summary

Backend engineer and former technical lead building services in Go and PHP. I designed a Go helpdesk gateway around a shared contract for different vendors and owned a telephony backend from design through security review and production launch. I have also shipped work on GDPR export and deletion workflows and maintained versioned event integrations in a concurrent PHP engagement. Those projects involved separating service responsibilities while keeping production data flows and support operations working.

## Skills

Backend: Go, PHP, Laravel, REST APIs, OpenAPI, microservices

Data and messaging: PostgreSQL, MySQL, RabbitMQ, Amazon SQS, event-driven systems

Operations: AWS, Kubernetes, Prometheus, monitoring, CI/CD, Terraform

## Experience

### Simple App / Simple.life — Software Developer | November 2023 – October 2026

- Enabled a business customer demo of the support product by moving helpdesk integrations behind a Go service with a common event model and separate vendor adapters.

- Released a production callback backend on Amazon Connect after security review, keeping customer phone numbers masked and attaching call outcomes to the existing support ticket.

- Made GDPR data exports self-service for administrators and reworked account deletion to handle downstream requests and cancellation.

- Replaced separate scheduled Snowflake processes with a common engine that added test coverage across the jobs and removed repeated full-history reads without a public API change.

- Added production support-agent actions for cancellation offers and refunds, letting the agent call backend operations for those support scenarios.

Technologies: Go, PostgreSQL, Amazon Connect, Amazon SQS, OpenAPI, Kubernetes CronJobs, Snowflake, Intercom API.

### CRURATED — PHP Software Developer | August 2024 – January 2026

Concurrent part-time subcontract alongside Simple App.

- Maintained a versioned analytics contract by owning the parallel publication of events in production and defining a schema for integrating additional event types.

- Connected account and collection workflows to an external trading platform by owning production authentication, account linking, data exchange and verification of purchase ownership.

- Shortened new analytics stream setup by designing modular components for the production DataLake pipeline.

- Kept production event delivery reliable under technical ownership and used Grafana to monitor deliveries.

Technologies: PHP, Amazon EventBridge, Amazon S3, webhooks, Grafana.

### airSlate — Technical Lead / Software Developer | February 2021 – August 2023

- Improved peak-traffic stability by removing bottlenecks and redistributing work away from the primary database.

- Made releases across services faster and more consistent by implementing CI/CD pipelines.

- Improved backend API response times as the backend lead, with results tracked in Prometheus.

Technologies: PHP, Laravel, MySQL, Elasticsearch, RabbitMQ, Kubernetes, Prometheus, CI/CD.

### Hyprr — Technical Lead | November 2019 – January 2021

### Sixt — Senior Software Developer | December 2018 – November 2019

### PDFfiller.com — Technical Lead | October 2016 – November 2019

## Education

MSc in Computer Science, National Technical University, Kharkiv, Ukraine

## Languages

Ukrainian (native), English (upper-intermediate), Russian (native or bilingual)
