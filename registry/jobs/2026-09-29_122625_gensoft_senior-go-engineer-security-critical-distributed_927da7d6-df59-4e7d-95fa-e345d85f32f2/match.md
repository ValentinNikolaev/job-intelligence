# Match Analysis

**Score:** 77/100
**Recommendation:** Match

Strong Go, distributed-systems, ownership, reliability, and remote fit; the security-critical cryptographic and mobile-signing domain is not established in the candidate evidence.

## Why it matches

- Production Go, event-driven architecture, retries, observability, and operational reliability.
- Experience with security assessments, compliance, and high-impact backend systems.
- Remote collaboration and technical-lead background support the ownership model.

## Gaps

- MPC/threshold signing, applied cryptography, and mobile bindings are not evidenced.
- Exact UK/North America overlap availability is unknown.

## Concerns

- The central signing-service domain has a steep security and correctness learning curve.

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| Security engineering and applied cryptography | critical / stated | unknown | Applied cryptography concepts: digital signatures, hashing, key management and signature verification. |  | Cryptography is central and no direct candidate evidence is available. / Require a focused technical screen before relying on transferability. |
| Production Go and concurrency | critical / stated | strong | Strong hands-on production experience with Go: goroutines, channels, context cancellation, race detection, profiling and resource management. | Go-based support automation platform | The profile does not enumerate goroutines or race detection by name. / Probe concurrency debugging and profiling examples. |
| Production ownership and distributed systems | critical / stated | strong | Experience owning production services, diagnosing complex failures and delivering well-tested fixes. | fallback logic | Signing-specific failure semantics are not evidenced. / Translate prior failure-recovery work to interrupted signing sessions. |
| Testing, CI/CD, Linux, containers, and observability | high / stated | strong | Automated testing, CI/CD, Linux, containers and production observability. | Kubernetes | Linux depth is not separately detailed. / Confirm operational ownership and release practices. |
