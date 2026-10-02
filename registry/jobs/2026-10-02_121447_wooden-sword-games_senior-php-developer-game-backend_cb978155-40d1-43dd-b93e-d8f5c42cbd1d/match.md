# Match Analysis

**Score:** 74/100
**Recommendation:** Match

Senior backend experience, recent production PHP ownership, and earlier Laravel work align with much of the primary API stack. PostgreSQL and performance work are evidenced. The required Nakama TypeScript runtime and its async programming practices remain unverified, and game experience is only a preference.

## Why it matches

- Recent PHP ownership, earlier Laravel work, and long backend tenure support much of the primary stack.
- PostgreSQL, API design, performance, and technical ownership are evidenced.
- The vacancy is marked remote in its current source metadata.

## Gaps

- No verified TypeScript or Nakama production experience in the candidate sources.
- No verified game backend or live-service game experience.

## Concerns

- Depth with PostgreSQL transactions and locking is not established by the candidate sources.
- The job text does not describe time-zone or country limits for remote work.

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| Independent Laravel/PHP implementation | critical / stated | partial | Ability to independently develop migrations, Eloquent models, API controllers, and Artisan commands without constant guidance. | I have a strong track record in PHP, with 5 years of leadership experience. | PHP depth and some Laravel work are evidenced, but the specific Eloquent, migration, and Artisan deliverables are not individually confirmed. / Confirm examples of those Laravel components before presenting them as direct experience. |
| At least five years of backend development | critical / stated | strong | 5+ years of backend development experience. | Backend engineer with 15+ years of experience building and improving production | / |
| Implement Nakama backend features in TypeScript | high / stated | unknown | Implement backend features in the Nakama Game Server TypeScript runtime |  | The candidate evidence does not establish production TypeScript or Nakama experience for this central runtime. / Ask about actual TypeScript work and assess a short Nakama ramp-up example. |
| TypeScript typing and asynchronous runtime practices | high / stated | unknown | Understanding of asynchronous programming pitfalls in a single-threaded runtime environment. |  | Specific single-threaded async and typing practice is unverified. / Verify concrete TypeScript async and type-system examples before claiming proficiency. |
| Strong PostgreSQL and efficient SQL design | high / stated | partial | Strong experience with PostgreSQL, efficient SQL query design, transactions, and basic locking concepts. | - PostgreSQL | PostgreSQL is evidenced, while transaction and locking depth is not separately documented. / Ask for a production query, transaction, and locking example. |
| Laravel REST API integration | meaningful / stated | partial | Integrate with the Laravel REST API | **Skills:** PHP \| Go \| Laravel \| MySQL \| AWS \| Kubernetes \| Microservices \| REST APIs \| | Laravel and REST API experience appear together in the candidate record, but this does not establish a specific Laravel REST integration example. / Confirm a concrete Laravel API integration before making that claim. |
| Unit tests for new modules | meaningful / stated | partial | Write and maintain unit tests for all new modules | Tests: 1 of 3 → 3 of 3 processes covered. | Evidence shows testing improvements but not a consistent unit-test practice across both target runtimes. / Discuss recent test design and the target team's coverage expectations. |
| Performance optimization of RPC hot paths | meaningful / stated | partial | Profile and optimize hot-path RPC handlers | Identified and optimized performance bottlenecks | General backend performance experience transfers, but Nakama RPC profiling is unverified. / Explain a source-backed profiling approach and learn the Nakama instrumentation. |
| Remote working arrangement | meaningful / inferred | strong |  | Rome, Italy | The current metadata marks the role remote but gives no explicit geographic or time-zone policy. / Confirm that an Italy-based candidate can work in the required hours. |
| Game development experience | preferred / stated | unknown | Any game development or live-service game experience. |  | / |
