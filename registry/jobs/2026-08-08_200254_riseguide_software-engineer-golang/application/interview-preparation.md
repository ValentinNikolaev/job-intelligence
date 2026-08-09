## Recruiter / HR Screening

Підготувати точні відповіді про комерційну Go-хронологію, причину інтересу до RiseGuide, роботу з Рима, формат B2B/EOR, CET/EET overlap, work authorization, sponsorship, notice period, start date і compensation. Пояснити overlap Simple.life/CRURATED та дату завершення Simple.life. Уточнити мову інтерв'ю, локаційні обмеження й очікування щодо Варшави/Києва.

## Culture Fit / Behavioral Interview

1. Ownership за production-систему — Simple.life automation platform.
2. Сміливе архітектурне рішення — CRURATED event-driven pipeline.
3. Ітеративний delivery — запуск нових analytics streams менш ніж за чотири години.
4. Пріоритезація під тиском — BFCM у PDFfiller або delivery в Hyprr.
5. Ідея, яку команда “roasted” — підготувати реальний приклад технічного review.
6. Аргументована незгода — реальна architecture discussion з airSlate/Hyprr.
7. Production failure і навчання — incident troubleshooting в airSlate або Simple.life.
8. Допомога іншим зростати — mentoring і technical interviews.
9. Швидкий feedback loop — metrics після міграції Zendesk/Intercom flows.
10. Баланс 2x initiative проти incremental improvement — пояснити, коли кожен підхід виправданий.

## Technical Interview

- **High — Go internals:** goroutines, channels, context, memory allocation, interfaces, error handling, race detector, profiling.
- **High — Service design:** boundaries, API contracts, idempotency, retries, backpressure, graceful shutdown, configuration.
- **High — Kubernetes:** workloads, probes, resources, autoscaling, rollouts, secrets, observability, failure modes.
- **High — System design:** greenfield architecture for hundreds of thousands of users, scaling, queues, data consistency, caching, rate limits.
- **High — Production reliability:** SLOs, structured logs, metrics, traces, alerting, incident response.
- **Medium — GraphQL:** schema design, resolvers, N+1, federation, authorization, pagination; state clearly that production evidence is absent.
- **Medium — GCP:** map verified AWS/Kubernetes concepts to GKE, Pub/Sub, Cloud SQL, storage and observability without claiming experience.
- **Medium — Data layer:** PostgreSQL/MySQL indexes, transactions, consistency and migrations.
- **Medium — Product speed:** feature flags, thin vertical slices, reversible decisions and instrumentation.
- **Low — PHP:** background context, unless legacy integrations unexpectedly require it.

Expect Go coding around concurrency, an API/service task, or a greenfield system-design interview. Narrate invariants, failure modes, observability and rollback.

## CV Deep-Dive Questions

- Яка точна хронологія production Go?
- Як були виміряні 35% first-response та 28% resolution improvements?
- Які саме компоненти Simple.life були у прямій ownership?
- Чому CRURATED і Simple.life перетинаються?
- Як досягли 10x DataLake throughput і 99.9% delivery reliability?
- Яка роль у ECS-to-Kubernetes migration?
- Які рішення довелося захищати перед CTO або product leadership?
- Як були організовані mentoring та code review?

## Company-Specific Preparation

Вивчити RiseGuide app, SEEK, personalized journeys, subscription model і team manifesto. Не заявляти, що користувалися продуктом. Підготувати системний дизайн для mobile microlearning: content delivery, personalization events, progress tracking, search, notifications, experimentation та analytics. Уточнити, що саме “build from scratch” означає для backend і які частини вже працюють.

## Preparation Plan

**Must prepare:** Go timeline, location/contract, role overlap, motivation, salary, notice period, and a two-minute Ukrainian and English introduction.

**Pre-technical:** Go concurrency/profiling, Kubernetes, greenfield system design, REST-to-GraphQL concepts, AWS-to-GCP mapping, database consistency, observability, and two architecture stories with metrics.

**Pre-final/culture:** examples of bold decisions, receiving critique, ownership, helping others grow, high-intensity delivery, and setting limits that protect production quality.

## Questions to Ask

1. Які backend-компоненти вже існують, а які треба будувати з нуля?
2. Які GCP services і GraphQL architecture використовує команда?
3. Які current scale, traffic patterns і growth targets?
4. Які SLOs, observability та on-call expectations?
5. Як команда приймає й документує архітектурні рішення?
6. Як балансуються speed і technical quality?
7. Що буде зоною ownership у перші три місяці?
8. Який склад engineering team і хто є ключовими stakeholders?
9. Які contract/location constraints для кандидата з Італії?
10. Який формат technical interview і coding task?
