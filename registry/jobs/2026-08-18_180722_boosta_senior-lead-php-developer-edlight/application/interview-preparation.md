# Підготовка до співбесіди — Boosta / Edlight Senior/Lead PHP Developer

## Recruiter / HR Screening

Підготуйте короткі, конкретні відповіді:

- **Senior чи Lead.** Поясніть бажаний баланс hands-on розробки, архітектури й менеджменту двох інженерів. Підтвердіть комфорт із player-coach роллю, а не лише управлінською позицією. Окремо поясніть перехід від останнього title `Software Developer` до Senior/Lead через попереднє керівництво командами та недавній PHP-консалтинг.
- **Мотивація.** Пов’яжіть інтерес із end-to-end backend ownership, AI-продуктами, глобальним digital-бізнесом, технічним наймом і можливістю впливати від discovery до scaling. Не стверджуйте використання продуктів Edlight або знання нерозкритого продукту.
- **Локація та графік.** Ви перебуваєте в Римі. Підтвердіть готовність до старту між 08:00–11:00 за Києвом і командних годин; уточніть сезонну різницю часу, дозволені країни, юридичну модель, валюту виплат та можливі поїздки.
- **Компенсація й доступність.** Підготуйте діапазон, gross/net, валюту, notice period і найранішу дату старту. Спочатку уточніть контракт, probation, benefits за межами України та on-call.
- **Мови.** Українська — рідна, англійська — Upper-intermediate. Будьте готові пояснити архітектурне рішення англійською.
- **Рекомендації.** Процес включає reference collection. Визначте 2–3 релевантних контакти, отримайте їхню згоду та узгодьте спільні проєкти, titles і дати.
- **Прогалини.** PHP 8/Symfony 6 duration, SOLID/KISS/DRY, explicit refactoring, daily coding agents, GraphQL/Messenger, Redis/Memcached, WebSocket/Centrifugo, Python/FastAPI, формальні 1:1/development plans і пряме Frontend/QA leadership не підтверджені CV.

## Culture Fit / Behavioral Interview

Побудуйте правдиві STAR-каркаси без вигаданих деталей:

1. **End-to-end ownership:** Hyprr — roadmap із CTO, архітектура та доставка від прототипу до closed beta.
2. **Управління командою:** п’ять інженерів у PDFfiller або десять у Hyprr; підготуйте реальні практики delegation, feedback і coaching.
3. **Планування доставки:** airSlate — evaluation, planning, distribution і відповідальність від draft до production.
4. **Технічний стандарт:** airSlate Laravel/Symfony logger або PDFfiller messaging architecture. Для code review потрібен конкретний нещодавній приклад, якщо він справді був.
5. **Якість проти швидкості:** CRURATED modular event schemas або airSlate performance work. Назвіть фактичний trade-off; CV не доводить формального technical-debt ownership.
6. **Крос-функціональна взаємодія:** Simple.life із Support Ops, Product та AI або Hyprr із business/technical stakeholders. Не перетворюйте це на Frontend/QA leadership.
7. **Найм:** 20+ технічних інтерв’ю в airSlate; поясніть rubric, calibration, signals і власну роль у рішенні.
8. **Помилка чи перегляд рішення:** підготуйте справжню історію з наслідками й lessons learned; CV конкретного провалу не містить.

## Technical Interview

