---
name: manual-job-intake
description: Add a manually sourced vacancy to the Job Intelligence registry and optionally prioritize it for match analysis. Use when the user wants to add a job manually from raw pasted vacancy text, a link, pasted job post, recruiter message, company careers page, or other non-collector source, especially when Codex should extract metadata from unstructured text, ask only for missing or ambiguous fields, mark analysis priority, and publish through the deterministic manual vacancy command.
---

# Manual Job Intake

Obey `AGENTS.md` first. Never add model calls to project code. This skill is an interactive intake workflow: accept raw vacancy text with any included metadata, extract the manual-job schema, ask the user only for missing or ambiguous evidence, create a deterministic manual-job draft, publish it with `python run.py add-manual --input <draft.yaml>`, then follow the repository's normal finalization rules.

## Intake

Treat the user's pasted vacancy text as the primary source. It may be messy: copied page text, recruiter notes, Telegram/LinkedIn message text, headings, URLs, salary snippets, location badges, or metadata lines. First extract every field that can be grounded in that text. Do not ask questions before attempting extraction.

Extract these required fields when present:

- `source_url`: original posting, careers page, recruiter message URL, or the best available source link.
- `company`
- `title`
- `description`: pasted full job description or a faithful manual extraction from the source.

Extract these optional fields when present:

- `analysis_priority`: use `100` only when the user explicitly says this vacancy is priority, urgent, hot, hire-priority, analyze first, or similar. Otherwise use `0`.
- `location`, `remote`, `employment_type`, `published_at`
- `company_url`, `company_description`
- `apply_url`, recruiter/contact details, and extraction notes.

Preserve the extracted job description as the body of the posting, not as a terse summary. Remove obvious page chrome, navigation, cookie text, duplicate buttons, and unrelated recommendations. Keep requirements, responsibilities, benefits, salary, hiring process, stack, language requirements, and application instructions when present.

After extraction, ask concise follow-up questions only for:

- Missing required fields.
- Ambiguous required fields, such as several company names or several job titles.
- Optional fields that materially affect routing, especially whether the job should be priority, when the pasted text suggests priority but does not say so clearly.

Do not invent vacancy facts. If an optional field is unknown, omit it or preserve the uncertainty in `extraction_notes`, not in canonical fields.

Before publishing, briefly show the extracted field values and call out any omitted unknowns. If required fields are complete and there are no material ambiguities, proceed without asking for confirmation unless the user asked to review first.

## Draft

Create `.codex-work/manual-job/<safe-name>.yaml` with this schema:

```yaml
source_url: "https://example.com/jobs/123"
company: "Example GmbH"
title: "Senior Backend Engineer"
description: |
  Full extracted job description.
analysis_priority: 100
location: "Remote Europe"
remote: true
employment_type: "Full-time"
published_at: "2026-07-24"
company_url: "https://example.com"
company_description: |
  Optional company context from the source.
apply_url: "https://example.com/jobs/123/apply"
source_name: "Company careers page"
source_notes: "User supplied the link and pasted the description."
extraction_notes: "Salary was not present in the source."
```

Only `source_url`, `company`, `title`, and `description` are required. Use `analysis_priority` as an integer from `0` to `100`; high priority affects analysis queue order only and must not bias the fit score.

## Publish

Run:

```text
python run.py add-manual --input .codex-work/manual-job/<safe-name>.yaml
```

Then run `python run.py catalog` as the separate deterministic catalog step. Run the required checks from `AGENTS.md`, inspect the diff, stage, commit, and push if files changed.

If the user also asks to analyze the vacancy immediately, invoke `$job-intelligence-workflow` in analysis mode after publishing and process the resulting vacancy through the sealed analysis workflow.