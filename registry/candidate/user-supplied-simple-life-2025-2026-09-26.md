# Candidate-supplied Simple.life 2025 experience block — 2026-09-26

The candidate supplied the block below for resume generation. Preserve its wording as candidate evidence; the cited Jira/Slack records were not independently inspected here. The ESTIMATES section contains unmeasured or inferred outcomes, including some projected effects. Earlier direct career clarification gives a different role title and end date; reconcile those before an employer-facing CV. Read this alongside the Sep 2025–Sep 2026 block and combine overlapping LLM-agent and DeepL claims.

## Supplied block

# Prompt block: Simple.life experience (Jan 2025 – Dec 2025)

Paste this block into the resume-generation prompt as the source-of-truth for the Simple.life role for calendar year 2025. Same structure as the 2025-09 → 2026-09 block: (1) rendering rules, (2) verified facts, (3) estimates with basis. The generator must not invent numbers beyond what is listed here. When both blocks are used together, deduplicate: the LLM-agent line and the DeepL line appear in both periods — merge them into one bullet each.

---

## ROLE: Senior Backend Engineer — Simple.life (Simple App), Support & Content Platform

Period covered by this block: 2025-01 – 2025-12.
Stack: Go, PostgreSQL, Kubernetes CronJobs, Intercom API (custom actions, workflows, Fin), OpenAI / Azure OpenAI (GPT-4 → GPT-4o), DeepL, Braze, App Store / Google Play / TrustPilot review APIs, Cloudtalk, Data Platform events, OpenAPI.
Team context: support-backend team of 3 engineers plus a support-ops product owner; Valentin is the backend owner of the Intercom automation contour (email + chat), LLM-reply pipelines and public-review automation.

### RENDERING RULES FOR THIS ROLE

1. Output 5–7 bullets max, ordered by relevance to the target vacancy (AI/LLM roles → lead with A, B, C; backend/platform roles → lead with D, E, F; product-engineering roles → lead with A, C).
2. Every bullet follows: **Built/Led/Architected [X] using [Y], resulting in [Z with a number]**. One sentence, ≤ 40 words.
3. Use only figures from FACTS and ESTIMATES. FACTS may be stated as-is. ESTIMATES are stated as approximate figures with "~" (e.g. "~35%", "~3×"); do not add words like "estimated" or "roughly" to the bullet itself.
4. Never claim "led a team of N"; use "with a 3-person backend team" or "as backend owner of …".
5. Preferred verbs: architected, built from scratch, launched, migrated, consolidated, hardened, cut, automated.
6. Do not mention internal codenames (Emily, support-automation, support-legacy, palta) — use functional names (LLM reply engine, support automation service, legacy support service, legacy billing).

### PROJECTS — VERIFIED FACTS (from Jira/Slack, safe to state exactly)

**A. LLM-powered cancellation & refund automation for support emails (Mar–Sep 2025, epic DEV-21969)**
- Built OpenAI-generated replies for step 1 of the cancellation workflow (regular subscriptions), then turned AI replies on for cancellation emails at the first step (Jun 2025); added 1-step automation for refunds over 30 days; reworked the refund flow after cancellation.
- Prompt engineering and iteration: cancellation prompts (regular plans), deletion-request predictor, TrustPilot prompts, 4-5★ and 1-3★ review prompts; migrated all prompts from GPT-4 to GPT-4o (May 2025).
- Built the deletion-request predictor (OpenAI classifier) and hardened it against moderation failures and mapping errors; routed users with active deletion requests to L1.
- Preprocessing pipeline: stop-word cleanup for cancellations/refunds, text sanitization for both automation services, removal of boilerplate before categorization, CC-contacts support, "get email from inquiry" action, empty-body ticket workaround.
- Fixed 5 production defects in cancellation emails in one release (incorrect cancellation/end dates, tags & pending status not applied, missing name in AI reply, AI note not sent).

**B. Ticket categorization: ML model → Intercom Fin A/B test → migration (Jun–Aug 2025)**
- Designed and launched an A/B test comparing the in-house ML categorization model with Intercom AI Categorization (Fin) via two Intercom attributes (`fin_automation_category`, `general_email_categorization`), with category mapping into the existing billing automation (cancellation / refund / other / billing_other / account deletion).
- Migrated ticket categorization to Intercom AI Categorization (Aug 2025), then executed the switch to Fin with ML kept as fallback.
- Added token input/output telemetry for the general categorization action and OpenAI event logging per generated reply.

**C. Public-review automation on App Store, Google Play and TrustPilot (Jan–Jul 2025, epic DEV-23082)**
- Built from scratch the automation that replies to public reviews (Jan 2025), extended it to 2-3★ reviews (Mar 2025) and to 1-3★ App Store / Google Play reviews and TrustPilot 2-3★ / 4-5★ (May 2025).
- Keyword guardrails: reviews with sensitive/legal keywords are excluded from auto-reply and routed to a human with the review link in an internal note; internal note with the exact payload sent to OpenAI for auditability.
- Handled rate limiting (HTTP 429) on the review-reply endpoint and Azure OpenAI call-rate limits.

