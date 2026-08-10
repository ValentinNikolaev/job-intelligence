## Recruiter / HR Screening

Prepare a concise two-minute introduction centered on recent Go backend ownership, 15+ years of engineering experience, Rome-area location, remote collaboration, and the reason client-facing enterprise delivery is attractive. Keep chronology factual and reconcile the Simple.life end date and overlapping CRURATED period before the call.

Likely screening topics:

- **Motivation:** Connect the role to hands-on Go engineering, varied technical problems, client collaboration, and Nearform's focus on building both software and client capability.
- **Location and working model:** Confirm residence in Italy and comfort working remotely with distributed teams. Ask whether any client travel or office attendance is expected.
- **English:** Expect the entire process to test professional spoken English. Prepare technical explanations and project stories in English.
- **Salary:** The posting states a range starting at EUR 60,000 plus bonus and benefits. Decide a truthful target range and whether it refers to gross annual base compensation before the call.
- **Notice period / availability:** Not present in the candidate evidence; provide the current factual answer.
- **Job change:** Explain the current employment situation and what type of long-term role, client work, and engineering scope is being sought without criticizing former employers.
- **Timeline overlap:** Be ready to explain accurately how Simple.life and CRURATED overlapped.
- **Eligibility:** Confirm the right to work in Italy if asked; no status is recorded in the supplied evidence, so do not assume it.

## Culture Fit / Behavioral Interview

Prepare concise STAR stories from real evidence for these likely questions:

1. Tell me about a time you translated an operational or stakeholder problem into a technical solution. Use the Simple.life support automation platform.
2. Describe a production reliability problem you owned. Use message-delivery fallbacks, retries, and monitoring at Simple.life.
3. Give an example of improving performance or scalability. Use airSlate database/API optimization or CRURATED's 10x throughput increase.
4. Tell me about working with non-engineering stakeholders. Use collaboration with Support Operations, Product, and AI teams.
5. Describe a disagreement or difficult technical decision. Choose a verified project and state the options, evidence, decision process, and outcome; do not invent conflict.
6. How have you supported technical leaders or led delivery yourself? Use airSlate planning/release work or the Hyprr roadmap with the CTO.
7. Tell me about introducing a better engineering practice. Use CI/CD improvements, versioned event schemas, or observability.
8. Describe a failure or incident and what changed afterward. Use a real production incident only if details can be stated accurately; otherwise discuss the supported resilience improvements without inventing the trigger.
9. How do you maintain quality in a distributed team? Prepare real examples involving reviews, monitoring, release practices, and cross-team schema standards.
10. How do you learn an unfamiliar technology or domain? Use a real transition into Go, Kubernetes, or event analytics and keep the chronology accurate.

## Technical Interview

The posting says the technical assessment is a one-hour live Go coding exercise via screen sharing. Practice explaining decisions while producing a complete, tested solution.

**High Priority**

- **Go fundamentals:** interfaces, composition, error handling, context cancellation, goroutines, channels, synchronization, maps/slices, memory behavior, package design, and idiomatic naming. Deep Go knowledge is central and will be tested live.
- **Coding under observation:** clarify requirements, state complexity, write small functions, handle edge cases, add tests, and narrate trade-offs without over-talking.
- **Concurrency and reliability:** worker pools, bounded concurrency, timeouts, retries, idempotency, backpressure, and graceful shutdown. These connect directly to the candidate's message and event pipelines.
- **API and service design:** REST semantics, validation, authentication boundaries, error models, pagination, versioning, observability, and compatibility.
- **Data storage:** schema design, indexes, transactions, isolation, query plans, migration safety, caching trade-offs, and choosing between relational and event-oriented approaches.
- **Testing:** Go unit tests, table-driven tests, mocks/fakes, integration boundaries, deterministic concurrent tests, and how end-to-end tests fit a delivery pipeline. The CV under-documents this area, so verified examples are essential.
- **Performance and scalability:** profiling, measuring bottlenecks, database load, latency, throughput, queue behavior, and safe optimization. Prepare airSlate and CRURATED evidence.

**Medium Priority**

- **Cloud and delivery:** AWS, Kubernetes, Helm, GitHub Actions, ArgoCD, deployment strategies, observability, and rollback. These are strong supporting skills even if the exercise is coding-focused.
- **System design:** design a resilient client-facing service, job processor, or event pipeline; cover failure modes, data consistency, scaling, security, and operational ownership.
- **AI in the SDLC:** clarify what Nearform means. Prepare an honest distinction between building LLM-enabled product workflows and using AI tools for coding, testing, review, or documentation.
- **Client consultancy scenarios:** handling ambiguous requirements, presenting options, documenting trade-offs, and adapting to client standards.

