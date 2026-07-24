## Recruiter / HR Screening

Prepare concise, factual answers for:

- Why this role: connect production reliability, Kubernetes/CI/CD, and customer-impacting systems to ACCURIDS’ data-infrastructure work; do not claim pharmaceutical expertise.
- Current status and timeline: reconcile the Simple.life end date in the primary CV with the LinkedIn “Present” entry before speaking with a recruiter.
- Location and working model: explain the realistic plan for a Cologne hybrid role from Rome; do not assume relocation support, remote exceptions, work authorization, notice period, or travel expectations.
- English: describe the documented upper-intermediate level candidly and provide examples of cross-functional collaboration; do not claim German proficiency.
- Salary and availability: prepare a range and notice-period answer based on current circumstances; neither is evidenced in the source documents.
- Career changes: explain the move from backend/technical leadership toward platform reliability as a continuity of operational ownership, not as invented DevOps tenure.

## Culture Fit / Behavioral Interview

Likely questions:

1. Tell us about a production incident where you improved the system afterward.
2. How have you balanced delivery speed and reliability?
3. Describe a time you learned a new infrastructure tool or approach quickly.
4. How do you document and transfer operational knowledge?
5. Tell us about a cross-functional disagreement involving operational priorities.
6. Describe your approach to an unclear customer deployment constraint.
7. How do you prioritize security, observability, and feature work?
8. Tell us about leading through a high-traffic or high-pressure period.
9. How do you use AI-assisted tools responsibly in scripting or debugging?
10. What would you do during your first 90 days as the senior operational pillar?

STAR stories grounded in the CV: airSlate ECS-to-Kubernetes migration; Simple.life resilient message delivery with fallback/retries/monitoring; PDFfiller’s 50-million-email monthly service and BFCM traffic; Hyprr’s prototype-to-closed-beta delivery. Prepare personal contributions, context, constraints, decisions, and outcomes without extending beyond source evidence.

## Technical Interview

**High Priority**

- Kubernetes deployment and operations: explain the airSlate migration, Helm, ArgoCD, workload health, rollout safety, logs, monitoring, and troubleshooting.
- CI/CD and GitOps: articulate the supported GitHub Actions and ArgoCD experience; be explicit that GitLab CI and Kargo are learning gaps.
- Reliability and incident response: demonstrate a disciplined approach to alert triage, logs/metrics, retries, fallback behavior, runbooks, post-incident learning, and progressive mitigation.
- AWS/platform fundamentals: prepare how you have used AWS in supported roles, then study AWS account boundaries, IAM least privilege, EKS, RDS, S3, networking, backups, and disaster recovery as role-specific learning topics.
- Observability: prepare Prometheus, monitoring/logging, service symptoms, meaningful SLIs/SLOs, alert quality, and dashboard use. Do not claim Grafana ownership unless supported.

**Medium Priority**

- Terraform: learn plan/state/module/remote-state concepts and review a small practice configuration; state clearly that production Terraform experience is not listed.
- Security and compliance: review vulnerability-management workflow, secrets handling, IAM concepts, audit evidence, and ISO 27001 concepts; do not claim certification or implementation experience.
- PostgreSQL and Elasticsearch: be ready to discuss the supported database/performance and Elasticsearch experience, with operational trade-offs.
- Docker and on-premise deployment: prepare container fundamentals, images, configuration, secrets, persistent volumes, networking, and upgrades; frame customer on-premise work as a learning area.

**Low Priority**

- Keycloak and Spring Boot: understand the role they may play in the platform, but do not present prior experience.
- Pharmaceutical data and IDMP: read the [ACCURIDS overview](https://accurids.com/) and [EMA’s PMS information](https://www.ema.europa.eu/en/human-regulatory-overview/research-development/data-medicines-iso-idmp-standards-overview/substance-product-organisation-referential-spor-master-data/substance-product-data-management-services) to ask informed questions; do not claim domain expertise.

## CV Deep-Dive Questions

Be ready to defend:

- What exactly did the ECS-to-Kubernetes migration involve, and what was your scope?
- How did Helm, GitHub Actions, and ArgoCD interact in the airSlate delivery process?
- What metrics/logs were used to troubleshoot production problems?
- How did fallback logic and retries improve message-delivery resilience at Simple.life?
- What did leading five engineers at PDFfiller entail, and what decisions did you personally own?
- How was the 50-million-monthly-email scale handled during BFCM spikes?
- Which Elasticsearch and PostgreSQL problems have you personally solved?
- What does “AWS experience” mean in terms of systems and responsibilities?

## Company-Specific Preparation

ACCURIDS publicly describes a pharma data-standardization platform, SaaS plus containerized private-cloud/on-premise deployment options, and a culture of ownership and clear communication. Its Kubernetes guide references StatefulSets, persistent volumes, ConfigMaps, Secrets, Services, Ingress, and cluster permissions. Review these concepts, then frame your questions around safe deployments, customer environments, auditability, and operational documentation. Unknowns to clarify include the production stack, GitLab/Kargo and Terraform usage, AWS topology, on-call expectations, team size, customer-installation process, and the practical scope of ISO 27001 work.

## Preparation Plan

**Must prepare:** truthful explanation of location/hybrid feasibility, employment chronology, English, notice period, salary, and the main gaps; ECS-to-Kubernetes and reliability STAR stories; AWS/Kubernetes/CI/CD/observability fundamentals.

**Pre-technical:** review an EKS/IAM/RDS/S3 architecture, Kubernetes troubleshooting flows, Terraform basics, GitLab CI versus GitHub Actions, ArgoCD/GitOps, and ISO 27001/security operations concepts. Be ready to distinguish demonstrated experience from topics being learned.

**Pre-final/culture:** study ACCURIDS’ product and deployment documentation; prepare ownership, collaboration, incident, learning, and customer-constraint examples; confirm the work-model decision before accepting an interview loop.

## Questions to Ask

1. What proportion of the role is SaaS-platform work versus customer on-premise installation and support?
2. Which AWS services and account boundaries does the team operate directly?
3. How are Terraform, GitLab CI, ArgoCD, and Kargo used today, and what changes are planned?
4. What does the on-call or incident-response rotation look like?
5. Which reliability or security outcomes would define success in the first six months?
6. How are deployment changes documented and validated for customer environments?
7. What ISO 27001 responsibilities belong to this role versus a dedicated security/compliance function?
8. What are the hardest operational differences between the SaaS and on-premise offerings?
9. How does the engineering team collaborate with customer-facing and product teams during installations or incidents?
10. What does the Cologne hybrid arrangement mean in practice for this role?