- **High — Leadership/delivery.** Будьте готові декомпозувати initiative, оцінити ризики й залежності, розподілити роботу двом backend developers, визначити acceptance criteria, провести review і спланувати release/rollback. Формальні 1:1 та development plans описуйте лише після особистого підтвердження.
- **High — PHP/Symfony.** Повторіть dependency injection, service container, lifecycle, configuration, modules, events, error handling, testing, upgrades і performance. Розберіть airSlate logger package. PHP 8, Symfony 6 і три роки саме з цією версією — прогалини, а не автоматичний висновок із дат.
- **High — MySQL.** Практикуйте `EXPLAIN`, indexes, cardinality, join order, pagination, isolation, locks, migrations і вимірювання до/після. Результати airSlate підтверджені, але конкретні index/execution-plan досягнення — ні.
- **High — Architecture/API.** Спроєктуйте backend для AI expert service: boundaries, data ownership, REST contracts, async processing, failures, observability, compatibility, scaling і rollout. Пояснюйте trade-offs через реальні системи Simple.life, CRURATED або Hyprr.
- **High — Quality/debt.** Підготуйте risk-based refactoring plan із characterization tests, incremental rollout, telemetry та rollback як запропонований підхід. Не видавайте SOLID/KISS/DRY або explicit refactoring за зафіксований досвід.
- **High — AI tools.** LLM product work не доводить daily coding-agent use. Якщо прямий досвід відсутній, скажіть чесно. Обговоріть small diffs, permissions, context control, tests, human review і secrets лише як workflow, який можете застосувати.
- **Medium — Cross-stack integration.** Продумайте API compatibility, fixtures, test environments, release ordering і contract changes для Frontend/QA. Пряме керівництво цими напрямами не підтверджене.
- **Medium — RabbitMQ/AWS.** Повторіть routing, acknowledgements, retries, dead letters, idempotency та monitoring; окремо CRURATED EventBridge-to-S3/Webhook routing, backpressure і versioned schemas. Symfony Messenger не заявляйте.
- **Low — Bonus stack.** GraphQL/Overblog, Redis/Memcached, WebSocket/Centrifugo, Python/FastAPI не підтверджені. Відповідайте лише на рівні реальних знань або плану навчання.

## CV Deep-Dive Questions

Підготуйте захист цифр: Simple.life — 30% автоматизованих/відхилених tickets; CRURATED — понад 10x throughput і stream менш ніж за чотири години; Hyprr — beta менш ніж за шість місяців і десять developers; PDFfiller — приблизно 50 млн email щомісяця, піки понад 10x і п’ять engineers; airSlate — 20+ interviews. Для кожної поясніть baseline, measurement source, власний внесок, constraints, рішення та verification. Якщо цифру неможливо відновити, опишіть результат без псевдоточності.

Очікуйте уточнень щодо Go-focused Simple.life, паралельного part-time CRURATED, Symfony recency, ролі в hiring decisions, реального people-management cadence та конкретного code-review прикладу. Не переносіть технології між роботодавцями.

## Company-Specific Preparation

Перевірені факти: Boosta розвиває 15+ digital-бізнесів, а її команда працює з 44 країн. Edlight входить до Boosta, створює AI-продукти й expert services для студентів і professionals, має понад 500 тисяч unique customers і 90+ experts, працює від discovery до scaling та фокусується на Tier-1 markets.

Конкретний продукт, AI-функціональність, revenue model, архітектура, traffic, team maturity і technical-debt scale невідомі. Не заявляйте product use. Мотивацію будуйте навколо hands-on PHP architecture, people leadership, повного product lifecycle та відповідального AI workflow.

## Preparation Plan

- **До pre-screen:** Senior/Lead calibration, мотивація, Rome/remote, Kyiv hours, compensation, notice, language, references і gap statement.
- **До Tech:** один system-design, PHP/Symfony, MySQL exercise, architecture/API, RabbitMQ/AWS, quality/debt scenario; перевірка CV-метрик.
- **До final:** три STAR-історії — delivery ownership, people leadership, cross-functional decision — з trade-offs і lessons.
- **До references:** згода контактів і точна хронологія Simple.life/CRURATED.

## Questions to Ask

1. Який продукт і backend boundaries отримає ця роль?
2. Як калібруються Senior і Lead та який hands-on/management split?
3. Який досвід і потреби розвитку мають два backend developers?
4. Хто ухвалює architecture/product trade-offs і як вимірюється результат?
5. Які масштаби technical debt, release cadence, SLO та on-call?
6. Як організовані API contracts і координація Backend, Frontend та QA?
7. Наскільки PHP 8/Symfony 6 duration і bonus stack є жорсткими screens?
8. Які coding agents дозволені та які data/review controls діють?
9. Чи може компанія контрактувати спеціаліста з Італії та які core Kyiv hours?
10. Які результати визначатимуть успіх через три й шість місяців?
