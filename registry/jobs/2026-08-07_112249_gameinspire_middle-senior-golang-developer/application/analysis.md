## Vacancy Summary

The vacancy seeks a mid-to-senior backend engineer with at least three years of Go, including web-server development, concurrency, and context handling. Explicit requirements include SQL and NoSQL fundamentals, indexes, transactions and query optimization; MySQL or PostgreSQL plus MongoDB; RabbitMQ or Kafka; Redis; high-load behavior such as locks, isolation and replication; microservices/SOA; REST APIs; production delivery and alert response; code review and mentoring; and English at Intermediate level or above. The role is remote-compatible and also available in Kyiv or abroad.

The strongest candidate evidence is recent ownership of a Go backend platform, production message-delivery reliability, event-driven systems, RabbitMQ, MySQL and PostgreSQL, database and API optimization, monitoring, microservices, code review, mentoring, and leadership under peak traffic. The main evidence gaps are MongoDB, Redis, Kafka, explicit Go context-handling examples, and iGaming experience. The vacancy treats PHP developers moving into Go as acceptable, which further reduces stack risk.

Inferred hiring-manager priorities are safe delivery across a large service estate, practical reasoning about concurrency and data consistency, disciplined incident response, and engineers who contribute to architecture without stepping away from implementation.

## Company Research

