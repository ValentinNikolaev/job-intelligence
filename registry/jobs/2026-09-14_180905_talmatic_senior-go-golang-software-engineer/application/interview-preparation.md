## Recruiter / HR Screening

Expect Talmatic to confirm the remote EU contract, unnamed end client, English communication, start timing, and three hours of Eastern US overlap. State only what is documented: you work from Rome and should confirm a regular afternoon overlap block before representing it as agreed. Ask whether Talmatic employs the contractor or acts as an intermediary, who signs the contract, and who owns day-to-day prioritization. The candidate record does not confirm notice period or earliest start date.

For motivation, say that you want a hands-on technical-lead role close to backend architecture and reliable delivery. Do not claim financial-crime, platform, Neo4j, Python, Node.js, React or TypeScript experience. Work-authorization wording still needs confirmation.

## Culture Fit / Behavioral Interview

Prepare these behavioral questions and use only the documented experience as the basis for a STAR answer:

1. **Tell us about ownership under operational pressure.** Use Simple App: design and ownership of the Go support platform; at least 20,000 ordinary monthly tickets and up to three times that in the US peak season. Explain your personal operational scope and distinguish it from work done by others.
2. **Describe a time you made an architecture decision with limited process.** Use Hyprr: technology roadmap work with the CTO and product progress from prototype to closed beta in less than six months. Be ready with a real design decision; do not invent a trade-off.
3. **How have you improved a production system?** Use airSlate: database bottleneck removal and workload redistribution improved stability during high traffic.
4. **How do you investigate incidents?** Use airSlate logs, monitoring and SRE dashboards, then explain the diagnostic sequence actually used.
5. **How do you share knowledge?** Use verified airSlate onboarding, knowledge sharing, technical interviews, planning and technical monitoring. Present this as technical leadership, not formal people management.
6. **How do you communicate with product partners?** Use airSlate planning and roadmap context, and describe concrete communication habits without claiming client ownership.
7. **Why change roles now?** Tie the answer to continued hands-on backend architecture and reliable delivery, without negative commentary on previous employers.

For every answer, state context, contribution and supported outcome. Acknowledge the lack of direct fintech or graph-database evidence.

## Technical Interview

**High priority — system design.** The posting explicitly says system design is central. Rehearse the Go support platform: service boundaries, integration contracts, API orchestration, lifecycle tracking, monitoring, operations, and peak-load handling. Discuss only known components: Zendesk, Intercom, internal services, Go, monitoring and Grafana-backed metrics.

**High priority — SQL and database performance.** Build a structured approach: reproduce and bound the problem; inspect query shape, indexes, waits, resource saturation and application behavior; make one reversible change; observe the result; document the outcome. Use the airSlate story about removing bottlenecks and redistributing workload to reduce peak database load and improve stability. Do not attribute a specific percentage or AWS migration to yourself.

**High priority — distributed production troubleshooting.** Explain logs, monitoring and SRE dashboards as evidence sources, distinguish symptoms from causes, establish a timeline, protect the service, and add follow-up observability.

**Medium priority — AWS and containers.** The CV supports AWS and Kubernetes exposure, Helm, ArgoCD and GitHub Actions as skills, but the candidate cannot confirm the specific airSlate ECS-to-Kubernetes migration. Be ready to explain concepts and actual scope, never claim that unconfirmed migration as an achievement.

**Medium priority — Go coding and backend breadth.** Refresh Go concurrency, cancellation, error handling, HTTP APIs, testing, interfaces, profiling and safe rollout patterns. Be candid about unconfirmed Python, Node.js, React or TypeScript experience.

**Low priority — Neo4j and financial-crime domain.** Learn graph data-modeling basics and investigation-platform concerns, while stating clearly that you lack claimed Neo4j or financial-services production experience.

## CV Deep-Dive Questions

Expect a detailed review of Simple App ticket volume, personal operational ownership, automation scope and measurement. The accurate answer is that the metric combines internal Intercom and backend metrics exported to Grafana, and that you implemented many but not all scenarios.

For airSlate, expect a request to explain the database bottleneck, signals used, workload redistribution, and production-fix process. Be ready to separate supported outcomes from broad tool experience. For Hyprr, expect questions about the CTO roadmap, the product's path to closed beta, and a specific architecture decision. For CRURATED, explain that the work was a concurrent part-time consulting engagement and describe only the production ownership documented for DataLake, event-version publication and the Crutrade integration.

## Company-Specific Preparation

Talmatic's public position is as the staffing intermediary. The end client is unnamed, although the posting says its product is a financial-crime investigation platform used by financial institutions and global companies. Before a technical round, ask for the end-client name, product boundary, principal data sources, current Go-service estate, expected frontend contribution, database and search choices, compliance constraints, and system-design format. This information is necessary to tailor architecture answers; do not infer it from the job title.

Explain why high-accountability SaaS systems are a credible match through the Go support platform, operational monitoring, database stability and technical roadmaps. Ask what success in six months and shared on-call ownership look like.

## Preparation Plan

**Must prepare:** rehearse a 10-minute Simple App system-design walkthrough; a five-minute airSlate SQL and production-diagnosis story; and a concise Hyprr roadmap story. Confirm availability, notice period, salary expectations, work authorization and Eastern-US overlap before committing to any answer. Review Go concurrency, cancellation, HTTP services, SQL diagnostics, observability, APIs and safe production changes.

**Before the technical round:** learn the end-client name and system context; map your design explanation to their data sensitivity and workflow; prepare questions about Neo4j, Elasticsearch, PostgreSQL, AWS managed services, on-call, RFC process and code review. Practise explaining documented achievements in plain English without relying on unconfirmed imported metrics.

**Before the final or culture round:** prepare questions about decision rights, collaboration, delivery expectations and contract logistics. Rehearse an honest gap answer for fintech, formal mentoring and named frontend or scripting tools.

## Questions to Ask

1. Who is the end client, and what part of the financial-crime investigation workflow would this role own?
2. What problem should the successful engineer solve in the first six months?
3. How is the system-design interview structured, and what system context can you share beforehand?
4. Which Go services, AWS managed services, relational databases, Neo4j and Elasticsearch components are in active use?
5. How is on-call organized: frequency, escalation path, observability and incident ownership?
6. What does the required Eastern-US overlap look like in the team's normal week?
7. What share of the role's 20% frontend work is React/TypeScript delivery versus architecture and collaboration?
8. What does Talmatic handle after placement, and who manages performance and contract renewal?
