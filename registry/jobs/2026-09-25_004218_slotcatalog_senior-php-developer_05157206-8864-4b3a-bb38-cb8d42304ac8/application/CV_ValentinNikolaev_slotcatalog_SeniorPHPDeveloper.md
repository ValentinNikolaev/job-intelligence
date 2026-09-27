# Valentin Nikolaev
Senior PHP Developer | Event-Driven Systems and Production Delivery

Rome, Italy | valeinikolaev@gmail.com | +39 351 370 1194  
LinkedIn: https://linkedin.com/in/valentinnikolaev | GitHub: https://github.com/ValentinNikolaev

## Summary

Senior backend developer with 15+ years across PHP and Go systems. I build privacy-sensitive production platforms, event-driven data services and integrations, including a health-domain Amazon Connect platform designed around PII/PHI protection. My work combines deliberate API and schema design with operational results: lawful calling controls, reliable event delivery, faster onboarding of new streams and database stability under load.

## Skills

**Languages and frameworks:** PHP, Laravel, Symfony, Go.  
**Data and integration:** MySQL, PostgreSQL, REST APIs, AWS EventBridge, queues, event-driven architecture, versioned schemas.  
**Delivery and operations:** AWS, Kubernetes, CI/CD, monitoring, production troubleshooting, Amazon Connect.

## Experience

### Simple.life / Simple App — Software Developer
November 2023 – 2026

- Designed the health-domain Amazon Connect backend around PII/PHI protection: phone numbers remained server-side and masked in browser and logs, with transient Connect attributes and TTL purging; formal security and call-recording compliance reviews cleared the production release.
- Made lawful-calling decisions backend-owned through timezone windows, holidays, do-not-call enforcement and opt-out withdrawal; zero Amazon Connect retries ensured that retries could not bypass those controls.
- Established least-privilege agent access with opaque Entra identities, role federation and lazy Connect-user lifecycle management, avoiding per-agent AWS accounts and a SAML application.
- Built a multi-tenant Go helpdesk gateway with vendor-neutral events, Intercom and Zendesk adapters, tenant ingestion and SQS queues, enabling the first B2B demonstration of the support-AI product.
- Made ticket processing resilient during Intercom API degradation through partial-success handling and sharded cursor searches, retaining visibility of incomplete work instead of failing the full run.
- Built self-service GDPR export workflows across seven data sources, giving administrators request creation, status tracking and review in one place.

**Technologies:** Go, PHP, PostgreSQL, AWS, Amazon Connect, SQS, Kubernetes, Intercom API, Zendesk API

### CRURATED — PHP Software Developer, concurrent part-time subcontract
August 2024 – January 2026

- Architected a production event analytics pipeline with queues and AWS EventBridge; DataLake throughput grew by more than tenfold under technical ownership.
- Reduced onboarding of a new analytics stream from several days to under four hours through modular stream design.
- Maintained event delivery reliability above 99.9% with fault-tolerant routing, retries and observability.
- Designed versioned event schemas with parallel publication in production, letting consumers move between schemas while new events continued to arrive.
- Delivered the production Crutrade integration for authentication and OTP, account linking, collection exchange, purchase-ownership verification and request/response logging.

**Technologies:** PHP, Laravel, AWS EventBridge, queues, REST APIs, event-driven architecture

### airSlate — Senior Software Developer
February 2021 – August 2023

- Reduced peak load on the main database by isolating bottlenecks and redistributing workload, improving stability during high-traffic periods.
- Built a Laravel/Symfony logger package used across services and aligned it with the interservice communication standard.

**Technologies:** PHP, Laravel, Symfony, MySQL, monitoring

## Education

MSc in Computer Science, National Technical University, Kharkiv, Ukraine (2003–2008)

## Languages

Ukrainian (native), English (upper-intermediate)
