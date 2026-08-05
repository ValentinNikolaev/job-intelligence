# Workflow Developer & Tester

Posted: 2026-08-05T05:45:07Z

## Description

- Implement Temporal workflow activities in Go: HSS adapter, PCRF adapter, Inventory update.
- Build and validate unit tests for all workflow activities from day one.
- Build the Inventory Management Database: tables, indexes, partitioning for 30M records.
- Build bulk import tooling: CSV → ICCID/IMSI/MSISDN range ingestion from vendor.
- Implement REST API endpoints for Inventory DB (allocate, reserve, release, query SIM records).
- Write integration tests: workflow → mock NE → database assertions.
- Support Sr. Developer on all workflow development tasks — pair programming expected.
- End-to-end test suite: full provisioning flow from SIM activation to order closed.
- Load and stress testing: simulate peak TPS provisioning against all systems.
- Test automation: CI pipeline integration for all workflow and API tests.
- HSS sync integration: IMSI allocation state reflected in HSS (mock → real NE).
- MNP (number portability) hooks in Inventory DB.
- UAT support: reproduce bugs, write regression tests, validate fixes.

## Requirements

**Must Have**

- 2–4 years backend software development in production environments.
- Go or Java — primary development language for this role is Go.
- Java accepted if strong fundamentals and willing to work in Go (we will support the transition).
- REST API development — building APIs consumed by other services and tested by automated suites.
- PostgreSQL — table design, indexes, writing queries, understanding query plans .
- Unit and integration testing — writing tests is a first-class responsibility, not an afterthought.
- Git — branching, pull requests, code review participation.
- Experience with event-driven architectures using RabbitMQ, Kafka, or Redis Pub/Sub.
- Basic Kubernetes knowledge — understanding how your workloads are deployed.
- Ability to work under technical direction of a senior lead and execute quickly.
- Fluent English.

**Strong Advantage**

- * Any workflow engine experience: Temporal, Camunda, Apache Airflow, AWS Step Functions.
- * Telecom or BSS/OSS background — understanding of SIM lifecycle, provisioning, activation.
- * Test framework experience: Go testing, Testify, mock frameworks.
- * Load testing tools: k6, Locust, JMeter — running and interpreting results.
- * Docker — building and running containerised services.
- * Experience with event-sourced or append-only database patterns.

**Nice to Have**

- Temporal.io SDK experience — even personal/side project counts.
- Python — useful for scripting, test tooling, data processing.
- Prometheus — understanding how to instrument code with metrics.
- Telecom protocol familiarity: Diameter, SS7, SMPP.

## About Webbing

Founded in early 2010, Webbing is a global data MVNO that delivers enterprise grade, global connectivity and IoT services across more than 200 countries and 600+ mobile carriers' networks. Webbing's secured network delivers network protection and web content intelligence.

Enterprise customers can manage, monitor, and optimize data usage in real-time with Webbing's powerful software platform. Gain visibility by application type and have the power to white list applications and limit non-business applications with the click of a button, saving money and improving compliance.

## What we offer

- Fully remote
- An exciting and challenging greenfield platform with great skill and knowledge development opportunities.
- The opportunity to join a team of highly professional specialists in an international environment.
- The opportunity for professional development within a reputable international innovative and growing company.
