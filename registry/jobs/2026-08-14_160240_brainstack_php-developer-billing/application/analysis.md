## Vacancy Summary

Brainstack шукає PHP Developer до Billing-команди для розробки, рефакторингу й підтримки backend-продукту, проєктування архітектури, тестування, документації та виправлення дефектів. Явні вимоги: 3+ роки PHP 8.x і PHP-фреймворків, Symfony 7+, MySQL, RabbitMQ, Redis, DDD, мікросервіси й моноліти, сторонні API, unit/functional tests, статичний аналіз, OOP/патерни/SOLID/KISS/DRY, Docker-конфігурація, створення сервісу з нуля та платіжні інтеграції. Kubernetes і coding agents є плюсом; щодо AI обов’язкова відкритість і людська перевірка результатів.

CV сильно відповідає PHP, Laravel/Symfony, MySQL-оптимізації, RabbitMQ, REST/API-інтеграціям, мікросервісам, Kubernetes, архітектурі та greenfield-доставці. Платіжні шлюзи підтверджені лише раннім досвідом. Не підтверджені PHP 8, Redis, Symfony 7, DDD, моноліти, Docker-конфігурація, functional tests, статичні аналізатори, названі практики дизайну та coding-agent usage. Імовірні очікування: безпечна обробка платежів, ідемпотентність, reconciliation, надійні черги та прагматична модернізація змішаного legacy/greenfield середовища.

## Company Research

