# Senior Full-Stack Engineer

Posted: 2026-07-29T23:11:32Z

## Rejection

- Category: stale
- Reason: published_at 2026-07-29T23:11:32Z is older than 7 days

### About Hairball

Hairball.io is an Inc. 5000 e-commerce integration consultancy with 550+ client relationships in

the Shopify, NetSuite, and Celigo ecosystem. We are building a new AI-powered SaaS product

for our market. Details about the product will be shared during the interview process.

### The Role

We need a senior full-stack engineer to build the multi-tenant platform foundation for a new

SaaS product over a 6-month contract engagement. You will be the primary architect and

builder of the core infrastructure. A junior JavaScript developer on the team will work alongside

you, learning the stack and eventually owning day-to-day development after your engagement

### ends.

This is a founding-level role. You are not joining a team — you are building the platform that a

team will grow around. The architecture decisions you make in the first 8 weeks will shape this

### product for years.

### What You Will Build

### Months 1-2: Platform Spine

- Multi-tenant database schema with PostgreSQL Row-Level Security (RLS) enforcement

### on every tenant-scoped table

- Authentication integration with Clerk, including multi-organization switching (one user,

### many tenants)

- Role-based access control for six user roles with JSONB-based extensible permissions

### and ABAC extensions

- API call logging pipeline with full attribution chain (tenant → service → execution →

### result)

- Super Admin and Tenant Admin interfaces

### Months 3-4: Billing & Integrations

- Stripe Billing integration: subscriptions, metered usage-based pricing, Customer Portal

- External API integration pipeline with encrypted credential storage per tenant

- Connection management UI for tenant-managed third-party credentials

- Configuration inheritance system: platform defaults → tenant overrides → user

### preferences

- Feature flag and module entitlement system for gating product capabilities per plan

### Months 5-6: Hardening & Handoff

- Security hardening: immutable audit trails, environment separation (sandbox +

### production per tenant)

- Performance optimization and production readiness review

- Architecture Decision Records (ADRs) and documentation for the team inheriting the

### codebase

- Code review and mentoring of the junior developer to ensure smooth transition

### Technology Stack

### Layer

### Technology

### Notes

### Framework

### Next.js 14 App Router + TypeScript

### Hosted on Vercel

### Database

### PostgreSQL 16+ (Neon)

### Drizzle ORM. RLS is non-negotiable.

### Cache / Queue

### Upstash Redis

### Job queuing, rate limiting

### Auth

### Clerk

### Multi-organization support required

### AI

### Anthropic Claude (primary)

### Multi-LLM gateway planned

### Billing

### Stripe Billing

### Subscriptions + usage-based

### metering

### CI/CD

### GitHub + Vercel

### Branch-based deploys, PR workflow

### Required Experience

These are non-negotiable. If you have not done these things in production, this is not the right

### role.

- Multi-tenant SaaS architecture: You have personally built (not just contributed to) a

multi-tenant application with tenant data isolation. You understand the difference

between application-level tenant filtering and database-level enforcement.

PostgreSQL Row-Level Security: You have implemented RLS policies in production.

You know how to set tenant context per transaction and test for cross-tenant data

### leakage.

Next.js 14+ App Router: You are current with App Router (not Pages Router). You

understand server components, server actions, route handlers, and middleware.

TypeScript: You write TypeScript fluently, not JavaScript with type annotations bolted

### on.

Stripe Billing integration: You have wired up subscriptions, handled webhooks with

signature verification, and implemented metered/usage-based billing.

Multi-org authentication: You have implemented multi-organization auth (Clerk, Auth0,

or similar) in a SaaS product. You understand session scoping per organization.

### Strongly Preferred

Experience with Drizzle ORM (or Prisma with willingness to learn Drizzle)

AI/LLM application development — calling LLM APIs, streaming responses, token

### tracking

### Vercel deployment and optimization

### Experience mentoring junior developers

Prior work in e-commerce, fintech, or financial data platforms

### What We Provide

Complete architecture spec: A detailed specification covering every subsystem you

will build. You are implementing a well-defined plan, not designing from scratch.

Deep domain expertise: The product owner has deep expertise in the target market.

You will never be guessing about business requirements.

Working prototype: The backend pipeline and database schema already exist. You are

### building on a foundation, not from zero.

AI development tooling: Claude Code is available as a pair programmer. The spec

documents are structured for AI-assisted implementation.

Autonomy: You make the technical decisions within architectural boundaries. No

micromanagement. Weekly video check-in, daily async on Slack.

### How We Evaluate

Step 1 — Portfolio review (async). Send links to multi-tenant SaaS products you have built.

We want to see architecture decisions, not algorithm skills.

Step 2 — Architecture conversation (60 min). We share the product spec and ask you to

walk through how you would implement the multi-tenant isolation layer. We are looking for

awareness of edge cases and honest assessment of complexity.

Step 3 — Paid trial task (8-10 hours). Implement a specific piece of the platform against the

actual codebase. Compensated at your hourly rate.

### Logistics

Schedule: 30-35 hours/week, flexible. Overlap with US Eastern for 3-4 hours daily.

Communication: Slack (daily async), weekly 30-minute video check-in, GitHub PRs for

### all code.

Documentation: Every architectural decision gets a brief ADR in the repo.

Payment: Biweekly invoicing, Net-15. Rate negotiable based on experience

Originally posted on [Himalayas](https://himalayas.app)
