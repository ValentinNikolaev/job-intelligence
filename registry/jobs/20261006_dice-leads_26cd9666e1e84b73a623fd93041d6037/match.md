# Match Analysis

**Score:** 73/100
**Recommendation:** Match

Strong senior PHP/backend, SQL, payments, integrations, and production-operations alignment; iGaming-specific and Python evidence are not established, and the Ukrainian posting provides limited location detail beyond Europe or Ukraine.

## Why it matches

- Strong PHP backend and relational-database experience with query optimization and high-volume systems.
- Payment gateway, API integration, incident analysis, testing, and production reliability evidence maps well to the responsibilities.
- Remote Europe eligibility is stated and the candidate is based in Italy.

## Gaps

- No direct iGaming experience is established.
- Python endpoint development is not established in the candidate profile.

## Concerns

- The source text is Ukrainian and English requirements are not stated; language expectations should be confirmed.
- Exact compensation and working-hour overlap are unspecified.

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| Senior PHP backend experience | critical / stated | strong | 5+ років backend-розробки, з них значна частина на PHP 8. | Develop integration with Stripe/PayPal/Skrill payment gateway providers. | / |
| MySQL, SQL optimization, indexes, and transactions | critical / stated | strong | MySQL або інша реляційна база на рівні «розумію план запиту»: оптимізація SQL, індекси, транзакції | Normalized database tables and performed extensive query optimization. | The profile does not enumerate transaction-isolation examples for this specific candidate record. / Probe transaction and migration experience in technical screening. |
| Tests and safe database migrations | high / stated | partial | Звичка писати тести на бізнес-логіку та перевіряти міграції на копії даних перед продом. | Increased unit-tests coverage. | Migration validation on copied data is not evidenced. / Confirm migration-testing practice with a production example. |
| External payment/API integrations | high / stated | strong | Досвід інтеграції зовнішніх API з грошима: підписи запитів, повтори, таймаути, дублікати | Develop integration with Stripe/PayPal/Skrill payment gateway providers. | The profile does not explicitly detail idempotency and signature handling. / Ask for a concrete payment-integration example covering retries and duplicate protection. |
| iGaming or payment-domain experience | preferred / stated | partial | Досвід у iGaming, фінтеху або платіжних системах. | Develop integration with Stripe/PayPal/Skrill payment gateway providers. | Payment experience is evidenced, but iGaming is not. / Position payment and fintech-adjacent work without claiming iGaming experience. |
