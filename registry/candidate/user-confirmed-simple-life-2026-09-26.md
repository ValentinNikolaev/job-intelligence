# Candidate-supplied Simple.life experience block — 2026-09-26

The candidate supplied the block below in this task. Preserve its wording as direct candidate evidence; the cited Jira/Slack records were not independently inspected here. The ESTIMATES section explicitly contains unmeasured figures. The role title and end date conflict with the earlier direct clarification in `user-confirmed-career-clarifications.md`; do not silently prefer either record when preparing an employer-facing CV.

## Supplied block

# Prompt block: Simple.life experience (Sep 2025 – Sep 2026)

Paste this block into the resume-generation prompt as the source-of-truth for the Simple.life role. It contains (1) rules for how to render this role, (2) verified facts, (3) estimated figures with their basis. The generator must not invent numbers beyond what is listed here.

---

## ROLE: Senior Backend Engineer — Simple.life (Simple App), Support & Content Platform

Period: 2023-10 – present (this block covers the last 12 months: 2025-09 – 2026-09).
Stack: Go, PostgreSQL (GORM), AWS (Amazon Connect, SQS, IAM/IRSA, Lambda), Kubernetes CronJobs, Terraform, Intercom API, Zendesk API, Snowflake, OpenAI/LLM tooling, OpenAPI, DeepL, Braze, AppsFlyer, Microsoft Entra ID.
Team context: support-backend team of 3 engineers (backend, frontend, SRE) plus product/support stakeholders; Valentin is the sole backend owner of the telephony, helpdesk-gateway and GDPR-automation domains.

### RENDERING RULES FOR THIS ROLE

1. Output 5–7 bullets max, ordered by relevance to the target vacancy (architecture/platform roles → lead with items A, B, D; AI/LLM roles → lead with C; backend-reliability roles → lead with E, D; compliance/fintech → lead with F).
2. Every bullet follows: **Built/Led/Architected [X] using [Y], resulting in [Z with a number]**. One sentence, ≤ 40 words. No task lists.
3. Use only figures from the FACTS and ESTIMATES sections. FACTS may be stated as-is. ESTIMATES must be rendered with a softener ("~", "up to", "roughly") or converted to a qualitative claim ("cut turnaround from days to hours"); never present an estimate as an exact measured value.
4. Never claim "led a team of N" — the honest framing is "with a 3-person cross-functional team" or "as sole backend owner".
5. Prefer verbs: architected, designed, built from scratch, led backend development, diagnosed and eliminated, consolidated, automated, drove.
6. Do not mention internal codenames (Kova, med-support, support-automation-ai) — use functional names (support admin panel, LLM support agent, helpdesk gateway).

### PROJECTS — VERIFIED FACTS (from Jira/Slack, safe to state exactly)

**A. Outbound telephony platform on Amazon Connect (Aug–Sep 2026)**
- Owned architecture and backend end-to-end; wrote the epic/design doc; passed security sign-off; released to production on 2026-09-25.
- Agent federation via AssumeRole + GetFederationToken: no per-agent AWS accounts, no SAML app, IT removed from the critical path.
- Connect users created lazily by the backend (moved out of Terraform); stale users cleaned by cron; admin activate/deactivate.
- PII controls: customer phone number never rendered or logged (masked only), purged from contact record by TTL, DevTools disabled by policy.
- Compliance logic: call windows with timezones/Sundays/holidays, do-not-call list, queued-callback withdrawal on opt-out, retry policy owned by backend (Connect retries = 0), outcome written to the existing Intercom ticket (no duplicate tickets).
- Designed load: 10–20 calls/day per agent, max 50. Cross-functional team: backend (Valentin), frontend, SRE.
- Authored a 30-scenario telephony QA checklist with run journal; 4 documented runs in 2 days before launch; every finding converted to a ticket.

**B. Multi-tenant helpdesk gateway, built from scratch (Jul–Aug 2026)**
- New Go service abstracting helpdesk vendors (Intercom, Zendesk) behind a vendor-neutral event model; the only repo holding vendor SDKs.
- Delivered: domain model, OpenAPI contracts + inbound event schema, webhook ingestion with per-tenant store and SQS queues (IRSA), Intercom adapter, Zendesk adapter with full outbound (reply, note, tags, status), client + service in the support-agent, dev environment and deploy.
- Enabled the company's first B2B demo of the support-AI product (golden cases + admin console).

