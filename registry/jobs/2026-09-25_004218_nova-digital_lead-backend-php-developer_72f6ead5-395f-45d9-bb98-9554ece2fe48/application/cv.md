# Valentin Nikolaev
Lead Backend PHP Developer | Product Architecture and Event Platforms

Rome, Italy | valeinikolaev@gmail.com | +39 351 370 1194  
LinkedIn: https://linkedin.com/in/valentinnikolaev | GitHub: https://github.com/ValentinNikolaev

## Summary

Lead backend developer with 15+ years across PHP and Go production systems. I own architecture for privacy-sensitive integrations, event-driven platforms and operational tooling. Recent work includes a PII/PHI-protected health-domain calling platform, vendor-neutral Go integration services and support automation. I combine system design, delivery ownership and production controls with event analytics and PHP platform work.

## Skills

**Languages and frameworks:** PHP, Laravel, Symfony, Go.  
**Architecture and data:** REST APIs, OpenAPI, event-driven systems, AWS EventBridge, queues, versioned event schemas, MySQL, PostgreSQL.  
**Operations:** AWS, Kubernetes, CI/CD, monitoring, production troubleshooting, SQS.

## Experience

### Simple.life / Simple App — Software Developer
November 2023 – 2026

- Owned the architecture and backend of a health-domain calling platform where PII/PHI protection led the design: customer numbers stayed server-side, masked in UI and logs, and short-lived in Amazon Connect; security and call-recording compliance reviews approved production release.
- Designed backend-enforced calling policy for timezone windows, holidays, do-not-call controls and opt-outs, with zero Amazon Connect retries so the platform could not circumvent customer-contact restrictions.
- Designed federated agent access around opaque Entra identities and least privilege, separating operational diagnostics from call access while removing per-agent AWS accounts and a SAML application.
- Built the multi-tenant Go helpdesk gateway that isolated vendor SDKs behind a shared event model and enabled the first B2B support-AI demonstration.
- Built the evaluation pipeline for the production support agent, combining ticket conversations, action events and subscription-state snapshots into evaluation JSON.
- Automated GDPR export and deletion workflows across seven sources through a self-service administration flow.

**Technologies:** Go, PHP, PostgreSQL, AWS, Amazon Connect, SQS, Kubernetes, Intercom API, Zendesk API

### CRURATED — PHP Software Developer, concurrent part-time subcontract
August 2024 – January 2026

- Owned the production event analytics architecture using queues and AWS EventBridge as DataLake throughput grew by more than tenfold.
- Reduced new analytics stream setup from several days to under four hours through modular stream design.
- Kept event delivery reliability above 99.9% through fault-tolerant pipeline design, retries and observability.
- Designed versioned event schemas and parallel event-version publication, allowing consumers to transition without blocking new events.
- Owned the production Crutrade integration across authentication and OTP, account linking, collection exchange and purchase-ownership verification.

**Technologies:** PHP, Laravel, AWS EventBridge, queues, REST APIs, event-driven architecture

### airSlate — Senior Software Developer
February 2021 – August 2023

- Developed a Laravel/Symfony logger package used across services and aligned it with the interservice communication standard.
- Reduced peak load on the main database by removing bottlenecks and redistributing workload, improving stability during busy periods.

**Technologies:** PHP, Laravel, Symfony, MySQL, monitoring

## Education

MSc in Computer Science, National Technical University, Kharkiv, Ukraine (2003–2008)

## Languages

Ukrainian (native), English (upper-intermediate)
