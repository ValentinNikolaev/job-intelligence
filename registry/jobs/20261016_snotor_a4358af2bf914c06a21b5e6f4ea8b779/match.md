# Match Analysis

**Score:** 78/100  
**Recommendation:** Match

Strong Go backend, REST, PostgreSQL, AWS, reliability, integration, and delivery evidence aligns well with the role; WebSockets, multi-tenancy/JWT, and industrial IoT remain material unknowns.

## Why it matches

- Production Go backend ownership and support automation experience.
- Strong evidence for APIs, messaging reliability, retries, monitoring, AWS, Kubernetes, and CI/CD.
- PostgreSQL and SQL-oriented performance work are supported.

## Gaps

- WebSocket implementation is not established in the supplied profile.
- Multi-tenant authorization and JWT validation with JWKS are not established.
- Industrial IoT, TimescaleDB, and device telemetry experience are not established.

## Concerns

- The role's real-time device and security model may require experience not visible in the profile.
- Docker and formal OpenAPI ownership are not explicitly documented.

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| REST APIs and WebSockets | critical / stated | partial | Experience designing REST APIs, maintaining OpenAPI contracts and working with WebSockets. | REST APIs | REST is supported, but WebSockets and OpenAPI contract ownership are not evidenced. / Verify real-time channel and API-contract experience before preparation. |
| Production backend services in Go | critical / stated | strong | Strong commercial experience building production backend services in Go. | backend in Go. | / |
| PostgreSQL and SQL optimization | high / stated | partial | Strong PostgreSQL and SQL skills, including indexing, transactions and query optimisation. | - PostgreSQL | PostgreSQL and optimization are supported, but indexing and transaction examples are not explicit in the profile. / Use confirmed database and performance evidence and verify the detailed SQL scope. |
| Multi-tenant authorization and JWT validation using JWKS | high / stated | unknown | Understanding of multi-tenant systems, authorisation and JWT validation using JWKS. |  | A security-critical requirement is not covered by the supplied candidate evidence. / Confirm direct multi-tenant and JWT/JWKS experience before claiming fit. |
| Integrations, timeouts, retries, idempotency, and failure handling | high / stated | strong | Experience with service integrations, timeouts, retries, idempotency and failure handling. | - Build resilient message delivery pipelines with fallback logic, retries, and | Idempotency is not named directly, although reliability and retry handling are well evidenced. / Verify an idempotency example if the role advances. |
| AWS services and deployed-application troubleshooting | high / stated | strong | Experience integrating AWS services and troubleshooting deployed applications. | - AWS | / |
| Automated tests, deployment, and CI/CD | meaningful / stated | partial | Write automated tests, document API contracts and support deployment and troubleshooting. | GitHub Actions | CI/CD and deployment are supported, but automated test and API-documentation evidence is limited. / Confirm testing and OpenAPI documentation examples. |
