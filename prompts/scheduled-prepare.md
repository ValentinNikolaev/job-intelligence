# Scheduled application preparation

## Conditional letter generation

Default scope: CV, application analysis and interview preparation. Inspect the apply
route before assigning letter work. Generate a letter only for a required form field;
for an email-only application, always draft the email in the company's evidenced
language. Skip optional fields. Required letters use a separate `--document cover-letter`
pass, reusing the final CV and research. Finish it before reporting the package ready.
Both channels require current voice, `write-cover-letter`, `humanizer`, `ai-detector`
and a separate naturalness rating of at least 90/100. Preserve unselected artifacts.
The mandatory receipt schema and rubric are in `docs/application-review-contract.md`,
section "Conditional letter generation and delivery gate". Missing external feedback
required by the installed detector skill stays incomplete; never fabricate a score.



Automatic scheduled application preparation is disabled.

Read `prompts/job-intelligence-workflow.md` for the shared manual-application
contract. A user-provided vacancy URL must enter through the interactive
`manual-application` mode and `$manual-vacancy-application`; this Scheduled Task must
not invent a selection or silently prepare a queue.

When that manual URL flow has no current match, export its one-item sealed pack with
`python run.py analyze <vacancy-directory> --pack <pack.yaml> --workflow analyze`,
evaluate that item in Codex and publish the complete envelope plus keyed result with
`python run.py analyze <vacancy-directory> --input <draft.yaml> --workflow analyze`.
It must not borrow this or the scheduled analysis queue to process unrelated vacancies.

Do not select vacancies automatically, do not run `python run.py api queues prepare`,
and do not publish application packages from a schedule. Application preparation now
starts only from an explicit user chat request naming a vacancy ID or registry
directory from the analyzed vacancy matches.

If this Scheduled Task still exists, it should stop after reporting that manual
selection is required. The manual chat workflow is:

1. Use analyzed vacancy matches from Telegram or the catalog.
2. The user explicitly provides one to 10 vacancy IDs or registry directories.
   The three-document package (CV, analysis and interview preparation) is the default; the user may instead explicitly name
   exactly one document.
3. A Codex task reads `AGENTS.md`, invokes `$job-intelligence-workflow` in preparation
   mode and runs the explicit selection's `prepare-preflight`. Resolve preparation
   paths and career rules from `config/application-profile.yaml`, voice sources from
   `config/application-review.yaml`, and copy preflight's exact
   `preparation_context_version` into each new schema-3 quality draft. Write isolated drafts under
   `.codex-work/application/<vacancy-directory>/`, validates each completed draft set
   once with `python run.py validate-application <vacancy-directory> --input
   .codex-work/application/<vacancy-directory> [--document <document>]`, and publishes the verified batch with
   `python run.py prepare <selector-1> [<selector-2> ...] --input .codex-work/application --workflow prepare --model-profile <selected-profile> [--document <document>]`.