**D. Launch of the standalone LLM support agent service (Oct–Dec 2025)**
- Bootstrapped the new AI-agent service: scenario for "account found but subscription not found", useful-links generation for the new billing system, PayPal invoice-ID / order-ID parsing, tagging of users with workbooks, subscription lookup from the second email in the body, user-search time limits, removal of `is_issue_resolved` logic.
- Automated closing of conversations handled by the LLM reply engine (new workflow, Nov 2025); added alerts for TrustPilot processing.

**E. Localization: migration to DeepL (Sep 2025)**
- Migrated translation from the previous provider to DeepL after mass language-detection failures on customer messages; added Arabic support; built a prototype translation bot for Intercom (Jul 2025); fixed inconsistent translations and non-EN first-message handling.

**F. Cost optimization and platform hygiene**
- Admin panel cost optimisation (epic DEV-20905): load only the last 40 days of customer events on first open; capped the Data Platform events loop at 1 year; stopped loading events for tickets handled by the LLM engine unless escalated to L1.
- Dropped the Zendesk usecase and all methods depending on it (Apr 2025); removed unused refund threads and outdated cron commands; unified the tagging system in support-api; migrated legacy support service onto shared packages (Nov 2025); fixed linter in CI; upgraded Go to 1.22.10.
- Moved OpenAI integration into the support-automation service; introduced feature flags; replaced link generation and user lookup in the API with calls to the automation service (Support API v2).

**G. Compliance and data hygiene**
- Account-deletion custom action: cancels active subscriptions and deletes all Braze accounts linked to the email; aligned API deletion behaviour with in-app deletion; emails and second notification for under-18 users (Nov–Dec 2025); anonymization service modifications and fixes.
- Started receiving CSAT data from Cloudtalk on the backend; sent CEO feedback as requests into Intercom.

**H. Volume**
- 150+ Jira issues resolved in calendar 2025 (~35 bugs, 2 epics closed) across 4 Go services (support-api, support-automation, support-automation-ai, support-legacy).

### ESTIMATES (approximate figures — render with "~")

| Item | Estimate | Basis |
|---|---|---|
| Cancellation/refund emails handled without a human after AI replies went live | ~35% of billing emails (from ~10% with rule-based templates) | AI replies turned on at step 1 for regular subscriptions + 1-step refund >30d automation |
| Monthly volume of the email automation contour | ~25,000 inbound support emails/month | ~7,000 pending tickets in a 7-day window observed in 2026 |
| Review-reply coverage | ~80% of public reviews across 3 platforms answered automatically, ~2,000 reviews/month | 1-5★ prompts exist for App Store, Google Play, TrustPilot; keyword-guarded exceptions go to humans |
| Time-to-first-reply on public reviews | ~3 days → under 1 hour | automated pipeline vs manual moderation |
| Categorization: A/B test ML vs Intercom Fin | Fin won: ~72% → ~90% category accuracy (+18 pp), ~40% lower categorization cost, in-house ML model retired to fallback | A/B test launched Jun 2025, migration completed Aug 2025 |
| Admin panel: events-load cost | −65% of Data Platform read volume, page load ~6 s → ~2 s | 40-day window instead of full history; 1-year cap on events loop |
| DeepL migration: language-detection failures | ~5% of non-EN messages mistranslated → under 0.5% | ticket cites mass detection problems as the trigger |
| GPT-4 → GPT-4o migration | ~50% lower per-request LLM cost, ~2× faster responses | public list pricing and latency difference at the time |
| Cancellation-email defect fix release | 5 defects in one release, L1 escalations on cancellation emails −30% | verified defect count; escalation drop is the expected effect |
| Deletion-request predictor | ~95% precision on routing deletion requests to L1 | classifier hardened over 6 fix iterations (Mar–May 2025) |

### EXAMPLE RENDERED BULLETS (reference style)

- Built an LLM reply engine (OpenAI GPT-4o) for the cancellation and refund email workflows in Intercom (~25,000 emails/month), with a deletion-request classifier (~95% precision) and keyword guardrails, raising the share of billing emails resolved without a human from ~10% to ~35%.
- Designed and ran an A/B test of in-house ML ticket categorization vs. Intercom Fin and led the migration to Fin with ML fallback, lifting category accuracy from ~72% to ~90% while cutting categorization cost by ~40%.
- Built from scratch automated replies to ~2,000 public reviews/month on App Store, Google Play and TrustPilot with keyword-based escalation to humans, cutting time-to-first-reply from ~3 days to under 1 hour.
- Cut Data Platform read volume for the support admin panel by ~65% and customer-card load time from ~6 s to ~2 s by limiting first-load event history to 40 days and capping the events loop at one year.
