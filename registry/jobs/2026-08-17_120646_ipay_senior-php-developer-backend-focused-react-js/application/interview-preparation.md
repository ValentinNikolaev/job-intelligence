# Interview Preparation — iPay Senior PHP Developer

## Recruiter / HR Screening

Prepare short, factual answers to these screens:

- **React.js gate:** The vacancy requires practical React, while the CV contains none. State the actual level immediately. Older AngularJS/frontend exposure is distant, transferable context only; do not imply React delivery.
- **Role/title fit:** Explain interest in a hands-on Senior PHP IC role despite previous lead positions, emphasizing architecture, reliability, review, and mentoring.
- **Motivation:** Connect iPay's critical payment flows with demonstrated high-load systems, MySQL/API performance, failure-aware delivery, PCI DSS work, and older payment integrations. Do not claim iPay product use or current PSP ownership.
- **Location/model:** State that you are in Rome. Confirm Italy eligibility, legal entity, contract model, Kyiv-hour overlap, data restrictions, equipment, and office expectations.
- **Compensation/availability:** Prepare range, currency, gross/net basis, notice period, and start date. Clarify tax, probation, benefits, and on-call.
- **Languages:** Present Ukrainian as native and English as Upper-intermediate; be ready to explain a production incident in English.
- **Confirmations:** PHP 7/8, legacy systems, Docker, 10M+ rows, index outcomes, and recent payment depth are unestablished.

## Culture Fit / Behavioral Interview

Prepare factual STAR outlines rather than invented answers:

1. **High-load ownership:** PDFfiller's approximately 50 million monthly emails and traffic peaks above 10x normal.
2. **Performance improvement:** airSlate database-load and API/query bottleneck work; explain the real signal, diagnosis, change, and verification.
3. **Failure handling:** Simple.life fallback, retry, and monitoring pipelines during incidents and peak load.
4. **Consistency across integrations:** CRURATED versioned schemas, downstream routing, delivery guarantees, and backpressure. Do not reframe this as financial consistency.
5. **Security-sensitive engineering:** Sixt work under PCI DSS constraints, audits, assessments, and vulnerability scans.
6. **Architecture decision:** Hyprr roadmap and architecture with the CTO, or CRURATED's event platform. Identify actual alternatives and consequences.
7. **Mentoring/review:** PDFfiller's five-engineer team or Hyprr's ten developers. Bring one genuine recent code-review example if available.
8. **Cross-functional problem solving:** Simple.life work with Support Ops, Product, and AI teams or Hyprr stakeholder collaboration.

## Technical Interview

- **Critical — React practical gate:** Expect components, hooks, state, routing, data fetching, testing, build tooling, and a feature task. If direct experience is absent, say so. Do not present AngularJS as React.
- **High — PHP/Laravel:** Review lifecycle, dependency injection, service boundaries, queues, errors, testing, migrations, upgrades, and performance. Confirm PHP 7/8 role by role; do not infer versions.
- **High — MySQL at scale:** Practice `EXPLAIN`, indexes, cardinality, joins, pagination, isolation, locking, replicas, partitioning, schema change, and measurement. airSlate grounds outcomes; 10M+ rows and index results remain unconfirmed.
- **High — Payment consistency system design:** Design a payment state machine covering idempotency keys, duplicate callbacks, retries, timeouts, partial failures, reconciliation, refunds, audit logs, and PSP outages. Treat these as design topics unless direct implementation is confirmed; older gateway work does not prove current ownership.
- **High — REST/API integration:** Cover versioning, authentication, validation, errors, pagination, compatibility, observability, partner timeouts, and rollout. Use Simple.life and other REST work.
- **High — PCI/security:** Prepare card-data boundaries, least privilege, secrets, logging hygiene, vulnerability management, and auditability. Ground answers in Sixt without claiming iPay-specific responsibility.
- **Medium — CI/CD and production:** Explain GitHub Actions, ArgoCD, Helm, Kubernetes, deployment checks, rollback, and incident diagnosis. Docker basics are not evidenced and need honest confirmation.
- **Medium — Observability:** Use Prometheus/logging at airSlate, Jaeger at Hyprr, and CRURATED delivery observability. Cover metrics, logs, traces, alerting, SLOs, and regression detection with employer-specific examples.
- **Medium — Legacy stabilization/design:** Discuss characterization tests, incremental change, feature flags, schema compatibility, telemetry, and rollback only as an approach unless a real legacy case exists. OOP, SOLID, and named patterns are also unconfirmed terms.

## CV Deep-Dive Questions

Prepare to defend: CRURATED's 10x throughput; PDFfiller's 50-million monthly volume, 10x peaks, and five engineers; Hyprr's under-six-month beta and ten developers; airSlate's database/API improvements; and the Simple.life reliability claims. For every metric, know the baseline, measurement source, personal contribution, constraints, decision, verification, and lasting effect. If exact precision cannot be reconstructed, describe the supported outcome without false confidence.

Expect questions about recent PHP continuity after Go-focused Simple.life, the concurrent part-time CRURATED engagement, the exact Laravel/Symfony logger contribution, and why older bank/Stripe/PayPal/Skrill work remains relevant. Keep payment history clearly dated and never move technologies between employers.

## Company-Specific Preparation

Verified context: iPay is a Ukrainian online payment service for card-funded payments on its own and partner sites. It publicly emphasizes payment convenience, card-data protection, anti-fraud, and merchant growth. The vacancy states more than 76,000 daily payments, over 27 million 2025 transactions, and 2,000+ merchants.

Official pages use different partner totals and cite over one million daily “operations,” a broader undefined measure. Do not combine these figures; ask how payments, transactions, and operations are defined. The employing entity, current PCI details, architecture, on-call, legacy age, and React workload are unknown. Do not claim product use.

## Preparation Plan

- **Before recruiter:** confirm React level, PHP versions, Rome-remote eligibility, title fit, compensation, notice, language, and truthful gap statement.
- **Before technical:** complete one React readiness check, one MySQL exercise, and one payment system design; refresh PHP/Laravel, REST, PCI, CI/CD, and observability; verify CV metrics.
- **Before final:** prepare three STAR stories—performance, reliability, and security/mentoring—with trade-offs and lessons.

## Questions to Ask

1. How much React work is expected weekly, and is there a practical assessment?
2. Which payment flows and partner integrations would this role own?
3. How do you define payments, transactions, and operations in published scale figures?
4. What are the current SLOs, main failure modes, and on-call expectations?
5. What does the legacy estate look like, and which modernization work is highest priority?
6. How are idempotency, reconciliation, and partner outages handled today?
7. What are the database scale, migration constraints, and most urgent MySQL bottlenecks?
8. Which PCI/security responsibilities belong directly to this engineering team?
9. Can iPay contract a Rome-based engineer, and what collaboration hours apply?
10. What outcomes define success after three and six months?
