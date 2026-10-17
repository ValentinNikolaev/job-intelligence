# Match Analysis

**Score:** 88/100  
**Recommendation:** Strong Match

Excellent Go backend alignment across APIs, PostgreSQL, AWS, Docker, CI/CD, testing, retries, and production operations; some IoT-specific tools remain gaps.

## Why it matches

- Go, REST APIs, PostgreSQL, AWS, Docker, testing, and failure handling are directly supported.
- The candidate has relevant event-driven, support-automation, and production backend experience.
- The role is backend-focused and does not impose a decisive location conflict.

## Gaps

- Industrial IoT, WebSockets, MQTT, TimescaleDB, and Cognito are not established in the profile.

## Concerns

- Client-facing English and the exact remote arrangement should be confirmed.

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| Production Go backend services | critical / stated | strong | Strong commercial experience building production backend services in Go. | I design and own a support automation platform that connects Zendesk, Intercom, and internal services through a robust, scalable backend in Go. | / |
| REST APIs, PostgreSQL, AWS, Docker, and testing | high / stated | partial | Technology environment ** Go, PostgreSQL / TimescaleDB, AWS, Docker, REST, OpenAPI, WebSockets. | Stack: Go, PostgreSQL (GORM), AWS (Amazon Connect, SQS, IAM/IRSA, Lambda), Kubernetes CronJobs, Terraform, Intercom API, Zendesk API, Snowflake, OpenAI/LLM tooling, OpenAPI, DeepL, Braze, AppsFlyer, Microsoft Entra ID. | WebSockets and TimescaleDB are not evidenced, although the core backend stack is. / Confirm the missing transport and time-series database experience. |
| Reliability, retries, and failure handling | high / stated | strong | Experience with service integrations, timeouts, retries, idempotency and failure handling. | Diagnosed and eliminated daily fatal failures (up to 14/day) of a cron scanning ~7,000 tickets under Intercom API degradation by introducing partial-success semantics and sharded cursor pagination, cutting full-scan time roughly 4×. | / |
