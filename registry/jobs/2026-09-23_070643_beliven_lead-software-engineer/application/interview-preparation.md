## Recruiter / HR Screening

Prepare a concise motivation answer: the role combines technical leadership, project evolution, collaboration, and structured development. Say that the application is grounded in backend delivery and technical-lead evidence, not in unverified frontend claims. Confirm location, ability to attend four office days each month, preferred office, salary expectations, notice period, English comfort, and work authorization only from the candidate’s actual circumstances; these are unknown in the evidence. For job change, explain the target role as an interest in hands-on technical leadership without inventing dissatisfaction or a personal connection to Beliven.

Likely screen: “Why Beliven?” Answer from the posting: its hybrid model, individual and team training, and structured feedback are documented; avoid claiming product use. “Why lead now?” Use Hyprr’s roadmap work with the CTO [cv-hyprr] and PDFfiller’s five-engineer team [email-team]. “What is your frontend level?” State that modern JavaScript/framework experience is not established by the submitted evidence and ask which framework and delivery depth are required.

## Culture Fit / Behavioral Interview

Prepare 7 STAR outlines, each with only sourced facts:

1. Leadership: leading 5 backend engineers on a transactional email service at PDFfiller [email-team].
2. Technical direction: defining Hyprr’s technology roadmap with the CTO [cv-hyprr].
3. Delivery pace: bringing Hyprr’s product from prototype to closed beta in under 6 months [cv-hyprr].
4. Reliability: removing airSlate database bottlenecks and redistributing workload [database-reliability].
5. Delivery readiness: preparing airSlate’s Kubernetes stack with Helm, GitHub Actions, and ArgoCD [kubernetes-migration].
6. Product-support integration: connecting Zendesk, Intercom, and internal services at Simple.life [support-platform].
7. Automation outcome: auto-triage flows that automated or deflected up to 30% of inbound tickets [support-triage].

For each, prepare Situation, Task, Action, Result, and a lesson. Do not supply unstated conflict, coaching, stakeholder, or project-count details. Likely behavioral questions: how do you set direction; how do you handle an unreliable service; how do you make trade-offs; how do you collaborate across functions; how do you support developers; how do you respond to uncertainty; and how do you prioritize concurrent work. For the last topic, say the evidence does not establish two-project ownership, then describe only a real example if the candidate can attest to one.

## Technical Interview

**High Priority — PHP, Laravel, REST APIs, and MVC.** The posting names these directly, while verified Hyprr context includes PHP, Laravel, and REST APIs [cv-hyprr]. Review API resource design, authentication boundaries without asserting Sanctum experience, error handling, versioning, observability, and backward-compatible changes.

**High Priority — relational databases and reliability.** Be ready to explain airSlate’s database bottleneck removal precisely: reduced peak load by removing bottlenecks and redistributing workload, improving stability in high traffic [database-reliability]. Prepare principles for query diagnosis, indexes, schema trade-offs, contention, load redistribution, rollback, and how to measure improvement. Do not state SQL expertise beyond what the candidate can demonstrate.

**High Priority — CI/CD and platform delivery.** Explain the ECS-to-Kubernetes migration preparation using Helm, GitHub Actions, and ArgoCD [kubernetes-migration]. Review deployment manifests, rollout strategies, configuration, health checks, observability, and recovery. Avoid claiming ownership not in the record.

**High Priority — leadership and architecture.** Defend the Hyprr roadmap and core-stack decisions with the CTO [cv-hyprr], including how decisions were communicated and revisited. The interviewer may ask how a five-engineer team was led at PDFfiller [email-team]. Be exact about individual actions versus team outcomes.

**Medium Priority — JavaScript and frontend framework.** The posting requires JavaScript ES6+ and React, Angular, or Vue. This is a gap, so ask whether the lead must contribute daily frontend code and answer with truthful current capability. Do not turn older or general experience into current Angular.

**Medium Priority — testing.** The job desires automated testing. Explain actual testing practice only if the candidate can substantiate it; ask which tools and expectations Beliven uses.

**Low Priority — TypeScript, RxJS, CSS preprocessing, Laravel ecosystem tools.** These are desired rather than required and are not documented. Learn the vocabulary, but do not claim experience.

## CV Deep-Dive Questions

Expect: “What did you personally do to reduce database load?” Use the exact airSlate claim and distinguish it from team work. “How did the Kubernetes migration work?” Explain that the verified record says services moved from ECS and the runtime stack was prepared with Helm, GitHub Actions, and ArgoCD [kubernetes-migration]. “How did you lead the email-service team?” Anchor the answer in leading five backend engineers [email-team]. “What was the roadmap contribution?” State that you defined it with the CTO and helped establish the core stack [cv-hyprr]. “How did the email service scale?” State only around 50 million emails per month [email-scale]. “What was the Simple.life platform?” Say it connected Zendesk, Intercom, and internal services [support-platform].

## Company-Specific Preparation

Review the Beliven posting before each interview. The role says the selected person will support the Dev team and contribute to project evolution. It specifies four office days per month, individual training, team training, and structured one-to-one feedback. Prepare questions that show interest in the operating model without claiming company knowledge beyond the posting. Confirm the team size, project count, framework, frontend responsibilities, decision rights, and office location. The posting is the research source: [Beliven Lead Software Engineer](https://careers.beliven.com/recruiting/details/lead-software-engineer).

## Preparation Plan

**Must prepare:** a 90-second role-fit introduction; Hyprr roadmap; PDFfiller team leadership; airSlate reliability; clear answers on JavaScript/frontend and travel gaps. **Pre-technical:** refresh PHP/Laravel, REST API design, relational-database diagnosis, Kubernetes deployment concepts, CI/CD, and testing terminology. **Pre-final/culture:** prepare questions about feedback, growth, team collaboration, hybrid expectations, success measures, and the relationship between project managers and the lead. Rehearse all metrics exactly: under 6 months, 5 engineers, 50 million emails per month, and 30% inbound tickets.

## Questions to Ask

1. Which frontend framework is in active use, and what hands-on contribution is expected from the lead?
2. How many projects and developers would this role directly support in the first six months?
3. How are technical decisions shared among the lead, project managers, and stakeholders?
4. What does successful project evolution look like after 90 days?
5. Which PHP, Laravel, database, and API challenges are most immediate?
6. How are CI/CD, automated testing, and operational ownership handled today?
7. Which office is associated with the four required monthly days, and how is scheduling managed?
8. How do structured feedback and individual training influence technical growth?
