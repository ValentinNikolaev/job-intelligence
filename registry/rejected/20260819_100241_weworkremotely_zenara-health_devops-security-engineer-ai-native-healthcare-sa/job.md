# DevOps & Security Engineer - AI-Native Healthcare SaaS

Posted: 2026-08-18T20:34:31Z

## Rejection

- Category: tech_stack
- Reason: role does not mention Go/Golang or PHP

**Headquarters:** India

### About the Company

Zenara Health is a mental healthcare organization driven by technology, aiming to improve the accessibility and quality of mental wellness services. By integrating AI-driven platforms with professional clinical care, we deliver personalized and effective mental health solutions, creating a smooth digital experience for both patients and providers. We operate as a startup, distinct from a mere department.

### Why This Role Exists

**This position serves as the company's foremost line of defense.**

You will operate under the assumption that systems are constantly under threat, crafting infrastructure that is resilient, auditable, and inherently secure. You will be the most risk-aware individual in the startup — and that’s exactly what we require. While others concentrate on feature rollout, you will prioritize the security of patient data, regulatory compliance, and system integrity.

### About the Role

**If your understanding of DevOps is limited to "I occasionally execute kubectl apply," this position is likely not for you.**

**This role is not suited for those who prioritize speed over safety or view security as an afterthought to be addressed later.** At Zenara, safeguarding patient data and maintaining system integrity takes precedence over rapid deployment.

Our team is in the process of developing a platform that manages clinical data, operates AI workflows, and processes insurance billing — all within a HIPAA-regulated environment catering to real psychiatric practices. Our infrastructure is operational; however, we lack an individual who will take ownership with a security-first perspective. We currently do not have a dedicated CI/CD owner, a comprehensive security posture, or monitoring that extends beyond simple uptime checks. If HIPAA auditors were to arrive tomorrow, we could withstand the scrutiny — but it wouldn’t be a pleasant experience.

You will be responsible for Zenara’s infrastructure, security posture, and compliance engineering — everything from the ground up. This includes CI/CD pipelines, HIPAA-compliant deployment automation, monitoring and alerting systems, cybersecurity measures and threat defense, access controls, and audit logging — the complete spectrum of "essential elements that ensure the safe operation of a healthcare company."

However, your role will go beyond mere maintenance. You will also develop infrastructure for our AI platform, encompassing model serving, scaling AI workloads, and supporting production AI pipelines. You will have a dual mandate: ensure the stability and security of the platform while also building the necessary infrastructure for AI at scale.

**This represents a unique opportunity for greenfield infrastructure engineering within a healthcare AI company with genuine compliance obligations and real users.** You will devise systems from fundamental principles, make architectural choices, establish best practices to guide us through growth and compliance audits, and serve as the ultimate security gatekeeper.

### What You Will Own

### 1. Cybersecurity & Threat Defense

You will manage threat modeling, reduce attack surfaces, oversee intrusion detection, handle vulnerability management, and plan incident responses. You will be the final reviewer for infrastructure and security risks, possessing the authority to halt releases that do not satisfy security or compliance criteria. The security of patient data is non-negotiable.

### 2. CI/CD and Deployment Automation

You will design and implement CI/CD pipelines for all Zenara products, establishing deployment automation, managing environments, and setting quality thresholds. Your goal is to eliminate chaotic releases and establish a system that enables the team to deploy confidently and consistently — without compromising security.

### 3. Security Posture and HIPAA Compliance

You will develop and uphold a HIPAA-compliant security posture across all Zenara systems. This involves implementing access controls, managing secrets, maintaining audit logs, and enforcing encryption standards. You will ensure our adherence to regulatory requirements while avoiding bureaucratic slowdowns.

### 4. Monitoring, Alerting, and Incident Response

You will create monitoring and alerting capabilities to proactively identify issues before they affect users. You will establish incident response protocols, define service level objectives (SLOs), and monitor reliability metrics. You will lead the on-call rotation and develop runbooks for common incidents.

### 5. AI Infrastructure Support

You will address the AI infrastructure needs, including model serving, GPU provisioning (if necessary), and autoscaling for AI workloads. You will collaborate with the Head of AI to ensure that the infrastructure supports production AI efficiently and securely.

### 6. Cloud Infrastructure Management

You will oversee cloud infrastructure (AWS/Azure), focusing on cost optimization, reliability, disaster recovery, and capacity planning. You will make architectural decisions that find a balance between cost, performance, and compliance obligations.

### 7. SOC 2 Readiness

You will spearhead SOC 2 Type II preparedness as we approach fundraising, implementing necessary controls, organizing evidence collection, and liaising with auditors. You will ensure compliance becomes an integrated process rather than an ad-hoc measure.

### 8. Security Incident Response

You will take charge of security incident response, establishing procedures, conducting regular security evaluations, and responding to incidents as they arise. Your efforts will help the organization recognize security as an essential discipline rather than an afterthought.

### Your First 90 Days

**Week 1-2:** Fully immerse yourself in the current infrastructure, deployment processes, and security posture. Identify the most significant security vulnerabilities and critical gaps. Build rapport through active listening and insightful inquiries.

**Month 1:** Set up basic monitoring and alerting systems. Outline the CI/CD roadmap. Begin documenting existing systems and security protocols. Establish communication channels with engineering leadership. Conduct initial threat assessments.

