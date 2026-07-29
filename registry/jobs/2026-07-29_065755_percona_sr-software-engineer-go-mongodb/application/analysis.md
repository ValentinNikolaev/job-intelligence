## Vacancy Summary

**Role:** Sr. Software Engineer - Go/MongoDB at Percona, MongoDB Tools team, remote for Croatia, Italy, Poland, and Spain. The role focuses primarily on Percona ClusterSync for MongoDB and also contributes to Percona Backup for MongoDB.

**Explicit requirements:** strong production Go, concurrency with goroutines/channels/context cancellation/worker pools/backpressure, distributed systems and data consistency, at-least-once versus exactly-once reasoning, idempotency, ordering, resumability, MongoDB change streams/oplog/resume tokens/replica sets/sharding, CLI and HTTP API development, metrics, structured logs, tests, Git pull-request workflows, code review, JIRA, and clear written communication.

**Inferred requirements:** the hiring manager will likely screen for careful failure-mode thinking, operational humility, and the ability to make correctness trade-offs visible. Because PCSM is pre-1.0, the role likely rewards engineers who can shape architecture while keeping implementation grounded in tests and production behavior.

**Candidate fit:** strong on Go, event-driven services, resilient pipelines, backpressure, retries, monitoring, Kubernetes delivery, performance troubleshooting, AWS/S3-adjacent routing, and senior technical ownership. The main gap is direct MongoDB internals, change streams, oplog, sharding, and backup/restore implementation evidence.

## Company Research

