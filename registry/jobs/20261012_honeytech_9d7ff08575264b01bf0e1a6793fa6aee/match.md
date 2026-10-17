# Match Analysis

**Score:** 86/100  
**Recommendation:** Strong Match

Strong senior PHP architecture and high-load backend fit with queues, databases, Kubernetes, AWS, reliability patterns, and product ownership; some exact tooling is missing.

## Why it matches

- PHP/Symfony, high-load backend, relational databases, RabbitMQ, Kubernetes, AWS, and system design align.
- The candidate has idempotency/retry/observability-adjacent reliability work and product impact evidence.
- Remote work and European context are compatible.

## Gaps

- Kafka, Terraform/Pulumi, BigQuery, Twig, Sass, and Webpack Encore are not explicitly supported.

## Concerns

- The role's Ukrainian-language environment and exact location expectations should be confirmed.

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| Senior backend architecture and high-load systems | critical / stated | strong | Досвід побудови систем, які легко підтримувати роками: чіткі межі доменів, зниження зв’язності, безпечні зміни без зупинки трафіку. | Backend engineer with 15+ years of experience building and improving production systems across **PHP** and **Go**. | / |
| PHP, Symfony, queues, databases, and infrastructure | high / stated | partial | - Досвід роботи з чергами повідомлень (**Kafka, RabbitMQ**). | **Skills:** PHP \| Laravel \| MySQL \| Elasticsearch \| RabbitMQ \| AWS \| Kubernetes \| Prometheus \| REST APIs \| CI/CD | Kafka, Redis, BigQuery, and exact Symfony version are not confirmed. / Confirm the missing named technologies while foregrounding the supported equivalents. |
| Idempotent asynchronous processing and observability | high / stated | partial | Проєктувати **idempotent та asynchronous processing**. | Diagnosed and eliminated daily fatal failures (up to 14/day) of a cron scanning ~7,000 tickets under Intercom API degradation by introducing partial-success semantics and sharded cursor pagination, cutting full-scan time roughly 4×. | The exact outbox/observability vocabulary is not all present in the profile. / Use only the confirmed failure-handling and reliability evidence. |