**Month 2-3:** Develop CI/CD pipelines for high-priority services with security gates. Implement secrets management and access controls. Create the first set of operational and security runbooks. Initiate SOC 2 gap analysis and planning for remediation. Introduce intrusion detection and vulnerability scanning.

**Ongoing:** Take on full ownership of infrastructure and security. Deliver reliable and secure systems. Establish compliance practices and enhance security standards. Assertively say “no” when risks are unacceptable. Inspire confidence in the CEO that infrastructure and security are in capable hands.

### Values & Vibe (Who You Are)

You perceive infrastructure primarily through the lens of **security and reliability**, rather than merely uptime. You are the one who enters an unmanaged infrastructure landscape and brings order — not through an excess of tools, but through clarity, automation, and effective monitoring. For you, security is not a mere checklist; it shapes your worldview.

You possess an **innate sense of paranoia** — assuming systems are under threat and designing with that understanding. You find an infrastructure environment that functions like a black box, relying on heroic measures rather than standard practices, to be unacceptable. You recognize that healthcare compliance is mandatory and understand how to implement it practically, without hindering development speed.

You are hands-on enough to diagnose production issues, write Terraform modules, and review security configurations — yet you know that your primary responsibility lies in creating systems that are both reliable and secure, rather than solely reacting to incidents. You have successfully built infrastructure in regulated sectors while adhering to compliance constraints.

You have considered issues related to security threats, compliance frameworks, and disaster recovery — moving beyond the simplistic notion of "we use AWS defaults." You understand the trade-offs between security, cost, developer experience, and compliance requirements. When faced with uncertainty, your choice will always be security.

You are **comfortable saying “no”** when risks are unacceptable, even if it delays feature deployment. This is not obstruction; it is part of your role.

### What Success Looks Like

- The infrastructure is both reliable and secure — the CEO no longer concerns themselves with outages or breaches.
- CI/CD pipelines are in place and delivering regularly — deployments become routine, low-risk, and security-gated.
- **The cybersecurity posture is robust** — threat modeling is thorough, attack surfaces are minimized, and vulnerabilities are monitored for remediation.
- The security posture is firm — access controls, audit trails, and secrets management are strictly enforced.
- Monitoring and alerting systems identify issues before they are reported by users.
- HIPAA compliance is systematic — we are audit-ready without frantic preparations.
- AI infrastructure supports production workloads reliably and cost-effectively.
- **A security review process is established** — any risky releases are identified and halted prior to shipping.
- Incident response is documented and efficient — problems are resolved swiftly.
- The infrastructure and security posture are more robust, reliable, and compliant than upon your arrival.

### Required

- **5-10 years of experience in DevOps, SRE, or Platform Engineering** — you have designed and maintained large-scale production infrastructure.

- **A strong security mindset: naturally cautious, detail-focused, and able to express concerns when risks are too high.** For you, security is not merely a feature; it is a fundamental necessity.

- **Familiarity with HIPAA, SOC 2, or healthcare compliance frameworks** — you comprehend BAAs, audit trails, and regulatory obligations. You have successfully implemented compliant systems.

- **Proficient in AWS or Azure with infrastructure-as-code** (Terraform, Pulumi, or CloudFormation) — you handle infrastructure through programming rather than manual console operations.

- **CI/CD pipeline design and implementation** (GitHub Actions, CircleCI, Jenkins, or similar) — you have developed deployment automation from the ground up.

- **Experience in container orchestration** (Kubernetes, ECS, or equivalent) — you know how to deploy and scale applications in containers.

- **Skills in cybersecurity**: including threat modeling, vulnerability assessment, intrusion detection, and incident response.

- **Strong English communication skills** — You operate asynchronously and provide clear written documentation, incident reports, and architectural designs.

- **Experience in startup or high-growth environments** — You have thrived in situations marked by uncertainty, constrained resources, and pressing deadlines.

### Strongly Preferred

- Experience in supporting ML/AI infrastructure (model serving, GPU clusters)

- Security expertise in healthcare SaaS (handling PHI, encryption at rest/transit, access auditing)

- Background in penetration testing or security audits

- Prior experience with SOC 2 or HITRUST certification processes

- Knowledge of observability and monitoring tools (Datadog, Prometheus, Grafana, or similar)

### Nice to Have

- Understanding of FHIR/HL7 healthcare data standards

- Production experience with Kubernetes

- Acquainted with multi-tenant SaaS security strategies

- Exposure to mental health or behavioral health sectors

- Experience with cloud infrastructure cost optimization

- Relevant security certifications (CISSP, CEH, or equivalent)

### Schedule

Evening IST hours with **4–8 hours of daily overlap with US Pacific** (9am–5pm PT). You are welcome to propose a schedule that works best for you — our emphasis is on overlap and team availability rather than rigid clock-in requirements. On-call availability is expected during key security incidents.

- Salary between ₹22–35 LPA, based on your skills and responsibilities

- Fully remote work options available throughout India

- Provision for equipment allowance

- Acknowledgment of culturally significant local holidays (India)

- Flexible paid leave options

- Direct and regular communication with the CEO — you will have direct access without any intermediaries

- Opportunity to build infrastructure and security practices from the ground up

**To apply:** [https://weworkremotely.com/remote-jobs/zenara-health-devops-security-engineer-ai-native-healthcare-saas](https://weworkremotely.com/remote-jobs/zenara-health-devops-security-engineer-ai-native-healthcare-saas)
