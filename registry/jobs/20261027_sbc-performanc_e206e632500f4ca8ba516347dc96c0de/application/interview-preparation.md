# Interview preparation — SBC Performance, Senior Go Developer

## Recruiter / HR Screening

Start with the recent backend work rather than a full career chronology. A concise introduction could say: “I build and operate backend services in Go and PHP. Recently I owned the backend of a multi-tenant helpdesk gateway, with a vendor-neutral model and production integrations. I also worked on AI support automation and event pipelines. I like roles where the business workflow has to become a clear, reliable service contract.” Keep the wording natural to the candidate. Do not imply previous marketing-platform employment. The approved analysis scored this role 84/100, but that score is an internal selection judgment, not something to quote to an interviewer.

## Technical Interview

The posting puts business-case decomposition first. Expect a question about turning an ambiguous request into deliverable slices. Use the Go gateway as an example: the source supports a domain model, inbound event schema, per-tenant storage and queues, vendor adapters, and a first business demo. Describe the sequence of those deliverables and what was known at each stage. Do not invent a meeting, ownership decision, or product metric. The interviewer may then ask how you decided on the service boundary. Explain the confirmed vendor-neutral event model and the fact that vendor SDKs were isolated in one repository. If asked for alternatives, state which trade-offs you actually considered rather than constructing a retrospective story.

PostgreSQL is explicit, including modelling, query optimisation and migrations. The candidate's confirmed recent stack includes PostgreSQL with GORM; the evidence does not currently document a specific Go/PostgreSQL query improvement. Speak to genuine database practices and be candid about which examples come from previous systems. For a whiteboard exercise, first clarify entity identity, lead-state transitions, deduplication rules, event history, idempotency and retention. Ask whether marketing attribution is part of the operational model or a separate analytic projection. These are design questions for this interview, not facts about SBC's current system.

The AI-first wording is unusually specific: build features with AI tools while critically evaluating generated code. The candidate has confirmed experience building LLM-backed workflows and evaluation pipelines, but that does not itself prove coding-assistant usage or the review routine. Prepare one truthful example of how you personally assess generated changes if you have one. Otherwise distinguish the production AI work from the coding-tool question and explain the review standards you would apply: correctness against the contract, error handling, data access, tests and operational observability. Do not name a particular assistant or promise a speed gain without evidence.

## CV Deep-Dive Questions

**Go platform delivery.** The helpdesk gateway abstracted Intercom and Zendesk through a common event model. The candidate delivered the domain model, OpenAPI and inbound event contracts, webhook ingestion, tenant store, SQS queues and adapters, and integrated it with the support agent. The source states it enabled the first B2B demonstration of the support AI product. Explain where integration responsibilities ended and how the service made the demonstration possible. Avoid saying it launched commercially or materially grew revenue.

**Production AI and evaluation.** The LLM support agent had candidate-built action tools and an evaluation pipeline connecting conversation text, action events and subscription-state snapshots. Use this to explain how a product AI workflow is observed and improved after release. It can support a discussion of operational judgment, but it is separate from the employer's AI code-review requirement. Avoid quoting unconfirmed platform-wide automation percentages as personal outcomes.

**Data system simplification.** The Snowflake-to-Intercom work consolidated separate feeds into a common engine and removed repeated full-history reads and an item cap. For a design question, explain why a shared pipeline may reduce duplicated operational behaviour. The source supports the implementation and no-downtime release, not a measured cost saving. Another valid example is CRURATED's production DataLake and versioned event publication. Keep that consulting engagement distinct from the Simple.life employment role.

**Reliability and privacy.** The calling platform reached production after security sign-off and included privacy and lawful-calling controls. It is useful when discussing constraints beyond raw performance. Do not describe internal control names or claim regulatory certification. The GDPR export workflow across customer and analytics sources is another grounded example of coordinating data movement, but do not invent measured time savings from the unconfirmed estimate table.

## Company-Specific Preparation

Revisit the verified DOU posting and company product context before the conversation. Learn the actual lead lifecycle from the team before proposing architecture changes.

## Questions to Ask

Ask what “lead” means in the platform, who owns each state transition and which teams consume the data. Ask whether the Go services already exist or this hire will establish the first boundary. Ask how PostgreSQL is used for operational records, migrations and analytics, and whether event or attribution data lives elsewhere. Ask what the current code-review process looks like when AI tools contribute code. Ask how Product, Engineering and Marketing agree on a change to lead quality or monetisation logic. These questions are grounded in the posting's responsibilities and avoid assuming an internal failure.

## Culture Fit / Behavioral Interview

For AdTech, say plainly that your direct product history is support automation and event analytics. Then identify what transfers: building integrations, keeping data contracts stable, connecting operational events to useful analytics, and working with product and operations. Do not describe yourself as an acquisition specialist. For SOLID and GRASP, use concrete examples of service separation and interface design, then discuss the terminology if the interviewer wants it. For English B2, use the interview itself as evidence rather than inventing a certificate. If work authorisation or contract-country questions arise, answer with confirmed personal details only; current profile records leave these fields open.

## Preparation Plan

Before any interview, rehearse the Go gateway story in two minutes and be ready to draw its service boundary without exposing confidential internals. Prepare a precise answer on the personally owned parts of the LLM agent and the event pipeline. Recheck the recent role's August 2026 end date and the concurrent nature of CRURATED. Keep a short list of questions about the actual lead lifecycle and engineering expectations. The interview should establish whether the role is genuinely senior platform work and whether the marketing-domain transition is attractive to the candidate.
