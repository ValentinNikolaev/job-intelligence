# Interview preparation — INTERACTIVE REEL LTD, Tech Lead — Fintech

## Recruiter / HR Screening

Prepare a concise opening: a hands-on backend lead with PHP and Go production work, leadership at airSlate, recent PHP delivery at CRURATED, and security decisions at Simple.life. The role is remote for Europe or Ukraine, so Rome fits the stated geography. Confirm contract model and travel expectations. English B1 is listed; the profile supports professional working English. Explain CRURATED as a concurrent part-time subcontract.

Expect salary, notice and start-date questions. The application profile still marks these for confirmation, so give only candidate-approved values. For job-change questions, the latest direct confirmation says Simple.life ended in August 2026. A later project description does not extend employment.

## Culture Fit / Behavioral Interview

Prepare STAR outlines for these questions: “What technical decision did you own?” — CRURATED's production event analytics. “How did you keep a product stable during change?” — airSlate's database pressure reduction. “How did you work with product and engineering?” — airSlate planning through release. “When did security change implementation?” — Simple.life telephony review. “How did you work across specialties?” — backend, frontend and SRE collaboration. “How did you mentor others?” — airSlate lead duties. “How did you handle an integration?” — CRURATED Crutrade work. “What would you do differently?” needs the candidate's own real example.

Separate team work from personal contribution. Avoid unsupported percentages or invented incident timelines.

## Technical Interview

**High priority — card lifecycle.** Review authorisation, holds, capture, clearing, settlement, reversal, refund and chargeback as distinct states. Distinguish past implementation from design knowledge. Ask whether the platform is issuer-side, processor-side or an orchestration layer before choosing invariants.

**High priority — balances and reconciliation.** Sketch immutable postings, balance derivation, settlement records, exception queues and traceable corrections. Discuss idempotency keys and unique constraints for retry safety, then reconciliation against processor statements. These are preparation topics, not experience claims. Distinguish pending, committed and reversed operations.

**High priority — PHP/Laravel/MySQL/Redis.** Expect transaction boundaries, locking, unique indexes, queues, migrations and safe deployment. Anchor PHP answers in CRURATED and airSlate. Production Redis use needs candidate confirmation before any personal claim.

**High priority — leadership.** Prepare a real example of weighing delivery against operational risk and explaining it to product colleagues. airSlate release work and CRURATED production ownership are strongest.

**Medium priority — infrastructure.** Review Docker, Linux operation, monitoring, backups and rollback. AWS, Kubernetes, CI/CD and Prometheus are supported; exact Docker and backup ownership need confirmation. Design observability for delayed payment events and recovery that preserves audit history.

**Medium priority — crypto.** Review coins versus tokens, networks, native gas assets, confirmations and deposit failure modes. Hyprr supports Ethereum asset exposure, not regulated wallet operation.

**Low priority — frontend.** Discuss integration contracts and collaboration; do not claim Vue or React delivery without a specific project.

## CV Deep-Dive Questions

For Simple.life, expect “What did you personally decide in the telephony architecture, and who approved security?” and “How were opt-outs and call windows enforced?” Keep the answer at architecture and privacy level unless asked for implementation detail. The confirmed employment end is August 2026, while some candidate project descriptions mention September; reconcile that chronology before using a production-release date aloud.

At CRURATED, the candidate had technical ownership of production event analytics. Expect “What was the event versioning boundary, how were downstream consumers protected, and what was your direct contribution?” Describe the confirmed event system and integration without converting it into a payment ledger. For airSlate, prepare to explain the database bottleneck, the redistribution of work, the metrics used to evaluate API performance, and the lead's role in releases. Do not use the unconfirmed ECS-to-Kubernetes migration. For Hyprr, explain the prototype-to-beta result and the limits of Ethereum asset work. For Sixt, say which PCI DSS-related code changes are remembered and avoid assuming an audit outcome.

## Company-Specific Preparation

Re-read the [Djinni posting](https://djinni.co/jobs/856652-tech-lead-fintech/) before the call. Its language makes financial correctness and technical ownership unusually explicit. The [company site](https://interactivereel.tech/) and [privacy policy](https://interactivereel.tech/privacy_policy.html) verify the identity and broad software-services context, but reveal little about this particular payments product. Build questions around that uncertainty. Do not assume the product is live, card issuing is in-house, or that the site describes the same team. The public application route requires Djinni login and does not expose a required letter field.

## Preparation Plan

**Must prepare before recruiter screening:** a two-minute career narrative, the overlapping CRURATED explanation, true August 2026 end date, compensation expectations, notice period and one honest sentence about the card-ledger experience boundary. Check the live posting's status and application form.

**Before technical rounds:** practise one card-state diagram, a duplicate-event and idempotency design, a reconciliation exercise, and concrete PHP/MySQL migration tactics. Select source-backed STAR notes for database stability, production event analytics and privacy review. Verify any Redis, Docker and frontend examples against personal records before speaking.

**Before final or culture rounds:** prepare a 30/60/90-day approach as a proposal, not a promise based on unseen systems. Ask who owns regulatory and financial correctness decisions, how the technical lead's authority is divided with product and studio leadership, and which operational measures indicate progress.

## Questions to Ask

1. Which parts of the card lifecycle and money movement are implemented by this team, and which are delegated to a processor or issuer?
2. How are balances represented today, and what is the current reconciliation process?
3. Where do duplicate or delayed events cause the most operational risk?
4. What would the lead be expected to decide independently in the first months?
5. How large is the engineering team, and how are PHP backend, frontend and infrastructure responsibilities divided?
6. What are the current deployment, rollback, monitoring and backup practices?
7. Which part of the existing codebase most constrains new product work?
8. What does “long-term engineering ownership” mean in decisions, production support and team growth?
9. What is the employment or B2B arrangement for a Rome-based remote candidate?
