## Recruiter / HR Screening

- Prepare a concise motivation: Percona combines open source database tooling, Go backend engineering, distributed systems, and remote collaboration.
- Location: candidate is based in Rome/Fiumicino, Italy, which matches the listed location restrictions.
- Working model: confirm comfort with remote work, written communication, public GitHub workflows, and distributed collaboration.
- Language: English is listed as upper-intermediate/professional working proficiency; be ready to discuss day-to-day written and spoken communication.
- Notice period and current employment: reconcile the source difference between Simple.life ending March 2026 and LinkedIn listing Present before recruiter calls.
- Salary: prepare a range based on senior Go backend roles in Italy/Europe and remote seniority; do not anchor without current compensation goals.
- Job-change story: emphasize Go, production reliability, distributed systems, and interest in deeper infrastructure/database tooling.

## Culture Fit / Behavioral Interview

Likely behavioral questions:

1. Tell us about a production incident where retries, fallback logic, or monitoring changed the outcome.
2. Describe a time you had to debug a performance bottleneck under load.
3. How do you communicate trade-offs when correctness and delivery speed conflict?
4. Tell us about a code review where you changed your mind or helped another engineer improve a design.
5. How do you work with a remote team when most decisions happen in writing?
6. Describe a time you owned a system from design through production support.
7. How have you handled ambiguous requirements in backend or infrastructure work?
8. Tell us about mentoring or leading engineers while still contributing technically.

STAR stories to prepare:

- Simple.life Go support automation platform: ownership, integrations, fallback logic, retries, monitoring, and 30% ticket deflection.
- CRURATED event analytics infrastructure: versioned event schema, backpressure, downstream routing, S3, and 99.9% delivery reliability.
- airSlate Kubernetes migration and bottleneck reduction: ECS to Kubernetes, Helm/GitHub Actions/ArgoCD, database load reduction, API response improvements.
- PDFfiller transactional email service: team leadership, 50 million emails/month, and BFCM traffic surge.

## Technical Interview

**High Priority - Go concurrency and reliability.** Review goroutines, channels, contexts, cancellation, worker pools, race detection, idempotency, retries, backpressure, and graceful shutdown. Prepare examples from Simple.life and CRURATED.

**High Priority - Distributed systems correctness.** Prepare clear explanations of at-least-once versus exactly-once delivery, ordering, duplicate handling, resumability, checkpoints, replay, and consistency trade-offs.

**High Priority - MongoDB internals ramp-up.** Study change streams, oplog basics, resume tokens, replica sets, elections, sharding, chunk migration, balancer behavior, write concerns, read concerns, and failure modes. Be honest that direct production MongoDB internals are a gap.

**High Priority - Replication and CDC design.** Practice designing an initial clone plus continuous change capture flow. Cover checkpoints, ordering, idempotent apply, schema/index changes, TTL, DDL edge cases, network drops, and restarts.

**Medium Priority - Backup and restore.** Review consistent backups, point-in-time recovery, object storage failure modes, snapshots versus logical backups, and restore validation.

**Medium Priority - Observability.** Prepare examples of metrics, logs, SRE dashboards, alert signals, throughput, lag, retry counters, and saturation/backpressure indicators.

**Medium Priority - APIs and CLIs.** Review how to design operator-facing HTTP APIs and CLI commands for long-running jobs, status inspection, cancellation, and error reporting.

**Low Priority - Packaging/security scanning.** Be aware of golangci-lint, Trivy, deb/rpm packaging, and release gates, but do not claim hands-on experience unless asked.

## CV Deep-Dive Questions

- What exactly did the Go platform at Simple.life do, and which parts did you own?
- How did fallback logic and retries work, and how did you avoid duplicate processing?
- What did "backpressure handling" mean in the CRURATED event pipeline?
- How did you measure 99.9% event delivery reliability?
- What changed during the ECS to Kubernetes migration at airSlate?
- How did you diagnose API and database bottlenecks?
- What technical decisions did you make for the PDFfiller messaging service?
- How did you lead five engineers while staying close to implementation?
- Why does the LinkedIn profile show overlapping Simple App and CRURATED dates?
- Have you worked with MongoDB replication, sharded clusters, or backup systems directly?

## Company-Specific Preparation

- Read PCSM documentation and be ready to describe initial cloning, continuous replication, source/target clusters, and supported deployment constraints.
- Read PBM documentation and prepare a high-level explanation of agents, CLI, consistent backup, point-in-time recovery, and object storage.
- Review Percona's public GitHub repositories for issue and pull-request style.
- Prepare a short answer about working in the open: clear PR descriptions, respectful review, small changes, tests, and written design notes.
- Map candidate evidence to Percona's problems: Go services, event pipelines, ordering/retries, monitoring, performance, production troubleshooting, and remote collaboration.

## Preparation Plan

**Must prepare before recruiter screen:** motivation for Percona, location/remote fit, current employment chronology, English communication, compensation range, and a crisp explanation of the MongoDB domain gap.

**Before technical interview:** build a one-page study note on change streams, oplog, resume tokens, replica sets, sharding, idempotent apply, ordering, and resumability. Practice one system design: clone a large MongoDB collection, then keep it synchronized through change streams.

**Before final/culture interview:** prepare stories about ownership, code review, written communication, incident response, and how you ramp up in unfamiliar domain-heavy systems.

## Questions to Ask

1. How do you divide work between PCSM and PBM for this role during the first six months?
2. What correctness guarantees does PCSM aim to provide today, and which guarantees are still being defined?
3. Which MongoDB sharding or balancer edge cases create the most production complexity?
4. How do you test replication and backup behavior across elections, network drops, and restarts?
5. What metrics tell operators that a sync or backup is healthy?
6. How much design discussion happens in GitHub issues, pull requests, or separate design documents?
7. What does successful onboarding look like for an engineer without deep MongoDB internals experience?
8. How does the team balance community-visible work with customer-driven priorities?
9. What release-quality gates matter most for PCSM before 1.0?
