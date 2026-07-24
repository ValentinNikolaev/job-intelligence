---
name: manual-job-intake
description: Add a manually sourced vacancy to the Job Intelligence registry and optionally prioritize it for match analysis. Use when the user wants to add a job manually from a link, pasted job post, recruiter message, company careers page, or other non-collector source, especially when Codex should ask intake questions, extract source details, mark analysis priority, and publish through the deterministic manual vacancy command.
---

# Manual Job Intake

Obey `AGENTS.md` first. Never add model calls to project code. This skill is an interactive intake workflow: ask the user for missing evidence, create a deterministic manual-job draft, publish it with `python run.py add-manual --input <draft.yaml>`, then follow the repository's normal finalization rules.

## Intake

Ask concise follow-up questions until these required facts are known:

- `source_url`: original posting, careers page, recruiter message URL, or the best available source link.
- `company`
- `title`
- `description`: pasted full job description or a faithful manual extraction from the source.

Ask for these optional facts when they are useful and not already clear:

- Whether this should be analyzed first. Use `analysis_priority: 100` for a user-designated priority vacancy, otherwise `0`.
- `location`, `remote`, `employment_type`, `published_at`
- `company_url`, `company_description`
- `apply_url`, recruiter/contact details, and extraction notes.

Do not invent vacancy facts. If a field is unknown, omit it or preserve the uncertainty in `extraction_notes`, not in canonical fields.

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