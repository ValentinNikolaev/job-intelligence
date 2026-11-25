# Application analysis: Go Developer at Payward

## Vacancy Summary

Proceed with a tailored application if the candidate is comfortable with the payment-processing and on-call scope. The role calls for correctness under retries and provider failures, and the candidate can offer relevant Go service ownership, event-driven systems and security-sensitive work. The current match is 82/100, a strong match, but that score does not establish the missing payment-specialist skills below. The [Djinni posting](https://djinni.co/jobs/859359-go-developer/) describes full-time remote work worldwide. The company presents itself as a payment orchestration startup on its [Djinni profile](https://djinni.co/jobs/company-payward/); its legal identity and working arrangements need confirmation.

## Company Research

The job asks for at least two years of Go within three years of commercial backend work, concurrency, PostgreSQL, message brokers, test practice, Docker and CI/CD. Its core service receives payment requests, routes them to providers, manages callbacks and keeps transaction state correct. Security, observability, incidents, settlement and reconciliation form part of the work. Payment and PCI experience are listed as advantages.

The candidate owned a Go support platform connecting Zendesk, Intercom and internal services. At CRURATED, event analytics used queues and EventBridge. At Simple.life, the candidate built a Go gateway that separates helpdesk vendors behind a common event model. It combined webhooks, tenant storage and queues, and enabled a product demonstration. That is a strong example of integration boundaries, but it was a helpdesk system, not a payments router. The telephony platform offers a second example: the candidate owned backend design and delivery through security sign-off and production release, including privacy controls. At CRURATED he owned a production analytics platform and event versioning, including modular work that shortened setup for a new stream. At airSlate, backend work reduced database load and improved release processes. Sixt included code work within PCI DSS requirements.

The candidate also worked with payment integrations earlier in his career, outside the CV's approved employer window. That history may be discussed accurately in an interview but is omitted from the CV. Neither this nor the support gateway demonstrates ownership of settlement, card tokenisation, ISO 8583 or payment-provider state machines.

## Red Flags

The sources reviewed do not establish the depth of Go concurrency primitives, PostgreSQL isolation and tuning, Docker, test ownership, outbox design, circuit breakers or exactly-once processing expected by the posting. Prepare concrete examples only where they describe actual work; present a whiteboard proposal as a proposal. Clarify the team's operational definition of exactly-once and how provider idempotency and reconciliation handle ambiguous responses. The job describes on-call but not frequency, support or compensation. Ask about the contract, team location and legal employer as well.

The candidate's professional English is upper-intermediate, matching the stated level. The named profile is a small startup; the separate identity of any similarly named company is not established. Avoid assuming a relationship or its benefits from the name.

## Initial Resume Audit

| Dimension | Baseline / 10 | Strength | Weakness and concrete change |
| --- | --- | --- | --- |
| Impact | 6 | The source includes operational and delivery results. | Some older figures are contradicted or lack context; use the confirmed qualitative gateway and database outcomes. |
| Relevance | 6 | Go, events and production systems are visible. | Lead with the Go gateway and security-sensitive delivery rather than a generic technology list. |
| Readability | 7 | Roles and skills are easy to locate. | Correct the latest Simple.life end date and label the CRURATED overlap as a concurrent subcontract. |
| Summary | 6 | Backend identity and core languages are clear. | Add integration and production ownership, without claiming payment state-machine expertise. |
| ATS | 7 | Standard headings and recognizable backend terms are present. | Retain evidence-backed PostgreSQL, queues and CI/CD; omit unsupported ISO 8583 and tokenisation. |

Overall baseline: 6.4/10. The tailored draft emphasizes the service boundary, production security and event analytics. It retains the permitted career chronology; older permitted entries are compact to keep the recent work prominent. The CV needs an independent editorial review and rendered-page check before publication.

## Strict Hiring Manager Review

Three strengths are hands-on Go integration work, operational ownership across service boundaries, and an evidenced track record working with event-driven data. Three material concerns are the gap between helpdesk integration and payment-state guarantees, unproven hands-on knowledge of concurrency and database isolation, and a change of domain into payment orchestration. A defensible rewrite is “built a vendor-neutral Go gateway” rather than “designed a payments platform.” Similarly, “developed code under PCI DSS requirements” is narrower than “led PCI compliance.” For retries, describe a known system's actual behavior and state what remains to be designed.

## Final Quality Gate

The original application is through Djinni. The logged-in form inspected on 25 November 2026 has a message field that is not required. A letter is therefore not part of this package. No application has been submitted. Confirm the employer and terms before sharing further personal information.

## ATS Keyword Analysis

Use only supported Go, PHP, API integration, production reliability and event-driven terms. Do not add requirements without evidence.

## Major CV Changes

The draft prioritizes relevant integration work, corrects dates and labels the concurrent subcontract. The accompanying claim ledger links the experience examples to their source records.

## Recommendation

Consider applying after confirming the contract and on-call terms; keep unsupported payment-specialist claims out of the CV.
