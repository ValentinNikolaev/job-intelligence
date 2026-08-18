# Sr. Software Engineer - Go/MongoDB

Posted: 2026-07-29T05:07:32Z

## Rejection

- Category: stale
- Reason: published_at 2026-07-29T05:07:32Z is older than 7 days

### MongoDB Tools Team

**Team: **MongoDB Tools (Product and Engineering)

**Location: **Remote

**Projects: **percona/percona-clustersync-mongodb and percona/percona-backup-mongodb

### About the team

The MongoDB Tools Team builds [Percona](https://himalayas.app/companies/percona)'s open source operational tooling for MongoDB. Two projects sit at the center of what we do. [Percona](https://himalayas.app/companies/percona) ClusterSync for MongoDB (PCSM) clones and continuously replicates data between clusters. [Percona](https://himalayas.app/companies/percona) Backup for MongoDB (PBM) is a distributed, low-impact backup and restore solution for replica sets and sharded clusters. Both are written in Go, both are Apache 2.0 licensed, and both are built fully in the open.

This role sits primarily on PCSM, which is younger and moving fast, so you will have real influence over how it takes shape. You will also work across into PBM. The two tools share many hard problems: cluster topology, the oplog and change streams, consistency across shards, and performance in very large production clusters. Backup and restore experience is a real advantage here, not just a box to tick.

### The projects

-

**PCSM **(primary focus): initial data cloning followed by continuous change replication over MongoDB Change Streams, for both replica sets and sharded clusters. Still pre-1.0 and evolving quickly.

-

**PBM **(secondary): consistent backup and restore with point-in-time recovery, using oplog capture to stay consistent across replica sets and sharded clusters, with S3-compatible and filesystem storage. Driven by pbm-agent processes on each node and a pbm CLI. Mature and widely deployed in production.

### What you will work on

### Primary, on PCSM

-

**The core replication engine: **initial collection cloning followed by continuous change capture over MongoDB Change Streams, with correct handling of resume tokens, ordering, and resumability after failures.

-

**Correctness and fault tolerance at scale: **recovering cleanly from network drops, primary elections, and restarts without losing or duplicating changes, and reasoning carefully about the delivery guarantees we can honestly promise.

-

**Sharded cluster support: **replicating across shards, dealing with the realities of chunk migrations and balancer activity, and keeping the target consistent.

-

**Namespace filtering and automatic index management, **plus the edge cases that show up with DDL, TTL, and index differences between source and target.

-

**Performance and throughput: **parallelizing the clone, applying backpressure, and keeping memory and connection use sane against large clusters with great change volume.

-

**The CLI and HTTP API **that drive and observe a sync, and the metrics and logging that let an operator trust what is happening.

### Also across PBM

-

**Consistent backup, restore, and point-in-time recovery** across replica sets and sharded clusters, using physical or logical type of the backup.

-

**Backup storage: **integrating reliably with main cloud object storage (S3, GCS, Azure Blob Storage...) and remote filesystems, and handling the throughput and failure modes that show up at scale.

-

**The pbm-agent and pbm CLI, **and the control-collection state in MongoDB that coordinates them across the cluster.

### Shared across both

-

**Working in the open: **pull requests, code review, JIRA, and the community forum.

-

**Release quality: **tests, packaging, and the CI and security scanning that gate every change.

### What Have You Done:

-

**Strong Go experience in production, **with real fluency in concurrency: goroutines, channels, context cancellation, worker pools, and backpressure. You have debugged a race condition that only showed up under load, and you know how you found it.

-

**Solid grounding in distributed systems and data consistency. **You can talk clearly about at-least-once versus exactly-once, idempotency, ordering, and what it takes to make a stateful process resumable.

-

**Hands-on MongoDB knowledge: **change streams, the oplog, resume tokens, replica sets, and sharding. You do not need to have built replication before, but you should understand why it is hard.

-

**Comfort building and operating command-line tools and HTTP APIs, **and instrumenting them with metrics and structured logs.

-

**A habit of writing tests that catch real problems, **and comfort working across a mixed toolchain.

-

**Experience working in the open: **Git and pull request workflows, giving and taking code review well, and communicating clearly in writing with contributors you have never met in person.

### Nice to have

-

Prior work on database internals, CDC pipelines, ETL, or data migration tooling.

-

Familiarity with the Prometheus style of metrics and observability.

-

Experience with golangci-lint, vulnerability scanning (for example Trivy), and deb and rpm packaging.

-

Background maintaining or contributing to an open source project with an external community.

-

Exposure to MongoDB sharded clusters at large scale, where balancer behavior and backup interaction stop being theoretical.

### How we work

Both projects live on GitHub, contributions go through pull requests and code review, and we track work in JIRA. We care about keeping open source open, so the default is that the work you do here is public and stays that way.

### Why [Percona](https://himalayas.app/companies/percona)?

At [Percona](https://himalayas.app/companies/percona), we believe an open world is a better world. Our mission is to enable everyone to innovate freely, by providing the best open source database software, support, and services. We make databases and applications run better through a unique combination of expertise and open source software built with the community for you. Our technical teams are experts in MySQL, MongoDB, PostgreSQL, and MariaDB.

[Percona](https://himalayas.app/companies/percona) is proud to be a remote-only and globally dispersed workforce – we have colleagues in more than 50 countries! We offer a collaborative, highly-engaged culture where your ideas are welcome and your voice is heard.

Our staff receives generous benefits including flexible work hours and various paid time off programs, all your equipment for your remote office, funds for career development (external training, certifications, conferences), ongoing connectivity allowances, and the opportunity to participate in our equity incentive plan. We also have benefits that support a healthy work/life balance such as The [Percona](https://himalayas.app/companies/percona) Adventure Team, Work-from-Anywhere, FlowDays, FryDays, and overall flexibility. We also support being socially responsible through our PAVE volunteering program and Women Transforming Technology.

If you love the idea of working with a high-growth tech company that is one of the best in the business and known globally as a leader in the open-source database space, let’s talk!

Connect with us and stay up to date on our latest news and developments by following us on LinkedIn and Twitter. We look forward to connecting with you!

Originally posted on [Himalayas](https://himalayas.app)