**Low Priority**

- **Next.js implementation:** It is an explicit gap, but the primary task is Go. Learn the high-level request lifecycle, server/client components, API integration, rendering modes, and deployment model; do not claim production experience.
- **Deep frontend design:** Likely secondary unless the client project expects full-stack work.

## CV Deep-Dive Questions

- What parts of the Simple.life Go platform did you personally design and implement?
- How was the 30% automated or deflected ticket figure measured?
- What failure modes required fallbacks and retries, and how did monitoring expose them?
- What were the boundaries and consistency guarantees in the CRURATED event-driven architecture?
- How was the 10x throughput improvement measured, and what architectural change produced it?
- What does 99.9% event-delivery reliability mean in that system, and over what measurement window?
- How did the ECS-to-Kubernetes migration produce the reported 30% cost and 20% performance improvements?
- Which database and API bottlenecks were found at airSlate, and how were the 30% response-time gains validated?
- What was your personal scope as Technical Lead at Hyprr, and how much hands-on coding remained in the role?
- How did the PDFfiller service handle more than 10x BFCM traffic while delivering approximately 50 million emails per month?
- Why do Simple.life and CRURATED overlap, and what was the contractual or working arrangement?
- Why does the final CV show July 2026 when one source says March 2026 and another says Present?

For every metric, prepare the baseline, measurement method, personal contribution, team contribution, and technical mechanism. If an exact detail is confidential or cannot be recalled, say so and explain the architecture or decision without guessing.

## Company-Specific Preparation

- Review the official posting immediately before the interview and map one real example to each of: Go application design, data storage, performance, client requirements, CI/CD, testing, and collaboration.
- Explore [Nearform's Initium documentation](https://initium.nearform.com/) and be ready to discuss the developer/infrastructure handoff, ephemeral environments, CI automation, Kubernetes, ArgoCD, and how these ideas compare with the airSlate migration.
- Expect a consultancy mindset: ask clarifying questions, separate facts from assumptions, present options with trade-offs, and demonstrate comfort joining different client domains.
- Research the interviewer and the likely client only if names are provided later. Do not assume the project domain from Nearform's public customer list.
- Prepare an honest gap statement: “My recent work is backend-focused in Go; I have not claimed production Next.js experience, but I can collaborate across API boundaries and ramp up on the framework where the project needs it.”

## Preparation Plan

**Must prepare before the talent call**

- Reconcile employment dates and the CRURATED overlap.
- Decide factual availability, notice period, work authorization response, and salary expectations.
- Practice a two-minute English introduction and two concise Go project stories.
- Prepare why Nearform, why client-facing work, and why this role now.

**Before the technical assessment**

- Complete several timed 45-60 minute Go exercises while screen sharing or recording narration.
- Practice table-driven tests, concurrency cancellation, error handling, and refactoring a working solution for readability.
- Review database design, API contracts, performance profiling, and failure handling.
- Prepare verified examples of unit, integration, and end-to-end testing; if evidence is limited, state the gap directly.

**Before the hiring-manager or client interview**

- Prepare STAR stories for stakeholder collaboration, ambiguity, technical quality, performance, delivery pressure, and leadership.
- Review Nearform's delivery model and Initium project.
- Prepare questions about the client, project stage, team, quality expectations, travel, and success measures.

## Questions to Ask

1. What client or product context would this role join first, and what phase is the project in?
2. How much of the work is greenfield Go development versus modernization of an existing system?
3. Where does Next.js fit into the role, and how often are Go engineers expected to contribute directly to the frontend?
4. What does “strong AI in SDLC skills” mean in practice at Nearform: coding assistance, test generation, review, documentation, delivery automation, or client-facing AI features?
5. Which databases, cloud platform, deployment stack, and observability tools are used on the likely project?
6. How are technical decisions shared between Nearform engineers and the client team?
7. What quality gates are expected across unit, integration, and end-to-end testing?
8. How does Nearform evaluate success for a senior engineer during the first three to six months?
9. How frequently do engineers move between client projects, and how are transitions and learning supported?
10. Does the Italy-based role involve client travel, fixed collaboration hours, or other location-specific expectations?
