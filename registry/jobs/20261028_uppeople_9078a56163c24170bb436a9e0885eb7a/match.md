# Match Analysis

**Score:** 78/100  
**Recommendation:** Match

Strong fit for the hands-on Laravel platform lead scope: the profile supports PHP/Laravel, production ownership, technical leadership, product delivery, AWS, and AI automation. The main risks are unverified Vue/UI ownership, GCP, analytical stores, and formal FRD practice.

## Why it matches

- The profile states 5 years of leadership experience and records direct management of 10 developers at Hyprr.
- The candidate owns a production support automation platform in Go and has built resilient message delivery pipelines with retries and monitoring.
- The profile supports Laravel, Symfony, PostgreSQL, AWS, Kubernetes, GitHub Actions, Prometheus, and production reliability work.
- The candidate has product and stakeholder experience through work with product and engineering leadership and defining a technology roadmap with a CTO.
- The candidate profile includes support automation and LLM automation systems, relevant to the role's AI-assisted development baseline.

## Gaps

- The profile does not provide evidence of Vue, Vuex, UI/UX ownership, or shipping frontend improvements.
- The profile does not establish hands-on ClickHouse, BigQuery, Snowflake, or Apache Druid experience.
- The profile lists AWS and Kubernetes but does not establish GCP service-design experience with Cloud Run, Cloud SQL, or GCS.
- The profile does not explicitly document writing FRDs or maintaining API contracts and data models as a formal responsibility.

## Concerns

- The role combines technical leadership with substantial product and frontend ownership, while the supplied profile is materially stronger on backend and platform delivery.
- The vacancy requires daily agentic coding and parallel-agent practice; the profile supports LLM automation but does not explicitly confirm that exact working practice.

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| 5+ years building and shipping web products as a full-stack engineer | critical / stated | partial | 5+ years building and shipping web products as a full-stack engineer | I'm a highly experienced developer with over 15 years of expertise. | The profile demonstrates extensive backend delivery but does not establish five years of full-stack ownership. / Clarify the extent of frontend and full-stack responsibility before preparation. |
| Laravel in depth | critical / stated | partial | Laravel in depth: Eloquent, queues, events, service providers, testing. | Laravel/Symfony-based product-wide logger package | Laravel is evidenced, but the supplied quote does not cover every named Laravel subsystem. / Use only documented Laravel evidence and verify Eloquent, queues, events, service providers, and testing scope. |
| 2+ years leading engineers as a tech lead, team lead or hands-on engineering manager | critical / stated | strong | 2+ years leading engineers as a tech lead, team lead or hands-on engineering manager: task breakdown, code review, mentoring, 1:1s | I have a strong track record in PHP, with 5 years of leadership experience. | / |
| Vue experience and frontend platform judgement | high / stated | unknown | Either Vue 2 or Vue 3 experience counts, as long as you can work inside an existing codebase and improve it. |  | No Vue or UI/UX evidence appears in the supplied profile. / Ask for concrete Vue and user-flow examples before advancing. |
| PostgreSQL beyond CRUD and analytical-store SQL | high / stated | partial | Real SQL ability plus hands-on work with an analytical store: ClickHouse, BigQuery, Snowflake or similar. | Normalized database tables and performed extensive query optimization. | PostgreSQL and query optimization are evidenced, but analytical-store experience is not. / Verify any ClickHouse, BigQuery, Snowflake, or Druid work before using it as evidence. |
| GCP service-design ownership | high / stated | missing | GCP at the service-design level: Cloud Run, Cloud SQL, GCS. You answer for what you deploy | AWS | The profile names AWS rather than GCP services. / Treat GCP as a gap unless separate candidate evidence confirms it. |
| AI-assisted development and parallel-agent practice | high / stated | partial | Able to run 2–4 agents in parallel on isolated branches or worktrees and merge the results yourself | AI / Automation - OpenAI APIs - LLM automation systems | LLM automation is evidenced, but the required development workflow is not explicitly evidenced. / Confirm daily agentic coding and isolated parallel-agent practice before preparation. |
| Production releases, incidents, reliability, and observability | high / stated | strong | Own releases and reliability: deploys across four production VMs with an NFS-shared release directory and automatic rollback, monitoring, alerting, incident response | Build resilient message delivery pipelines with fallback logic, retries, and | The exact four-VM deployment model is not evidenced. / Confirm deployment topology while preserving the demonstrated reliability evidence. |
| Fully remote with EU timezone overlap | meaningful / stated | strong | Fully remote with flexible hours, overlapping EU timezones for syncs | Fiumicino, Latium, Italy | / |
| English B2 or above | meaningful / stated | strong | English B2 or above. Most of our communication is written and async | English - Upper-intermediate | / |
