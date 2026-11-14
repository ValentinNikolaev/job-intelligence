# Match Analysis

**Score:** 74/100  
**Recommendation:** Match

Strong relevance for a remote Senior Go backend role: the profile evidences production Go, event-driven systems, AWS services, PostgreSQL, multi-tenant helpdesk infrastructure, retries, and observability. The sealed evidence does not establish five years of production Go, native OpenTelemetry, pgx/sqlc, or fluent Italian, so those points need verification before application.

## Why it matches

- Production backend ownership in Go, including a multi-tenant helpdesk gateway with vendor-neutral events, per-tenant storage, webhooks, and SQS queues.
- Strong distributed-systems and reliability evidence through event-driven queues, EventBridge, retries, backpressure handling, and delivery guarantees.
- Relevant AWS, PostgreSQL, external API, and support-automation experience aligned with the role's backend responsibilities.

## Gaps

- The profile does not establish at least five years of production Go on distributed systems.
- Specific pgx/sqlc experience and native OpenTelemetry usage are not evidenced.
- Italian fluency is not stated in the Candidate Profile.

## Concerns

- The role is client-facing and requires fluent Italian and English; English is evidenced, while Italian remains unknown.
- The stated RAL range of 35,000-45,000 EUR may be below the candidate's target, which is not supplied in the sealed profile.

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| Five years of production Go on real distributed systems | critical / stated | partial | Almeno 5 anni di esperienza con Go in produzione su sistemi distribuiti reali (non solo API CRUD/REST). | through a robust, scalable backend in Go. | The profile shows production Go and distributed systems but does not prove the required five-year duration. / Verify the Go production timeline and distributed-system scope before applying. |
| Operational AWS experience including ECS or Lambda, SQS, Step Functions, IAM, and VPC | critical / stated | partial | Esperienza operativa su AWS: deploy e gestione di servizi su ECS o Lambda; conoscenza concreta di SQS, Step Functions, IAM e VPC. | Stack: Go, PostgreSQL (GORM), AWS (Amazon Connect, SQS, IAM/IRSA, Lambda), Kubernetes CronJobs, Terraform, Intercom API, Zendesk API, Snowflake, OpenAI/LLM tooling, OpenAPI, DeepL, Braze, AppsFlyer, Microsoft Entra ID. | Lambda, SQS, and IAM are evidenced, but Step Functions, VPC, and direct ECS operations are not all established in the sealed profile. / Confirm hands-on deploy and troubleshooting scope for ECS or Lambda, Step Functions, IAM, and VPC. |
| Multi-tenant data isolation | critical / stated | strong | Esperienza comprovata in contesti multi-tenant con gestione dell’isolamento dei dati per cliente/account. | Multi-tenant helpdesk gateway, built from scratch (Jul–Aug 2026) | / |
| Advanced PostgreSQL and pgx/sqlc | high / stated | partial | PostgreSQL avanzato: lettura piani di esecuzione, progettazione indici, ottima padronanza SQL; esperienza con pgx e sqlc. | Stack: Go, PostgreSQL (GORM), AWS (Amazon Connect, SQS, IAM/IRSA, Lambda), Kubernetes CronJobs, Terraform, Intercom API, Zendesk API, Snowflake, OpenAI/LLM tooling, OpenAPI, DeepL, Braze, AppsFlyer, Microsoft Entra ID. | PostgreSQL and GORM are evidenced, but execution plans, index design, pgx, and sqlc are not explicitly evidenced. / Confirm advanced SQL tuning and the pgx/sqlc toolchain with a concrete production example. |
| Native OpenTelemetry and correlated logs, traces, and metrics | high / stated | partial | Observability: utilizzo nativo di OpenTelemetry (non prima implementazione), capacità di correlare log/trace/metriche. | fault-tolerant pipelines with automatic retries and observability | Observability is evidenced, including Prometheus/Jaeger elsewhere in the profile, but native OpenTelemetry is not explicitly established. / Verify production OpenTelemetry instrumentation and log, trace, and metric correlation experience. |
| Fluent Italian and English for teams and clients | high / stated | partial | Italiano e inglese fluenti (comunicazione con team e clienti). | English - Full Professional | English is evidenced, but the Candidate Profile does not state Italian proficiency or client-facing Italian communication. / Confirm Italian fluency and client-facing communication ability before applying. |
| AWS deployment and infrastructure troubleshooting by the development team | high / stated | partial | Gestire l’infrastruttura su AWS direttamente dal team di sviluppo (deploy, configurazione e troubleshooting). | Migrated managed services from ECS to Kubernetes | Infrastructure ownership and troubleshooting are evidenced, but the sealed profile does not clearly connect this experience to AWS deployment ownership across the requested services. / Confirm direct AWS deployment, configuration, and troubleshooting duties. |
| Reliable asynchronous event-driven pipelines with retries and idempotency | high / stated | strong | Lavorare su pipeline asincrone (event-driven), con gestione di retry, idempotenza e resilienza operativa. | event-driven system using queues and EventBridge | / |
| External provider services and APIs | high / stated | strong | Integrare servizi e API di provider esterni, curando robustezza, contratto e gestione errori. | Stack: Go, PostgreSQL (GORM), AWS (Amazon Connect, SQS, IAM/IRSA, Lambda), Kubernetes CronJobs, Terraform, Intercom API, Zendesk API, Snowflake, OpenAI/LLM tooling, OpenAPI, DeepL, Braze, AppsFlyer, Microsoft Entra ID. | / |
