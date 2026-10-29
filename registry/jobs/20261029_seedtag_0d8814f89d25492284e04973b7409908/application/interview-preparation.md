# Seedtag interview preparation

## Recruiter / HR Screening

Prepare a short introduction around Go backend ownership, production AI integration and event-driven systems. Use the final CV's progression rather than listing every employer. The supported starting point is: “My recent work combines Go services, AI-agent integrations and production responsibility. I have also owned event analytics infrastructure and led backend delivery.” Treat this as a draft framing to practise, not a quotation from a previous interview.

Explain why this role is relevant through its engineering work: turning AI capabilities into reliable services and processing contextual data. Do not claim personal use of Liz or existing AdTech experience. Rome is the confirmed location, and the posting lists Italy among remote-contract countries. Ask whether selecting Milan in the form is administrative or implies regular office attendance.

Prepare current salary expectations, notice period and earliest start directly with the candidate before answering. The form requests annual gross fixed salary, while the posting gives no range. Do not infer compensation or contractual terms. Keep English upper-intermediate as stated in the CV. Do not infer citizenship or permit type from an Italian location. Explain that CRURATED was concurrent part-time consulting. The CV uses year-only precision for Simple App under the bound configuration. If asked for the month, use the latest direct confirmation of August 2026.

## Culture Fit / Behavioral Interview

Prepare six real stories as outlines. For each, identify the situation, personal decision, colleagues involved, delivery stage and observed result. Use only facts the candidate can defend.

- “Tell us about a system you owned beyond implementation.” Use telephony architecture, the design document, security decisions, review and production launch. Separate backend ownership from frontend and SRE contributions.
- “How did you turn an AI idea into usable production behavior?” Use the LLM agent's action tools and evaluation pipeline. Explain the customer workflow and avoid claiming a measured accuracy improvement.
- “When did you change a service boundary?” Use the vendor-neutral Go gateway. Its concrete outcome was the first B2B demonstration, not proven external adoption.
- “How did you simplify an established system?” Use the Snowflake-to-Intercom consolidation and removal of repeated historical reads. Explain compatibility and rollout without invented cost savings.
- “How have you handled competing integration needs?” Use CRURATED's event versions and downstream routing. Clarify what was decided independently and what needed agreement.
- “How did you help a team deliver more effectively?” Use airSlate's backend delivery responsibility and performance measures. Attribute the result to directed team work, not sole implementation.

Be ready for a follow-up about something that did not work. Select a genuine limitation or revision from these projects, then explain the response. Do not manufacture a failure story to complete the STAR format.

## Technical Interview

High Priority — Go and distributed services. Practise context cancellation, goroutine lifecycle, concurrency limits, idempotency, duplicate delivery and graceful shutdown. Connect each concept to an actual service when supported. For a coding exercise, implement a bounded worker pipeline with cancellation and tests for failure behavior. This is practice, not a claim about a previous implementation.

High Priority — system design and performance. Sketch contextual ingestion, enrichment, storage and request-serving boundaries. State assumptions about freshness, consistency and latency before choosing queues or caches. Discuss saturation, load shedding, hot keys and p99 measurements. Distinguish what the candidate has operated from hypothetical RTB-scale design. Monthly support activity is not requests per second.

High Priority — production AI integration. Explain tool authorization, retries, malformed output, evaluation datasets, fallback and operational visibility. Use the documented conversation/action/subscription-state evaluation pipeline. Prepare to discuss how one would separate model quality from service reliability. RAG and embeddings are study topics, not confirmed experience.

High Priority — data pipelines and database behavior. Revisit schema evolution, parallel event versions, backpressure, delivery semantics and consumer compatibility. Explain keyset pagination, query-plan inspection and overload isolation. Be precise about which decisions came from CRURATED and which from Simple App.

Medium Priority — infrastructure and operations. Review AWS queues, IAM boundaries, Kubernetes workloads, Terraform workflow, Prometheus signals and safe rollout. Terraform is in the confirmed stack, but the CV does not establish every infrastructure responsibility. Prepare a concrete defensible example before claiming ownership. Medium Priority — AdTech fundamentals: bid requests, OpenRTB, CTV metadata and contextual enrichment. Low Priority — secondary-language exercises in Python, Node.js or TypeScript unless the recruiter confirms they are tested.

## CV Deep-Dive Questions

Expect “What exactly did the evaluation pipeline produce, who used it, and how were failures investigated?” Prepare the real data flow and distinguish delivered tooling from unmeasured model improvement. For telephony, expect questions about where architectural authority began, why security review was needed, how sensitive data was handled and what happened after launch.

For the gateway, defend tenant separation, event contracts, vendor adapters and the demonstration milestone. For the pipeline consolidation, explain the reason for unification, behavior preserved and operating work eliminated. For CRURATED, explain parallel-version compatibility, downstream pressure and personal production responsibility. For airSlate, discuss the bottleneck, contribution as backend lead and Prometheus measurement basis. No financial saving or withdrawn migration should appear in an answer.

## Company-Specific Preparation

Read the already verified [role](https://jobs.seedtag.com/jobs/8578657-senior-software-engineer) and [Liz overview](https://www.seedtag.com/liz) before the interview. The useful connection is productionizing AI and enriching contextual information across open-web and CTV environments. Treat marketing scale figures as company statements. The interview should establish this team's actual workload, latency budget and operational authority.

## Preparation Plan

Must prepare: a concise career explanation, telephony ownership story, agent evaluation walkthrough and honest account of the domain gap. Before the technical round: rehearse the gateway and event architecture on a diagram, revisit Go concurrency and database performance, and practise one bounded coding problem. Before the final/culture round: prepare a concrete collaboration example, current availability and compensation position, and questions about autonomy and on-call responsibility.

## Questions to Ask

- Which contextual tasks run asynchronously, and which are directly on the bidding path?
- What latency and reliability objectives does this team own?
- How are AI changes evaluated before rollout and monitored afterward?
- Where does the platform team work directly with Data Science and Product?
- What would successful delivery in the first few months look like?
- How is on-call organized, and what support exists during incidents?
- What contract, compensation range and travel expectations apply to someone based in Italy?
