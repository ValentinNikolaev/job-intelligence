# Match Analysis

**Score:** 78/100  
**Recommendation:** Match

Strong fit for senior production Go ownership, distributed-service reliability, observability, security-sensitive data handling, and careful incremental delivery; applied cryptography, threshold-signing, and mobile SDK experience are not established.

## Why it matches

- Strong production Go and backend ownership, including a Go-based support automation platform and production integrations.
- Relevant reliability and distributed-systems evidence through resilient message delivery, retries, monitoring, event-driven systems, and production troubleshooting.
- Security and operational experience includes GDPR and PCI DSS services, Kubernetes, CI/CD, AWS, Prometheus, and production incident work.
- Candidate has led technical decisions and cross-functional delivery, matching the ownership and judgement expectations.

## Gaps

- The profile does not establish applied cryptography, threshold signatures, MPC, DKG, or cryptographic signing implementation.
- The profile does not establish mobile-platform SDKs, bindings, Swift, Kotlin, or Go interoperability with mobile clients.
- Goroutine, channel, race-detection, and context-cancellation experience is not stated explicitly in the supplied profile.

## Concerns

- Security-critical cryptographic protocol work would require close collaboration with cryptography specialists and may have a meaningful learning ramp.
- The vacancy asks for UK and North American overlap; the profile confirms remote work but does not specify availability across those hours.

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| Strong hands-on production experience with Go, including concurrency, cancellation, profiling, and resource management | critical / stated | partial | Strong hands-on production experience with Go: goroutines, channels, context cancellation, race detection, profiling and resource management. | Go-based support automation platform | Explicit goroutine, channel, context-cancellation, and race-detection evidence is not present in the profile. / Confirm concurrency, race-detection, profiling, and resource-management examples during screening. |
| Distributed systems, retries, idempotency, state management, and partial failures | critical / stated | partial | Distributed systems knowledge: asynchronous messaging, retries, idempotency, state management and partial failures. | resilient message delivery pipelines | Idempotency and partial-failure handling are not fully evidenced with exact examples in the profile. / Probe for concrete distributed-state and idempotency decisions. |
| Applied cryptography concepts and digital-signature verification | critical / stated | unknown | Applied cryptography concepts: digital signatures, hashing, key management and signature verification. |  | The profile does not establish applied cryptography or signing-protocol implementation. / Confirm baseline cryptography knowledge and willingness to work under specialist review. |
| Ownership of production services and diagnosis of complex failures | critical / stated | strong | Experience owning production services, diagnosing complex failures and delivering well-tested fixes. | Go-based support automation platform | / |
| Practical security engineering for authentication, encrypted storage, sensitive data, and safe logging | high / stated | partial | Practical security engineering: authentication, encrypted storage, sensitive data handling and safe logging. | PCI DSS | Authentication, encrypted storage, and safe-logging implementation are not all directly established. / Validate security ownership and sensitive-data handling examples. |
| Automated testing, CI/CD, Linux, containers, monitoring, and observability | high / stated | strong | Automated testing, CI/CD, Linux, containers and production observability. | Migrated managed services from ECS to Kubernetes. | Linux is implied by the container and Kubernetes work but not separately described. / Confirm Linux operational depth in interview. |
| Careful ownership, technical judgement, and clear explanation of trade-offs | high / stated | strong | Assess technical risks and trade-offs, explain decisions clearly and make incremental changes with sound security judgement. | Made key technical decisions | / |
| English at Upper-Intermediate level or higher | high / stated | strong | English at Upper-Intermediate level or higher. | English - Upper-intermediate | / |
| SDK development or mobile-platform integration | preferred / stated | unknown | SDK development for JavaScript/TypeScript or mobile platforms (Swift, Kotlin), including asynchronous APIs, packaging and Go interoperability. |  | Mobile SDK and binding experience is not established. / Treat as a nice-to-have and ask for transferable cross-platform integration examples. |
| MPC, threshold signatures, DKG, or blockchain transaction signing | preferred / stated | unknown | MPC or threshold signatures, distributed key generation (DKG). |  | No direct evidence of MPC, threshold signatures, DKG, or cryptographic transaction signing. / Assess learning plan and specialist-collaboration approach; do not treat as a mandatory rejection. |
