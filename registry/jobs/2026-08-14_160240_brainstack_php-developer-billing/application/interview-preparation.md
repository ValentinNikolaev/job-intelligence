# Підготовка до співбесіди — Brainstack PHP Developer (Billing)

## Recruiter / HR Screening

Підготуйте короткі, конкретні відповіді на такі блоки:

- **Мотивація та назва ролі.** Поясніть інтерес до hands-on PHP-розробки в Billing-команді через сильний PHP-бекграунд, недавній паралельний PHP-консалтинг у CRURATED, високонавантажені транзакційні системи та давніший досвід платіжних інтеграцій. Окремо підтвердьте, що назва `PHP Developer`, без Lead/Senior, відповідає очікуванням щодо відповідальності й компенсації.
- **Локація та формат.** Ви перебуваєте в Римі, а вакансія вказує Київ/remote і оформлення через український ФОП. До інтерв’ю з’ясуйте, чи можливе міжнародне залучення з Італії, чи потрібен чинний ФОП, чи існує інша контрактна модель, які часові перетини та вимоги щодо відвідування Києва.
- **Компенсація.** Підготуйте діапазон, валюту та gross/net. Уточніть модель договору, податки, випробувальний термін і benefits.
- **Доступність.** Назвіть точний notice period і найранішу дату старту; у наданих матеріалах цього немає.
- **Мови.** Українська — рідна, англійська — Upper-intermediate. Будьте готові коротко пояснити архітектуру англійською.
- **Reference Check.** Заздалегідь визначте 2–3 релевантних контакти, отримайте їхню згоду й узгодьте назви ролей, дати та спільний контекст. Не передавайте контакти без дозволу.
- **Прогалини.** PHP 8, Redis, Docker-конфігурація, Symfony 7, DDD, моноліти, functional tests, static analysis, конкретні patterns/principles та coding agents не підтверджені CV. Розділяйте реальний досвід, теоретичні знання й план адаптації.

## Culture Fit / Behavioral Interview

Для кожної відповіді підготуйте фактичний STAR-каркас, не вигадуючи деталей:

1. **Як ви приймали стратегічне технічне рішення?** Hyprr: roadmap і архітектура разом із CTO під час переходу від прототипу до closed beta.
2. **Як ви покращили продуктивність?** airSlate: зниження пікового навантаження на БД та пошук API/query bottlenecks.
3. **Як балансували швидкість і надійність?** CRURATED: модульна схема подій, routing, backpressure і гарантії доставки.
4. **Як діяли під піковим навантаженням?** PDFfiller: транзакційні email-сервіси, близько 50 млн повідомлень на місяць і понад 10x traffic peaks.
5. **Як будували новий продукт або сервіс?** Hyprr — найчіткіша історія від прототипу до beta; CRURATED — архітектура нової analytics infrastructure.
6. **Як наставляли людей?** Команда з п’яти інженерів у PDFfiller, десять розробників у Hyprr або 20+ технічних інтерв’ю в airSlate. Оберіть один приклад із реальним результатом.
7. **Як взаємодіяли з нетехнічними командами?** Simple.life із Support Ops/Product/AI або Hyprr із business stakeholders.
8. **Розкажіть про помилку чи перегляд рішення.** Потрібен справжній приклад; CV підтверджує ownership, але не містить конкретної невдалої гіпотези.

## Technical Interview

