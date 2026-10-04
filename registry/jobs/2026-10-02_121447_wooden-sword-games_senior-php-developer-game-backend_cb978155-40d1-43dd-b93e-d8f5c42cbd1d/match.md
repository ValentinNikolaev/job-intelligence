# Match Analysis

**Score:** 77/100
**Recommendation:** Match

Senior backend experience, production PHP and Laravel work, and recent technical ownership of PHP event systems align with the primary stack. Candidate-confirmed airSlate database and API performance results strengthen the high-load fit. PostgreSQL is present, but transaction and locking depth is not established. Nakama TypeScript runtime work and game backend experience remain unverified.

## Why it matches

- More than 15 years of backend experience, including PHP/Laravel and recent PHP production ownership.
- Candidate-confirmed airSlate database stability and average API response-time improvements support the vacancy's performance work.
- Production analytics throughput, event delivery, and backend team leadership show transferable scale and delivery judgment.

## Gaps

- No verified Nakama or production TypeScript runtime experience, including single-threaded async practices.
- No verified game backend or live-service game experience.

## Concerns

- PostgreSQL experience is evidenced, but transactions and locking depth are not separately documented.
- The vacancy is marked remote, but does not state Italy or time-zone eligibility.

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| Independent Laravel/PHP implementation | critical / stated | partial | Ability to independently develop migrations, Eloquent models, API controllers, and Artisan commands without constant guidance. | I have a strong track record in PHP, with 5 years of leadership experience. | PHP leadership and Laravel are documented, but the listed Laravel deliverables are not each confirmed. / Ask for concrete migration, Eloquent, controller, and Artisan examples. |
| At least five years of backend development | critical / stated | strong | 5+ years of backend development experience. | Backend engineer with 15+ years of experience building and improving production | / |
| Implement Nakama backend features in TypeScript | high / stated | unknown | Implement backend features in the Nakama Game Server TypeScript runtime |  | No candidate source establishes Nakama or production TypeScript runtime work. / Verify actual TypeScript experience and assess the Nakama learning path. |
| TypeScript typing and asynchronous runtime practices | high / stated | unknown | Understanding of asynchronous programming pitfalls in a single-threaded runtime environment. |  | Strong typing, async/await, and single-threaded runtime practices are unverified. / Request a concrete example before representing this as experience. |
| Strong PostgreSQL and efficient SQL design | high / stated | partial | Strong experience with PostgreSQL, efficient SQL query design, transactions, and basic locking concepts. | - PostgreSQL | PostgreSQL and database performance are supported, while transaction and locking examples are missing. / Ask for a production query, transaction, and locking example. |
| Laravel REST API integration | meaningful / stated | partial | Integrate with the Laravel REST API | **Skills:** PHP \| Go \| Laravel \| MySQL \| AWS \| Kubernetes \| Microservices \| REST APIs \| | Laravel and REST APIs are documented together, but a specific Laravel API integration is not confirmed. / Confirm a production Laravel REST integration example. |
| Unit tests for new modules | meaningful / stated | partial | Write and maintain unit tests for all new modules | Tests: 1 of 3 → 3 of 3 processes covered. | A recent testing improvement is documented, but consistent unit testing in both target runtimes is unverified. / Discuss recent test design and target-team expectations. |
| Performance optimization of RPC hot paths | meaningful / stated | partial | Profile and optimize hot-path RPC handlers | Identified and optimized performance bottlenecks, which decreased API response times | The candidate-confirmed airSlate result supports backend performance work, but Nakama RPC profiling is unverified. / Discuss the Prometheus-measured API example and how its method would transfer to Nakama instrumentation. |
| Remote working arrangement | meaningful / inferred | strong |  | Rome, Italy | The posting is marked remote but gives no explicit country or time-zone policy. / Confirm Italy-based remote eligibility and required hours. |
| Game development experience | preferred / stated | unknown | Any game development or live-service game experience. |  | / |
