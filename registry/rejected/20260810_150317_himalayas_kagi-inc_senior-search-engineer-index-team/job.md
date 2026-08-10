# Senior Search Engineer, Index Team

Posted: 2026-08-07T23:19:04Z

## Rejection

- Category: tech_stack
- Reason: role does not mention Go/Golang or PHP

### Senior Index Team Engineer

### About KagiKagi is your companion for a better web. We're building a friendly internet where you can explore, learn, and interact with confidence - free from ads, tracking, and distractions. Kagi builds advanced, user-centric technology to empower you, not replace you. Our products include Kagi Search, Orion browser, Kagi Assistant, Kagi News, Kagi Summarizer, and Kagi Translate. Every product reflects our commitment to a surveillance-free internet, designed around the user.

### About the Index TeamThe Index team builds and maintains Kagi's own search index - the layer that makes our results meaningfully different from everyone else's. While most search engines stop at aggregating results from the same sources, we go further: we build, maintain, and continuously improve our own index to give Kagi users results that nobody else can offer. It's a hard technical problem involving distributed job scheduling, large-scale data pipelines, index quality engineering, and real-time monitoring - and the work directly shapes what millions of searches return.

### The RoleWe're looking for a Senior Engineer to work on the systems that power Kagi's own index. You'll own pieces of the full pipeline - from URL frontier and job scheduling through document ingestion, processing, and indexed retrieval - and help us make that pipeline faster, fresher, and more reliable. You'll also work on index quality: understanding what's in the index, what should be, and what shouldn't be.
This is a role for someone who finds deep satisfaction in the unglamorous work that makes a search index actually good: the scheduling logic that's wrong 0.1% of the time, the deduplication that keeps coverage clean, the monitoring that catches quality regressions before users do.

### What You'll Do

- Embed within the Search team to ensure index improvements translate into better results for user.

- Design and improve the URL frontier and crawl job scheduling system - how we decide what to index, when, and in what order

- Own and evolve the indexing strategy (what we index post-crawl) and ranking implementation.

- Investigate and fix index quality issues - spam, stale content, deduplication, coverage gaps

### Must-Haves

- 5+ years of backend engineering experience in production information retrieval/search systems

- Prior experience with search index infrastructure, URL frontier systems, or crawl scheduling

- Deep expertise across the information retrieval stack: index design, relevance scoring and ranking optimization, near-duplicate detection, query engine architectures, and graph-based signal extraction.

- Strong database skills - you're comfortable designing and optimizing complex PostgreSQL schemas and queries, including large job/task tables that need to scale

- Proficiency in **Python** and/or **Rust** - our primary languages for this work

- Ability to reason about large-scale data pipelines: throughput, correctness, idempotency, and operational reliability

**Nice to have:**

- Experience with observability tooling (Prometheus, Grafana or similar)

- Comfort with Redis for distributed state and queue management

- Experience with distributed job scheduling or work queue systems - you understand the failure modes and edge cases

- Experience operating systems where correctness and data quality are the primary constraints

If you've ever spent a week tracking down a subtle bug in a distributed job scheduler and felt proud rather than defeated at the end of it, this is the role.

Originally posted on [Himalayas](https://himalayas.app)
