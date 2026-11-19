# Interview preparation — Seedtag Senior Go Engineer

## Recruiter / HR Screening

Present yourself as a backend engineer with recent Go production ownership and a longer history of building and operating backend systems. Lead with the helpdesk gateway and the failure-recovery example, then explain the CRURATED event pipeline as a separate PHP consulting engagement. The connection is the discipline of boundaries, delivery and observation. Do not imply previous auction engineering or equate support tickets per month with an exchange's traffic rate.

The official vacancy says the team owns the AdExchange end to end and must balance millisecond decisions, cost and reliability. Its stated requirements include measured p99 or serving-cost work, distributed systems, cloud delivery and a daily AI coding workflow. Prepare to distinguish what you have done from how you would approach a new problem. The posting also lists Italy for remote contracts. Ask what the arrangement means in practice.

## CV Deep-Dive Questions

### Story 1: vendor-neutral gateway

**Question:** Tell us about a Go service you designed and shipped.

**Evidence:** At Simple.life the candidate built a Go gateway that placed Intercom and Zendesk behind a vendor-neutral event model. The delivered scope included an inbound schema, webhook ingestion, per-tenant storage and SQS queues, adapters and deployment. It enabled the first B2B demonstration of the support AI product.

**Answer structure:** Start with the problem of keeping vendor-specific SDKs at one boundary. Explain the interface and event model, how tenant data and queues were separated, and which adapters and outbound operations were implemented. Finish with the demo and deployment, not a speculative estimate of future integration savings. If asked about ordering, duplication, tenant isolation or replay, distinguish the actual gateway's behaviour from the design you would propose today. The record does not establish every guarantee.

### Story 2: degraded API and incomplete scans

**Question:** Describe a production failure and how you made the system safer.

**Evidence:** A support-ticket scan exceeded its overall run budget when Intercom search degraded, and the overall-context-done branch bypassed per-page retry. The candidate diagnosed the behaviour in logs and code, added partial-success semantics and an incomplete-scan metric, and sharded the search into parallel cursor chains.

**Answer structure:** Explain why exiting successfully without visibility would be misleading. Show how the metric distinguished an incomplete scan from a complete one and what operational response that signal enabled. Describe the sharding as an implemented change, but do not claim the estimated fourfold speedup or that all future failures disappeared. Be ready to discuss how to test the overall deadline, retries, cursor boundaries and duplicated records without inventing test results.

### Story 3: event versioning and delivery

**Question:** How have you managed changing event schemas and downstream consumers?

**Evidence:** In the concurrent CRURATED subcontract, the candidate owned production event analytics and DataLake work, including parallel event-version publication. The source describes versioned schemas, routing to downstream destinations, retries, observability and backpressure handling.

**Answer structure:** Explain the actual event contract and what parallel versions allowed teams to do. Discuss the consumer compatibility problem and how downstream routing was organised. The record confirms technical ownership and production use, not sole authorship of every line or specific adoption and financial outcomes. If the interviewer asks for delivery guarantees, explain the actual semantics you can substantiate and do not automatically call them exactly-once.

### Story 4: architecture and privacy controls

**Question:** Describe a system you owned from design through launch.

**Evidence:** The Simple.life outbound telephony system reached production after security sign-off. The candidate owned its backend and architecture, wrote the epic and design document and worked with frontend and SRE colleagues. It used agent federation and masked customer numbers, with retention and calling-rule controls.

**Answer structure:** Explain the operational need, the candidate's own boundary of responsibility, the federation approach and the privacy controls. Give the launch as the concrete outcome. Avoid presenting a three-person cross-functional team as a team directly managed by the candidate or claiming a regulatory certification. The detailed QA checklist can support a discussion of release readiness if asked.

## Technical Interview

**Tail latency:** The source record does not establish prior p99 measurement. Describe how you would first define the population, endpoint and time window, then gather a latency histogram across the full request path. Break the distribution down by partner, region and response status. Check whether timeouts or errors are omitted from the observed population, and compare tail behaviour under realistic load. Choose one suspected bottleneck, make a bounded change and compare the same distribution before and after. Explain that this is a proposed method, not a past result.

**Backpressure:** Use the CRURATED routing example to discuss why producers and consumers can run at different rates. Ask what happens when a destination is slow, when queues grow and when retries compete with new traffic. Consider limits, monitoring, retry timing and a clear degradation policy. Give actual implementation details only where you can recall them accurately.

**Auction-domain learning:** Review the basic roles of an SSP, DSP and exchange, what a bid request and response contain, and why a deadline changes timeout and fallback decisions. Seedtag mentions OpenRTB, bid floors and demand/supply integrations as a plus. Be honest that these are areas to learn, not prior delivered systems. Ask the team where auction correctness, latency and cost trade off in their own architecture.

**AI coding tools:** The role asks for daily use and critical review. The supplied candidate record does not establish that frequency. Answer from actual current practice, including any limits, instead of inferring use from having built LLM features.

## Questions to Ask

1. What is the end-to-end latency budget, and which dependencies account for the largest share of tail latency?
2. Which service-level objectives and error budgets guide exchange changes, and how is an auction handled when a partner is slow?
3. What is the expected on-call rotation and how are production incidents shared with platform or data teams?
4. Where is the team based, and what employment or contracting arrangement is available for someone working remotely from Italy?
5. What would a successful first three months look like for an engineer joining without prior AdTech experience?

## Company-Specific Preparation

## Culture Fit / Behavioral Interview

Use the actual collaboration examples above and explain your contribution.

## Preparation Plan

Rehearse one concrete system diagram for the gateway and one failure timeline for the scan. Review the CRURATED production scope and the concurrent nature of the engagement. Bring honest boundaries around p99, Kafka, GCP and auction mechanics. Confirm availability and contract details before giving definitive answers. No salary figure is supplied because the relevant team's pay market and policy have not yet been established.
