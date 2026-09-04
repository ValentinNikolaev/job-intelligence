# Senior Golang Engineer with AdTech experience

Posted: 2026-08-28

## Rejection

- Category: stale
- Reason: published_at 2026-08-28 is older than 7 days

### Role Description

The engineer who owns everything that happens after the real-time operations. Notifications arrive from the broadcaster’s exchange in three stages. The audience figure is restated twice, and the exchange reports a billing amount that our records have to agree with. None of this exists today: the client confirmed on the call that the reconciliation workflow will be built from scratch.

The counting model is the product in this seat. An estimated audience arrives with the ad opportunity. A delivery notification follows immediately after broadcast. Preliminary impression counts and a billing figure arrive shortly after that, derived from an external viewing-rating system. Confirmed figures arrive the following business day. Three numbers describe one commercial, and none of them may overwrite the others.

The client already runs analytics infrastructure and intends this system to plug into it rather than replace it: in their words, we just need to plug into that existing analytics infrastructure so that we can easily build those reporting and billing capabilities. Interface documentation has been requested and has not arrived, so establishing what that interface actually is forms part of the first weeks.

Full-time from the first milestone through production handover. Reports to our solution architect and works alongside the C++ engineers on the request path.

### About the Project

**Client:** an established supply-side platform operating at scale. The engagement is a full outsourced build. The client supplies a product manager for requirements and scope, an architect in review and supervision mode, and an infrastructure specialist for the UAT and production environments. We own delivery, the architecture, and everything before UAT.

**Product:** an ad-serving bridge connecting the client to a Japanese broadcaster’s programmatic linear platform, built apart from the client’s core RTB stack. It works as a translation layer and as a lightweight supply-side platform running the auction. Three parties define its edges:

- The broadcaster’s exchange is the source of ad opportunities, reached through a connection specification the broadcaster defines and we implement against, with no leverage to change it.
- An external viewing-rating system decides how many people saw each commercial. We never call it. The exchange derives impression counts from those ratings and reports them back twice: preliminary shortly after air, confirmed the following business day.
- The client’s configuration surface supplies demand as activated direct deals. An optional second phase adds third-party demand-side platforms over oRTB.

Phasing: a mandatory first phase runs entirely in the broadcaster’s native protocol and needs no protocol conversion. An optional second phase adds oRTB conversion and direct communication with demand-side platforms. The internal model is oRTB-aligned from the first phase, so the second becomes an edge-mapping job.

Position today: greenfield. Nothing is built. The broadcaster’s connection specification exists and is versioned, though its revision history shows continued amendment. The requirements document does not exist yet.

**Stack: **Go on the settlement, reconciliation and reference-data side, with C++ on the request path. The client named Go for independent tools and jobs, and has floated moving deal evaluation into a Go service for concurrency; that boundary is open, and this seat helps settle it. The system deploys into the client’s own data centres and must be built cloud-ready.

### Key Responsibilities

**Notification and settlement**

- Build the notification receiver: idempotent under retry, since the exchange retries on 429 and 5xx with exponential backoff, five attempts initially, and tolerant of duplicates and late arrival.
- Handle notifications the exchange sends for time windows in which nothing aired, without letting them register as delivery.
- Capture predicted, preliminary, and confirmed impression and billing figures side by side as an append-only record with restatement, so no figure overwrites its predecessor.
- Reconcile our figures against the billing amount the exchange reports, and emit the drift as a first-class output rather than an investigation.
- Treat delayed settlement as normal traffic. The rating source has scheduled maintenance windows and the specification states that the later notifications may be delayed.

**Reference data**

- Build the synchronisation service for the exchange’s three reference interfaces: creative and material status, base programme schedules, and daily programme schedules.
- Handle identifiers that are not unique across broadcast stations, and schedule corrections the broadcaster registers after air.

**Analytics and reporting**

- Plug the pipeline into the client’s existing analytics infrastructure rather than standing up a parallel one, and define that interface with them where it is undocumented.
- Hold the counting unit constant from event capture through aggregation to the buyer’s report while the number underneath it moves.
- Make a genuine zero distinguishable from a failed integration inside the pipeline, before anyone reads a report.
- Produce an auditable trail from any billed figure back to the auction that produced it.

**Services carved out of the request path**

- Build independent Go services where the architect and the client agree they belong there. The client has named deal evaluation as a candidate, for concurrency reasons, and that decision has not been taken.

### Required Qualifications

**Experience**

- 5+ years of production Go, including services and batch pipelines rather than one or the other.
- Has built a data pipeline whose source of truth was external and subject to restatement, not a reporting pipeline over data the system produced itself.
- Has built an idempotent receiver for a third party’s callbacks under at-least-once delivery, and has dealt with the duplicates in production.
- Has integrated into an analytics or data platform owned by another team, against an interface they did not design and could not change.

**Technical Acumen**

- Go for services and pipelines, with concurrency primitives chosen deliberately rather than reached for.
- Idempotency and deduplication under at-least-once delivery: retries with backoff, duplicates, out-of-order and late arrival.
- Append-only event modelling with restatement, where a superseded figure is retained rather than replaced.
- Reconciliation design that locates a discrepancy rather than only detecting one.
- Reference-data synchronisation with retroactive amendment, where identifiers are not unique across sources.
- Analytical data modelling for reporting, and working command of a columnar or large-scale analytics store. The client named big-data awareness as one of three key skill areas.
- HTTP client and server design against a specification the counterparty owns.

**Judgement & Soft Capabilities**

- Treats a billed figure as a commercial claim, and will not ship a number whose derivation they cannot walk backwards.
- Knows that a number restated twice is three numbers, and that discarding the first two is how a billing dispute becomes unanswerable.
- Comfortable that the interface to the client’s analytics platform is undefined on day one, and treats defining it as part of the job rather than a blocker.
- Distinguishes what a specification states from what it implies, and marks the difference as an open question.
- Raises a dependency risk with a named owner and a date, not as a general concern.

### Domain Knowledge — required

The person deciding what counts as a delivered impression is deciding what a buyer is billed against, and an error there produces confident, wrong numbers that survive review because nothing looks broken.

Required and portable across adtech platforms:

- Impression accounting where one delivered advertisement reaches more than one person, and where the audience figure is supplied or modelled rather than counted at the device.
- Notification and callback semantics: win and billing notices, macro substitution, duplicate and late delivery, and the proof-of-play analogue.
- Billing reconciliation across parties: booked against delivered against what the counterparty reports it owes, and discrepancy detection when the layers disagree.
- Programmatic auction mechanics from the sell side, enough to know that a won bid is not a delivered impression.
- Reporting granularity, and the difference between an estimate, a preliminary figure, and a settled one on a buyer’s report.

Specific to this engagement, and expected to be ramped rather than pre-held:

- The broadcaster’s notification specification and its three-stage settlement.
- Third-party viewing-rating measurement as the source of the billable impression count.

Depth in adtech billing, revenue reconciliation, or media measurement is expected.

### Nice to Have

- Adtech billing, revenue reconciliation, or publisher payouts.
- Settlement or financial systems outside advertising, where restatement and audit trails are ordinary requirements.
- Columnar analytics stores at reporting scale, including schema design for query-time aggregation.
- Reading-level C++, since the request path is written in it and the boundary between the two may move.
- Prior work with panel-derived or survey-derived measurement data, where the figure is an estimate with a confidence attached.
- Prior work against technical documentation in translation.
