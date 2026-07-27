# Senior Software Engineer (Data Platform, C++)

Posted: 2026-07-27T03:15:50Z

**About Nebius:**

Nebius is leading a new era in cloud infrastructure for the global AI economy. We are building a full-stack AI cloud platform that supports developers and enterprises from data and model training through to production deployment, without the cost and complexity of building large in-house AI/ML infrastructure.

Built by engineers, for engineers. From large-scale GPU orchestration to inference optimization, we own the hard problems across compute, storage, networking and applied AI.

Listed on Nasdaq (NBIS) and headquartered in Amsterdam, we have a global footprint with R&D hubs across Europe, the UK, North America and Israel. Our team of 1,500+ includes hundreds of engineers with deep expertise across hardware, software and AI R&D.

#### The role

We’re looking for a **Software Engineer with strong C++ expertise** to join the team building and operating **Nebius Data Platform** — a distributed storage and a processing platform that acts as the company’s “source of truth” and the backbone of many internal (and some external) products.

Nebius Data Platform is a **single multi-tenant ecosystem based on YTsaurus** — instead of running separate HDFS/Kafka/HBase-style systems, we provide storage, compute, and analytics capabilities inside one platform.

Built on top of the open-source YTsaurus ecosystem, we run and extend our own Nebius distribution and develop significant in-house functionality (core and platform-level). We can design, implement, and roll out features end-to-end on our clusters without waiting for upstream approvals and contribute upstream when it makes sense.

At scale today, this includes**~500 servers, ~20k CPU cores** and **~10 PB of compressed** **data** in our largest production cluster, supporting workloads ranging from business-critical pipelines and financial transactions to large-scale ML/LLM training datasets and compute.

#### What’s inside the platform

You’ll work on a system that includes (and ties together):

- **Distributed Storage (Cypress)**: transactional semantics, tiered storage, erasure coding, replication, and strong reliability expectations.

- **Compute & ETL**: a cluster-wide job scheduler (tens of thousands of cores), MapReduce, **YQL** for SQL-like data processing, and **SPYT (Spark over YTsaurus)** for modern data engineering.

- **Interactive analytics (CHYT)**: ClickHouse® instances spun up directly on compute nodes for fast SQL over data in-place.

- **Dynamic Tables**: low-latency NoSQL KV with distributed ACID transactions for OLTP-style workloads and feature stores.

- **Orchestracto**: workflow orchestration deeply integrated with the platform (Airflow-like, but platform-native).

#### What you’ll do

We’re looking for engineers who combine strong systems skills with **product sense**: understanding who uses the platform, why certain capabilities matter, and making pragmatic trade-offs to maximize impact. On our team, engineering work is expected to be connected to real users and outcomes — you’ll regularly align with internal stakeholders, clarify requirements, and help drive prioritization.

In this role, you will:

- **Design and implement new functionality in YTsaurus core** (C++) with production reliability in mind.

- **Build and evolve platform-level capabilities:** platform architecture and operating model—multi-cluster growth, shared primitives, and a consistent experience that scales with new teams and use cases.

- Improve **end-to-end platform experience** for internal (and external-facing) users: APIs, guardrails, debugging workflows, and automation.

- Own production quality: **incident response / on-call rotation**, root cause analysis, and turning learnings into durable fixes.

#### Example projects

- Roll out sharded YTsaurus masters (incl. Kubernetes operator support) and build automatic balancing of metadata across master cells (consensus groups) to remove control-plane bottlenecks and **unlock 10–100x cluster growth**.

- **Make CHYT interactive SQL faster and more predictable at high load** via performance work like data-skipping / min-max-style indexes and improved execution introspection.

- Turn **Orchestracto into a platform product **by defining the building blocks, developer experience, and governance for how teams create and share workflows.

- **Scale and harden Parquet-on-S3 for native YTsaurus workloads** by tackling replication/movement, consistent lifecycle semantics, and master-server metadata optimizations for performance and reliability.

- Design and ship **complete, trustworthy audit trails for data changes** (who/what/when) across heterogeneous storage and compute paths.

#### Tech stack

- Core: **modern C++** (C++20, async + multithreaded primitives)

- Services & tooling: **Go** and **Python** (microservices, utilities, integration tests)

#### What we expect

- **5+ years** of software engineering experience.

- Strong **C++** skills (you’ll write core code).

- Working knowledge of **Python and/or Go** (you don’t have to be expert, but should be comfortable navigating them).

- Experience developing and/or operating **high-load, distributed services**.

- Production mindset: ability to **use SSH, read logs/metrics/traces**, and debug distributed systems behavior.

- Solid CS fundamentals: algorithms, data structures, concurrency basics.

#### Nice to have

- Experience with Big Data systems (YTsaurus/Hadoop/Spark/ClickHouse/Kafka-like ecosystems).

- Experience with multi-tenant platforms, schedulers, resource isolation, quotas, and reliability engineering.

- Strong performance engineering skills (profiling, lock contention, latency/throughput tradeoffs).

*We conduct coding interviews as part of the process.*

**Benefits & Perks:**

- Competitive compensation

- Career growth and learning opportunities

- Flexibility and ownership

- Collaborative and innovative culture

- Opportunity to work on impactful AI projects

- International environment and talented teams

**What's it like to work at Nebius:**

Fast moving - Bold thinking - Constant growth - Meaningful impact - Trust and real ownership - Opportunity to shape the future of AI

**Equal Opportunity Statement:**

Nebius is an equal opportunity employer. We are committed to fostering an inclusive and diverse workplace and to providing equal employment opportunities in all aspects of employment. We do not discriminate on the basis of race, color, religion, sex (including pregnancy), national origin, ancestry, age, disability, genetic information, marital status, veteran status, sexual orientation, gender identity or expression, or any other characteristic protected by applicable law.

Applicants must be authorized to work in the country in which they apply and will be required to provide proof of employment eligibility as a condition of hire.

If you need accommodations during the application process, please let us know.

Find [Jobs in Germany](https://www.arbeitnow.com) on Arbeitnow
