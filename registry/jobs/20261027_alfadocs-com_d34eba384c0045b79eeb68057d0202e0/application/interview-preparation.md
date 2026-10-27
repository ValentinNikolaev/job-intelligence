# AlfaDocs interview preparation

## Recruiter / HR Screening

Lead with supported backend identity: PHP and Go production systems, technical leadership, data protection, event pipelines and operational reliability. Connect the role to healthcare workflows through the confirmed health-domain calling platform. State that this experience is adjacent to, rather than identical with, practice-management software. Do not claim direct use of AlfaDocs or a personal history with its product. If asked about the full-stack title, say that backend architecture is the strongest fit and give an exact account of any direct React work only if the candidate confirms it.

## Technical Interview

**Secure feature delivery.** The calling platform is the best concrete example. Explain the business need, personal architecture/backend ownership, formal security sign-off, and production release. Then trace the privacy controls: the phone number stayed server-side, the browser saw only a mask, logs omitted it, access was permission-limited, contact records had retention controls, and recording/transcription required explicit consent. Show how the design handled opt-outs and calling windows. Do not imply that this proves familiarity with every healthcare standard or medical-record regulation.

**Architecture and data flow.** Discuss the vendor-neutral helpdesk gateway with its event model, OpenAPI contracts, webhooks, tenant-aware store, queues and adapters. Explain which interfaces were designed and which parts reached a deployable environment. Distinguish the candidate's backend ownership from frontend/SRE contributions. For the concurrent PHP engagement, discuss the production event analytics pipeline, versioned event publication, downstream routing and Crutrade integration. Clarify the exact boundaries of individual technical ownership rather than saying every line was written alone.

**PHP and Symfony depth.** Prepare a current, specific PHP example from the CRURATED engagement and the supported Laravel/Symfony work at airSlate. The posting calls out Doctrine ORM, Security and Event Dispatchers. Those component details are not verified in the current evidence. Ask the candidate to confirm which components they used, the project period and what they personally changed. If the answer is no or limited, explain the transferable PHP and service-design experience without presenting it as deep Doctrine expertise.

**MySQL and performance.** AirSlate evidence supports backend leadership in database and API performance work. Describe how peak load and bottlenecks were identified, what changes were made, and how service stability or response times improved. The candidate named Prometheus as the measurement source for imported airSlate results, but the financial savings figure lacks separate context and should stay out. Do not reintroduce the withdrawn ECS-to-Kubernetes migration.

**AI-assisted workflows.** The confirmed LLM support-agent work includes action tools, conversation/action/account-state evaluation inputs and production defect work. Explain what was evaluated and where human review or control sat. Avoid converting overall platform automation rates into an individual achievement. The role asks about advanced prompting and cross-team optimisation; prepare specific examples only from the candidate's own work.

## CV Deep-Dive Questions

React implementation is unverified. So are Doctrine ORM, practical DDD, Docker-based development, and GitLab CI/CD. The candidate has evidence of GitHub Actions and ArgoCD, which supports transferability in release design but does not establish experience with GitLab's syntax or operations. Have short, candid answers ready for each item and decide which can be confirmed from existing work before applying. The posting expects senior experience and mentoring, so use the airSlate lead scope and PDFfiller team context without invented team sizes for other employers.

## Culture Fit / Behavioral Interview

When the interviewer asks for architecture trade-offs, start with the constraint the source actually supports, then the candidate's decision and the released behaviour. The telephony case supports a discussion of privacy and lawful calling controls. The gateway case supports interface boundaries between vendors. Avoid claiming that a particular trade-off was made to cut cost, satisfy a named regulation, or move a product metric unless the candidate can provide evidence. For behavioural questions, explain how the cross-functional backend, frontend and SRE team brought the telephony work through review and launch without presenting the whole team's delivery as one person's implementation. For mentorship, use the documented lead or coaching periods and describe actual actions rather than assuming that every recent role carried formal management authority.

## Company-Specific Preparation

For a practical Symfony exercise, prepare to discuss dependency injection, request handling, security boundaries and persistence only to the level directly remembered from real work. If the interviewer asks for a Doctrine-specific optimisation example and the candidate cannot substantiate one, it is better to explain the relevant MySQL performance work and then ask about their data access patterns. For a React task, state where backend ownership ended and where frontend colleagues owned delivery. Keep the answer short and candid.

## Questions to Ask

1. Which part of the product would this engineer own first: appointments, clinical documentation, patient communications or the shared platform?
2. How much of the weekly work is hands-on React compared with backend architecture and implementation?
3. Which Doctrine and Symfony components are central to the current codebase, and where are the biggest design constraints?
4. What security and privacy requirements shape feature review, and who signs off on changes involving patient data?
5. How do product, design and engineering decide whether a workflow change is ready for release?
6. Which tests and GitLab pipeline checks currently protect deployment, and what would you want improved?
7. The source feed says Contractor, while the posting describes full-time employment. Which arrangement applies to this role?

## Preparation Plan

Confirm work authorisation and the exact wording appropriate for an EU remote application. Confirm the stated working hours, October start request, compensation expectations and employment arrangement. The current candidate profile does not settle these points. The source posting is at https://himalayas.app/companies/alfadocs-com/jobs/senior-full-stack-backend-engineer-php-react?utm_source=api. Recheck that it remains open before applying. This preparation document is for discussion, not evidence that any application has been submitted.