- **High — PHP/Symfony.** Повторіть dependency injection, service container, lifecycle request, middleware/events, error handling, backward compatibility, refactoring і performance. Детально розберіть airSlate logger package. PHP 8 і Symfony 7 не підтверджені: називайте лише версії та features, які можете захистити фактичним досвідом.
- **High — MySQL.** Тренуйте `EXPLAIN`, індекси, joins, pagination, transaction isolation, locks/deadlocks, migrations, replicas та вимірювання до/після. Опирайтеся на airSlate database/query optimization, не вигадуючи конкретний SQL.
- **High — RabbitMQ.** Підготуйте exchanges, routing keys, acknowledgements, prefetch, retries, dead-letter queues, idempotent consumers, ordering, duplicate handling та observability. Redis — окрема непідтверджена прогалина, а не синонім черг.
- **High — Billing/payments.** Практикуйте state machine платежу, idempotency keys, webhook signatures, retries, reconciliation, refunds, chargebacks, audit trail і PCI-sensitive boundaries. Stripe/PayPal/Skrill та bank integrations — реальний, але давніший досвід; не подавайте його як недавнє володіння billing-платформою.
- **High — Tests/quality.** Складіть стратегію unit, integration, contract і functional tests для payment flow, включно з gateway failures і duplicate webhooks. Недавні functional tests, static analyzers та конкретні tools у CV не підтверджені.
- **Medium — Architecture.** Спроєктуйте Billing service із API, persistence, gateway adapters та asynchronous handlers. Поясніть транзакційні межі й evolution. DDD, конкретні Design Patterns, SOLID/KISS/DRY та monolith experience не заявляйте без особистого підтвердження.
- **Medium — Infrastructure.** Kubernetes, Helm, GitHub Actions і ArgoCD підтверджені airSlate. Підготуйте probes, resources, rollout/rollback, secrets і monitoring. Docker configuration у CV відсутня.
- **Medium — AI workflow.** Досвід AI/LLM-продуктів не доводить coding-agent use. Якщо прямого досвіду немає, скажіть чесно; обговоріть human verification, тести, small diffs, доступи й захист секретів лише як запропонований workflow.
- **Low — Product-specific domain.** Ознайомтеся з метриками payment success, approval rate, retention і revenue impact, але не припускайте конкретний продукт чи архітектуру Brainstack.

## CV Deep-Dive Questions

Підготуйте захист ключових цифр: CRURATED — понад 10x throughput і запуск stream менш ніж за чотири години; Hyprr — beta менш ніж за шість місяців і десять розробників; PDFfiller — приблизно 50 млн email на місяць, піки понад 10x і п’ять інженерів; airSlate — понад 20 інтерв’ю. Для кожної поясніть baseline, джерело вимірювання, власний внесок, обмеження та перевірку. Якщо точність неможливо відновити, опишіть результат без псевдоточності.

Очікуйте питань про PHP-актуальність після Go-focused Simple.life, паралельний part-time CRURATED, точний внесок у Symfony logger і Kubernetes migration, а також давність payment-gateway integrations. Не переносіть технології між роботодавцями.

## Company-Specific Preparation

Підтверджено лише таке: Brainstack — українська multi-product IT-компанія з глобальними кросплатформними сервісами, внутрішнім R&D та PHP/Symfony серед backend technologies. Вакансія належить Billing-команді й охоплює development, refactoring, support, architecture, tests, documentation та bug fixing. Команда щодня використовує AI-інструменти, але очікує людської верифікації.

Окрема вакансія Billing Manager описує payment infrastructure у Wellness, але не доводить, що ця PHP-позиція працює над тим самим продуктом. Не припускайте Wellness, конкретні масштаби транзакцій, провайдерів, team size чи on-call.

## Preparation Plan

- **До HR:** мотивація, title fit, Rome/remote/FOP, salary range, notice period, мови, references і чесний список прогалин.
- **До Tech:** один Billing system-design exercise; PHP/Symfony, MySQL, RabbitMQ, payment failure modes, testing і Kubernetes; перевірка всіх CV-метрик.
- **До Reference Check:** згода контактів, узгоджена хронологія Simple.life/CRURATED і релевантні спільні результати.
- **До фіналу:** три STAR-історії — architecture, production reliability, mentoring — із trade-offs та lessons learned.

## Questions to Ask

1. Який саме продукт і які payment flows обслуговує Billing-команда?
2. Які провайдери, валюти, ринки та compliance boundaries входять у scope?
3. Які поточні масштаби, SLO та найболючіші failure modes?
4. Наскільки Symfony 7, Redis, DDD і Docker є жорсткими вимогами на старті?
5. Як розподілена система між монолітом і мікросервісами та що планують змінювати?
6. Які test, static-analysis і deployment gates обов’язкові?
7. Як команда використовує coding agents і перевіряє згенеровані зміни?
8. Чи можливе оформлення спеціаліста з Італії, якщо український ФОП непридатний?
9. Які результати визначатимуть успіх через три та шість місяців?
