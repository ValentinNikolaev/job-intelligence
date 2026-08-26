## Vacancy Summary

Firetics шукає Backend Developer для платежів у віддаленому iGaming-продукті. Ядро ролі — не звичайна API-розробка, а безпечна експлуатація payment-модуля: інтеграції з провайдерами, уніфікований adapter layer, callbacks/webhooks, повторні спроби, дедуплікація, консистентні стани платежів, reconciliation та виплати. Обов’язкові технологічні сигнали: PHP, Laravel або Symfony, MySQL під навантаженням, Redis та REST/JSON-інтеграції. Це роль із суттєвою відповідальністю за коректність фінансових операцій, навіть якщо назва не містить senior.

## Company Research

За [вакансією DOU](https://jobs.dou.ua/companies/firetics/vacancies/361314/) Firetics прямо описує платіжний контур і очікувані failure-сценарії. На [сайті Firetics](https://firetics.com/) компанія називає себе розробником технологічного ядра iGaming-продуктів; [сторінка кар’єри](https://firetics.com/career) підтверджує remote-формат, гнучкий графік і внутрішнє зростання. Практична мотивація кандидата може будуватися на відповідальності за надійні інтеграції та продуктову архітектуру, а не на непідтвердженому досвіді в iGaming чи сучасних платежах.

Публічні матеріали не уточнюють провайдерів, обсяги транзакцій, юрисдикції або on-call режим. Не варто приписувати компанії PCI DSS-відповідальність, конкретну мікросервісну архітектуру чи власну платіжну ліцензію. Натомість на інтерв’ю доречно з’ясувати, хто володіє reconciliation, як організовано incident response і якими обмеженнями регулюється payout flow.

## Initial Resume Audit

Поточне CV добре позиціонує кандидата як hands-on PHP/Laravel інженера з інтеграціями та reliability-практикою. Найсильніші докази: Laravel/Symfony і MySQL performance work в airSlate, PHP/event-driven infrastructure та webhook routing у CRURATED, unified API orchestration, retries, fallback logic і monitoring у Simple.life. Таке формулювання доречне: «Будував resilient delivery pipelines з retries, fallback logic і monitoring». Воно перекладається на релевантність до payment events, але не називає ці системи платіжними.

Історичні інтеграції Stripe, PayPal, Skrill і банківських систем можна лишити у Summary/Skills як ранній payment background. Їх не слід подавати як недавнє ownership платіжного gateway. CV також правильно не додає Redis, PHP 8.x, reconciliation, idempotency або state machines без доказів.

## Strict Hiring Manager Review

Найімовірніше, hiring manager побачить сильного senior backend кандидата для API-інтеграцій, MySQL-оптимізації та операційної надійності. Приклад сильного мосту: «У CRURATED реалізував webhook routing, automatic retries та observability з delivery reliability понад 99.9%». Це конкретніше за загальну заяву про reliability і не перетворює досвід на платежі.

Водночас для цієї ролі бракує підтвердження ключових payment-обов’язків: автентифікації callback, idempotency keys, конкуренції за стан платежу, settlement/reconciliation і chargeback-процесів. У менеджера також виникне питання, чи не буде роль Backend Developer занадто вузькою після техлідерських позицій. Відповідь має бути про бажання власноруч будувати критичний backend-контур і менторити без вимоги менеджерського титулу.

## Red Flags

- Redis є прямою вимогою, але в доказах кандидата його немає; RabbitMQ не є заміною Redis для locks або rate limiting.
- PHP-досвід підтверджений, проте версію PHP 8.x потрібно чесно підтвердити до співбесіди.
- Payment provider integrations документовані переважно у 2014–2015 роках; потрібна точна розповідь про власну відповідальність, типи помилок і поточність знань.
- Не підтверджені GitHub flow, MySQL locking/isolation, signature validation, reconciliation, антифрод, Docker/Nginx/Node.js.
- Потрібно окремо уточнити право працювати з Італії/EU, notice period, старт, компенсацію та комфорт щодо iGaming.

## ATS Keyword Analysis

Безпечно зберегти або підсилити: PHP, Laravel, Symfony, MySQL, REST APIs, API integrations, payment-provider integrations, webhooks, RabbitMQ, queues, event-driven systems, retries, monitoring, logging, AWS, Kubernetes, GitHub Actions, CI/CD, performance optimisation, production reliability, remote/CET. У тексті досвіду варто повторити «API orchestration», «webhook routing» та «delivery guarantees» там, де вони вже доказані.

Не можна додавати як досвід: Redis, PHP 8.x, idempotency, deduplication, payment state machine, reconciliation, chargebacks, signature validation, transaction isolation, Docker, Nginx чи Node.js. Їх варто підготувати як питання до роботодавця або як теми для чесної технічної розмови.

## Major CV Changes

1. У заголовку залишити «Backend Developer — PHP, Laravel & Payment Integrations», не «Payments Expert».
2. У Summary зберегти ранні payment-provider і bank-payment integrations із застереженням про їхню давність; не виносити їх у сучасний досвід.
3. У CRURATED підкреслити versioned event schema, downstream webhook/S3 routing, retries і observability; це найкращий доказ дисципліни доставки.
4. У airSlate зробити видимими Laravel/Symfony, MySQL bottleneck analysis і 30% скорочення API response time.
5. Не змінювати Experience за межами останніх 10 років і не додавати непідтверджені платежі до Simple.life.

## Final Quality Gate

У CV немає вигаданих доменних або стекових тверджень; overlap CRURATED із Simple.life прозоро позначений як part-time consulting. Перед відправкою слід перевірити п’ять фактів: PHP 8.x, практику Redis, точний обсяг Stripe/PayPal/Skrill або bank-payment work, право на роботу/старт і ставлення до iGaming. Фінальні оцінки: технічна база — 4/5; API/reliability — 5/5; PHP/Laravel/MySQL — 4/5; платежі — 3/5; критичні вимоги та логістика — 2/5.

## Recommendation

Apply With Reservations
