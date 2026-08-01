## Recruiter / HR Screening

Likely screening topics:

- Motivation for ShippyPro and for the Fulfillment Pod.
- Current location, remote-work expectations, and ability to work CET +/-2.
- Willingness to travel to Florence HQ for meetups.
- Salary expectations within the EUR 52,000-72,000 range.
- Notice period and availability.
- English communication level.
- Current employment status and clarification of the Simple.life / CRURATED timeline.
- Right to work in Italy or the EU.
- Comfort with a process including People interview, COO technical deep dive, live coding, and final team interview.

Suggested positioning:

"I am looking for a hands-on technical lead role where I can stay close to backend architecture and code while helping a team ship reliable systems. ShippyPro is interesting because the Fulfillment Pod owns core order management and label-generation systems, which sounds close to my experience with high-volume messaging, automation workflows, APIs, and production reliability."

Salary:

Use a confirmed personal number before submitting. If staying inside the stated range, a safe answer is: "Given the scope and leadership expectations, I would like to discuss the upper part of the published range, depending on the full package, responsibilities, and growth path."

Timeline clarification:

Prepare a precise explanation of Simple.life, CRURATED, and any overlapping contractual work. Keep it factual and brief.

## Culture Fit / Behavioral Interview

Likely questions:

1. Tell us about a time you led a team while still contributing technically.
2. How do you raise engineering standards without slowing delivery?
3. Describe a production incident or reliability problem you improved.
4. Tell us about a time you had ambiguity and had to create a plan.
5. How do you mentor engineers with different levels of experience?
6. Tell us about a time you disagreed with Product or leadership.
7. How do you decide whether to refactor, rewrite, or ship incrementally?
8. Describe a time you automated work that was slowing a team down.
9. How do you run planning, reviews, and retros so they stay useful?
10. What does "lead by doing" mean in your day-to-day work?

STAR stories to prepare:

- PDFfiller: leading 5 backend engineers and scaling transactional email to 50 million emails/month.
- Hyprr: taking a prototype to closed beta in under 6 months while directly managing 10 developers.
- airSlate: ECS to Kubernetes migration with Helm, GitHub Actions, and ArgoCD.
- Simple.life: LLM-powered support triage automating or deflecting up to 30% of inbound tickets.
- CRURATED: event-driven analytics pipeline with EventBridge, routing, delivery guarantees, retries, and observability.

## Technical Interview

**High Priority**

- Backend system design for order management, label generation, fulfillment, carrier integrations, and retryable workflows.
- API design, idempotency, consistency, error handling, rate limits, and integration failure modes.
- Scalability and reliability for high-volume request paths.
- Database design with MySQL/PostgreSQL, indexes, transactions, query optimization, and load reduction.
- AWS architecture using ECS/Lambda-style services, Docker, queues, and observability.
- Leadership trade-offs: hands-on coding versus mentoring, delivery speed versus maintainability.

**Medium Priority**

- PHP architecture and modernization in a mixed stack.
- Event-driven systems, queues, backpressure, dead-letter handling, and replay.
- CI/CD design, deployment safety, rollback, and environment promotion.
- AI workflow automation: where to use it, where not to use it, and how to keep outputs observable and safe.
- Live coding in a backend language: clear problem decomposition, tests, edge cases, and communication.

**Low Priority**

- React, TypeScript, and Tailwind implementation details, unless the interview crosses into full-stack collaboration.
- DynamoDB internals unless the interviewer asks specifically; prepare basic NoSQL trade-offs without claiming deep production experience.
- Logistics domain vocabulary beyond the job description; focus on analogous integration and reliability patterns.

System design drills:

- Design a label-generation service that integrates multiple carriers and handles retries, carrier downtime, duplicate submissions, and status tracking.
- Design order fulfillment workflow orchestration from order import to label creation, tracking update, and notification.
- Design migration from a monolith or legacy PHP service toward distributed cloud-native services.
- Design observability for a fulfillment service where failed requests directly affect merchants.