- **Verified fact:** The official product site describes a B2B casino platform covering casino games, betting, payments, KYC/anti-fraud, responsible gaming, reporting, affiliates, and CRM. It publishes figures including 6M+ monthly active players, 250+ casinos powered, and 100+ payment methods. [Official platform site](https://gameinspire.com/en)
- **Verified fact:** The DOU profile lists the company as a Kyiv-based tech product business with 81–200 specialists and shows remote vacancies across engineering and product. [DOU company profile](https://jobs.dou.ua/companies/gameinspire/)
- **Verified fact:** The company's LinkedIn page describes a platform of more than 200 modules and services intended for 24/7 operation and lists the organization as privately held with 51–200 employees. [LinkedIn company page](https://www.linkedin.com/company/gameinspire)
- **Inference:** Because payments, player activity, CRM, KYC, and reporting share one platform, backend changes likely carry data-consistency, availability, and cross-service integration risk beyond ordinary CRUD work.
- **Inference:** The open-management language in the vacancy and public emphasis on team autonomy suggest that architecture proposals and production ownership are expected from individual contributors.
- **Unknown:** Public sources reviewed do not establish the exact Go framework, deployment platform, observability stack, team topology, on-call rotation, database ownership, or the relative use of RabbitMQ versus Kafka.

## Initial Resume Audit

**Impact — 8/10.** Strength: the source material contains credible scale evidence, including 30% ticket automation, more than 10x analytics throughput, 50 million emails per month, and peak traffic above 10x. Weakness: several source bullets describe responsibilities before outcomes. Rewrite example: “Built routing logic for multiple downstreams” → “Built modular routing to Webhook and S3 destinations, reducing implementation time for new analytics streams from several days to under four hours.”

**Keyword relevance — 7/10.** Strength: Go, RabbitMQ, MySQL, PostgreSQL, microservices, APIs, monitoring, and high-load operations are supported. Weakness: the original summary did not foreground database consistency, queues, production alerts, mentoring, or code review. Rewrite example: “Backend engineer with PHP and Go experience” → “Backend engineer and technical lead with production experience in Go, event-driven services, RabbitMQ, SQL databases, microservices, monitoring, code review, and mentoring.”

**Readability — 7/10.** Strength: the source CV has clear company chronology and concise bullets. Weakness: skills were split across many small subsections, making the target stack harder to scan. Rewrite example: consolidate the target technologies into one ordered 15-item Skills section.

**Summary effectiveness — 7/10.** Strength: it establishes seniority and a backend focus. Weakness: it spends space on broad domains instead of the vacancy's operational requirements. Rewrite example: lead with Go platform ownership, event-driven systems, database/API performance, and peak-load reliability.

**ATS compatibility — 8/10.** Strength: the source structure is text-first and uses standard headings. Weakness: exact supported terms such as high-load systems, SQL, code review, and observability were not prominent enough. Rewrite example: add those terms naturally to Skills and relevant experience bullets without adding MongoDB, Redis, or Kafka.

**Overall baseline: 7.4/10.** The most important changes were to make Go and high-load operations visible in the first screen, consolidate supported target keywords, retain measurable scale, and expose leadership evidence without turning the CV into a management profile.

## Strict Hiring Manager Review

**Strength 1: Recent hands-on Go ownership.** The Simple.life work shows ownership of a production Go backend integrated with external and internal systems, not only training or side-project exposure.

**Strength 2: Reliability at operational scale.** Retries, fallback logic, monitoring, peak-load response, database optimization, and delivery guarantees align with alert response and high-load service ownership.

**Strength 3: Technical leadership without leaving implementation.** The candidate has led teams of five and ten, reviewed code, mentored engineers, planned delivery, and still contributed to backend architecture and code.

**Weakness 1: No explicit MongoDB or Redis evidence.** These are named requirements, so a hiring manager may question immediate breadth across the current data stack. Safe rewrite: do not claim them; foreground proven MySQL, PostgreSQL, Elasticsearch, RabbitMQ, and event-driven design, and prepare a concrete learning plan.

**Weakness 2: Go concurrency and context handling are not described explicitly.** General Go ownership does not prove command of goroutines, cancellation, race prevention, or context propagation. Safe rewrite: keep “Go-based backend platform” in the CV and prepare a source-backed technical example before interview rather than adding unsupported details.

**Weakness 3: Overlapping Simple.life and CRURATED dates are unexplained.** The overlap from August 2024 through January 2026 may create concerns about engagement type, workload, or disclosure. Safe rewrite: preserve both timelines; confirm the relationship and explain it accurately during recruiter screening.

After review, the CV was revised to emphasize recent Go delivery, event-driven scale, database/API optimization, production reliability, and mentoring. No unsupported database, concurrency, or gaming claims were added.

## Red Flags

- **Conflicting Simple.life end date:** the CV registry records March 2026, while the LinkedIn export says Present. Use March 2026 in this package because it is the newer dated source, but confirm the current status before submitting.
- **Concurrent Simple.life and CRURATED timelines:** preserve the dates and prepare a transparent explanation of whether CRURATED was part-time, contract, or another arrangement; the source does not establish the engagement type.
- **Broad 15+ year tenure:** the tailored Experience section includes only roles from October 2016 onward, complying with the ten-year limit and keeping the document relevant.
- **Technology gaps:** MongoDB, Redis, Kafka, Go context handling, and iGaming are not supported by the candidate records. They remain gaps instead of being converted into keywords.
- **Work authorization, notice period, and salary:** all remain unconfirmed and should be answered before recruiter contact.
- **Job transitions:** the chronology is generally continuous. The Sixt/PDFfiller boundary and the concurrent 2024–2026 entries should be explained plainly if asked.

## ATS Keyword Analysis

The top 15 prominent terms in the final CV are: Go, microservices, high-load systems, REST APIs, RabbitMQ, SQL, MySQL, PostgreSQL, event-driven systems, AWS, Kubernetes, CI/CD, observability, system design, and mentoring/code review.

**Direct matches:** Go, SQL, MySQL, PostgreSQL, RabbitMQ, microservices, REST APIs, high-load operation, monitoring, production delivery, code review, mentoring, system design, and database/query optimization.

**Fully missing required terms:** MongoDB, Redis, Go context handling, and explicit Go web-server development. Kafka is missing, but RabbitMQ satisfies the vacancy's stated queue alternative.

**Underrepresented but supported before tailoring:** event-driven systems, observability, SQL, peak-load reliability, technical interviews, code review, and mentoring. These were made more visible in Summary, Skills, and Experience.

**Terms deliberately not added:** MongoDB, Redis, Kafka, SOLID, Go context propagation, replication implementation, and iGaming domain experience. The vacancy uses these terms, but the candidate sources do not provide adequate evidence.

The final pass improved supported keyword coverage without changing the unsupported gap list. Estimated ATS alignment improved from 7.8/10 to 8.7/10.

## Major CV Changes

- **Summary:** “Backend engineer with 15+ years across PHP and Go” → a focused summary covering Go platform ownership, event-driven services, database/API performance, high-load reliability, and mentoring.
- **Skills:** many fragmented technology subsections → one vacancy-ordered list of 15 supported hard skills.
- **Simple.life:** “Designed and owned a Go-based support automation platform” → retained the Go ownership and added supported integration, automation, retry, fallback, monitoring, and peak-load outcomes.
- **CRURATED:** descriptive architecture bullets → outcome-led bullets with more than 10x throughput, under-four-hour stream implementation, and above-99.9% delivery reliability.
- **airSlate:** infrastructure duties → stronger emphasis on database/API performance, production troubleshooting, Kubernetes delivery, technical interviews, and end-to-end team delivery.
- **Experience scope:** removed roles beginning before the most recent ten-year window; no dated Experience entry predates October 2016.
- **Credibility:** excluded unsupported MongoDB, Redis, Kafka, Go context, and iGaming claims and retained the visible timeline overlap for honest discussion.

## Final Quality Gate

- **Role fit: 8.7/10.** Strong Go/backend, queue, database, microservice, high-load, and production-operations alignment; named data-store gaps remain.
- **Recruiter screening potential: 8.2/10.** Remote location, English, seniority, and leadership fit well; authorization, availability, compensation, and overlapping dates need clear answers.
- **Hiring-manager appeal: 8.8/10.** The package shows ownership, measurable scale, reliability, architecture participation, mentoring, and continued hands-on work.
- **ATS compatibility: 8.7/10.** Standard structure and strong supported keyword coverage; unsupported requirements are correctly absent.
- **Credibility: 9.0/10.** Claims are grounded in the two candidate records, conflicts are disclosed, and no missing stack item is presented as experience.

The final CV is internally consistent with the chosen March 2026 Simple.life end date, preserves the CRURATED overlap, uses standard ATS headings, and limits Experience to the last ten years. The cover letter was tightened with Stop Slop guidance: it opens with evidence, avoids repeating the company or vacancy title, removes generic enthusiasm, and keeps each claim source-backed.

## Recommendation

**Strong Apply.** The candidate has unusually relevant evidence in recent Go platform ownership, event-driven design, production reliability, databases, queues, high-load systems, and technical leadership. MongoDB, Redis, explicit Go context handling, and iGaming remain genuine interview risks, but the vacancy's openness to PHP engineers moving into Go and the candidate's production Go work make the application well justified.
