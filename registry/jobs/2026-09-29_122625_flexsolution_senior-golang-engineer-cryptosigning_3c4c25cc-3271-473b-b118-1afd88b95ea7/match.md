# Match Analysis

**Score:** 76/100
**Recommendation:** Match

Strong production-Go and reliability fit for a remote European service-ownership role, with material uncertainty around cryptography, MPC, and signing-specific security work.

## Why it matches

- Go backend ownership, distributed messaging, retries, and production troubleshooting.
- CI/CD, containers, Kubernetes, AWS, and observability evidence.
- European remote scope is compatible with the stated candidate location.

## Gaps

- Applied cryptography, MPC/TSS, DKG, blockchain signing, and secure key handling are not evidenced.
- Mobile SDK bindings and React Native/Expo are not evidenced.

## Concerns

- The role expects a concrete production/security incident example and rate/availability information not present in the profile.

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| Applied cryptography and secret handling | critical / stated | unknown | Working knowledge of applied cryptography: digital signatures, hashing, key management, signature verification |  | The core domain is not established by the candidate profile. / Confirm baseline cryptography knowledge before assignment. |
| Commercial production Go | critical / stated | strong | Several years of commercial Go in production — you're confident with goroutines, channels, context, the race detector, pprof and resource management | Go-based support automation platform | Specific pprof and race-detector evidence is absent. / Validate these techniques in technical screening. |
| Distributed systems and live-service ownership | critical / stated | strong | A track record of owning a live service: debugging hard failures and shipping fixes backed by tests | fallback logic | No direct signing-service example is documented. / Use a comparable incident and describe verification of the fix. |
| Remote European work and English | high / stated | strong | Full-time, 100% remote, long-term contract (6+ months, likely extension) | Fiumicino, Latium, Italy | Contract and rate preferences are not stated. / Confirm commercial terms separately. |
