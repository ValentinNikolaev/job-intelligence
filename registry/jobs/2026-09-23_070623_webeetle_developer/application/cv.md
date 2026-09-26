# Valentin Nikolaev
Backend Developer | PHP, Go and distributed services

Rome, Italy | valeinikolaev@gmail.com | +39 351 370 1194  
LinkedIn: https://linkedin.com/in/valentinnikolaev | GitHub: https://github.com/ValentinNikolaev

## Summary

Backend developer with 15+ years of production experience across PHP and Go. I have owned event analytics, support automation and database reliability work, from versioned event contracts to services operating through seasonal traffic peaks. Recent work includes a PHP consulting engagement with production responsibility for event delivery and a Go support platform serving at least 20,000 tickets in an ordinary month. I combine hands-on service design with production diagnosis and team-level delivery work.

## Skills

Languages and frameworks: PHP, Go, Laravel, Symfony.  
Data and integration: MySQL, PostgreSQL, REST APIs, event-driven systems, EventBridge, RabbitMQ.  
Delivery and operations: AWS, Kubernetes, CI/CD, monitoring, production troubleshooting, microservices.

## Experience

### Simple App (Simple.life) — Software Developer
November 2023 – 2026

- Architected and released an outbound-calling platform on Amazon Connect, using federated agent access and masked customer numbers to meet security requirements without creating individual AWS accounts.
- Built a Go helpdesk gateway with a vendor-neutral event model and Intercom and Zendesk adapters, enabling the company's first B2B demonstration of its support AI product.
- Consolidated three Snowflake-to-Intercom jobs into one two-phase engine, reducing implementation from 1,670 to 800 lines and removing a 100-item daily cap without an API change.
- Eliminated fatal outcomes during degraded Intercom searches by introducing partial-success handling and sharded cursor scans after diagnosing runs that previously failed up to 14 times a day.
- Owned the Go support automation platform connecting Intercom, Zendesk and internal services, including its operation at 20,000+ tickets in an ordinary month and up to three times that volume in the US peak season.
- Designed an A/B comparison of in-house ticket categorization and Intercom Fin, then migrated categorization to Fin while retaining the earlier model as fallback.

Technologies: Go, PHP, PostgreSQL, AWS, Amazon Connect, SQS, Intercom API, Zendesk API, REST APIs, OpenAI tooling.

### CRURATED — PHP Software Developer (concurrent part-time consulting engagement)
August 2024 – January 2026

- Led the production event analytics and DataLake system, including modular stream design that reduced new stream setup from several days to under four hours.
- Defined versioned event contracts to keep product metrics consistent across teams and support new event types.
- Built routing to downstream destinations with backpressure handling; event delivery reliability in this system exceeded 99.9% under my technical ownership.
- Took full technical ownership of production authentication, account linking and request/response logging for the Crutrade integration.

Technologies: PHP, AWS EventBridge, event-driven architecture, REST APIs.

### airSlate — Software Developer / Programming Team Lead
February 2021 – August 2023

- Reduced peak load on the main database by removing bottlenecks and redistributing work, improving stability during high-traffic periods.
- Built a Laravel/Symfony logger package aligned with the product's interservice communication standard.
- Delivered production fixes after diagnosing incidents through logs, monitoring and SRE dashboards.
- Coordinated epic decomposition, technical health checks and onboarding in the development team.

Technologies: PHP, Laravel, Symfony, MySQL, monitoring.

## Education

MSc in Computer Science, National Technical University, Kharkiv, Ukraine (2003–2008).

## Languages

Ukrainian (native), English (upper-intermediate), Italian (learning).
