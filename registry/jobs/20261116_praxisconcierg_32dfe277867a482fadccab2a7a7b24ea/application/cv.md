# Valentin Nikolaev
Software Engineer | Product Integrations (Schnittstellen)

Rome, Italy | valeinikolaev@gmail.com | +39 351 370 1194
[LinkedIn](https://linkedin.com/in/valentinnikolaev) | [GitHub](https://github.com/ValentinNikolaev)

## Summary

Backend engineer and former technical lead building Go and PHP systems that connect external APIs to day-to-day operations. I built a Go helpdesk gateway that puts Intercom and Zendesk behind a shared event contract. I also owned a production telephony backend that checks calling windows and consent before scheduling callbacks. My work covers integration design, production debugging and data protection, with enough time spent alongside support teams to see how backend decisions affect their queues.

## Skills

Languages and frameworks: Go, PHP, Laravel, Symfony

Integrations: REST APIs, OpenAPI, webhooks, Amazon Connect, Intercom API, Zendesk API

Data and delivery: PostgreSQL, MySQL, Amazon SQS, Kubernetes, Terraform, Prometheus, CI/CD

## Experience

### Simple App / Simple.life — Software Developer | November 2023 – October 2026

- Enabled the first B2B demo of a support product by building a Go gateway that normalized Intercom and Zendesk events, ingested webhooks and queued work per tenant.

- Released an outbound telephony backend on Amazon Connect that enforced calling windows, withdrew queued callbacks on opt-out and recorded outcomes in the existing Intercom ticket.

- Made GDPR data exports self-service for support administrators by building a workflow that tracks requests and collects data from connected systems.

- Replaced separate Snowflake-to-Intercom jobs with a shared ingestion and delivery engine, eliminating daily full-history reads without changing the public API or admin interface.

- Restored consistent translation of inbound support messages by migrating providers to DeepL after language-detection failures, and added Arabic support.

Technologies: Go, PostgreSQL, Amazon Connect, Amazon SQS, OpenAPI, Intercom API, Zendesk API, Snowflake, DeepL.

### CRURATED — PHP Software Developer | August 2024 – January 2026

Concurrent part-time subcontract alongside Simple App.

- Connected production customer accounts and collections to an external trading platform by owning authentication, account linking, imports and exports, and purchase verification.

- Published versions of the analytics events in parallel so the production pipeline could deliver more than one version of the event contract.

- Shortened setup for new analytics streams by designing reusable parts of the production event pipeline.

- Maintained reliable event delivery under technical ownership of the production analytics pipeline and monitored it through Grafana.

Technologies: PHP, Amazon EventBridge, webhooks, Amazon S3, Grafana.

### airSlate — Technical Lead / Software Developer | February 2021 – August 2023

- Improved stability during traffic peaks by removing bottlenecks and redistributing work away from the main database.

- Made service releases faster and more consistent by implementing CI/CD pipelines across services.

- Improved backend API response times as backend lead, with the change tracked in Prometheus.

Technologies: PHP, Laravel, MySQL, Elasticsearch, RabbitMQ, Kubernetes, Prometheus, CI/CD.

### Hyprr — Technical Lead | November 2019 – January 2021

### Sixt — Senior Software Developer | December 2018 – November 2019

### PDFfiller.com — Technical Lead | October 2016 – November 2019

## Education

MSc in Computer Science, National Technical University, Kharkiv, Ukraine

## Languages

Ukrainian (native), English (upper-intermediate), Russian (native or bilingual)