**C. Production LLM support agent — backend lead (whole year, ~60 tickets)**
- Implemented 10+ agent action tools: subscription cancel, cancellation offer, refund, marketing/Braze unsubscribe, user search (incl. via OpenAI vision), attachments extraction, useful-links generation for new billing, review processing for a second product.
- Built the evaluation pipeline: conversation texts + action events + subscription-state snapshots on ticket open/close → Eval JSON.
- Built email and product-ticket categorization on prompts; retro-mapped 500+ product tickets and all emails since Jan 2026 as training/eval data.
- Fixed 15+ production defects in the AI path (swallowed non-2xx Intercom responses, nil-error wrapping, malformed session data, content_filter errors, duplicate handling, language misdetection).
- Migrated 3 services to DeepL without language detection.
- Working set in production: ~7,000 pending tickets in a 7-day window.

**D. Consolidation of three Snowflake→Intercom pipelines into one engine (Sep 2026)**
- Researched the codebase, proved ~70% structural identity, replaced 3 independent cron pipelines (CEO questions, profile reports, deletion feedback) with one two-phase engine (ingest + push; keyset pagination, run budget, throttle, retries, feature flag) via Template Method with 6 hook points.
- Code: 1,670 → 800 LOC (−52%). Tests: 1 of 3 → 3 of 3 processes covered. Removed a hard cap of 100 items/day. Eliminated daily full-history re-reads from Snowflake. No public API / admin-UI changes; no downtime.

**E. Elimination of daily cron fatal failures under Intercom API degradation (Jul–Aug 2026)**
- Diagnosed from logs and code: up to 14 fatal runs/day; a 48-page scan of ~7,000 tickets exceeded the 19.5-minute run budget when Intercom search degraded; per-page retry was bypassed by the overall-context-done branch.
- Fix: partial-success semantics with an "incomplete scan" metric instead of fatal; sharded search by updated_at with 3–4 parallel cursor chains.

**F. GDPR automation and account-deletion contour (Dec 2025 – Sep 2026, ~37 tickets)**
- End-to-end GDPR data-export automation across 7 sources: Users, Payments, Data Platform, AppsFlyer, Intercom + support backends, Slack, Snowflake analytics (two products). Self-service admin workflow (create / list / detail / status).
- Deletion contour rework: new dp-gdpr-service contract (bulk requestId + lookup), rollback on Data Platform when a request is cancelled, cascade deletion to Braze and avo-ai, cancellation contract with actor + reason.
- Executed an under-18 compliance program: account deletion, subscription cancellation and refunds after two notification waves.

**G. Tech-debt reduction across 7 Go services (whole year, ~28 tickets)**
- Decommissioned Zendesk legacy (services, DB tables, payment-domain entities), migrated legacy service to shared pkg, removed GOOGLE_OAUTH and outdated crons, unified tagging in support-api, merged 3 OpenAPI post-processing tools into 1, upgraded golangci-lint.

**H. Volume**
- 200+ Jira issues resolved in 12 months (30 bugs, 4 epics closed) across 7 services.

### ESTIMATES (plausible, not measured — always soften or qualify)

| Item | Estimate | Basis |
|---|---|---|
| Telephony: epic → production | ~6 weeks | epic created 2026-08-19, prod 2026-09-25 (≈5.5 weeks) |
| Telephony: agent onboarding time | days → under 1 minute | lazy Connect-user creation on first session request |
| Gateway: new-vendor integration cost | multi-week rewrite → ~1-week adapter | Zendesk adapter delivered as a draft inside the MVP epic |
| LLM agent: tickets auto-resolved without a human | +20–30 pp over the year | Slack: "fewer requests handled by humans while the team does not grow" — get the real number from #support-ai-agent-internal |
| Snowflake engine: warehouse query cost | −30–50% on this contour | full-history re-reads removed for 2 of 3 feeds |
| Cron fix: full-scan time | ~4× faster | 48 pages ÷ 4 shards |
| Cron fix: failed pods | → 0 | partial-success exits 0 |
| GDPR: request turnaround | ~5 days → < 4 hours | manual multi-team process replaced by admin workflow |
| GDPR: manual work removed | ~90% | analysts + engineers out of the loop; Slack cases remain semi-manual |
| Tech debt: codebase reduction | −15–20% of support-platform code | Zendesk removal + pkg migration + tool merges |

### EXAMPLE RENDERED BULLETS (reference style)

- Architected and shipped an outbound-calling platform on Amazon Connect for L1 support, designing agent federation (AssumeRole + GetFederationToken) that eliminated per-agent AWS accounts and SAML setup; passed security sign-off and reached production in ~6 weeks with a 3-person cross-functional team.
- Consolidated three duplicated Snowflake→Intercom pipelines into a single generic engine, cutting code by 52% (1,670 → 800 LOC), raising test coverage from 1/3 to 3/3 processes and removing a 100-items/day throughput cap with zero API changes.
- Diagnosed and eliminated daily fatal failures (up to 14/day) of a cron scanning ~7,000 tickets under Intercom API degradation by introducing partial-success semantics and sharded cursor pagination, cutting full-scan time roughly 4×.
