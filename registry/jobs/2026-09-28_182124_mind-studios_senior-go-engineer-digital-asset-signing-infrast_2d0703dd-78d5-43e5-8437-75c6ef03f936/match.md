# Match Analysis

**Score:** 77/100
**Recommendation:** Match

Strong Go ownership, distributed reliability, and infrastructure fit for the virtual-signer role, offset by no direct evidence of cryptography, MPC, or mobile bindings.

## Why it matches

- Production Go, event-driven systems, retries, observability, and Kubernetes experience.
- Technical ownership, architecture, and careful production troubleshooting are documented.
- Europe/Ukraine remote scope is broadly compatible with Italy, subject to contract eligibility.

## Gaps

- Digital-asset signing, MPC/threshold signatures, and cryptographic key management are not evidenced.
- Swift, Kotlin, TypeScript SDK, and mobile lifecycle work are not evidenced.

## Concerns

- UK/Eastern Canada overlap and occasional customer-support work need confirmation.

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| Security engineering and applied cryptography | critical / stated | unknown | Applied cryptography concepts, including digital signatures, hashing, key management and signature verification. |  | This is a central requirement with no direct candidate evidence. / Require targeted technical validation. |
| Production Go concurrency and ownership | critical / stated | strong | Strong hands-on production Go, including goroutines, channels, context cancellation, race detection, profiling and resource management. | Go-based support automation platform | Technique-level concurrency evidence is not itemized. / Prepare concurrency and profiling examples for screening. |
| Distributed reliability and failure recovery | critical / stated | strong | Distributed-systems knowledge, including asynchronous messaging, retries, idempotency, state management and partial failures. | fallback logic | Signing-session state management is not directly evidenced. / Explain analogous retry, recovery, and idempotency decisions. |
| Linux, Docker, testing, CI/CD, and observability | high / stated | strong | Automated testing, CI/CD, Linux, containers and production observability. | Kubernetes | The profile does not separately name Docker. / Confirm container workflow details. |
