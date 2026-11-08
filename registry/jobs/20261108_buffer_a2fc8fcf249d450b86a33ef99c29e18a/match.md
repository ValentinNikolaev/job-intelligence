# Match Analysis

**Score:** 38/100  
**Recommendation:** Weak Match

The candidate has useful adjacent engineering and infrastructure evidence, including AWS, Kubernetes, production reliability, compliance-oriented security assessments, and AI automation. The role is principally a hands-on security leadership position requiring application security, incident leadership, SOC 2, vulnerability disclosure, and TypeScript depth that the profile does not establish.

## Why it matches

- Senior technical leadership and roadmap ownership are supported by Technical Lead experience and product planning responsibilities.
- AWS, Kubernetes, CI/CD, monitoring, production troubleshooting, and reliability work are documented.
- Security assessment and compliance-adjacent experience is documented in a PCI DSS/GDPR context.

## Gaps

- No evidence of SOC 2 Type II controls, audits, or Trust Center ownership.
- No evidence of vulnerability disclosure or bug bounty program triage.
- No demonstrated TypeScript/Node.js application-security implementation, OAuth/OIDC, IDOR/SSRF, or end-to-end security incident leadership.

## Concerns

- The candidate's documented security work is adjacent to software engineering rather than a primary security-engineering leadership role.
- The role requires UTC-3 to UTC+3; Italy is UTC+1/UTC+2 seasonally, so the timezone appears compatible, but on-call expectations remain unverified.

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| Lead security strategy, roadmap, priorities, and execution | critical / stated | partial | Define the strategy and roadmap, set priorities, drive execution, and change how we work where it matters. | technological plan for the product | Technology leadership is evidenced, but security strategy leadership is not. / Verify security-roadmap ownership before preparation; do not relabel general technical leadership as security leadership. |
| Hands-on application and API security depth | critical / stated | missing | You have hands-on application and API security depth in a multi-tenant SaaS, ideally one with a public API: authorization models, OAuth and OIDC, session and auth flows, IDOR and SSRF, and threat modeling. | system audits | The evidence supports assessments and scans but not hands-on remediation or the specified application-security domains. / Obtain explicit evidence before considering this role; do not infer OAuth, OIDC, IDOR, SSRF, or threat modeling. |
| Lead security incidents end-to-end | critical / stated | missing | You’ve led security incidents end-to-end, including the writing of status updates, customer comms, and postmortems that people act on. | fallback logic | Operational incident-reduction work is not evidence of leading security incidents or customer communications. / Verify incident-command examples before preparation. |
| SOC 2 Type II or similar compliance ownership | critical / stated | partial | You’ve worked with SOC 2 Type II (or similar), including handling evidence, implementing controls, and interacting with auditors. | PCI DSS | PCI DSS compliance experience is relevant but does not establish SOC 2 controls, evidence handling, or auditor interaction. / Verify audit and control ownership explicitly. |
| Write and review TypeScript code | high / stated | missing | You write code. You can read and change a TypeScript codebase well enough to ship a fix and review someone else’s |  | The candidate profile documents Go and PHP but no TypeScript experience. / Treat TypeScript as an unverified gap; do not claim transferability as evidence. |
| AWS and Kubernetes infrastructure-risk reasoning | high / stated | partial | You’ve worked with AWS, Kubernetes, and Cloudflare, or similar, enough to reason about infrastructure risk with an infrastructure team. | Migrated managed services from ECS to Kubernetes. | AWS/Kubernetes are supported; Cloudflare and security-risk reasoning are not explicit. / Use only documented AWS/Kubernetes delivery evidence. |
| Run or triage vulnerability disclosure or bug bounty | high / stated | missing | You’ve run or triaged a vulnerability disclosure or bug bounty program |  | No disclosure or bug-bounty program evidence is present. / Do not claim this experience; verify before preparation. |
| Use modern AI tools and secure AI systems | meaningful / stated | partial | You’re fluent with modern AI tools, and you use them to multiply your output and your team’s. You’ve thought hard about securing systems that use them. | OpenAI-powered auto-triage flows | AI automation is supported, but securing AI systems is not established. / Describe automation implementation only; verify security-specific AI work. |
