# Forward Deployed Engineer, DACH

Posted: 2026-09-13T11:55:03Z

## Rejection

- Category: location_requirement
- Reason: vacancy is explicitly non-remote

**About Telnyx**

*Telnyx is an industry leader that's not just imagining the future of global connectivity—we're building it. From architecting and amplifying the reach of a *[*private, global, multi-cloud IP network*](https://telnyx.com/our-network)*, to bringing *[*hyperlocal edge*](https://telnyx.com/resources/about-edge-connectivity)* technology right to your fingertips through intuitive APIs, we're shaping a new era of seamless interconnection between people, devices, and applications.*

*We're driven by a desire to transform and modernize what's antiquated, automate the manual, and solve real-world problems through innovative connectivity solutions. As a testament to our success, we're proud to stand as a financially stable and profitable company. Our robust profitability allows us not only to invest in pioneering technologies but also to foster an environment of continuous learning and growth for our team.*

*Our collective vision is a world where borderless connectivity fuels limitless innovation. By joining us, you can be part of laying the foundations for this interconnected future. We're currently seeking passionate individuals who are excited about the opportunity to contribute to an industry-shaping company while growing their own skills and careers.*

###

**The Role**

We're building a local Enterprise Sales Pod in Munich — one AE and one Forward Deployed Engineer (FDE), working together to build a Telnyx enterprise business in your market. You'll embed directly with enterprise customers to architect and ship production systems on Telnyx's global network — voice, messaging, AI, and wireless.

This isn't about demoing products. It's about building real solutions that work at scale.

You'll work side-by-side with a dedicated Enterprise AE — not a demo resource, but a commercial partner who owns the named-account list, builds executive relationships, and closes the deal. You own the technical side: discovery, architecture, POC, and production go-live. You win together. No throw-over-the-wall.

*The Pod Model*

*Enterprise AE* — owns the named-account list, builds executive relationships, gets in the room, owns commercial qualification and close, expands the account. .

*Forward Deployed Engineer* — owns technical discovery, designs the architecture, builds the POC when gated, gets the first workload live, removes blockers and finds the next workload.

We sell the workload, not the SKU. Customers buy a production outcome — an AI contact center, a SOC/NOC agent, global communications, connected mobility, or enterprise inference — that runs on Telnyx primitives (voice, messaging, numbers, wireless, Voice AI, inference, agents, connectivity). You lead with the outcome conversation, not a product menu.

**What You'll Do**

• Embed with enterprise customers to understand their communications workflows, AI use cases, and integration challenges firsthand
• Build and deploy custom implementations: AI Voice Assistants, Telnyx APIs (Voice, Messaging, Fax, Wireless), WebRTC
• Run open-weight LLMs in customer environments — consume GLM, Kimi, DeepSeek, Qwen, and MiniMax through Telnyx Inference (OpenAI-compatible API; there's no model infrastructure for you to run), or deploy self-hosted stacks (Llama, Mistral, and region-specific models like Aleph Alpha's Luminous, or sovereign EU models) behind your own serving engine when air-gapped or sovereign-cloud requirements demand it
• Deploy and operate LiteLLM as the model gateway in customer environments: a unified OpenAI-compatible interface across self-hosted open-weight models and hosted providers, with routing, load balancing, retries and fallbacks, rate limits, and per-team virtual keys
• Instrument and govern LLM usage through the gateway — cost tracking and budgets, caching, logging and observability (OpenTelemetry, Langfuse, or similar), and guardrails — so customers can see and control what their AI workloads are doing
• Wire production observability for everything you ship — metrics, logs, traces, dashboards, and alerting (e.g. Prometheus + Grafana for metrics, OpenTelemetry for traces, Graylog or ELK for logs — or the customer's existing stack) — so you and the customer's ops team both know what "healthy" looks like and what pages whom when it isn't
• Design model routing strategies for real-time voice workloads, balancing latency, cost, and quality, with sane fallback behavior when a provider degrades
• Make the build-vs-buy case between self-hosted open-weight models and hosted frontier APIs, and keep the customer's application code portable across both
• Adapt models to customer domains: prompt and RAG pipelines and evaluation harnesses for German-language use cases and DACH-specific regulatory environments (GDPR, EU AI Act, German data localization)
• Lead POCs, pilots, and production launches from whiteboard to go-live
• Own customer outcomes — stay engaged until the solution is live and stable
• Collaborate directly with Product and Engineering to shape the roadmap based on field insights from Germany, Austria, and Switzerland
• Create clear technical documentation, runbooks, and maintainable solutions for handoff

[2:29 PM]

• Troubleshoot and resolve complex integration issues alongside customer teams

**What We're Looking For**

• CS degree or equivalent experience
• 3+ years building and shipping production software — you've written code that real users depended on, you've been on-call for it, and you've debugged it when things broke. (A consulting background counts if this is also true of you.)
• Proficiency in multiple languages: Python, Node.js/TypeScript, Go — you're more dangerous in some than others. (Telnyx Edge Compute — functions and stateful actors — is TypeScript, so that one pulls double duty.)
• Practical understanding of what breaks in front of a model in production: provider rate limits and quotas, timeout and retry behavior, streaming, token accounting and cost attribution, and the failure modes that only show up under concurrency
• Comfortable deploying containerized services on Kubernetes, with secrets management, config, and upgrades as part of the deployment story
• You've wired observability and been paged because of it — Prometheus + Grafana, OpenTelemetry, Graylog, ELK, or equivalent. You know what to monitor, what to alert on, and what "healthy" looks like
• High-concurrency experience — Kafka, message queues, or event streams at real scale. When throughput spikes you know what breaks — consumer lag, backpressure, hot partitions, rebalance stalls — and what absorbs it: partitioning, consumer groups, parallelism up to your partition count
• You've built APIs from scratch, not just consumed them — OpenAPI spec, REST/GraphQL design, auth, rate limiting, versioning, idempotency
• Event-driven thinking and cloud-native instincts
• Exposure to SIP, WebRTC, or real-time voice/messaging systems
• Self-sufficient by default — there's no engineering team behind you. You read the code and the docs, ask the customer (not your manager), and make sound engineering judgment calls on your own
• Customer-facing engineering experience — you can run discovery with a customer's engineers and present to their executives in the same week
• Ability to translate "it's not working" into root cause
• Comfortable working on customer sites and in high-stakes technical conversations
• Excellent written and verbal communication in English and German. You can run whiteboard sessions, live troubleshooting, and escalations with customer engineering teams.
• Based in Munich, or willing to relocate — this is a hybrid role with travel across Germany, Austria, and Switzerland
• Legally authorized to work in Germany, or eligible for sponsorship

*Bonus Points For*

• Experience with AI voice assistants, STT/TTS, or LLM-based conversational systems
• Building eval sets for a specific domain
• Hands-on production experience with an LLM gateway — LiteLLM, Portkey, Kong AI Gateway, or an in-house OpenAI-compatible proxy — including config-driven model definitions, routing and fallback rules, and virtual key management
• Familiarity with the open-weight model landscape and the trade-offs between regional and multilingual models, including EU sovereign AI initiatives (Gaia-X, Aleph Alpha, European LLM projects)
• Experience with an inference serving engine behind the gateway — vLLM, SGLang, or TGI for production serving; Ollama for lightweight on-prem — and sizing GPU capacity for self-hosted models (KV-cache footprint, concurrent batch size, and context length against VRAM)
• SQL proficiency (Postgres, MySQL, Oracle)
• ETL and data wrangling experience
• CI/CD pipeline design and automation
• Background in telecom, CPaaS, or high-growth SaaS
• Experience with sovereign or on-prem cloud deployments and DACH regulatory frameworks (GDPR, EU AI Act, German data sovereignty and localization requirements, Swiss data protection)
• Security mindset (IAM, encryption, audit logging)

###

*#LI-RH1*

Find [Jobs in Germany](https://www.arbeitnow.com) on Arbeitnow
