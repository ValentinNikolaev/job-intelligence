## Recruiter / HR Screening

Likely questions:

- Why are you interested in Blackbird Lab and this client role?
- Are you comfortable working remotely with an international team?
- What is your current location and preferred working arrangement?
- What is your English level in daily engineering communication?
- What is your notice period and availability?
- What compensation range are you targeting?
- Are you comfortable with on-call rotations and production support?
- Can you explain your recent Simple.life and CRURATED timeline?
- Do you prefer PHP, Go, or mixed backend roles?
- Have you used AI tools in your engineering workflow?

Suggested positioning:

- Interest: "The role combines PHP, Go, AWS, Kubernetes, event-driven backend systems, and senior ownership. That is close to the systems I have built and led."
- Remote: "I work from Rome and am comfortable with remote, async collaboration with product and engineering teams."
- English: "I use English for professional communication. I can discuss architecture, tradeoffs, incidents, and delivery planning in English."
- On-call: "I have production troubleshooting and incident-response experience. I would like to understand the rotation frequency, escalation rules, and support boundaries."
- Timeline: Prepare a direct explanation of the Simple.life and CRURATED overlap based on the real engagement structure. Do not improvise.

## Culture Fit / Behavioral Interview

Likely behavioral questions:

- Tell me about a time you owned a backend service from design to production.
- Describe a production issue you troubleshot and how you handled it.
- Give an example of mentoring engineers through code review.
- Tell me about a technical decision you influenced across a team.
- Describe a time you reduced technical debt while delivering product work.
- How do you work with Product, Design, QA, or Data stakeholders?
- Tell me about a time you improved CI/CD or release reliability.
- How do you use AI tools without lowering code quality?
- Describe a situation where you had to balance speed and correctness.
- How do you communicate in async remote teams?

STAR stories to prepare:

- airSlate Kubernetes migration: Situation: managed services on ECS. Task: prepare services for Kubernetes. Action: Helm charts, GitHub Actions, ArgoCD, service migration. Result: 30% cost cut and over 20% performance boost.
- CRURATED event analytics: Situation: product metrics and reporting needed scalable event infrastructure. Task: build reliable analytics routing. Action: queues, EventBridge, versioned schemas, S3/webhook downstreams. Result: 10x throughput and 99.9% delivery reliability.
- PDFfiller email service: Situation: transactional email volume grew. Task: scale the service and lead backend team. Action: messaging architecture, technical decisions, delivery infrastructure, team coaching. Result: 50 million monthly emails and BFCM readiness.
- Simple.life support automation: Situation: support team needed scalable automation. Task: own backend integrations. Action: API orchestration, retries, fallback logic, monitoring, Intercom migration. Result: lower disruptions, faster first response, better resolution rates.
- airSlate database/API optimization: Situation: peak load risk. Task: reduce bottlenecks. Action: query and API optimization, monitoring, SRE dashboards. Result: database load lowered and API response times improved.

## Technical Interview

High Priority:

- PHP backend architecture: Laravel/Symfony service design, dependency boundaries, clean code, SOLID, testing.
- Go backend systems: API design, concurrency basics, service ownership, production readiness.
- Event-driven systems: queues, delivery guarantees, retries, backpressure, idempotency, failure handling, schema versioning.
- AWS: practical experience with EventBridge and S3; prepare to discuss how experience maps to Lambda, API Gateway, and SQS/SNS.
- Kubernetes and Docker: deployments, Helm, CI/CD, service migration, operational tradeoffs.
- System design: scalable distributed services, API contracts, platform components, shared services, fault tolerance.
- Production troubleshooting: logs, metrics, dashboards, incident triage, performance bottlenecks.

Medium Priority:

- Databases: MySQL, PostgreSQL, Elasticsearch, query optimization, peak load reduction.
- CI/CD: GitHub Actions, ArgoCD, release consistency, pipeline improvements.
- Automated testing: unit and integration testing practices, testable code, legacy-system constraints.
- AI-assisted development: practical benefits, code-review guardrails, limitations, privacy and security boundaries.
- Security/compliance: GDPR, PCI DSS, system audits, risk awareness from Sixt.

Low Priority:

- Open-source library maintenance: vacancy lists it as nice to have, but candidate records do not show direct evidence.
- Mobile-specific backend concerns: prepare adjacent examples, but do not claim direct mobile backend ownership unless you have additional evidence.
- Retail marketing domain: know the product context, but the technical screen will likely focus on backend scalability and reliability.

Technical questions to rehearse:

- Design an event-driven service that processes high-volume offer or promotion events.
- How would you make a queue consumer idempotent?
- How do you handle retries, dead-letter queues, and backpressure?
- How would you design APIs shared by multiple internal teams?
- What changes when a backend supports high-traffic mobile applications?
- How do you migrate a service from ECS to Kubernetes?
- How do you structure a PHP service for testability?
- How do you decide between synchronous APIs and asynchronous messaging?
- How do you debug rising latency in a production API?
- How do you use AI tools in development while preserving code quality?

## CV Deep-Dive Questions

Prepare clear answers for:

- Simple.life: What exactly did you own in the Go support automation platform?
- Simple.life: How did fallback logic and retries reduce incident disruption?
- CRURATED: What was the event schema design and how did it improve integration speed?
- CRURATED: How did EventBridge fit into the analytics routing architecture?
- airSlate: What services moved from ECS to Kubernetes, and what did Helm/ArgoCD change?
- airSlate: How did you measure the 30% cost cut and over 20% performance boost?
- airSlate: What caused the database load reduction to 65%?
- Hyprr: What did you personally lead versus what the CTO owned?
- PDFfiller: What were the hardest scaling problems in the email service?
- Sixt: What did GDPR or PCI DSS change about backend engineering practice?

Claims to defend carefully:

- 15+ years backend experience: keep the explanation brief and focus on the last 10 years for detailed examples.
- Go experience: use Simple.life, CRURATED, and Hyprr examples.
- PHP experience: use airSlate, PDFfiller, Hyprr, and Sixt examples.
- AWS experience: be precise about EventBridge, S3, ECS, and AWS-backed infrastructure. Do not overclaim Lambda or API Gateway if not used.
- Messaging: explain RabbitMQ, queues, EventBridge, retries, backpressure, and delivery guarantees. Say Kafka/SQS/SNS are not the exact tools from the source CV if asked directly.
- AI tools: discuss LLM-assisted support automation and practical engineering use with review and privacy safeguards.

## Company-Specific Preparation

What to know:

- Blackbird Lab is a Ukrainian software development company with 90+ people and an engineering-led culture.
- The company says it works with US and Canadian product companies and values async communication, flexible work, and technical decision-making.
- This role supports Flipp and Shopfully mobile applications for a large-scale digital platform used by millions of users.
- Flipp and Shopfully are connected to drive-to-store marketing, retail offers, merchandising, and shopper engagement.

Prepare examples around:

- High-traffic backend reliability.
- Event-driven architecture for product data or user events.
- Shared internal backend services and platform thinking.
- Production support and incident handling.
- Collaboration with Product, Design, QA, and Data.
- Mentoring through architecture review and code review.

Questions to clarify:

- Which backend services are PHP and which are Go?
- What is the current architecture around messaging and event processing?
- Which AWS services are most used in production?
- How often does on-call happen and what incidents does the team handle?
- What is the balance between client delivery and internal platform work?

## Preparation Plan

Must prepare before recruiter screen:

- One-minute pitch connecting PHP, Go, AWS, Kubernetes, event-driven systems, and senior ownership.
- Clear answer about remote work from Rome and timezone overlap.
- Clear answer about English level.
- Transparent explanation of recent timeline overlap.
- Position on on-call willingness and questions about rotation expectations.

Before technical interview:

- Review EventBridge, queues, retries, idempotency, dead-letter handling, and backpressure.
- Refresh Kubernetes migration story: ECS to Kubernetes, Helm, GitHub Actions, ArgoCD, cost/performance outcomes.
- Prepare one PHP design-pattern/testing example from Laravel/Symfony work.
- Prepare one Go service ownership example from Simple.life or CRURATED.
- Prepare a system design outline for a high-traffic offers backend.

Before final or culture interview:

- Prepare leadership examples from airSlate, Hyprr, and PDFfiller.
- Prepare examples of async communication and cross-functional decision-making.
- Prepare questions about engineering culture, ownership boundaries, and client collaboration.
- Decide how to discuss AI-assisted engineering with practical guardrails.

## Questions to Ask

- What are the main backend services this role will own in the first three months?
- How is responsibility split between PHP and Go services?
- What event broker or messaging stack does the team use in production?
- What does on-call look like: frequency, escalation, severity, and compensation?
- Which AWS services are central to the current architecture?
- How does the team define service ownership from design through production support?
- What are the biggest reliability or scalability problems the team wants to solve this year?
- How do Product, Design, Quality, Data, and Engineering collaborate day to day?
- What practices does the team use for code review, testing, and CI/CD quality gates?
- How does Blackbird Lab balance client expectations with sustainable engineering quality?
