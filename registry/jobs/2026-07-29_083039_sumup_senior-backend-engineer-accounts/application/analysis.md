## Vacancy Summary

**Role:** Senior Backend Engineer - Accounts at SumUp, Berlin, Global Bank tribe. The team is building a global account platform for merchants, moving from fragmented regional setups to unified infrastructure across markets.

**Explicit requirements:** backend development with Kotlin as the primary language and opportunities in Go and Elixir; event-driven architecture; Kafka; distributed systems; AWS; Docker; Kubernetes; relational databases; API design; data modeling; object-oriented and functional design; observability with Prometheus, Grafana, and Honeycomb; ownership from design to production readiness; refactoring; Extreme Programming; small iterations; daily deliveries; collaboration and knowledge sharing.

**Inferred requirements:** the role likely needs careful reliability engineering, regulatory/compliance awareness, multi-region failure isolation, consistent account-state handling, and comfort with banking-domain constraints. The hiring manager may probe Kafka/event semantics, consistency trade-offs, internal platform design, and ability to work in a Kotlin-heavy environment.

**Candidate fit:** strong on Go backend ownership, event-driven systems, resilient pipelines, AWS, Kubernetes, relational databases, monitoring, production troubleshooting, migration work, and fintech/payment-adjacent history. Older source evidence includes payment gateway integrations with Stripe, PayPal, and Skrill; this is useful context but not listed as recent CV Experience because it is older than 10 years.

**Main gaps:** Kotlin, Kafka, Honeycomb, account/KYC/ledger-specific experience, and direct banking-platform ownership are not evidenced.

## Company Research

**Fact:** SumUp's Global Bank Tribe page says the tribe has 300 people, spans locations including Berlin, Cologne, Sao Paulo, Santiago, Sofia, and Vilnius, and aims to build the number 1 bank for small businesses. Source: [SumUp Global Bank Tribe](https://www.sumup.com/careers/global-bank-tribe/).

