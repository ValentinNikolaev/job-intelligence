# Interview Preparation

## Recruiter / HR Screening

Likely motivation question: "Why ACCURIDS and why this role?"  
Suggested angle: Focus on the role's mix of production reliability, AWS/Kubernetes operations, automation, regulated data, and a product where infrastructure quality directly supports customers. Mention verified public facts: ACCURIDS builds an IDMP-native data foundation for pharma product data and aims to make fragmented regulated data audit-ready and usable.

Likely history question: "Your background is backend engineering. Why DevOps / Cloud Engineering?"  
Suggested angle: Explain that several roles already involved platform-adjacent work: ECS-to-Kubernetes migration, Helm, ArgoCD, GitHub Actions, monitoring, SRE dashboards, production troubleshooting, event delivery reliability, retries, and backpressure handling. Position the move as a natural continuation of production ownership.

Likely location question: "Can you work in Cologne under a hybrid model?"  
Prepare a clear factual answer before the call. The vacancy is not listed as fully remote. Decide whether relocation, regular Cologne presence, or a specific hybrid arrangement is feasible.

Likely salary question: "What salary range are you targeting?"  
Prepare a researched range for Senior DevOps / Cloud Engineer roles in Cologne and answer with flexibility tied to scope, hybrid requirements, and benefits.

Likely notice-period question: "When could you start?"  
Prepare the current factual availability. Do not rely on stale source dates; the primary CV says Simple.life ended in March 2026 while LinkedIn says present.

Likely language question: "How comfortable are you using English at work?"  
Suggested angle: State practical working proficiency honestly. The sources support upper-intermediate/professional working proficiency, not native fluency.

Likely job-change question: "Why are you interested now?"  
Suggested angle: Emphasize a move toward cloud/platform reliability and regulated enterprise systems, without inventing dissatisfaction with previous roles.

## Culture Fit / Behavioral Interview

Likely behavioral questions:

- Tell me about a time you handled a production incident.
- Describe a migration you completed under operational constraints.
- Tell me about a time you improved observability or monitoring.
- Describe how you work with development teams to improve delivery pipelines.
- Tell me about a time you had to learn a new tool or platform quickly.
- Describe a situation where you reduced operational risk.
- Tell me about a time you balanced speed and reliability.
- Describe how you document systems to reduce dependency on one person.
- Tell me about a time you worked with product or support teams on an engineering problem.
- Describe how you handle disagreement about architecture or operations.

STAR stories to prepare from real CV evidence:

- airSlate ECS-to-Kubernetes migration: situation was managed services moving to Kubernetes; tasks included preparing Helm, GitHub Actions, and ArgoCD deployment workflows; actions included migration and pipeline implementation; results included cost and performance improvements from LinkedIn evidence.
- airSlate production troubleshooting: situation was production issues and peak database load; actions used logs, monitoring, SRE dashboards, API/query optimization; results included improved stability and lower workload.
- Simple.life support automation reliability: situation was support operations at scale; actions included Go backend, Zendesk/Intercom integration, retries, fallback logic, and monitoring; results included up to 30% ticket automation/deflection and reduced incident disruption.
- CRURATED event analytics infrastructure: situation was product metrics and business insights; actions included event-driven architecture, EventBridge, queues, S3 routing, backpressure, retries, observability; results included over 10x throughput and 99.9% delivery reliability.
- PDFfiller transactional email platform: situation was high-volume messaging; actions included technical leadership, email infrastructure, and peak-load preparation; results included about 50 million emails per month and 10x BFCM traffic handling.

## Technical Interview

High Priority:

- AWS operations: Prepare to explain hands-on AWS exposure clearly, including what was personally owned versus used. Be ready for EKS, RDS, S3, IAM, networking, account structure, and security questions. Supported evidence is AWS-backed systems, ECS-to-Kubernetes migration, EventBridge, S3 downstreams, and production systems.
- Kubernetes: Prepare deployment, service, ingress, config, secret, scaling, rollout, debugging, and cluster-observability examples. The strongest evidence is airSlate migration and Kubernetes deployment preparation.
- CI/CD and GitOps: Prepare Helm, GitHub Actions, ArgoCD, release workflow, rollback, environment promotion, and deployment consistency examples. Be direct that GitLab CI and Kargo are not evidenced if asked.
- Observability and incident response: Prepare examples using logs, monitoring, SRE dashboards, Prometheus, Elasticsearch, retries, fallback logic, and backpressure handling.
- Reliability architecture: Prepare to discuss reducing single points of failure, documenting operational processes, handling peak load, and designing resilient delivery pipelines.

Medium Priority:

- Infrastructure as Code: Terraform is explicit in the vacancy but not supported in the source CV. Prepare adjacent concepts from Kubernetes manifests, Helm, GitOps, and deployment automation, plus a ramp-up plan for Terraform.
- Security operations: Prepare GDPR, PCI DSS, system audits, security assessments, vulnerability scans, monitoring, and alerting examples. Avoid claiming ISO 27001 implementation ownership.
- Databases: Prepare MySQL, PostgreSQL, Elasticsearch, query optimization, peak load, RDS concepts, backups, and monitoring.
- Customer/on-premise deployments: The source has less direct evidence. Prepare a careful answer around production environments, restrictive operational contexts, documentation, troubleshooting, and customer-impact awareness.
- Docker/containerization: Prepare container fundamentals, image build, runtime configuration, registry, health checks, logs, networking, and debugging. The source supports Kubernetes/container ecosystem exposure but not detailed Docker achievements.

Low Priority:

- Spring Boot and Keycloak: These are vacancy nice-to-haves but not supported by candidate evidence.
- Deep pharma/IDMP domain expertise: Prepare a high-level understanding from research, but do not claim domain experience.
- Kargo-specific workflows: Treat as a learning area unless the candidate has unrecorded experience.

## CV Deep-Dive Questions

Defend these claims with specifics:

- "Migrated managed services from ECS to Kubernetes." Prepare what services, migration scope, rollout strategy, risks, and personal responsibility.
- "Prepared services for Kubernetes deployments using Helm, GitHub Actions, and ArgoCD." Prepare pipeline flow, chart structure, environment promotion, and rollback.
- "Troubleshot production issues through logs, monitoring, and SRE dashboards." Prepare one incident example with symptoms, investigation, fix, and prevention.
- "Reduced peak workload on the main database." Prepare what bottleneck existed, what changed, and how the outcome was measured.
- "Built resilient message delivery pipelines with fallback logic, retries, and monitoring." Prepare failure modes, retry strategy, alerting, idempotency, and business impact.
- "Implemented fault-tolerant pipelines with automatic retries and observability." Prepare EventBridge/queue/S3 routing details and how delivery guarantees were handled.
- "Led a team of 5 backend engineers." Prepare leadership style, task distribution, mentoring, and operational metrics.
- "Security assessments and vulnerability scans." Prepare exact involvement and avoid overstating ownership.

Clarify before interviews:

- Whether CRURATED was concurrent, contract, or separate employment during the Simple.life period.
- Whether Simple.life ended in March 2026 or is still current.
- Whether relocation or hybrid presence in Cologne is feasible.
- Whether there is unrecorded Terraform, GitLab CI, EKS, RDS, IAM, Docker, Grafana, Keycloak, Spring Boot, or ISO 27001 experience that can be truthfully added later.

## Company-Specific Preparation

Understand ACCURIDS:

- ACCURIDS builds an IDMP-native data standardization fabric and FAIR Data Registry for pharmaceutical product data.
- The product goal is to transform fragmented enterprise data into a unified, audit-ready product data backbone.
- Public materials position the product around regulated data, interoperability, compliance, analytics, and AI-ready data foundations.
- The vacancy's operations focus likely exists because reliability, security, customer deployment quality, and documentation are critical for enterprise pharma customers.

Prepare to connect your experience:

- airSlate document automation and SaaS operations: relevant to enterprise SaaS, deployment reliability, and operational maturity.
- Sixt GDPR/PCI DSS work: relevant to regulated or compliance-sensitive engineering, without claiming pharma compliance.
- Simple.life and CRURATED reliability systems: relevant to robust operations, monitoring, retries, and operational continuity.
- PDFfiller high-volume email platform: relevant to resilient infrastructure under peak load.

Avoid overclaiming:

- Do not claim prior pharma, IDMP, ISO 27001, Terraform, GitLab CI, or Keycloak ownership unless the candidate has additional evidence outside the registry.

## Preparation Plan

Must-prepare before recruiter screen:

- Clear answer on Cologne hybrid availability.
- Clear current employment and availability timeline.
- Salary range for Cologne Senior DevOps / Cloud Engineer roles.
- Two-minute explanation of backend-to-platform motivation.
- Honest English proficiency statement.

Before technical interview:

- One detailed Kubernetes migration story.
- One CI/CD/GitOps story using Helm, GitHub Actions, and ArgoCD.
- One observability/incident story.
- One AWS/event pipeline story using EventBridge, queues, S3 downstreams, retries, and backpressure.
- A Terraform ramp-up answer.
- A security/compliance support answer that stays within evidence.

Before final/culture interview:

- Examples of ownership and documentation that reduce operational dependency.
- Examples of collaboration with product, support, and engineering leadership.
- Questions about the platform roadmap, operational risk, on-call, customer deployment constraints, and security maturity.

## Questions to Ask

- What are the biggest operational risks you want this hire to reduce in the first six months?
- How are responsibilities split today between backend engineers, platform engineers, and whoever owns customer deployments?
- What parts of the AWS platform are most in need of improvement: EKS, networking, IAM, RDS, observability, CI/CD, or documentation?
- How mature are your Terraform and GitOps workflows today?
- What does incident response look like, and is there an on-call rotation?
- How do SaaS and on-premise customer installations differ technically?
- What security or ISO 27001 work would this role own versus support?
- Which observability tools are currently in production?
- What would make the first 90 days successful for this role?
- How often would you expect presence in the Cologne office?
