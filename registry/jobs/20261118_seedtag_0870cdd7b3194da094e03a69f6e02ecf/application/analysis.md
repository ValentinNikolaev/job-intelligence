# Application analysis — Seedtag, Senior Go Engineer

## Recommendation

## Vacancy Summary

The stored match is 78/100, with a match recommendation from the analysis workflow. It is a credible but incomplete match: recent Go ownership, event integration and production troubleshooting fit the core of the role, while real-time bidding and measured tail latency remain material gaps. The score is an existing analysis judgment, not a new preparation score or a prediction of an interview. The official posting describes a fully remote role and says remote contracts are available in Italy. Check the contract and team arrangements directly during screening.

The official application route is https://jobs.seedtag.com/jobs/8747016-senior-go-engineer/applications/new. On 19 November 2026 the form presented a cover-letter field without the required markers shown on required fields. It is optional, so the package does not include a letter. No application has been submitted. The originally recorded source is https://himalayas.app/companies/seedtag/jobs/senior-go-engineer?utm_source=api.

## Company Research

Seedtag describes its advertising business as contextual, using its Liz system without cookies or user tracking across the open web and connected TV. That is a statement from the company, not a separately verified assessment of its privacy outcomes. Its own posting says the Go team owns the AdExchange and makes decisions in milliseconds. Responsibilities cover scaling real-time bidding, onboarding supply and demand partners, auction mechanics, audience-data ingestion, event pipelines and production metrics. Source: https://jobs.seedtag.com/jobs/8747016-senior-go-engineer.

The strongest reason to consider the role is its combination of end-to-end backend ownership and explicit operational constraints. The candidate has worked on integration boundaries and production data flows, although the setting is different. Ask how the team defines ownership across product, platform and on-call responsibilities before assuming the scope matches the posting.

## Initial Resume Audit

## Strict Hiring Manager Review

**Production Go and service ownership — strong.** At Simple.life, the candidate owned a Go support platform, built a vendor-neutral gateway and led backend architecture for outbound telephony. The gateway put vendor adapters behind a shared event model with tenant queues. The platform's support workload is meaningful operational experience, but monthly ticket counts should not be presented as comparable to bid requests per second.

**Distributed systems and event delivery — strong, with scope limits.** At CRURATED, the candidate owned production DataLake and event analytics, designed event versioning and implemented downstream routing with backpressure and delivery guarantees. The role was a concurrent part-time PHP subcontract. This is transferable architecture experience, not evidence that the work used Go or Kafka.

**Reliability and observability — partial to strong.** The Simple.life scan recovery work has a concrete failure mode, partial-success behaviour and an incomplete-scan metric. CRURATED also supplies an example of event delivery and retries. The record does not support claiming every resilience pattern named in the vacancy, such as circuit breakers, bulkheads or load shedding, as personally delivered work.

**High throughput, p99 and serving cost — partial.** The posting explicitly asks for measured p99 latency or serving-cost improvement. There are relevant service and performance examples, but the current evidence does not establish a p99 measurement or ad-exchange latency result. Explain an investigation method and be candid about the gap. Do not turn an approximate cost estimate into an observed saving.

**Cloud and tooling — partial.** AWS, Kubernetes CronJobs, Terraform and CI/CD appear in candidate sources. Google Cloud and Kafka are not established. The candidate withdrew the airSlate ECS-to-Kubernetes migration attribution, so that example must not be used. The posting also asks for daily AI coding-tool use; the supplied evidence does not confirm its frequency.

**AdTech domain — gap.** OpenRTB, auctions, bid floors, SSP/DSP and connected TV are not documented candidate experience. The posting calls AdTech a plus. A discussion can focus on transferable principles and questions rather than claiming previous exchange ownership.

## Red Flags

The gaps above should be discussed directly.

## ATS Keyword Analysis

The CV uses supported Go and event-processing terms, while unsupported stack items stay out.

## Major CV Changes

The CV leads with the gateway, telephony and reliability work because they show delivered Go services and production boundaries. CRURATED supplies separate event-architecture evidence, explicitly labelled as a concurrent subcontract. airSlate adds database stability, shared logging and team delivery. The older roles retain concise, source-backed delivery and security context. No unsupported Kafka, GCP, p99 or auction experience has been added. Simple.life metrics and pipeline cost estimates are deliberately omitted where a measurement basis or attribution is uncertain.

The role asks for five years of backend experience with recent Go, rather than five years of Go specifically. The candidate's broader backend career supports the former and the Simple.life role supplies recent Go. Confirm technical depth and exact employment conditions in conversation. The CV presents the confirmed September end date and preserves the concurrent engagement.

## Final Quality Gate

The package presents documented work and keeps the material skill gaps visible.

## Questions for the employer

How is the latency budget distributed across the auction path, partner calls and data lookups? Which SLOs and failure policies govern traffic shedding or fallback? What does on-call look like for the exchange team? Is the Italy arrangement employment or another contract type, and where is the team physically based? The posting gives no reliable salary benchmark or pay policy, so no salary expectation is suggested here.
