# Cubbit — Senior Backend Developer GO: interview preparation

## Recruiter / HR Screening

Lead with Go backend services, distributed integrations, PostgreSQL and operational ownership. Connect your experience to Cubbit's storage challenges without claiming object-storage or NFS/SMB delivery. Its official posting allows full remote or hybrid work in Bologna; confirm actual team practice.

The first screening issue is the previous application. Project history records a user-reported application to this same URL on 25 July 2026 and a 25 September rejection, described by you as needing Italian for informal communication. The original employer message is unavailable. Ask whether that expectation still applies; the current posting requests full English proficiency but does not settle the Italian question. Your profile records professional working English. State your actual levels and give communication examples you can verify.

Expect questions about your Rome location, authorization, salary and availability. Authorization, visa needs, target salary and general notice period remain unconfirmed. Cubbit advertises €45,000–€65,000 base plus ESOP eligibility. Explain that Simple App ended in August 2026 and CRURATED was concurrent part-time consulting through January 2026. Frame your interest in storage through distributed-systems and reliability work.

## Culture Fit / Behavioral Interview

Prepare STAR notes for these eight likely questions, separating your own action from team results and leaving unknown measurements blank.

1. How did you clarify an ambiguous requirement? Consider the Simple App gateway's model and API contracts.
2. When did you disagree about a design? Choose an episode you can verify.
3. How did your code review improve a change without blocking delivery?
4. Which production bottleneck did you diagnose? AirSlate's API/database work is possible evidence; describe your lead scope.
5. How did you handle external-service failure? Name the actual Simple App failure and shipped remedy.
6. When did you simplify a system? Consider CRURATED's event versions or the helpdesk gateway.
7. How did you balance privacy and delivery? Consider the calling platform's masking and consent rules.
8. What changed after critical feedback? Choose a real episode.

## Technical Interview

**High Priority — Go and service design.** Practice error handling, context cancellation, concurrency, timeouts, retries, idempotency and testing. Code a small HTTP service or worker. Ground answers in the gateway and support platform.

**High Priority — distributed design.** Practice a proposed object-storage control plane: placement, replication, partial failures, consistency and recovery. Cubbit describes geo-distributed clusters and S3-compatible gateways. Ask about its actual guarantees; do not claim storage-engine experience.

**High Priority — PostgreSQL and tracing.** Practice indexes, plans, transactions, contention and schema changes. Use Simple App's Go/PostgreSQL service. Explain how to isolate slow application spans from database or network time. Prometheus/Grafana evidence is available; OpenTelemetry implementation is unconfirmed.

**Medium Priority — networking and infrastructure.** Refresh sockets, pooling, HTTP, DNS, TLS, backpressure, Linux diagnostics, Kubernetes deployments and Git review. Operator authoring is a bonus, with no confirmed experience.

**Medium Priority — AI development tools.** Cubbit asks about developer tools; the CV's LLM agent is a product. Prepare an actual coding-tool example and how you checked output, or discuss an evaluation approach.

**Low Priority — NFS/SMB and operators.** Understand the concepts; production experience is unconfirmed. Ask which product layer this team owns.

## CV Deep-Dive Questions

Expect a detailed walk-through of the Simple App gateway: Why a vendor-neutral event model? How were tenants separated? Which adapters and outbound actions reached the demo? What did you design independently, and what did frontend, SRE or product colleagues own? A safe evidence-backed anchor is: “At Simple App, I built a Go helpdesk gateway with a vendor-neutral event model, OpenAPI contracts and tenant queues, enabling the company's first business-customer demonstration of its support-AI product.” Be ready to identify the shipped boundary behind that sentence.

For CRURATED, describe the production DataLake and parallel event-version publication under your technical ownership. Explain what an event schema changed for consumers; do not assume a revenue or incident effect. For airSlate, explain the Prometheus evidence for performance improvements and your backend lead scope, without reviving the withdrawn ECS-to-Kubernetes migration. If asked about older positions, explain Hyprr's prototype-to-beta work concisely and the Sixt/PDFfiller overlap without inventing chronology. The CV lists Sixt and PDFfiller as dated entries; prepare only facts you can substantiate for either.

## Company-Specific Preparation

Read Cubbit's [role page](https://www.cubbit.io/careers/senior-backend-developer-go), [company overview](https://www.cubbit.io/about-us) and [technology page](https://www.cubbit.io/technology) shortly before an interview. The role page asks engineers to review code, turn requirements into tasks and use tracing to identify bottlenecks. The company describes geo-distributed data placement, customer data control and S3-compatible gateways. Connect your verified experience to the operational questions those features raise: partial failure, observable behavior, recovery and clear service contracts. Distinguish Cubbit's published claims from your own assumptions about architecture.

## Preparation Plan

**Must prepare before recruiter screening:** verify your current Italian and English levels, the prior application's exact dates and your own account of the language feedback, work authorization, practical Bologna visits, salary expectations and availability. Write a two-minute career story that explains the concurrent CRURATED work and why the storage role interests you.

**Before technical interviews:** rehearse one Go coding exercise, one distributed-storage design exercise, one PostgreSQL diagnosis and one tracing investigation. For each CV example, separate your decision, team contribution, delivery stage and outcome. Identify at least one concrete AI-assisted development workflow if you have used one; otherwise describe an honest evaluation approach.

**Before final or culture interviews:** prepare the eight behavioral stories above, with details you can verify. Decide which risks you need clarified: Italian as a social working language, ownership of storage versus control-plane services, remote practice, compensation components and the impact expected in the first six months.

## Questions to Ask

1. Does the team still expect Italian for informal collaboration, as was raised after my earlier application, or has the working-language arrangement changed?
2. Which parts of the product would this backend role own: storage nodes, the control plane, S3-compatible gateways or customer APIs?
3. What are the hardest current failure or recovery cases across geo-distributed sites?
4. How are consistency and durability guarantees exposed to customers, and where do engineers make those trade-offs?
5. Which traces and service metrics are most useful when diagnosing production bottlenecks today?
6. What degree of hands-on Kubernetes operator or storage-protocol work is expected in the first six months?
7. How often does the team meet in Bologna when someone works fully remotely?
8. How do engineers review design changes and code across the team?
9. What would make the first six months successful, and how is the salary/ESOP package shaped for that scope?
