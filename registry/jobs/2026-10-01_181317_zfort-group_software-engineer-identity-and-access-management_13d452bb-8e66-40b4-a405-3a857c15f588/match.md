# Match Analysis

**Score:** 61/100
**Recommendation:** Possible Match

Strong Go, AWS, Kubernetes, distributed-backend, and security-adjacent evidence, but the central IAM protocols, gRPC, cryptography, Terraform, and identity-provider experience are not established.

## Why it matches

- Go backend, AWS, Kubernetes, scalable systems, and secure-compliance work are supported.
- GDPR, PCI DSS, security assessments, vulnerability scans, and production reliability provide adjacent security evidence.
- The candidate has technical-lead and stakeholder communication experience.

## Gaps

- OAuth2/OIDC, SSO/MFA, JWT assertions, RBAC, Keycloak/Cognito, gRPC, Terraform, and cryptographic fundamentals are not explicitly evidenced.

## Concerns

- IAM is central to the role, so the unverified protocol experience is a material application risk.

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| Modern authentication and authorization protocols | critical / stated | unknown | AWS |  | Central IAM protocol experience is not evidenced. / Verify concrete OAuth/OIDC/JWT/RBAC projects before applying. |
| Go distributed backend engineering | critical / stated | strong | complex, distributed backend systems | robust, scalable backend in Go | / |
| AWS and Kubernetes | high / stated | strong | AWS | AWS \| Kubernetes | / |
