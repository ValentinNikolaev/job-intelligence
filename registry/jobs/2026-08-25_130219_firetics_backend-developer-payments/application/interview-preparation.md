## Recruiter / HR Screening

Коротке позиціонування: «Я PHP/Laravel backend-інженер із досвідом production-систем, API-інтеграцій, MySQL performance work, черг, спостережуваності та надійної доставки подій. Найближче до цієї ролі — побудова resilient pipelines з retries, fallback logic і monitoring у Simple.life та event/webhook delivery у CRURATED. Маю ранній досвід інтеграцій Stripe, PayPal, Skrill і банківських платіжних систем; деталі конкретних payment flows готовий уточнити чесно». Не називайте цей досвід недавнім iGaming ownership, якщо не можете підтвердити це прикладами.

Поясніть мотивацію через hands-on ownership: цікаві інтеграційні межі, коректність фінансових станів і операційна надійність, а не пошук керівної посади. Технічне лідерство подайте як уміння впливати на дизайн, документацію та менторство без очікування people-management. Для дистанційного формату підтвердіть роботу з Рима в CET та українську як рідну.

Підготуйте точні відповіді на TODO_CONFIRM: ваш статус права на роботу в Італії/ЄС і потреба у sponsorship; notice period; найближча дата старту; очікувана компенсація; комфортні години співпраці; розмовний рівень англійської. Якщо спитають про паралельні ролі, прямо скажіть, що CRURATED був part-time consulting engagement паралельно з Simple.life.

## Culture Fit / Behavioral Interview

Для питання про складний інцидент використайте Simple.life: опишіть контекст resilient message-delivery pipelines, ваш внесок у fallback logic, retries і monitoring, спосіб взаємодії з Support Operations, Product та AI-командами і підсумок без непідтверджених цифр. Структура відповіді: проблема, ваші рішення, як перевіряли вплив, що змінили в процесі. Не називайте це платежами.

Для впливу без формальної влади можна звернутися до airSlate: product-wide logger package, узгоджений зі стандартами interservice communication, або до CRURATED: versioned event schema і модульні streams. Підкресліть прагматичність: спочатку спільні контракти й вимірюваність, потім поступове впровадження. Підготуйте приклад технічної незгоди лише з власного досвіду; якщо конкретного прикладу немає, не вигадуйте його.

На запитання «чому iGaming?» сформулюйте мотивацію обережно: вам цікава відповідальна інженерія систем із високою ціною помилки, інтеграції та надійність. TODO_CONFIRM власну готовність працювати саме з iGaming і будь-які особисті або етичні межі. Не припускайте юрисдикції, продуктову політику чи регуляторні обов’язки Firetics.

## Technical Interview

Відпрацюйте дизайн adapter layer: канонічні внутрішні команди й результати, окремі provider adapters, конфігурація без секретів у логах, нормалізація помилок, versioning контрактів, метрики та correlation IDs. Поясніть, як додавати PSP через contract tests, sandbox-перевірки, feature flags і контрольований rollout. Це дизайн-підхід, а не твердження про вже реалізований вами payment gateway.

Для webhook scenario розберіть: автентичність повідомлення й перевірку підпису; зберігання idempotency key або provider event ID; атомарну фіксацію обробки; дедуплікацію; retries з backoff; out-of-order статуси; аудит; алертинг; відокремлення синхронної відповіді від асинхронної роботи. Чітко відділіть знання дизайну від TODO_CONFIRM власного production-досвіду з signature validation, idempotency та chargebacks.

Повторіть MySQL: індекси й EXPLAIN, короткі транзакції, contention, optimistic versus pessimistic locking, isolation trade-offs, deadlock retry та безпечний rollback. Зв’яжіть із підтвердженим airSlate досвідом: аналіз bottlenecks знизив пікове навантаження на основну БД до 65%, а оптимізація API/query bottlenecks скоротила середній response time на 30%. Не стверджуйте, що ці результати стосувалися payment tables.

Будьте готові порівняти RabbitMQ, Redis і БД. RabbitMQ та event-driven systems підтверджені; Redis як locks, cache, rate limiting або Pub/Sub — TODO_CONFIRM. Якщо Redis-досвіду немає, скажіть це прямо, поясніть теоретичні компроміси й готовність швидко закрити прогалину.

## CV Deep-Dive Questions

Підготуйте розгорнуту, але точну історію Simple.life: Go-платформа інтегрувала Zendesk, Intercom та внутрішні сервіси; ви будували API orchestration і lifecycle tracking, а також reliability mechanisms. Для CRURATED поясніть, як versioned event schema, streams, routing до Webhook і S3, backpressure, retries та observability підтримували delivery reliability понад 99.9%. Уточніть власну частку відповідальності, масштаби й межі ролі лише за пам’яттю.

На airSlate очікуйте питання про Laravel/Symfony, logger package, MySQL bottlenecks, Kubernetes migration і технічні інтерв’ю. На PDFfiller — про transactional-email service, приблизно 50 мільйонів emails на місяць і BFCM навантаження понад 10×; поясніть відмінність messaging reliability від фінансової коректності. На старі payment integrations підготуйте TODO_CONFIRM: провайдер, конкретний API flow, ваша зона відповідальності, помилки та обмеження знань, що могли змінитися.

## Company-Specific Preparation

Firetics описує себе як команду, що створює технологічне ядро iGaming-продуктів, із in-house development stack, real-time architecture і modular backend. Пов’яжіть це з інтересом до product ownership та операційно чутливої архітектури. Вакансія прямо охоплює PSP integrations, reconciliation, secure payouts і стан платежу; продемонструйте, що розумієте ціну помилки, але не приписуйте собі досвід конкретних схем.

Компанія заявляє remote work, гнучкий графік, низьку формалізацію та внутрішнє зростання лідерів. Сформулюйте, як можете бути hands-on інженером, який документує рішення, робить системи зрозумілими для колег і ділиться досвідом. TODO_CONFIRM у рекрутера: склад команди, продуктова юрисдикція, on-call, compliance ownership, обсяги платежів і використовувані PSP.

## Preparation Plan

1. Зафіксуйте односторінкові відповіді на HR TODO_CONFIRM та chronology.
2. Проведіть 45-хвилинний design rehearsal: adapter layer, webhook, state transitions, reconciliation і incident response.
3. Повторіть MySQL transactions, locks, isolation, EXPLAIN та deadlock handling; окремо вивчіть Redis patterns, не видаючи теорію за досвід.
4. Підготуйте три історії STAR: reliability у Simple.life, observability/event delivery у CRURATED, performance work в airSlate.
5. Відрепетируйте двохвилинне пояснення старих payment integrations із чесним позначенням актуальності знань.

## Questions to Ask

- Які PSP вже інтегровані, і як часто команда підключає нові?
- Який lifecycle платежу та де проходять межі відповідальності команди?
- Як організовано reconciliation, incident response і on-call для платежів?
- Які Redis, queue та observability practices уже працюють у production?
- Які compliance, security або jurisdiction constraints є частиною цієї ролі?
- За якими результатами ви оціните успіх людини в перші 90 днів?
