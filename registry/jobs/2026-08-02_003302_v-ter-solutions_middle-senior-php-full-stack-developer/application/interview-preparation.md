# Interview Preparation

## Recruiter / HR Screening

Prepare answers covering:

- Why a hands-on PHP product role is attractive despite prior lead responsibilities.
- Expected balance between backend work and simple frontend tasks.
- Experience working in PHP without relying on framework abstractions; provide only examples the candidate can verify personally.
- Remote collaboration from Rome, timezone overlap, contract/employment model, and availability.
- English level for documentation and team communication.
- Salary expectations, notice period, and motivation, which are not in the source records.
- Correct end date for the latest role because the two candidate sources conflict.

## Culture Fit / Behavioral Interview

1. Describe a product workflow you improved — use Simple.life routing and platform migration work.
2. Tell us about a database performance problem — use airSlate's peak-load reduction.
3. Give an example of integrating an external service — use Zendesk and Intercom.
4. How do you handle unclear requirements — use Hyprr roadmap work with the CTO and stakeholders.
5. Describe a production issue you diagnosed — use airSlate logs, monitoring, and SRE dashboards.
6. Tell us about a high-load event — use PDFfiller's BFCM traffic increase.
7. How do you work with product colleagues — use airSlate planning and Simple.life cross-functional work.
8. Describe a technical decision you influenced — use Hyprr architecture or the transactional email service.

## Technical Interview

- **High priority — PHP fundamentals:** object design, dependency boundaries, error handling, configuration, autoloading, secure input handling, and structuring a codebase without a framework.
- **High priority — MySQL:** indexes, `EXPLAIN`, joins, transactions, isolation, locking, schema evolution, batching, and diagnosing slow queries.
- **High priority — integrations:** REST contracts, authentication, idempotency, retries, rate limits, timeouts, webhooks, and reconciliation.
- **High priority — business-process optimization:** model current state, identify constraints, preserve auditability, and measure operational effects.
- **Medium priority — JavaScript/frontend:** DOM events, asynchronous requests, form validation, browser/backend contracts, HTML/CSS, and Bootstrap. Review jQuery syntax without claiming recent depth.
- **Medium priority — testing:** unit/integration boundaries, database tests, contract tests, fixtures, and safe refactoring.
- **Medium priority — code maintenance:** reading unfamiliar flows, profiling, characterization tests, small releases, and rollback.
- **Low priority — advanced distributed architecture:** useful context, but likely secondary to practical product work.

## CV Deep-Dive Questions

- What PHP services and shared components did you build at airSlate?
- Which database changes reduced peak workload, and how was the result observed?
- How did the Simple.life orchestration layer handle retries and duplicate events?
- What did you personally implement versus lead at Hyprr?
- How did the transactional email platform reach its monthly volume?
- Which frontend technologies have you used directly, and how recently?
- Can you describe a substantial PHP codebase built without a modern framework?

## Company-Specific Preparation

Review the [DOU company profile](https://jobs.dou.ua/companies/v-ter-solutions/) and [official product site](https://v-tersolutions.com/). Understand the stated modules—carrier connections, warehouse operations, customs, delivery tracking, and billing—but treat published scale metrics as company claims. Prepare to ask which product and modules the vacancy supports and whether PHP without a framework is a deliberate architecture or a legacy constraint.

## Preparation Plan

**Must prepare:** one detailed PHP/MySQL performance story; one external-integration story; recent frontend examples; an honest framework-free PHP answer; location and availability.

**Before the technical interview:** practice designing a small PHP service without Laravel/Symfony, review MySQL transactions and indexes, and rehearse failure handling for an external carrier API.

**Before final/culture rounds:** align on hands-on scope, autonomy, seniority expectations, and what influence over product decisions means in practice.

## Questions to Ask

1. Which product and modules would this engineer work on first?
2. Why is the PHP codebase framework-free, and how is it structured?
3. What are the largest current MySQL performance or data-quality challenges?
4. Which external integrations are most operationally critical?
5. How much of the role is frontend work in a typical month?
6. What automated testing and release checks are in place?
7. How are product decisions made and validated with customers?
8. What would a successful first 90 days look like?
