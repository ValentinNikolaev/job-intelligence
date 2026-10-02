# Match Analysis

**Score:** 80/100
**Recommendation:** Strong Match

Strong Go ownership and distributed-reliability fit for a security-critical service; applied cryptography and MPC are material but unverified gaps.

## Why it matches

- Go production systems
- failure recovery and observability
- security/compliance mindset

## Gaps

- Applied cryptography
- MPC/threshold signatures
- and mobile SDK bindings not evidenced

## Concerns

- Security-critical ownership raises a high verification bar

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| Production Go and distributed systems | critical / stated | strong | Strong hands-on production experience with Go | Go | / |
| Security engineering | high / stated | partial | Practical security engineering: authentication, encrypted storage, sensitive data handling and safe logging. | system audits | Cryptographic signing experience is not explicit. / Use interview to verify applied cryptography and secure-storage decisions. |
