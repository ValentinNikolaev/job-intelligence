# Interview preparation | Sr. Golang Developer

## Recruiter / HR Screening

Expect the recruiter to check the three explicit screening points first. State that you have five years of hands-on experience building production systems in Go. That is the aggregate duration you confirmed, so give project dates separately and do not imply every year was at Simple App. Your recent examples are the Go helpdesk gateway, outbound telephony backend on Amazon Connect, support-agent services, and reliability work. Describe the scope you personally owned before discussing the wider team's contribution.

The vacancy calls iGaming experience mandatory, and the application asks a direct yes-or-no question. Answer **No**. A useful spoken follow-up is that you have worked on production services with event processing, customer operations and operational controls, then ask whether the team would consider that experience transferable. This gives the recruiter a way to evaluate the gap without turning an unrelated product into an iGaming project. Be prepared for the recruiter to end the process on this criterion.

Confirm that you are based in Italy and can work remotely from Europe. Your notice period is two weeks. Describe the €65,000 annual gross figure as a provisional market-based expectation. Ask about contract terms and pay policy.

## Culture Fit / Behavioral Interview

Prepare a concise account of a production issue where you diagnosed the actual failure mode, chose a bounded fix and watched the service after release. The Intercom ticket-scan degradation is suitable. Explain the time budget and slow paginated searches, then the parallel cursor approach and partial-success reporting. Separate the observed failure from the changes you made and the later operational result. Avoid adding an incident duration, cost saving or availability percentage that the source does not verify.

For collaboration, use the telephony project to explain work across backend, frontend, security and SRE on calling windows, opt-outs and customer phone data. Describe a design decision you owned and a sign-off you received. For a disagreement question, choose a real decision you remember and explain the evidence and outcome.

- How did you identify the cause of the slow ticket scans?
- When did a security requirement change your telephony design?
- How did you coordinate a release across frontend, backend and SRE?
- How did you evaluate whether an integration was ready to demo?
- How did you decide which work to prioritise when the main database was under pressure?

## Technical Interview

Reconstruct the multi-tenant helpdesk gateway on a whiteboard. Start with vendor webhooks, the shared event model, tenant-specific storage and SQS queues. Explain why the vendor SDKs lived in one Go service, how outbound actions reached Intercom or Zendesk, and how downstream clients used the contract. For each component, distinguish implemented behavior from a design that you would choose today. Be ready to discuss idempotency, duplicate deliveries, retries and poison-message handling as design questions where the source does not specify your exact deployed solution.

For AWS, make a component inventory. The verified Simple App record covers Amazon Connect, SQS, IAM federation and IRSA, Lambda, Kubernetes CronJobs and Terraform. Separate what you provisioned personally from SRE-owned resources. The employer also lists EC2, ECS or EKS, RDS, S3 and CloudWatch. Explain any unfamiliar service as a proposed approach, including how you would learn its operations.

Expect a Go concurrency or service-design exercise. Practise context cancellation, timeouts, bounded goroutines, consumer shutdown, error handling, tests and observability through a built example. Telephony retries and the ticket-scan run budget are starting points. Use throughput figures only with their period, unit and measurement method.

Review PostgreSQL in the Simple App services and PHP in the CRURATED analytics work. RabbitMQ appears in the airSlate stack. Keep the employers and languages correctly attributed.

**High priority.** Go coding, gateway architecture, AWS ownership and iGaming screening map to explicit requirements. **Medium priority.** SQL diagnosis, queue semantics and Kubernetes are likely follow-ups. **Low priority.** PHP is useful context after the Go and AWS examples.

## CV Deep-Dive Questions

For “What did you personally build in the gateway?”, explain the event model, OpenAPI contract, webhook ingestion, per-tenant SQS queues and adapters, then how these enabled the first B2B demonstration. Keep the product-wide result distinct from your backend contribution.

For “What happened when Intercom searches slowed?”, explain how the scan could exceed its run budget and cause fatal runs. Describe parallel cursor chains and the incomplete-scan metric. Discuss duplicates, bounded parallelism and monitoring as reasoning, identifying any future design separately.

Explain the overlapping dates through CRURATED's concurrent part-time subcontract, where you worked on production DataLake and event analytics. For airSlate, focus on database pressure, CI/CD and operations. The withdrawn ECS-to-Kubernetes claim must stay out.

## Company-Specific Preparation

Bet On Talent is the recruiter; the hiring client is unnamed. Map your strongest examples to Go APIs, reliability, AWS operations and event processing. Explain your interest in hands-on backend ownership using the advertised responsibilities.

The AI-tools question calls for your own daily practice. The record supports building an LLM-assisted support agent with action tools and evaluation. Identify any coding or debugging assistants you personally used and how you checked their output.

## Preparation Plan

1. **Before screening.** Rehearse a two-minute introduction linking five production Go years to gateway, telephony and reliability work. Practise the iGaming answer and confirm salary expectations.
2. **Before the technical round.** Draw the Simple App service boundaries and review Go concurrency, REST contracts, SQL diagnosis, queues, Kubernetes and AWS.
3. **Before the final round.** Prepare the telephony sign-off and ticket scanner examples. Be ready to explain decisions you owned, disagreements and what you learned after release.

## Questions to Ask

- Which company and product is this role for, and where are the Go backend lead and software architect physically based?
- Is iGaming experience an absolute screening requirement, or will the team assess production Go and platform experience from another domain?
- Which AWS services and environments would this engineer own directly, and what do SRE or platform teams own?
- What are the current service scale, reliability targets and most pressing performance bottlenecks?
- How are deployment, incident response, monitoring and cloud-cost decisions shared between engineering and the infrastructure team?
- Is the remote-from-Europe role employment or contracting, and which location or pay policy applies to the annual salary discussion?
- What would success look like in the first three months, and how does the team review architectural decisions?