## CV Deep-Dive Questions

Prepare concise answers for:

- "What exactly did you own at Simple.life?"
- "How did the LLM auto-triage workflow work, and how did you measure 30% automation/deflection?"
- "What were the most difficult parts of the Zendesk to Intercom migration?"
- "What was your role in the airSlate ECS to Kubernetes migration?"
- "How did you reduce database load and API response time?"
- "How did you lead 5 backend engineers at PDFfiller?"
- "What happened during BFCM traffic growth, and how did the team prepare?"
- "At Hyprr, what did direct management of 10 developers involve?"
- "Can you explain the CRURATED timeline and how it relates to Simple.life?"
- "Which parts of ShippyPro's stack are new to you, and how would you ramp up?"

Defend important claims with evidence:

- 50 million emails/month: explain service scope, bottlenecks, monitoring, and team responsibilities.
- 30% support automation/deflection: explain routing, classification, integration points, and measurement source.
- Kubernetes migration: explain ECS baseline, deployment changes, Helm/GitHub Actions/ArgoCD, and operational outcomes.
- EventBridge/event analytics: explain schema versioning, downstream routing, retries, and backpressure.

## Company-Specific Preparation

What to know:

- ShippyPro is a shipping and fulfillment platform for e-commerce merchants.
- Public materials emphasize multi-carrier shipping, tracking, returns, delivery intelligence, shipping APIs, carrier integrations, and sales-channel integrations.
- The Fulfillment Pod owns order management and label generation, which are core operational workflows rather than side systems.
- The company highlights customer focus, curiosity, transparency, feedback, knowledge sharing, remote work around CET +/-2, and periodic meetups.
- The role reports to the COO, so business impact and operational clarity will matter.

Likely company-specific questions:

- "Why ShippyPro?"
- "What attracts you to fulfillment/order-management systems?"
- "How would you approach a pod that owns mission-critical label generation?"
- "How do you balance fast delivery with zero-room-for-sloppy-engineering systems?"
- "How would you bring AI into the team's workflow without making it a buzzword?"

Answer angle:

Connect ShippyPro to real experience with high-volume transactional systems, delivery guarantees, retries, observability, automation, and team leadership. Avoid pretending to have direct logistics experience; frame it as a domain you can learn through analogous systems.

## Preparation Plan

**Must prepare before recruiter call**

- Confirm salary expectation and minimum acceptable package.
- Confirm notice period and availability.
- Confirm work authorization wording.
- Clarify current employment status and overlapping Simple.life / CRURATED dates.
- Prepare a 60-second motivation answer.

**Before technical interview**

- Practice one system design around label generation or order fulfillment.
- Review PHP, Go, REST API, queues, retries, idempotency, observability, and database optimization examples.
- Prepare one live-coding language choice and practice explaining trade-offs aloud.
- Prepare examples of leading engineers, planning work, mentoring, and handling ambiguity.

**Before final / culture interview**

- Prepare examples around customer focus, feedback, curiosity, remote collaboration, and knowledge sharing.
- Prepare questions about team size, current architecture, modernization path, rituals, and success metrics.
- Be ready to explain how you would learn the logistics domain quickly.

## Questions to Ask

1. How large is the Fulfillment Pod today, and what roles are already in place?
2. What are the most important reliability or scalability problems in order management and label generation right now?
3. How is the current stack split across PHP, NodeJS, Python, and AWS services?
4. What would success look like for this role in the first 3 and 6 months?
5. How much hands-on coding do you expect from the team lead?
6. What engineering rituals are working well today, and which ones need improvement?
7. How does Product work with the Fulfillment Pod on roadmap decisions and trade-offs?
8. What kind of AI workflow adoption has already helped engineering, and what still feels experimental?
9. How do you handle remote collaboration and HQ meetups for engineering?
10. What are the main reasons candidates succeed or struggle in this role?
