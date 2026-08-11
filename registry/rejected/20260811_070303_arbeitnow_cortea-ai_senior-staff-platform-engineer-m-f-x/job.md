# Senior/Staff Platform Engineer (m/f/x)

Posted: 2026-08-10T20:40:20Z

## Rejection

- Category: location_requirement
- Reason: vacancy is explicitly non-remote

# **Your Role**

We ship fast, and we intend to keep shipping fast. The consequence is that our system is outgrowing the amount of deliberate design that went into it. We run AI agents over customer documents in a domain where being wrong is expensive, and a lot of the load-bearing decisions about how those fit together are still implicit.

You will be making those decisions explicit and then making them hold. That means codifying golden paths, building the shared primitives and APIs that product engineers work on top of, owning the architecture of the system as a whole, and establishing what our reliability actually needs to be before an incident establishes it for us.

Platform at Cortea sits between software engineering, DevOps and SRE. Its customers are other engineers. This is not a DevOps role under a different name: you will spend more time in application code than in YAML, and the reason we want infrastructure experience is that we don't believe you can design a system well without being able to run it.

The bar we are hiring against is someone who has taken a system from nothing to production and owned it end to end. You picked the technology, argued the tradeoffs in writing, provisioned the infrastructure, and were responsible for it when it broke.

## **
On AI**

We use AI heavily and we want you to. What we are not looking for is someone who outsources their judgment to it.

The mental model of this system has to live in your head, not in a context window. Use agents to move quickly on implementation. Do the design, the reasoning and the writing yourself, and be able to defend every decision you ship.

#
**What you'll do**

Four areas, roughly in the order you will spend time on them. You won't work on all of them at once, but you should be open to any of them.

**Product platform.** Make the easiest way for product engineers to do something (the paved road, or golden path) also the most secure, reliable and scalable way by default. Build the shared primitives, libraries and APIs that hide complexity and carry our quality and observability standards with them. Own the architecture and the core stack: what gets standardized, what gets reused, and where the system should be in eighteen months.

**Infrastructure, observability and reliability.** Infrastructure as code by default, from cloud resources through to dashboards and alerts. Provision, run and tune our Kubernetes cluster and cloud footprint, and keep CI fast as the deploy rate grows. Define SLIs for the workloads that
matter, build SLOs on top of them, and make the alerting high-signal enough that people trust it. Drive down AI and infrastructure spend.

**Security and compliance.** Keep the internal foundations secure by default: IAM, dependency management, secrets. Own the authentication and authorization stack, including ReBAC models covering both humans and agents. Implement SOC 2 and ISO 27001 controls without taxing every future change.

**AI dev tooling.** Keep product engineers and their agents on the paved road by making sure the documentation and agent guidelines they need are in place. Shorten the path from design to implementation with standardized automations and development environments that stay close to production.

##
**What this looks like in practice**

-

A system of record for managing and distributing constantly evolving agent configurations, under strict auditability and tenant isolation requirements

-

The harnesses powering our AI agents, abstracting over use cases that change faster than the code

-

Centralized progress tracking that holds up across a growing number of parallel agent executions

-

Usage-based tenant billing with quotas and rate limiting across a growing set of products

-

SLIs for the background job system behind our agents (execution latency, AI spend, memory, CPU), then fixing the bottlenecks they expose at both the application and infrastructure level

-

A document pipeline handling dozens of file formats, very large spreadsheets and hundreds of parallel uploads, under a strong reliability requirement

# **
You will fit into this role if you…**

-

Have designed, built and operated distributed systems end to end, and enjoy understanding how every part interacts with the rest

-

Are strong at backend software engineering **and** at DevOps/SRE, and don't think of those as separate jobs

-

Write design docs, RFCs, ADRs, postmortems

-

Reach for simple, boring solutions first, can tell essential complexity from accidental, and know which corners are safe to cut and which ones compound

-

Can turn a hard problem on its head and find the alternative nobody proposed

Concretely, you have scaled Postgres or another relational transactional database under real load, run production Kubernetes, and built observability rather than inherited it: SLIs, SLOs, distributed tracing.

No one checks every box. If you have designed a system from scratch, run it in production, and can explain in writing why it is shaped the way it is, let's talk.

## **
Nice-to-haves that are a plus:**

-

Durable workflow orchestrators like Temporal, and background job and queue processing generally

-

Infrastructure for LLM-based products or agentic systems

-

Audit, finance, compliance, or another high-accuracy domain

-

Azure and/or GCP

##
**This is probably not the right role if…**

-

You would describe application code as someone else's responsibility. A large share of platform work here happens inside the product codebase.

-

Your answer to reliability is more process. We want guardrails, not gates.

-

You need a well-defined system to work in. Ours is not one yet, and shaping it is the job.

# **
What you will get**

-

**You own the brand and shape how the product feels**. Work face-to-face with experienced founders and learn directly from customer insights.

-

**Real influence on strategy**. In a small team of excellent engineers and operators with high autonomy, you will shape product direction. Best idea wins, regardless of seniority.

-

**Fast, ambitious, and fun team**. Decisions get made in hours, not weeks. Rapid experimentation is the default.

-

**Meaningful equity and competitive salary**. You are one of the first to build this, and you share in the upside.

-

**A mission that matters.** Building intelligent systems for a $200bn industry. From Berlin, with AI at the core.

# **
Interview process**

-

**First Call** — Intro to Cortea with [Liza](https://www.linkedin.com/in/liza-shaban/?skipRedirect=true)

-

**Second Call** — Technical interview with [Dan](https://www.linkedin.com/in/dansvetlov/)

-

**Third Call** — Deep dive into our culture with our Co-Founder [Philipp](https://www.linkedin.com/in/philipp-hoevelmann/)

-

**On-site Day (Berlin)** — Meet the team and work on a real problem together

Find [Jobs in Germany](https://www.arbeitnow.com) on Arbeitnow
