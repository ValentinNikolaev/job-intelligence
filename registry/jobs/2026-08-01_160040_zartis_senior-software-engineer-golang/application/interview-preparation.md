# Interview Preparation

## Recruiter / HR Screening

Likely questions:

- Why are you interested in Zartis and this Senior Software Engineer (Golang) role?
- Are you based in the European Union, and can you work from Rome, Italy?
- The Lever page says European Union / Hybrid, but the offer says 100% remote. Are you open to occasional travel or onsite meetings?
- What is your current employment status and notice period?
- What compensation range are you targeting?
- How recent and hands-on is your Golang experience?
- Have you worked in the fitness industry or with studio/gym management platforms?
- How comfortable are you with Agile, Lean, Continuous Delivery, and cross-functional product teams?
- What quality and testing practices do you use?
- How do you mentor engineers while staying hands-on?

Suggested positioning:

- Motivation: "The role fits my strongest pattern: hands-on Go backend work, reliable APIs, cloud infrastructure, CI/CD, performance, and mentoring in a distributed team."
- Domain: "I do not have direct fitness-industry experience, but I have worked on consumer digital products, subscription platforms, automation systems, and backend services where reliability and product collaboration mattered."
- Remote: "I am based in Rome and comfortable working with distributed European teams. I would like to clarify the hybrid wording because the posting also mentions 100% remote work."
- Testing: "I care about code that is easy to validate and operate. My strongest examples are CI/CD, production validation, code review, monitoring, incident learning, and improving reliability under load."

Must confirm before recruiter call:

- Current Simple.life status and whether CRURATED overlapped with it.
- Notice period and earliest start date.
- Work authorization wording for Italy/EU and sponsorship needs.
- Expected salary or contractor range.
- Whether Zartis requires office presence or accepts fully remote work from Italy.

## Culture Fit / Behavioral Interview

Likely behavioral questions:

- Tell me about a time you mentored or paired with another engineer.
- Describe a time you improved platform scalability or performance.
- Tell me about a time you worked with product managers, designers, QA, or operations.
- How do you make technical decisions when requirements are unclear?
- How do you balance simple code with future flexibility?
- Describe a time you delegated work and still kept delivery quality high.
- How do you handle feedback in code review?
- Tell me about a time you learned a new technology or system quickly.
- How do you work in a remote distributed team?
- What does good Agile or Lean delivery mean to you in practice?

STAR stories to prepare:

- Simple.life Go automation platform: situation around scaling support workflows, task to connect Zendesk, Intercom, and internal systems, actions around API orchestration, fallback logic, retries, and monitoring, result in improved operational responsiveness.
- airSlate Kubernetes migration: situation around ECS services and deployment consistency, task to prepare Kubernetes runtime, actions with Helm/GitHub Actions/ArgoCD, result in better deployment and infrastructure readiness.
- airSlate API/database performance: situation around peak load and backend bottlenecks, task to stabilize services, actions around query/API investigation and workload redistribution, result in improved stability.
- PDFfiller high-volume email service: situation around transactional messaging, task to scale service and lead engineers, actions around architecture and reliability, result around 50 million emails per month and BFCM peaks above 10x.
- Hyprr prototype-to-beta: situation around early product, task to set technical direction, actions around architecture, roadmap, CI/CD, and team coaching, result of closed beta in under 6 months.

## Technical Interview

High Priority:

- Go backend service design: packages, interfaces, error handling, context, concurrency, goroutines, channels, locks, testing boundaries, logging, and observability.
- API design: resource modeling, versioning, authentication, idempotency, error handling, pagination, documentation, and backwards compatibility.
- Scalability and performance: profiling, bottleneck analysis, caching strategy if relevant, database pressure, queueing, and operational tradeoffs.
- Cloud and AWS: service deployment, IAM awareness, networking basics, runtime configuration, observability, cost/performance thinking.
- CI/CD and DevOps: GitHub Actions, ArgoCD, Helm, release safety, rollback, deployment consistency, and production validation.
- Quality and testing principles: unit tests, integration tests, contract tests, test data, testability in design, CI checks, and what to test at each layer.
- Mentoring and code review: constructive reviews, pairing, delegation, raising standards without slowing delivery.

Medium Priority:

- Microservices: boundaries, ownership, interservice communication, observability, failure modes, data consistency, and operational complexity.
- Kubernetes: deployments, health checks, resource limits, logs, rollouts, rollbacks, and debugging.
- Product collaboration: working with product managers, QA, designers, and testers to shape deliverable increments.
- Remote collaboration: written decisions, async handoffs, explicit communication, and trust-building.

Low Priority:

- Fitness industry domain: understand the client context, but avoid pretending deep domain experience.
- Frontend/UI: relevant only as API consumer context.
- Public speaking/community contribution: nice-to-have only; discuss mentoring and internal knowledge-sharing instead unless the candidate has confirmed public examples.

Questions to defend CV claims:

- What did you build in Go at Simple.life?
- How did the API orchestration layer work?
- How did retries and fallback logic improve reliability?
- How did you identify and fix API/query bottlenecks at airSlate?
- What did the ECS-to-Kubernetes migration involve?
- How did Helm, GitHub Actions, and ArgoCD fit together?
- How did you scale PDFfiller's email service?
- How did you mentor engineers in PDFfiller, Hyprr, or airSlate?
- How do you define simple, readable, flexible code?

## CV Deep-Dive Questions

Simple.life:

- Explain the Go support automation platform architecture.
- Which services did it connect?
- Which parts were APIs, workflows, and operational tooling?
- How did you monitor and recover from failure?
- How did you work with Support Ops, Product, and AI teams?

airSlate:

- Describe your backend and infrastructure work.
- How did you improve database and API performance?
- What changed during the Kubernetes migration?
- How did CI/CD improve delivery consistency?
- What leadership responsibilities did you have?

Hyprr:

- How did you bring the product from prototype to closed beta?
- What microservice or serverless decisions did you make?
- How did you work with the CTO?
- How did you delegate and coach engineers?

PDFfiller:

- What made the transactional email service difficult?
- How did the team scale to around 50 million emails per month?
- How did you handle BFCM traffic?
- Which reliability practices mattered most?

Timeline:

- Be ready to explain Simple.life and CRURATED dates. Use confirmed facts only.

## Company-Specific Preparation

Know these verified Zartis facts:

- Zartis is a digital solutions provider across technology strategy, software engineering, and product development.
- Zartis works across financial services, MedTech/healthcare, media, logistics technology, renewable energy, EdTech, e-commerce, and other sectors.
- The role is for a fitness-industry project associated with ABC Fitness / Glofox.
- The client platform supports digital solutions in more than 60 countries for studio and gym owners.
- The role asks for Golang, cloud/AWS, Agile/Lean/Continuous Delivery, quality/testing principles, mentoring, and scalability/performance work.
- Zartis careers material says the company has 300+ people, 60+ teams, remote-first distributed work across EMEA and LATAM, 50+ tech stacks, and benefits around training, WFH support, mentoring, coaching, and wellbeing.
- The role page contains a remote/hybrid ambiguity: top label says Hybrid, benefits say 100% Remote Work.

Translate experience to Zartis:

- Golang: Simple.life Go backend platform.
- Cloud/AWS/DevOps: airSlate and Hyprr.
- Scalability/performance: airSlate database/API work and PDFfiller high-volume messaging.
- Mentoring: PDFfiller team lead, Hyprr technical lead, airSlate planning/interviews.
- Cross-functional work: Simple.life with Support Ops/Product/AI and airSlate with product/development planning.
- Quality: CI/CD, code review, production troubleshooting, monitoring, and reliability.

Avoid unsupported claims:

- Do not claim direct Glofox or fitness-industry experience.
- Do not claim public speaking or author history unless confirmed.
- Do not claim current employment dates without reconciling source conflict.
- Do not claim the role is fully remote until Zartis confirms the hybrid wording.

## Preparation Plan

Must prepare before recruiter call:

- Confirm Simple.life and CRURATED timeline.
- Confirm notice period, earliest start date, and compensation range.
- Prepare a concise answer on remote/hybrid expectations from Rome.
- Prepare a 60-second story about the Simple.life Go platform.

Before technical interview:

- Refresh Go concurrency, context cancellation, error handling, interfaces, and test structure.
- Prepare a backend API design walkthrough.
- Prepare one scalability/performance story from airSlate.
- Prepare one CI/CD/Kubernetes story from airSlate.
- Prepare one mentoring/code-review story from PDFfiller or Hyprr.

Before final or culture interview:

- Read Zartis careers values and project context.
- Prepare examples of working in distributed teams and consulting/product-adjacent environments.
- Decide how to discuss lack of fitness-domain experience as a manageable ramp-up.

## Questions to Ask

- The Lever page says European Union / Hybrid, while benefits mention 100% remote work. What is the actual remote expectation for someone based in Rome?
- Which part of the ABC Fitness / Glofox platform would this role support first?
- How is the Golang codebase organized today, and what are the main scalability priorities?
- What AWS services and CI/CD tooling does the team use?
- How does the team define quality and testing expectations for backend services?
- What does mentoring look like in this team: pairing, code review, design reviews, onboarding, or delegation?
- How do product managers, designers, developers, and testers collaborate day to day?
- What would success look like after the first 90 days?
- Are engineers expected to work across multiple Zartis client projects or stay focused on this client?