- **Fact:** Brainstack називає себе українською мультипродуктовою компанією з продуктами у Parental Control, Wellness та AI, власним R&D і мільйонною глобальною аудиторією. Офіційний сайт також називає PHP/Symfony серед backend-технологій. [Brainstack](https://www.brainstack.team/)
- **Fact:** вакансія належить Billing-команді; робота охоплює backend, архітектуру, тести, документацію та підтримку. AI-результати мають перевірятися розробником. [Вакансія](https://jobs.dou.ua/companies/brainstack/vacancies/369880/)
- **Fact — лише контекст:** окрема вакансія Billing Manager у Wellness описує billing як критичну для LTV, approval rate і retention функцію глобального B2C SaaS. Вона **не доводить**, що PHP-вакансія належить Wellness-продукту. [Billing Manager — Wellness](https://brainstack.recruitee.com/o/billing-manager-wellness)
- **Inference:** мотивація може спиратися на поєднання PHP/Symfony, платіжної надійності, інтеграцій і можливості запускати нові сервіси з вимірюваним продуктовим впливом.
- **Unknown:** продукт, команда, провайдери, транзакційний масштаб, on-call, юридична особа, компенсація та міжнародні remote/FOP-умови.

## Initial Resume Audit

| Вимір | Бал | Сильна сторона | Слабкість | Фактичний rewrite |
|---|---:|---|---|---|
| Impact | 9/10 | Є 10x throughput, 50 млн листів/місяць і 10x піки. | Недавнього billing-результату немає. | “Increased DataLake throughput by more than 10x using queue-based routing and EventBridge.” |
| Keyword relevance | 8/10 | PHP, Symfony, MySQL, RabbitMQ, API та microservices видимі. | Частина hard-screen термінів відсутня. | “Developed a product-wide Laravel/Symfony logging package aligned with interservice communication standards.” |
| Readability | 9/10 | Прості секції, короткі bullets, role-specific Technologies. | Шість ролей роблять CV щільним. | “Led five backend engineers developing a high-volume transactional email service.” |
| Summary effectiveness | 9/10 | Одразу поєднує PHP, Billing-релевантність і масштаб. | Остання основна роль була Go-focused. | “Earlier project experience includes bank payment systems and Stripe, PayPal, and Skrill.” |
| ATS compatibility | 8/10 | Стандартні headings і точні підтримані keywords. | Redis/Symfony 7/DDD можуть бути автоматичними фільтрами. | Зберегти “PHP; Laravel; Symfony; MySQL; RabbitMQ; REST APIs” без keyword stuffing. |

**Baseline: 8.6/10.** Найкраще покращення — вакансійне позиціонування без вигаданих технологій.

## Strict Hiring Manager Review

**Три сильні сторони:**

1. MySQL/query optimization, RabbitMQ і high-volume PDFfiller демонструють production-масштаб.
2. airSlate підтверджує Laravel/Symfony, Kubernetes, CI/CD та delivery від планування до production.
3. Hyprr і CRURATED дають архітектуру з нуля, мікросервіси, черги та вимірювані результати.

**Три матеріальні слабкості:**

1. Не підтверджені PHP 8, Symfony 7, Redis і Docker; це важливо через прямі stack screens. Безпечний rewrite: “PHP, Laravel, Symfony, MySQL, RabbitMQ, Kubernetes.”
2. DDD, named patterns, functional tests і static analysis не мають доказів; це послаблює quality-tooling fit. Безпечний rewrite: “system design, modular backend systems, production reliability.”
3. Payment-gateway досвід старий, тому не доводить сучасне Billing ownership. Безпечний rewrite: “Earlier project experience includes payment integrations.”

## Red Flags

- **PDFfiller dates:** один запис завершується в листопаді 2019, інший — у грудні 2018; CV використовує грудень 2018, щоб не створювати overlap із Sixt. Потрібне підтвердження.
- **CRURATED overlap:** коректно позначений як part-time consulting паралельно із Simple.life; формулювання не можна прибирати.
- **FOP/Italy:** кандидат у Римі, а вакансія передбачає ФОП і не обіцяє remote abroad. Треба з’ясувати міжнародну юрисдикцію, український ФОП або альтернативний контракт, години й податкову сумісність.
- **Billing recency:** прямі Stripe/PayPal/Skrill і bank-payment інтеграції старші за десятирічне Experience-вікно.
- **Recent stack:** Simple.life — Go; CRURATED підтримує недавню PHP-безперервність, але recruiter може перевіряти мотивацію повернення до PHP.

## ATS Keyword Analysis

Топ-15 підтриманих термінів: **PHP, Laravel, Symfony, MySQL, RabbitMQ, REST APIs, third-party integrations, microservices, Kubernetes, event-driven systems, system design, performance optimization, AWS, payment gateway integrations, production reliability**.

Повністю відсутні й заборонені до додавання як досвід: **PHP 8, Redis, Symfony 7, DDD, monolith, functional tests, static analyzers, Docker configuration, SOLID/KISS/DRY, named Design Patterns, coding agents, agent contexts**. Недостатньо представлені, але підтримані: Symfony logger package, MySQL optimization, earlier payment integrations, unit-test coverage та production debugging; їх слід описувати лише в підтверджених межах.

## Major CV Changes

- **Before → After:** generic Backend Engineer → підтриманий vacancy-aligned `PHP Developer (Billing)`.
- **Before → After:** payment background без контексту → чітко позначений як earlier experience.
- **Before → After:** глобальний Symfony keyword → конкретний Laravel/Symfony logger package в airSlate.
- **Before → After:** неоднозначний overlap → CRURATED явно part-time і concurrent.
- **Before → After:** загальні infrastructure skills → технології прив’язані до роботодавців; Kubernetes не підміняє Docker.

## Final Quality Gate

- Role fit: **8/10**
- Recruiter screening potential: **7/10**
- Hiring-manager appeal: **8/10**
- ATS compatibility: **8/10**
- Credibility: **9/10**

Claims простежувані, chronology прозора, billing-релевантність не перебільшена. До подачі варто підтвердити FOP/Italy, PHP/Symfony versions, Redis/Docker, quality tooling, coding-agent practice і PDFfiller dates.

## Recommendation

**Apply With Reservations.** Сильний PHP/backend, MySQL, RabbitMQ, Symfony, API, масштаб і ранні payment integrations виправдовують подачу. Водночас FOP/Italy може бути hard blocker, а кілька прямих stack requirements не підтверджені; їх слід чесно винести в розмову, а не компенсувати суміжними claims.
