# Interview Preparation — FAVBET Senior PHP Developer

## Recruiter / HR Screening

Prepare concise, factual answers:

- **Motivation:** Explain the move to a PHP-centered role through sustained PHP depth, recent concurrent PHP consulting at CRURATED, and interest in hands-on architecture. Connect FAVBET to high-load integrations, security/correctness, and its public responsible-gaming safeguards. Do not claim betting experience or product use.
- **Location/model:** State that you are in Rome and confirm willingness to work fully remotely. Ask about contracting from Italy, legal employing entity, core hours, time-zone overlap, and jurisdiction restrictions.
- **Availability/compensation:** Prepare the exact notice period, earliest start date, full-time availability, and a range with currency. Clarify employment versus contracting, benefits, tax responsibility, and on-call before anchoring compensation.
- **Languages/timeline:** Present Ukrainian as native and English as upper-intermediate. Explain that CRURATED was part-time consulting concurrent with Simple.life, not another full-time job.
- **Gaps:** The CV does not establish Redis/Redis Streams, Docker, SOAP/XML/RPC, named API/design methods, or coding-agent use. Separate confirmed knowledge from ramp-up areas.

## Culture Fit / Behavioral Interview

Prepare factual STAR outlines, not memorized answers:

1. **Strategic decision:** Hyprr roadmap and architecture choices with the CTO during prototype-to-beta delivery.
2. **Production pressure:** PDFfiller's approximately 50 million monthly emails and traffic peaks above 10x normal.
3. **Speed versus correctness:** CRURATED's modular, versioned event schemas and delivery guarantees.
4. **Difficult migration:** airSlate's ECS-to-Kubernetes move; use only rollout and verification details actually remembered.
5. **Mentoring:** PDFfiller's five-engineer team, Hyprr's ten developers, or airSlate's 20+ interviews; identify real practices and outcomes.
6. **Cross-functional prioritization:** Simple.life with Support Ops, Product, and AI, or Hyprr with business stakeholders.
7. **Reliability incident:** Simple.life fallback/retry pipelines or airSlate troubleshooting; prepare failure mode, decision, verification, and follow-up.
8. **Revised approach:** Supply a genuine example; the CV proves ownership but not a specific rejected design.

## Technical Interview

- **High — PHP coding and Laravel/Symfony:** Expect dependency injection, module boundaries, queues, framework lifecycle, testing, error handling, upgrades, and performance. Explain the airSlate logger package and distinguish depth in each framework.
- **High — Architecture/system design:** Practice a high-throughput service with synchronous APIs and workers. Cover idempotency, ordering, retries, dead letters, backpressure, consistency, observability, failure isolation, rollout, and capacity, grounded in real roles.
- **High — Databases/PostgreSQL:** Review indexes, `EXPLAIN`, isolation, locks, transactions, migrations, pooling, replicas, partitioning, and load diagnosis. PostgreSQL is documented at Hyprr; airSlate's detailed optimization used MySQL.
- **High — Messaging:** Prepare RabbitMQ exchanges, routing, acknowledgements, prefetch, retry topology, poison messages, idempotent consumers, and monitoring. Redis and Redis Streams are gaps, not RabbitMQ equivalents; discuss conceptual preparation without claiming production use.
- **High — Infrastructure:** Explain Kubernetes deployments, probes, resources, autoscaling, configuration, secrets, observability, and safe rollbacks using airSlate/Hyprr evidence. Docker is not established in the CV; confirm separately or state the gap.
- **High — API/security:** Cover REST versioning, auth, validation, rate limits, errors, compatibility, and PCI DSS/GDPR lessons. SOAP, XML, RPC, OpenAPI, AsyncAPI, HTTP/2, HATEOAS, and OWASP are not documented experience.
- **High — AI-assisted development:** The CV proves AI/LLM product automation, not coding-agent use. If unconfirmed, say so. Discuss limited permissions, small diffs, tests, human review, and secret controls only as an approach.
- **Medium — Testing/design methods:** Review unit, integration, contract, end-to-end, and asynchronous tests. GoF, DDD, TDD, and Twelve-Factor are unsupported as experience; explain only defensible knowledge.
- **Medium — Observability and operations:** Prepare concrete metrics, logs, traces, alerting, SLO trade-offs, and incident follow-up from Prometheus/Jaeger and monitoring work.
- **Low — iGaming-specific implementation details:** Learn common concerns such as auditability and responsible controls, but do not imply domain experience. The team architecture is unknown.

## CV Deep-Dive Questions

Expect challenges on Simple.life's 30%, CRURATED's 10x and under-four-hour figures, PDFfiller's 50-million scale and 10x peaks, Hyprr's six-month beta, team sizes, and 20+ interviews. Prepare the baseline, measurement source, personal contribution, constraints, trade-offs, and verification. If a figure cannot be reconstructed, describe the outcome without false precision.

Also prepare CRURATED's engagement boundaries, PHP recency after Go-focused Simple.life, and exact airSlate logger/Kubernetes responsibilities. Bring a real recent code-review example if available.

## Company-Specific Preparation

Know only what is verified: FAVBET describes itself as a global Entertainment Tech company with Ukrainian roots and 25+ years in betting/gaming. Its Ukrainian operator publishes licensing and responsible-gaming measures, including eligibility controls, spending limits, and self-exclusion. The employing entity, team, markets, scale, on-call model, and product boundaries remain unknown.

Frame motivation around backend ownership, high-load integrations, security/correctness, and governed AI assistance. Avoid unsupported value claims.

## Preparation Plan

- **Before recruiter:** motivation, timeline, Italy-remote logistics, language, start date, compensation approach, and truthful gap statement.
- **Before technical:** rehearse one PHP design; refresh PostgreSQL, RabbitMQ, Kubernetes, testing, and API security; verify metrics and unsupported-skill boundaries.
- **Before final/culture:** build three STAR outlines—architecture, reliability, and mentoring—with trade-offs and lessons.

## Questions to Ask

1. Which product, markets, and service boundaries would this team own?
2. What are the current scale, reliability targets, and most important architecture constraints?
3. How are PostgreSQL, RabbitMQ, and Redis Streams used, and which problems are most urgent?
4. What does successful coding-agent adoption look like, and what review, testing, and security controls govern generated changes?
5. How are architecture decisions made, documented, and challenged across teams?
6. What proportion of the role is hands-on delivery, design leadership, review, and mentoring?
7. What are the on-call and incident-response expectations?
8. Which legal entity and contract model support a fully remote engineer based in Italy?
9. What outcomes would define success in the first three and six months?