**Fact:** Percona describes itself as an open source database software, support, and services company serving MySQL, PostgreSQL, MongoDB, Valkey/Redis, and MariaDB users. Source: [Percona](https://www.percona.com/).

**Fact:** Percona Backup for MongoDB is described as a distributed, low-impact solution for consistent backups of MongoDB sharded clusters and replica sets. Source: [Percona Backup for MongoDB GitHub](https://github.com/percona/percona-backup-mongodb).

**Fact:** Percona ClusterSync for MongoDB documentation describes PCSM as a tool for replicating data from a source MongoDB cluster to a target MongoDB cluster, supporting migrations with minimal downtime. Source: [Percona ClusterSync for MongoDB documentation](https://docs.percona.com/percona-clustersync-for-mongodb/).

**Fact:** Percona's MongoDB software pages position its MongoDB products around open source or source-available alternatives, support, services, and avoiding vendor lock-in. Source: [Percona MongoDB software](https://www.percona.com/mongodb/software/).

**Inference:** the team likely values public engineering discipline, code review quality, reproducible tests, and operator trust because both named products are public, infrastructure-heavy tools for production databases.

**Unknown:** public sources reviewed do not confirm the exact interview stages, team size, internal release cadence, or how much of the role will be PCSM versus PBM after onboarding.

## Initial Resume Audit

**Impact - 8/10.** Strength: the profile has strong production outcomes, including 30% ticket deflection, 10x DataLake throughput, 99.9% delivery reliability, reduced database load, and 50 million emails per month. Weakness: the original CV does not make resumability, backpressure, retries, and operational correctness visible enough for this role. Rewrite example: "Built resilient message delivery pipelines..." became a front-page Simple.life bullet aligned with failure handling and peak load.

**Keyword relevance - 7/10.** Strength: Go, event-driven systems, AWS, Kubernetes, RabbitMQ, Prometheus, monitoring, APIs, performance optimization, and reliability are supported. Weakness: MongoDB, change streams, oplog, sharding, replica sets, resume tokens, and backup/restore are not evidenced. Rewrite example: the Skills section now includes supported terms such as worker pipelines, backpressure, monitoring, and distributed systems while leaving MongoDB internals out.

**Readability - 8/10.** Strength: the source CV is structured and measurable. Weakness: the original source spreads role-relevant evidence across several sections. Rewrite example: CRURATED event-pipeline evidence is included as its own recent experience block for faster screening.

**Summary effectiveness - 7/10.** Strength: the original summary establishes senior backend, Go, APIs, automation, and reliability. Weakness: it was broader than Percona's systems role. Rewrite example: the tailored summary foregrounds Go-based platforms, event-driven services, backpressure-adjacent delivery, observability, performance optimization, and production reliability.

**ATS compatibility - 8/10.** Strength: the CV uses plain Markdown and standard headings. Weakness: key supported terms were underrepresented. Rewrite example: the Skills section is ordered around Go, distributed systems, event-driven systems, worker pipelines, backpressure, AWS, Kubernetes, databases, Prometheus, and monitoring.

**Baseline:** 7.6/10. Most important changes: make Go and reliability evidence visible, add CRURATED event-pipeline experience, emphasize backpressure/retries/observability, and avoid unsupported MongoDB internals.

## Strict Hiring Manager Review

**Strengths:** (1) recent Go platform ownership supports production seniority; (2) CRURATED and Simple.life show event-driven reliability, retries, backpressure handling, and observable delivery; (3) airSlate and PDFfiller show performance troubleshooting, production operations, and team leadership under load.

**Weakness:** no direct MongoDB internals evidence. This matters because the role explicitly names change streams, oplog, resume tokens, replica sets, and sharding. Safe rewrite: state adjacent experience in event-driven pipelines, ordering concerns, retries, and reliability without claiming MongoDB-specific implementation.

**Weakness:** no explicit database backup/restore or point-in-time recovery work. This matters for PBM. Safe rewrite: emphasize high-volume systems, S3 downstream routing from CRURATED, operational reliability, and production incident handling.

**Weakness:** source chronology has possible overlap between Simple.life and CRURATED, and Simple.life differs between March 2026 in the CV and Present in LinkedIn. This matters because recruiters may ask about current employment status. Safe rewrite: keep source dates factual in the CV and prepare a simple explanation if asked.

**Applied review:** the CV keeps only supported claims, includes recent CRURATED evidence because it directly supports event delivery and S3 routing, and omits MongoDB-specific keywords as experience claims. A second pass found no unsupported role-specific technology claims.

## Red Flags

- **MongoDB depth gap:** the vacancy asks for hands-on MongoDB internals. The candidate should prepare to discuss what is known, what is adjacent, and how they would ramp up on change streams, oplog behavior, resume tokens, replica sets, and sharding.
- **Backup/restore gap:** no direct backup product evidence appears in the candidate sources. The safest angle is production reliability, consistency thinking, retries, monitoring, and S3-adjacent routing.
- **Overlapping records:** LinkedIn lists Simple App and CRURATED overlapping. The CV should not hide this, but the candidate should explain the working arrangement plainly if asked.
- **Certification exclusion:** the source contains Zend certification, but the application prompt forbids mentioning it, so it is omitted.

## ATS Keyword Analysis

**Top vacancy terms:** Go, MongoDB, change streams, oplog, resume tokens, replica sets, sharding, distributed systems, consistency, idempotency, ordering, resumability, worker pools, backpressure, CLI, HTTP API, metrics, structured logs, tests, Git, pull requests, JIRA, S3, GCS, Azure Blob Storage, Prometheus.

**Matches supported by evidence:** Go, distributed systems, event-driven systems, consistency-adjacent delivery guarantees, ordering-adjacent event pipelines, retries, backpressure handling, HTTP/REST APIs, monitoring, logging, tests/CI, GitHub Actions, Kubernetes, AWS, S3 downstream routing, Prometheus, performance troubleshooting, code review/technical leadership.

**Fully missing or not evidenced:** MongoDB change streams, oplog, resume tokens, replica sets, sharding, database replication engines, point-in-time recovery, Azure Blob Storage, GCS, deb/rpm packaging, Trivy, golangci-lint, and open source maintainer work.

**Underrepresented but supported before tailoring:** backpressure, delivery guarantees, observability, production reliability, performance optimization, and event pipelines. These terms now appear in the summary, Skills, and Experience.

**Terms deliberately not added as experience:** MongoDB internals, sharded clusters, oplog, resume tokens, and backup/restore were not added because candidate evidence does not support them.

## Major CV Changes

- **Summary:** broad backend profile -> Go-based platforms, event-driven services, observability, performance optimization, and reliability.
- **Skills:** general skills list -> supported Percona-relevant hard skills such as Go, distributed systems, worker pipelines, backpressure, AWS, Kubernetes, Prometheus, and monitoring/logging.
- **Simple.life:** support automation evidence -> Go platform ownership, retries, fallback logic, monitoring, real-time workflow migration, and measurable automation impact.
- **CRURATED:** added because it provides strong evidence for event-driven architecture, S3 downstream routing, delivery guarantees, backpressure, observability, and 99.9% delivery reliability.
- **airSlate:** emphasized Kubernetes migration, performance bottleneck investigation, production troubleshooting, and delivery metrics.
- **Unsupported keywords:** MongoDB internals and backup/restore terms were kept in analysis as gaps, not inserted into the CV as experience.

## Final Quality Gate

Factual support: **9/10** - all CV claims trace to candidate records, and unsupported MongoDB internals are labeled as gaps.  
Role fit: **8/10** - strong Go, reliability, event-driven, cloud, API, and production operations fit; domain-specific MongoDB internals remain the main risk.  
Recruiter screening potential: **8/10** - seniority, location eligibility, Go, remote-compatible experience, and production outcomes are clear.  
Hiring-manager appeal: **7/10** - the candidate can credibly discuss reliability and pipelines, but must prove ability to ramp into MongoDB internals.  
ATS compatibility: **8/10** - simple text format, direct headings, and supported keywords.  
Credibility: **9/10** - the package avoids inflated MongoDB claims and names the learning areas.

## Recommendation

**Strong Apply.** The role is a strong match for the candidate's Go, event-driven systems, reliability, monitoring, performance, and production troubleshooting background. The application should be paired with targeted preparation on MongoDB change streams, oplog semantics, replica sets, sharding behavior, backup/restore consistency, and idempotent replication design.
