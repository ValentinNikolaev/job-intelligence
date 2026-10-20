# Match Analysis

**Score:** 84/100  
**Recommendation:** Strong Match

Strong PHP backend match; Kafka and Redis depth should be verified.

## Why it matches

- PHP
- Laravel
- Symfony
- RabbitMQ
- event-driven systems
- production troubleshooting

## Gaps

- Kafka and Redis are not explicit

## Concerns

- Domain preference and work authorization are unknown

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| Event-driven Kafka and RabbitMQ integrations | critical / stated | partial | Develop and support event-driven integrations based on Kafka and RabbitMQ (producers/consumers, queues, message processing). | PHP \| Laravel \| MySQL \| Elasticsearch \| RabbitMQ \| AWS \| Email | RabbitMQ is evidenced, but Kafka is not explicit. / Clarify Kafka and asynchronous integration ownership. |
| PHP backend development with Laravel and Symfony | critical / stated | strong | We’re looking for a **Senior PHP Backend Developer** to strengthen the engineering team of a high-load iGaming platform, built on PHP (Laravel and Symfony). | ### Frameworks - Laravel - Symfony | / |
| Relational data and Redis optimization | high / stated | partial | Design and optimize data handling: relational databases and caching/storage with Redis. | - MySQL - PostgreSQL - Elasticsearch | Redis is not explicit. / Confirm Redis experience or transferability. |
| Asynchronous delivery guarantees and failure handling | high / stated | strong | Understand how asynchronous processing works: message flow, delivery guarantees, idempotency, retries, ordering, backpressure, and failure handling. | - Build resilient message delivery pipelines with fallback logic, retries, and monitoring - reducing incident-related disruptions by over 50%. | / |
| Production incident investigation | high / stated | strong | Investigate and resolve defects and incidents using logs, databases, metrics, and monitoring. | - Troubleshot production issues by analyzing logs, monitoring system performance, SRE dashboards. Introduced necessary fixes and optimizations. | / |
