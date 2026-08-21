# Tech Lead AI Engineering (m/w/d)

Posted: 2026-08-20T15:30:29Z

## Rejection

- Category: location_requirement
- Reason: vacancy is explicitly non-remote

For a young company in the fast-growing AI implementation market we are looking for a Tech Lead, starting end of October or early November. The company operates LLM-based systems in production: content generation pipelines, retrieval-augmented generation (RAG) over internal documents, and automated workflows deeply integrated with their business systems. The stack is TypeScript and Next.js end to end.

These systems are already live. As Tech Lead you take ownership of them, improve their reliability and quality, and extend them to new use cases, while taking technical responsibility for a team. The role combines applied LLM engineering with solid backend engineering in TypeScript. It does not involve training or fine-tuning foundation models.

Stack: TypeScript, Next.js, Node.js, Postgres with pgvector, Docker, Azure, Anthropic and OpenAI APIs, Vercel AI SDK.

## Tasks

- Technical responsibility for a team: architecture decisions and code reviews

- Technical guidance and interface to non-technical colleagues

- Take over and maintain the existing LLM pipelines: assess the current architecture, identify failure modes, prioritise fixes, and refactor and extend without disrupting production

- Own the RAG systems end to end: document ingestion and parsing, chunking, indexing, hybrid retrieval (BM25 and vector), query rewriting, reranking, grounded generation with citations

- Implement and maintain chunk-level access control, index freshness and tenant isolation across retrieval systems

- Develop content generation pipelines that deliver consistent quality at volume, including human review steps

- Build and operate automated workflows against internal and third-party business systems (ERP, CRM, email, internal APIs), with durable and idempotent execution, retry and dead-letter handling, and approval steps for irreversible actions

- Establish an evaluation framework for systems currently running without one: golden datasets derived from observed production failures, retrieval metrics and more

- Implement observability across the full request path

- Optimise cost and latency through prompt caching, batching, model routing and use of smaller models where appropriate

- Assess where deterministic logic is the better solution and implement it accordingly

- Work directly with non-technical colleagues to specify and validate automated processes

## Requirements

- Professional experience with at least one LLM-based system in production use, including responsibility for its operation and incident handling

- TypeScript and Node.js at an advanced level: strict typing of non-deterministic model output, async and concurrency patterns, streaming responses, structured error handling

- Next.js in production: App Router, route handlers, server actions, streaming to the client

- Demonstrably taken over and improved existing codebases under production traffic

- Practical retrieval expertise: hybrid search, embedding model selection, cross-encoder reranking, metadata filtering, permission-aware retrieval, and structured diagnosis of poor retrieval quality

- Experience processing real-world documents: PDFs with tables, scanned material, DOCX, HTML, including layout-aware parsing, OCR, and evidence-based chunking

- Structured outputs and tool calling as part of your everyday work: JSON Schema, Zod or comparable runtime validation, function calling, handling of malformed or partial output, context window management

- Designed and run LLM evaluations

- Experience with LLM tracing and evaluation tooling in a TypeScript codebase (e.g. Braintrust, Langfuse, Promptfoo, OpenTelemetry or Arize Phoenix)

- Familiar with Postgres including vector search (pgvector or a comparable vector store), Docker, Git, CI/CD, and one major cloud platform

- Working experience with the Anthropic and/or OpenAI TypeScript SDKs

- Confident communication in English, German is a plus

**If you have experience with any of the following, that's a plus:**

- Nice to have: durable workflow execution for long-running, unattended processes (Temporal, Inngest, or comparable)

- Nice to have: agent orchestration in production, tool calling, recovery, multi-step workflows (Vercel AI SDK, LangGraph, Mastra, Claude Agent SDK, MCP TypeScript SDK)

- Nice to have: integration experience with enterprise systems such as ERP or CRM platforms like SAP

- Nice to have: security and data protection in LLM systems, prompt injection and data exfiltration defences, PII handling, GDPR-compliant design, EU-hosted or self-hosted inference

- Nice to have: structured or graph-based retrieval for entity-heavy data

- Nice to have: experience migrating live pipelines to a new model, embedding model or index without quality regression

- Nice to have: Azure DevOps, Pipelines, Repos and Boards

## Benefits

- Hybrid setup, 2 office days per week in the light-flooded office in the Belgian Quarter in Cologne (with two balconies and the best view over the city ;))

- AI implementation, the growth market of the coming years

- Trust-based working hours with overtime compensation

- Plenty of creative freedom and room for your own ideas

- Continuous development, professional, strategic and technological

- An open feedback culture, transparent communication and short decision paths

- Regular team events and workations

- Salary from €60,000 gross per year, with room upwards depending on experience

The company is an international team and actively fosters an inclusive environment. Applications from all genders and identities are welcome, regardless of origin, age, religion, sexual orientation or disability. Women are still underrepresented in the tech industry and are explicitly encouraged to apply.

We look forward to your application!

Find more [English Speaking Jobs in Germany](https://www.arbeitnow.com/english-speaking-jobs) on Arbeitnow