**Fact:** SumUp says it supports over 4 million merchants in 37 markets with tools and services for small, micro, and nano businesses. Source: [SumUp About Us](https://www.sumup.com/en-us/wtf-about-us/).

**Fact:** SumUp's careers site describes it as a global fintech with 3000+ people and lists many backend roles across Global Bank, Payments, Balance Management, Transfers, and other engineering areas. Source: [SumUp open positions](https://www.sumup.com/careers/positions/).

**Fact:** The role posting names Kotlin, Golang, Elixir, Java, AWS, Kafka, PostgreSQL, Kubernetes, Prometheus, Grafana, Honeycomb, Cursor, and GitHub Copilot. Source: [Arbeitnow role copy](https://www.arbeitnow.com/jobs/companies/sumup/senior-backend-engineer-accounts-berlin-181232).

**Fact:** A Confluent customer story says SumUp adopted Confluent Cloud to remove bottlenecks and support data mesh principles for product innovation and reusable data products. Source: [Confluent customer story](https://www.confluent.io/customers/sumup/).

**Inference:** SumUp likely values engineers who can combine product speed with operational rigor because banking/account systems need resilience, compliance, and clear observability across regions.

**Unknown:** public sources reviewed do not establish the exact Global Accounts team size, interview stages, Berlin office attendance expectations, Kotlin onboarding path, or the specific account/KYC/ledger systems this role owns.

## Initial Resume Audit

**Impact - 8/10.** Strength: the profile has measurable reliability and scale outcomes: 30% ticket deflection, 99.9% delivery reliability, 10x DataLake throughput, 30% API performance improvement, reduced database load, and 50 million emails per month. Weakness: the original CV does not frame these outcomes around multi-region financial-account infrastructure. Rewrite example: "Built resilient message delivery pipelines..." became a core Simple.life bullet tied to retries, monitoring, incidents, and peak load.

**Keyword relevance - 7/10.** Strength: Go, event-driven systems, AWS, Kubernetes, PostgreSQL/MySQL, REST APIs, Prometheus, monitoring, performance, and production reliability are supported. Weakness: Kotlin, Kafka, Honeycomb, account/KYC/ledger terminology, and explicit compliance-system design are not evidenced. Rewrite example: the Skills section now foregrounds event-driven systems, distributed systems, AWS, Kubernetes, PostgreSQL, monitoring, and performance optimization while excluding unsupported Kotlin/Kafka claims.

**Readability - 8/10.** Strength: the CV is plain, chronological, and easy to scan. Weakness: role-relevant event-pipeline evidence is split across Simple.life and CRURATED. Rewrite example: CRURATED is included as a distinct recent block focused on event schema, backpressure, Webhook/S3 downstreams, and 99.9% reliability.

**Summary effectiveness - 7/10.** Strength: the original summary establishes senior backend, Go, APIs, automation, and reliability. Weakness: it does not connect to financial infrastructure or platform ownership. Rewrite example: the tailored summary now names event-driven financial infrastructure, cloud-native delivery, migration work, and cross-functional collaboration.

**ATS compatibility - 8/10.** Strength: conventional Markdown structure and core supported backend keywords. Weakness: several prominent vacancy terms cannot be added as skills because evidence is missing. Rewrite example: supported terms were consolidated in Skills and repeated naturally in Experience.

**Baseline:** 7.6/10. Most important changes: highlight event-driven systems, distributed reliability, AWS/Kubernetes, PostgreSQL/MySQL, observability, migration work, and product/operations collaboration.

## Strict Hiring Manager Review

**Strengths:** (1) recent Go service ownership supports senior backend scope; (2) CRURATED and Simple.life show event-driven reliability, retries, backpressure handling, observability, and measurable outcomes; (3) airSlate shows cloud migration, database performance work, production troubleshooting, and team-level delivery ownership.

**Weakness:** Kotlin is the primary language in the vacancy and is not evidenced in the candidate records. This matters for day-one delivery. Safe rewrite: state strong Go/PHP backend experience and willingness to ramp into Kotlin; do not list Kotlin as a skill.

**Weakness:** Kafka is central to the vacancy, while the candidate evidence supports RabbitMQ, queues, EventBridge, and event-driven systems rather than Kafka specifically. Safe rewrite: describe event-driven architecture, delivery guarantees, and backpressure without claiming Kafka experience.

**Weakness:** account, KYC, ledger, or banking compliance systems are not directly evidenced. This matters because the Global Accounts platform must handle regional banking requirements. Safe rewrite: emphasize payment-adjacent older evidence, production reliability, data consistency, and compliance-adjacent Sixt evidence from interview prep rather than overstating account-domain ownership.

**Applied review:** the CV keeps unsupported Kotlin/Kafka/Honeycomb/account-domain terms out of Skills, uses recent event-driven reliability evidence, and frames the candidate as a strong distributed backend engineer who needs domain and Kotlin ramp-up. A second pass found no unsupported technology claims.

## Red Flags

- **Kotlin gap:** prepare a direct answer: production Kotlin is not evidenced, but Go/PHP backend experience, functional design exposure through system design, and typed-language learning discipline support ramp-up.
- **Kafka gap:** candidate has event-driven systems, queues, EventBridge, RabbitMQ, backpressure, and delivery guarantees, but no explicit Kafka evidence. Prepare to discuss concepts separately from tool experience.
- **Banking/account domain gap:** no direct KYC, ledger, IBAN/account, or regulatory workflow ownership appears in sources.
- **Location/onsite:** metadata says Berlin and `remote: false`; candidate is based in Italy. Confirm relocation, hybrid policy, or remote flexibility before investing further.
- **Timeline conflict:** Simple.life ends March 2026 in one source and Present in LinkedIn. Prepare a factual explanation.
- **Overlapping roles:** LinkedIn shows Simple App and CRURATED overlap. Explain engagement structure plainly if asked.

## ATS Keyword Analysis

**Top vacancy terms:** Kotlin, Golang, Elixir, Java, AWS, Kafka, PostgreSQL, Kubernetes, Prometheus, Grafana, Honeycomb, event-driven architecture, distributed systems, compliance, account platform, APIs, data modeling, cloud-native architecture, observability, Extreme Programming.

**Direct matches:** Go/Golang, AWS, Kubernetes, PostgreSQL, MySQL, REST APIs, event-driven systems, distributed systems, cloud-native delivery, Prometheus, monitoring/logging, production reliability, performance optimization, migration work, ownership, collaboration, CI/CD.

**Partially supported:** Kafka through event-driven systems, queues, EventBridge, RabbitMQ, delivery guarantees, and backpressure; compliance through GDPR/PCI-adjacent Sixt evidence and production reliability, but not banking compliance.

**Fully missing or not evidenced:** Kotlin, Elixir, Java, Kafka as hands-on tooling, Grafana, Honeycomb, account/KYC/ledger systems, Extreme Programming as explicit practice, and Berlin onsite availability.

**Underrepresented but supported before tailoring:** event pipelines, backpressure, delivery guarantees, production observability, database performance, and migration work.

**Terms deliberately not added as experience:** Kotlin, Kafka, Elixir, Java, Honeycomb, KYC, ledger, and banking compliance were not added to the CV because candidate evidence does not support them.

## Major CV Changes

- **Summary:** broad backend profile -> event-driven financial infrastructure, Go backend ownership, cloud-native delivery, observability, and migration work.
- **Skills:** general technologies -> 15 supported role-relevant skills led by Go, event-driven systems, distributed systems, AWS, Kubernetes, PostgreSQL/MySQL, CI/CD, Prometheus, and monitoring/logging.
- **Simple.life:** emphasized Go API orchestration, resilient delivery, retries, monitoring, and critical workflow migration.
- **CRURATED:** added event analytics infrastructure, Webhook/S3 downstreams, delivery guarantees, backpressure, observability, and 99.9% reliability.
- **airSlate:** emphasized Kubernetes migration, API/database performance, production troubleshooting, logging, and delivery metrics.
- **Unsupported terms:** Kotlin, Kafka, and account/KYC/ledger claims are handled as gaps rather than inserted into the CV.

## Final Quality Gate

Factual support: **9/10** - all CV claims trace to candidate records; missing Kotlin/Kafka/domain experience is explicit.  
Role fit: **8/10** - strong event-driven backend, Go, AWS, Kubernetes, relational database, reliability, and migration fit.  
Recruiter screening potential: **7/10** - strong senior backend evidence, but Kotlin and Berlin location may screen out.  
Hiring-manager appeal: **7/10** - strong adjacent distributed-systems reliability background, with tool/domain ramp-up required.  
ATS compatibility: **8/10** - clean format and supported keywords.  
Credibility: **9/10** - the package avoids inflated Kotlin/Kafka/banking claims.

## Recommendation

**Apply.** The candidate is a strong adjacent fit for SumUp's event-driven accounts platform through Go, distributed systems, cloud-native delivery, observability, and reliability experience. Apply after confirming Berlin/remote expectations and be candid about Kotlin, Kafka, and account/KYC domain ramp-up.
