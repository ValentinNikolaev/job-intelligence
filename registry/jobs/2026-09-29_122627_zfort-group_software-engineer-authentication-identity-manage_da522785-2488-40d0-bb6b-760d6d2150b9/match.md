# Match Analysis

**Score:** 70/100
**Recommendation:** Match

Good backend, Go, AWS, Kubernetes, and security-adjacent fit, but the identity-protocol, gRPC, and infrastructure-as-code requirements are only partly supported.

## Why it matches

- Backend experience across Go, PHP, APIs, and distributed services.
- AWS and Kubernetes infrastructure experience is documented.
- Security, compliance, and production troubleshooting exposure is relevant.

## Gaps

- OAuth2/OIDC, Keycloak/Cognito, gRPC, and Terraform are not directly evidenced.
- A dedicated identity-platform ownership example is absent.

## Concerns

- The role combines deep IAM specialization with hands-on platform operations.
- Remote location is stated, but work authorization is unknown.

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| Golang distributed backend and gRPC | critical / stated | partial | Golang | Go-based support automation platform | Go backend evidence is strong, but gRPC is not present in the candidate profile. / Confirm gRPC production work or assess transferability. |
| Modern authentication and authorization protocols | critical / stated | partial | OAuth 2.0 | GDPR | Compliance and security exposure do not establish OAuth2, OIDC, or JWT implementation. / Request concrete protocol and identity-provider examples. |
| AWS, Kubernetes, and infrastructure as code | high / stated | partial | Kubernetes | Kubernetes | Terraform or equivalent IaC is not explicitly evidenced. / Clarify IaC ownership and current proficiency. |
| Secure coding and web vulnerability mitigation | high / stated | partial | OWASP Top 10 | security assessments | OWASP-specific architectural mitigation is not stated. / Validate security design depth in screening. |
