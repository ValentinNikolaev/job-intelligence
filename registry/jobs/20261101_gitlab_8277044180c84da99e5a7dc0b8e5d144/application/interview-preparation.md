## Recruiter / HR Screening

Start by explaining the move towards infrastructure through the responsibilities you already own: service design, production rollout, operational reliability and cross-team interfaces. Be explicit that Go backend experience is direct, while repository storage is an area in which you would be building specialist depth. This gives the recruiter an accurate basis for assessing a transferable match.

Confirm whether this requisition accepts a Rome-based candidate. The live Jobicy page says Poland and quotes a Poland-specific salary range. Do not treat a global remote policy or EU residence as proof that this role is open in Italy. Ask for the applicable hiring entity, local compensation basis, working-hour expectations and employment arrangement. Give current salary expectations and availability only after reconfirming them. Use upper-intermediate English as recorded, without adding an unsupported Italian level.

CRURATED was concurrent part-time consulting. Explain that overlap clearly if the recruiter asks about the chronology. Simple.life is completed work, and delivery evidence does not automatically establish a later employment end month.

## Culture Fit / Behavioral Interview

Prepare seven real examples, separating personal decisions from team results.

1. An initiative from proposal to rollout. Use telephony architecture, the design document, security review and release. Explain your backend ownership and frontend/SRE collaboration.
2. A durable boundary between systems. Use the helpdesk gateway, explaining why vendor SDKs were isolated and what the delivered demonstration proved.
3. A simplification of existing production work. Use the common Snowflake ingestion and push engine. Discuss observable operating changes rather than code-volume statistics.
4. Compatibility during an evolving integration. Use CRURATED event versions. Explain the production state and do not invent a cost-saving trade-off.
5. A period of operational pressure. Use airSlate database stability and the employment evidence of on-call responsibility. Choose an actual incident you remember before supplying details about severity or coordination.
6. Bringing other engineers into a decision. Use the CTO roadmap at Hyprr or airSlate decomposition and delivery. Preserve collaborative scope rather than claiming sole authority.
7. Explaining a security constraint. Use the phone-data boundary in telephony, with a clear account of who needed access and which decisions received review.

For a mentoring or review question, draw on actual technical onboarding and knowledge-sharing responsibilities. Do not invent a mentee outcome, promotion or adoption count.

## Technical Interview

High Priority — storage correctness and failure modes. Practise reasoning about read/write guarantees, partial failure, retries, replication and recovery. These are preparation topics rather than claims of previous repository-storage delivery. In a design exercise, define required behaviour before choosing a replication scheme. Explain what happens when a request succeeds internally but its acknowledgement is lost, and how the caller can safely determine the outcome.

High Priority — Go concurrency and performance. Review contexts, cancellation, goroutine lifetime, bounded concurrency, contention, resource cleanup and error propagation. Work through a small concurrent service and test observable behaviour. Be prepared to explain profiling and benchmarking as methods you would use, distinguishing practised skills from production examples you can actually substantiate.

High Priority — operational judgment. Prepare an approach to diagnosing rising latency using traffic, saturation, failure rates, recent changes and tenant distribution. Label this as an interview approach, not a past incident. Use real production ownership to explain rollout, monitoring and follow-up. Discuss what evidence would justify rollback, reducing concurrency or isolating a workload. Avoid promising an incident response procedure you have never used.

High Priority — interface contracts. Relate the gateway and versioned events to compatibility, caller responsibility and explicit failure behaviour. Acknowledge that an event pipeline is not a Git repository server. The useful transfer is making boundaries understandable and safe under change, rather than claiming the same storage semantics.

Medium Priority — Git internals, gRPC and Ruby. Learn enough to discuss Git objects, refs and repository operations, plus RPC deadlines, streaming and errors. State clearly where your knowledge is study rather than professional experience. Do not add these technologies to the CV until evidence supports them. The posting calls them highly desirable, so a gap is worth discussing without automatically disqualifying yourself.

Medium Priority — databases and deployment. Review query diagnosis, indexing, workload distribution and service rollout. Use airSlate's qualitative stability outcome and the confirmed Simple.life cloud stack. The withdrawn ECS-to-Kubernetes migration is unavailable as a story. Avoid implying that Kubernetes familiarity proves storage-system capacity planning.

Low Priority — unrelated frontend and application frameworks. They have little bearing on this requisition compared with Go, operational responsibility and storage reasoning. Spend preparation time on the role's actual engineering boundary.

## CV Deep-Dive Questions

Expect the interviewer to ask what you owned before coding and after release. For telephony, explain architecture choices, security review and the privacy boundary without presenting yourself as legal counsel. For the gateway, distinguish a delivered demonstration from production adoption across external customers. For pipeline consolidation, explain how behaviour was preserved and what operating consequence changed.

For CRURATED, explain the DataLake's consumers and parallel schema publication under your technical ownership. For airSlate, describe database work and delivery coordination without claiming sole implementation of team results. Be ready to discuss why the final CV avoids unsupported specialist terms and omits routine repair bullets that would add little senior-level signal.

## Company-Specific Preparation

The official Gitaly team page describes a boundary between data operations and the calling application's business decisions. Prepare an example of drawing a comparable boundary in your own work. Ask which parts of Gitaly's current scope need an experienced service engineer and which require immediate repository-storage depth. Treat the current team page as context, not a promise about the interview or exact work assignment.

## Preparation Plan

Must prepare: confirm Italy eligibility, current availability and appetite for operational duties. Before technical: practise Go concurrency, a storage failure-mode discussion and a clear account of the gateway boundary. Before final/culture: rehearse an end-to-end ownership story, a collaborative decision and a real on-call example with honest limits. Keep source-backed facts separate from study notes throughout.

## Questions to Ask

- Is this Poland-listed requisition open to an Italy resident?
- Which technical initiative would this engineer first own?
- Where is immediate Git internals depth essential?
- What failure or capacity problem is currently most costly for users?
- How are production changes evaluated and rolled out?
- What are the current on-call and escalation expectations?
- How do engineers and SRE colleagues divide operational responsibility?
