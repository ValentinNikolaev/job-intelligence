# Interview Preparation — ZFORT Group, Backend/Golang Developer

## Recruiter / HR Screening

Prepare a 60-second introduction: backend engineer with more than 15 years across Go and PHP; recent Go platform ownership at Simple.life; production reliability and earlier technical leadership. Explain your interest in Go ownership, resilient microservices and platform design. ZFORT's stated peer review and automated testing offer a specific culture discussion point.

Prepare concise answers on employment chronology (Simple.life ended July 2026), job changes and next goals. Confirm whether remote hiring includes your location in Rome, the contract type and time-zone overlap. Decide your actual start date, notice obligations, work authorization, compensation range and currency before the call. Discuss remote collaboration and an architecture decision in English. The CV says upper-intermediate English; demonstrate current ability in conversation.

## Culture Fit / Behavioral Interview

Build short STAR outlines with your contribution, an observable outcome and a lesson. Likely questions:

1. Tell us about a backend service you owned end to end. Use the Simple.life Go support-automation platform; distinguish design and implementation from decisions made by others.
2. Describe a production reliability problem and your response. Use the airSlate database-load work and explain the measurements, change, and observed service-stability result.
3. How did you handle a design disagreement or difficult code review? Draw from Hyprr leadership and clarify the resolution.
4. When did you balance delivery speed against maintainability? Use Hyprr's prototype-to-closed-beta period, with a concrete trade-off you personally made.
5. How have you helped a colleague improve? Ground the answer in the five-engineer PDFfiller team or verified mentoring experience.
6. Tell us about an integration change with operational risk. Use only a Simple.life customer-support integration that you can describe with a concrete customer or operating outcome.
7. How do you work when requirements change? Identify what you reprioritized, communicated and shipped.
8. Describe an incident where your first hypothesis was wrong. Prepare a real diagnosis from database, API, or delivery-pipeline work, including evidence that changed your view.

Separate team outcomes from individual contributions. Preserve the CV's qualifiers: “up to 30%” ticket automation or deflection and “around 50 million” emails monthly.

## Technical Interview

**High priority — Go service design and reliability.** Review concurrency, context, timeouts, cancellation, retries, idempotency, graceful shutdown and backpressure. Use Simple.life pipelines to explain actual choices, failure modes and observability. The role emphasizes uptime.

**High priority — gRPC and API contracts.** Study protobuf evolution, unary versus streaming RPCs, deadlines, status codes, authentication and compatibility. Contrast REST design and versioning. Evidence does not establish hands-on gRPC delivery: state actual exposure precisely and explain how you would design and test a contract.

**High priority — architecture and system design.** Practice a real-time backend for several apps: service boundaries, request and event paths, latency, availability, partial failures, consistency and observability. Ask for traffic and business constraints; client scale is unknown.

**High priority — backend testing and code review.** Discuss unit, integration, contract and load tests, failure injection and review criteria. Describe only practices you have used; prepare one concrete review example.

**Medium priority — databases and infrastructure.** Revisit query plans, indexing, contention and peak-load measurement using airSlate. Review the CI/CD decisions you actually made and their release or operational effect.

**Medium priority — coding.** Practice Go interfaces, goroutines, channels, synchronization, errors, tests and an API or worker implementation. Explain race conditions aloud. **Low priority — cross-selling specifics.** Learn the vocabulary without guessing undisclosed requirements.

## CV Deep-Dive Questions

Expect “What did you personally own in the Simple.life Go platform?” and “How was the up-to-30% figure measured?” For airSlate, identify the database pressure point, measurements, and the resulting service-stability change. For Hyprr, distinguish Technical Lead responsibilities from hands-on implementation and specify architecture decisions. For PDFfiller, explain leading five engineers and the approximately 50-million-per-month scale claim. Keep titles and dates aligned with the CV. For gRPC or testing frameworks, state actual experience and learning needs.

## Company-Specific Preparation

Read the [vacancy](https://jobs.dou.ua/companies/zfort/vacancies/374288/) immediately before the call and confirm it is still open. Review [ZFORT's company overview](https://www.zfort.com/company/about): it describes custom software work, peer review and automated testing. Connect those verified points to your interest in collaborative quality practices. The client, product name, team size, on-call model and ownership boundaries are unknown; use the interview to establish them. Prepare a short explanation of how your support-platform and reliability experience might transfer to a real-time, user-facing cross-selling platform, framed as an informed hypothesis rather than claimed domain expertise.

## Preparation Plan

**Must prepare before screening:** Your current availability, location and contracting constraints, salary range, truthful gRPC exposure, spoken English introduction, and two concise STAR stories (Simple.life ownership; airSlate reliability or Hyprr leadership).

**Before the technical round:** Rehearse a Go/gRPC service-design exercise, REST-versus-gRPC trade-offs, testing and code-review examples, one production failure diagnosis, and the airSlate database story. Gather any architecture diagrams or metrics you can discuss without disclosing confidential details.

**Before the final or culture round:** Refine leadership, disagreement and change-management stories; confirm the client's platform goals, team shape and decision rights. Recheck each CV claim against your recollection and keep any uncertainty explicit.

## Questions to Ask

1. Which parts of the cross-selling platform would this engineer own in the first six months?
2. What are the current latency, availability and traffic expectations, and how are they measured?
3. Where does gRPC run today, and how do you manage protobuf compatibility across services?
4. Which failure modes or production incidents are the team trying to prevent next?
5. What testing levels and review practices are expected for backend changes?
6. How are architecture decisions divided among engineers, a Tech Lead and the client?
7. What is the current team composition, and how does it collaborate across time zones?
8. What are the on-call, incident response and release responsibilities?
9. What employment arrangement and location rules apply to someone based in Italy?
