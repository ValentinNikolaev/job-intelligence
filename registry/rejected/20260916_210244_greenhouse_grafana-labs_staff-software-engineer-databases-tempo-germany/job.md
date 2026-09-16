# Staff Software Engineer - Databases, Tempo | Germany | Remote

Posted: 2026-07-10T08:15:59-04:00

## Rejection

- Category: company_retry_block
- Reason: Grafana is blocked until 2027-02-01: CV rejected; retry allowed from February 2027.

Grafana Labs is the company behind Grafana Cloud, the fully managed observability platform trusted by more than 10,000 organizations to ensure reliability, resolve incidents faster, and optimize telemetry at scale. Built on open source and open standards and designed for interoperability across any stack, Grafana Cloud brings AI to observability and observability to AI, giving teams (and their agents) unified visibility so they can see, understand, and act on all their disparate data, wherever it lives, and move at the speed of their ambitions. Customers, including Anthropic, Bloomberg, NVIDIA, Microsoft, and Salesforce, rely on Grafana Labs. We are a 100% remote company with team members across 40+ countries, backed by leading investors including Lightspeed Venture Partners, Sequoia Capital, GIC, Coatue, J.P. Morgan, CapitalG, and Lead Edge Capital. Learn more at [grafana.com](http://grafana.com) and follow us on [LinkedIn](https://www.linkedin.com/company/grafana-labs/) and [X](https://twitter.com/grafana).

We’re scaling fast and staying true to what makes us different: an open-source legacy, a global collaborative culture, and a passion for meaningful work. Our team thrives in an innovation-driven environment where transparency, autonomy, and trust fuel everything we do.

You may not meet every requirement, and that’s okay. If this role excites you, we’d love you to raise your hand for what could be a truly career-defining opportunity.

### **This is a remote opportunity, and we would be interested in applicants located in Spain, Sweden, UK, Ireland or Germany. **

## Staff Software Engineer - Grafana Databases, Tempo

#### The Opportunity

We build **Tempo**, the open-source distributed tracing backend behind Grafana Cloud Traces and Grafana Enterprise Traces (GET). Tempo makes it easy to search traces, generate metrics from spans, and connect tracing data with logs, metrics, and profiles across the Grafana stack.

2026 is an inflection point for Tempo. After a major architectural upgrade and the launch of TraceQL metrics, we are shifting from foundational work to product and operational excellence, and evolving Tempo from a SaaS database into a platform that powers Grafana’s next generation of observability products (App Observability, Asserts, Traces Drilldown, and AI-driven assistants).

Over the next year, you will help us:

- Make Grafana Cloud Traces “just work” for customers by eliminating rough edges, confusing limits, and hidden failure modes.

- Achieve operational excellence at scale as we grow from close to 50 cells today into triple digits this year, with autoscaling, parameterized rollouts, and aggressive toil reduction.

- Evolve Tempo into a platform enabler: higher-density APIs, trace aggregation, TraceQL metrics math, and machine/LLM-friendly interfaces that downstream products and agents can build on.

- Push performance further: faster query latency at hundreds of MB/s ingestion and performant 30-day query ranges to match competitors.

- Prepare Tempo for an agent-driven world: larger, burstier, higher-cardinality workloads, and new categories of AI-powered workflows, such as assistant-driven triage and “why is this slow?”- style investigations.

#### What You'll Be Doing:

As a Staff Engineer on Tempo, you will set technical direction on the hardest problems in our roadmap and raise the bar across the team.

- **Lead multi-quarter technical initiatives** from problem framing through rollout, e.g., trace aggregation APIs, Limitless Tempo, autoscaling cells and customer limits, or query engine improvements.

- **Own the architecture** of core Tempo components: ingestion, storage, query, and metrics generation. Drive design reviews, make sharp trade-offs on performance, cost, and complexity, and document the “why” for the team.

- **Design APIs for humans and agents.** Shape the next generation of Tempo’s interfaces (structured, deterministic, discoverable) so that Act 3 products, LLM-driven assistants, and external integrators can build on Tempo reliably.

- **Drive operational excellence.** Own outcomes against concrete SLOs (P99 write latency, incident recurrence, TCO per ingested GB) and push the team toward Zero Ops through automation, parameterized rollouts, and actionable alerts.

- **Partner with Product and sibling teams.** Work closely with PMs and with App Observability, Asserts, Drilldown, and Grafana Assistant teams to understand how Tempo gets consumed and to ship what unblocks them.

- **Mentor engineers.** Raise the engineering bar through code review, design feedback, pairing on hard problems, and writing that leaves the team smarter than you found it.

- **Participate in on-call** for the services you help build, and be a force multiplier in incident response and post-incident learning.

- **Contribute to open source.** Tempo is OSS. You will engage the community, review external contributions, and help steer the project in the open.

We invest heavily in developer productivity. You can use modern AI coding assistants as part of your daily workflow (your choice of tools, within security guidelines), backed by a company-funded usage budget so you can iterate quickly without unnecessary friction.

We encourage pragmatic AI-assisted development: faster prototyping, test generation, refactors, documentation, and incident follow-ups—always paired with strong code review and quality standards.

You’ll also have access to frontier models (e.g., GPT-5.6, Claude Fable, Gemini Pro 3.1).

**Example problems you could work on:**

These are the kinds of projects landing in 2026. Any one of them is a Staff-sized problem:

- **Trace aggregation and higher-density APIs:** extend TraceQL metrics, design LLM-friendly response types, and make Tempo a first-class data source for Grafana’s AI assistant.

- **Autoscaling end to end:** customer limits and Tempo cells, with hysteresis, predictive scaling for spikes, and safe scale-down.

- **Agent-scale ingestion and query:** guardrails for bursty, high-cardinality, agent-generated workloads.

- **Query performance:** new data formats, smarter query pipelines, targeted optimizations for common Drilldown and Traces workflows, and 30-day query ranges.

- **Rollouts and multi-cell operations:** parameterized rollouts, push-button deploys, and the tooling to grow safely into triple-digit cell counts without a proportional increase in alert noise.

- **Limits and self-service:** drive customer-facing configuration and observability so escalations trend toward zero.

#### What Makes You a Great Fit:

- **Technical leadership.** A track record of leading complex, multi-quarter initiatives that spanned design, delivery, and operations, and made the teams around you better.

- **Deep systems experience.** Substantial hands-on experience building and operating distributed data systems in production: ingestion pipelines, storage engines, query execution, or similar.

- **Strong software craftsmanship.** You write clean, robust, performant software that others can maintain, and you know when to optimize vs. when to ship.

- **Strong Go, or a path to it.** We write Tempo in Go. Deep experience in other systems languages (Rust, C, C++) translates well.

- **Operational mindset.** You’ve owned production services, carried a pager, reduced toil, and treated SLOs as a product feature, not a chore.

- **Customer focus and pragmatism.** You break complex problems into short feedback loops: analyze, design, deliver an MVP, learn, iterate.

- **Leadership through writing and collaboration.** You lead through design docs, reviews, and shipped code, not hierarchy. You communicate clearly in a fully remote, asynchronous environment.

#### Bonus Points for:

- Experience with tracing, OpenTelemetry, or large-scale observability systems.

- Experience designing query languages, SQL/TraceQL-like engines, or APIs intended to be consumed programmatically (by services or agents).

- Experience with columnar storage formats (e.g., Parquet) or purpose-built on-disk formats for analytical workloads.

- Experience operating multi-tenant, multi-cell SaaS infrastructure at scale on Kubernetes.

- Experience building for AI/LLM consumers: structured APIs, metadata/discovery endpoints, deterministic outputs, evaluation harnesses.

- Open-source contribution or maintainership, and comfort engaging a community in the open.

- Experience as an on-call user of Grafana, Prometheus, Loki, or Tempo in a previous role (or on a homelab).

- Experience in a fully remote, globally distributed team.

**How we work:**

We are a remote-first team that meets regularly over video and does most of our work asynchronously, in writing. We value creativity, diverse perspectives, and clear communication. Tempo is relied upon by prominent global organizations to monitor critical applications and infrastructure, and we expect everyone on the team, including our Staff engineers, to contribute ideas that make it a more reliable, more useful, and more loved product.

**Compensation & Rewards:**

In Germany, the Base compensation range for this role is EUR 109,709 - EUR 131,651. Actual compensation may vary based on level, experience, and skillset as assessed in the interview process. Benefits include equity, bonus (if applicable) and other benefits listed [here](https://grafana.com/about/careers/#jobs).

**Compensation ranges are country specific. If you are applying for this role from a different location than listed above, your recruiter will discuss your specific market’s defined pay range & benefits at the beginning of the process*

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
