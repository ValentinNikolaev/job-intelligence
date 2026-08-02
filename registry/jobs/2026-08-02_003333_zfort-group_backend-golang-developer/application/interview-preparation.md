# Interview Preparation

## Recruiter / HR Screening

Likely questions:

- Why are you interested in this Backend/Golang Developer role?
- Are you comfortable working remotely with a Ukrainian/international team?
- What is your current location and preferred working timezone?
- What is your English level for business communication?
- What is your notice period and earliest start date?
- What are your salary expectations?
- Do you need visa sponsorship or any specific contract arrangement?
- How much hands-on Go experience do you have?
- Have you worked with gRPC in production?
- Why are you moving from your current or most recent role?

Suggested positioning:

- Motivation: "I am looking for a hands-on backend role where I can work on Go services, reliability, platform design, and technical leadership close to production systems."
- Location: Rome, Italy, comfortable with remote work and CET-compatible collaboration.
- English: professional working / upper-intermediate based on the application profile; be ready to interview in English.
- gRPC: be transparent. The source CV supports REST APIs, microservices, service ownership, and reliable backend integrations, but does not prove production gRPC. Prepare to explain adjacent experience and ramp-up approach.
- Availability, work authorization, and salary: confirm before applying or screening because the profile marks these as TODO_CONFIRM.

## Culture Fit / Behavioral Interview

Likely behavioral questions:

- Tell us about a backend system you owned end to end.
- Describe a production reliability issue you investigated and improved.
- How do you approach code reviews without slowing delivery?
- Give an example of mentoring or leading backend engineers.
- How do you make architectural decisions when requirements are incomplete?
- Describe a time you improved system scalability or performance.
- How do you collaborate with product or operations teams?
- Tell us about a migration you led or contributed to.
- How do you balance hands-on coding and technical leadership?

STAR stories to prepare:

- Simple.life support automation platform: situation around support scale, task of building Go backend orchestration, actions around Zendesk/Intercom integrations, retries, monitoring, and result of improved operational workflows and up to 30% ticket automation/deflection.
- airSlate ECS-to-Kubernetes migration: situation around service runtime and operational cost/performance, task of preparing Kubernetes deployment, actions with Helm, GitHub Actions, ArgoCD, and result of cost/performance improvements from the LinkedIn source.
- PDFfiller transactional email service: situation around high-volume email, task of scaling and leading a team, actions around infrastructure and technical decisions, result around 50 million emails per month and BFCM traffic peaks.
- Hyprr prototype-to-beta delivery: situation around early product build, task of leading delivery, actions around microservices, CI/CD, reliability, and result of closed beta in under 6 months.

## Technical Interview

High Priority:

- Go backend design: interfaces, package boundaries, error handling, context cancellation, concurrency basics, goroutines/channels, worker pools, graceful shutdown.
- Microservices architecture: service boundaries, API contracts, versioning, failure isolation, retries, idempotency, circuit breakers, and observability.
- REST APIs: request validation, authentication/authorization patterns, pagination, rate limiting, backward compatibility, error schemas.
- Reliability and uptime: fallback logic, retries with backoff, dead-letter handling, monitoring, alerting, incident debugging.
- System design for real-time user-facing backend: event flow, latency, throughput, data consistency, scaling, caching, and failure modes.
- Code reviews and technical leadership: review standards, mentoring, tradeoff explanation, delivery ownership.

Medium Priority:

- gRPC: service definitions, protobuf basics, streaming concepts, deadlines, status codes, backward-compatible schema evolution. The candidate should prepare from adjacent microservice/API knowledge and avoid overstating direct experience.
- Backend testing: unit tests, integration tests, contract tests, test doubles, test data, CI checks, and testing distributed failure paths.
- Kubernetes and CI/CD: deployments, Helm, rollout safety, service monitoring, and troubleshooting.
- Databases: MySQL/PostgreSQL query performance, indexes, transactions, bottleneck investigation.
- Queues and event-driven systems: RabbitMQ, retries, backpressure, delivery guarantees, duplicate handling.

Low Priority:

- Cross-selling business domain: prepare enough to ask good product questions, but do not present domain expertise.
- Frontend/mobile details: the role is backend-focused.

## CV Deep-Dive Questions

Prepare crisp answers for:

- What exactly did you own in the Go support automation platform?
- What were the most important service boundaries and APIs?
- How did you design fallback logic and retries?
- How did monitoring identify incidents or degradation?
- What does "automated or deflected up to 30% of inbound tickets" mean operationally?
- What was your role in the Zendesk to Intercom migration?
- How did the airSlate Kubernetes migration affect reliability and delivery?
- What code review standards did you use as Technical Lead?
- How did you lead the PDFfiller email team through peak traffic?
- How do you explain the Simple.life and CRURATED timeline overlap if asked?

## Company-Specific Preparation

Research points to know:

- ZFORT presents itself publicly as a full-cycle AI and software development company with long history in custom digital products.
- Public service pages mention dedicated engineering teams for product companies, agencies, and startups.
- The DOU vacancy emphasizes flexibility, training, conferences/certifications, corporate events and benefits, professional literature, and English courses.

Questions to be ready for:

- Why ZFORT and not only product companies?
- Are you comfortable working on a client/product platform where requirements and priorities may evolve?
- How do you communicate risks and tradeoffs in a distributed team?
- How do you maintain quality in code reviews while moving quickly?

## Preparation Plan

Must prepare before applying:

- Confirm work authorization wording, sponsorship needs, notice period, earliest start date, and salary expectations.
- Prepare a transparent gRPC answer: "I have strong adjacent microservice and API experience; I have not listed gRPC because it is not explicit in my source CV. I can ramp quickly and would be happy to discuss the architecture expectations."
- Rehearse the Simple.life Go backend ownership story.

Before technical screen:

- Review Go concurrency, context handling, error wrapping, testing, profiling basics, and service shutdown.
- Review gRPC fundamentals: protobuf, unary vs streaming RPCs, deadlines, interceptors, status codes, and compatibility.
- Prepare a system design answer for a real-time user-facing backend platform with multiple services.

Before final/culture stage:

- Prepare examples for technical leadership, code reviews, mentoring, conflict resolution, and delivery ownership.
- Prepare questions about team structure, ownership, on-call, engineering practices, and growth path.

## Questions to Ask

- What product or client context does the real-time cross-selling platform support?
- How large is the backend team and how is ownership split across services?
- How mature is the current gRPC architecture, and what are the biggest pain points?
- What reliability or scalability goals are most important in the next 6 months?
- What does success look like for this role after 3 and 6 months?
- How do code reviews and architecture decisions work in the team?
- What backend testing strategy do you expect for services in this platform?
- Are there on-call or incident-response responsibilities?
- What are the expected working hours and timezone overlap?
- What are the next steps in the hiring process?
