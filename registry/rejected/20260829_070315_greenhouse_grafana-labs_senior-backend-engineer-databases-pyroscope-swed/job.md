# Senior Backend Engineer - Databases Pyroscope | Sweden | Remote

Posted: 2026-07-24T16:46:52-04:00

## Rejection

- Category: company_retry_block
- Reason: Grafana is blocked until 2027-02-01: CV rejected; retry allowed from February 2027.

Grafana Labs is the company behind Grafana Cloud, the fully managed observability platform trusted by more than 10,000 organizations to ensure reliability, resolve incidents faster, and optimize telemetry at scale. Built on open source and open standards and designed for interoperability across any stack, Grafana Cloud brings AI to observability and observability to AI, giving teams (and their agents) unified visibility so they can see, understand, and act on all their disparate data, wherever it lives, and move at the speed of their ambitions. Customers, including Anthropic, Bloomberg, NVIDIA, Microsoft, and Salesforce, rely on Grafana Labs. We are a 100% remote company with team members across 40+ countries, backed by leading investors including Lightspeed Venture Partners, Sequoia Capital, GIC, Coatue, J.P. Morgan, CapitalG, and Lead Edge Capital. Learn more at [grafana.com](http://grafana.com) and follow us on [LinkedIn](https://www.linkedin.com/company/grafana-labs/) and [X](https://twitter.com/grafana).

We’re scaling fast and staying true to what makes us different: an open-source legacy, a global collaborative culture, and a passion for meaningful work. Our team thrives in an innovation-driven environment where transparency, autonomy, and trust fuel everything we do.

You may not meet every requirement, and that’s okay. If this role excites you, we’d love you to raise your hand for what could be a truly career-defining opportunity.

# **This is a remote position. We are looking for candidates in the UK, Germany, Spain, Sweden and Ireland only. **

## **The Opportunity**

We build **Pyroscope**, the open-source continuous profiling database behind Grafana Cloud Profiles. Pyroscope gives engineers code-level visibility into how their applications use CPU and memory, down to the specific line of code, and connects that signal with metrics, logs, and traces across the Grafana stack.

2026 is an inflection point for Pyroscope. We completed the rollout of our V2 architecture, cutting production costs by 92% while significantly improving scalability, and grew the number of customers using the product by 64% last year. The product is moving beyond profiling-savvy users, and our focus is shifting from standalone feature development to reducing friction across the full experience: better onboarding, deeper integration with the rest of Grafana, and profiles that work for operational and SRE workflows, not just performance specialists.

Over the next year, you will help us:

- Ship Adaptive Profiles as the default ingestion strategy, so customers automatically collect the profiles they need at a cost that makes sense.

- Turn Pyroscope into a platform capability inside Grafana: bi-directional trace-to-profile correlation, integration with Kubernetes Monitoring and App Observability, and profiles surfaced where engineers already start their investigations.

- Prepare Pyroscope for an agent-driven world: APIs, CLI, and docs designed so AI agents can drive profiling end to end, covering the full performance optimization lifecycle from finding an issue to verifying the fix.

- Push operational excellence and TCO further: generalized autoscaling, better UX for long queries, and BYOC automation that brings up a new cell with zero manual intervention.

- Double adoption by making profiling easy to start with: guided onboarding, use-case-driven docs, and assisted instrumentation so users get value in minutes instead of days.

## **What You'll Be Doing**

As a Senior Engineer on Pyroscope, you will own meaningful projects end to end and help shape what the team builds next.

- **Lead projects from concept to rollout**, e.g. Read path efficiency improvement, or trace-to-profile correlation, including design, delivery, operations, and customer follow-up.

- **Design, build, and operate core components** of a distributed database: ingestion, storage, and query, making sharp trade-offs on performance, cost, and complexity.

- **Wear the product hat.** We have no dedicated PM: engineers on this team join customer calls, translate pain points into manageable deliverables, and directly shape the roadmap. Your questions and ideas will steer what we build.

- **Drive operational excellence.** Own outcomes against concrete SLOs and unit cost targets, reduce toil through automation, and make on-call quieter every quarter.

- **Partner across Grafana.** Work closely with App Observability, Alloy, Tempo, and the other Databases squads to make profiles useful wherever engineers work.

- **Support your teammates** through design conversations, code review, and pairing in a fully remote setup.

- **Participate in on-call** (EMEA rotation) for the services you build, and treat incident response and post-incident learning as part of the craft.

- **Contribute to open source.** Pyroscope is OSS. You will engage the community, review external contributions, and help steer the project in the open.

We invest heavily in developer productivity. You can use modern AI coding assistants as part of your daily workflow (your choice of tools, within security guidelines), backed by a company-funded usage budget so you can iterate quickly without unnecessary friction.

We encourage pragmatic AI-assisted development: faster prototyping, test generation, refactors, documentation, and incident follow-ups, always paired with strong code review and quality standards. You'll also have access to frontier models (e.g., GPT-5.6, Claude Fable, Gemini Pro 3.1).

## **Example problems you could work on**

These are the kinds of projects landing this year:

- **Adaptive Profiles:** sampling and aggregation strategies that keep the signal while cutting cost and noise, plus the ingestion metrics that make its behavior transparent to customers.

- **Large queries:** query fairness, async execution, and autoscaling of the read path so long queries from our largest tenants run efficiently at any scale.

- **Traces and profiles together:** bi-directional correlation between traces and profiles, so a slow request links straight to the code that burned the CPU.

- **Agent-ready Pyroscope:** structured, deterministic APIs and a CLI that AI assistants can drive reliably, plus the benchmarks to prove tool quality and catch regressions.

- **BYOC and regions:** cell lifecycle automation, from provisioning to migration, targeting a new cell end to end with zero manual steps.

- **OTel-native profiling:** evolve ingestion, storage, and query as OpenTelemetry profiling matures, keeping Pyroscope the natural backend for OTel profiles.

## **What Makes You a Great Fit**

- **Solid experience with a systems language.** We write Pyroscope in Go; experience with one or more programming languages (e.g. Rust, C, C++, Python, Java, etc).

- **Distributed systems in production.** You have built and operated cloud services and understand what it takes to keep a multi-tenant data system fast, reliable, and affordable.

- **Product sense.** You are comfortable talking to customers, sitting with ambiguity, and breaking fuzzy problems into manageable deliverables. Since we have no dedicated PM, this matters as much as your code.

- **Curiosity and courage.** Pyroscope is nearing feature completeness while still refining product-market fit. We need someone who asks hard questions and challenges the status quo when appropriate.

- **Strong software craftsmanship.** You write clean, robust, performant software that others can maintain, and you know when to optimize versus when to ship.

- **Operational mindset.** You have carried a pager, done SRE-style work or infrastructure as code, and treat reliability as a feature.

- **Pragmatism.** You break complex problems into short feedback loops: analyze, design, deliver an MVP, learn, iterate.

- **Clear communication.** You work well in a fully remote, asynchronous environment and lead through writing, reviews, and shipped code.

## **Bonus Points For**

- Experience with profiling and performance engineering: flamegraphs, pprof, perf, or similar tooling.

- Experience with OpenTelemetry or large-scale observability systems.

- Experience operating multi-tenant SaaS infrastructure at scale on Kubernetes.

- Experience building for AI/LLM consumers: structured APIs, metadata and discovery endpoints, deterministic outputs.

- Open-source contribution or maintainership, and comfort engaging a community in the open.

- Experience as an on-call user of Grafana, Prometheus, Pyroscope, or similar in a previous role (or on a homelab).

- Experience in a fully remote, globally distributed team.

## **How we work**

We are a remote-first team that meets regularly over video and does most of our work asynchronously, in writing. We value creativity, diverse perspectives, and clear communication. Pyroscope is relied upon by prominent global organizations to optimize critical applications and infrastructure, and we expect everyone on the team to contribute ideas that make it a more reliable, more useful, and more loved product.

In Sweden, the compensation range for this role is SEK 775,444 - SEK 930,533. Actual compensation may vary based on level, experience, and skillset as assessed throughout the interview process. All of our roles include Restricted Stock Units (RSUs), giving every team member ownership in Grafana Labs' success. We believe in shared outcomes—RSUs help us stay aligned and invested as we scale globally.

**Compensation ranges are country specific. If you are applying for this role from a different location than listed above, your recruiter will discuss your specific market’s defined pay range & benefits at the beginning of the process.*

**Why You’ll Thrive at Grafana Labs:**

- **100% Remote, Global Culture - **As a remote-only company, we bring together talent from around the world, united by a culture of collaboration and shared purpose.

- **Scaling Organization** – Tackle meaningful work in a high-growth, ever-evolving environment.

- **Transparent Communication** – Expect open decision-making and regular company-wide updates.

- **Innovation-Driven** – Autonomy and support to ship great work and try new things.

- **Open Source Roots** – Built on community-driven values that shape how we work.

- **Empowered Teams** – High trust, low ego culture that values outcomes over optics.

- **Career Growth Pathways** – Defined opportunities to grow and develop your career.

- **Approachable Leadership** – Transparent execs who are involved, visible, and human.

- **Passionate People** – Join a team of smart, supportive folks who care deeply about what they do.

- **In-Person onboarding **- We want you to thrive from day 1 with your fellow new ‘Grafanistas’ to learn all about what we do and how we do it.

- **Balance is Key** - We operate a global annual leave policy of 30 days per annum. 3 days of your annual leave entitlement are reserved for Grafana Shutdown Days to allow the team to really disconnect. **We will comply with local legislation where applicable.*

**Equal Opportunity Employer:** *Grafana Labs is an equal opportunities employer. We welcome applications from everyone regardless of race, colour, nationality, origin, caste, sex, gender reassignment identity or expression, sexual orientation, age, religion or belief, disability, veteran status, genetic information, pregnancy, maternity, marital, family or carer status, or any other characteristic which is protected by local law. We believe that equality and diversity build a strong organisation, and we work hard to ensure that is the foundation of our organisation as we grow.*

*Grafana Labs may utilize AI tools in its recruitment process to assist in matching information provided in CVs to job postings. The recruitment team will continue to review inbound CVs manually to identify alignment with current openings.*

#LI-Remote

*For information about how your personal data is used once you’ve applied to a job, check out our [privacy policy](https://grafana.com/legal/applicant-and-candidate-privacy-policy/). *
