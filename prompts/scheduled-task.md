# Job Intelligence collection task

Work only inside the configured `job-intelligence` repository. Read `AGENTS.md` and use `$job-intelligence-workflow` in collection mode.

1. Preserve unrelated user changes and never expose or commit secrets from `sources/.env`.
2. Run all configured vacancy collectors with `python run.py all`. A failure in one source must not stop successful sources.
3. Run `python run.py reindex` and let `$job-intelligence-workflow` run and verify the final catalog process.
4. Run `python -m unittest discover -v` and the OpenAI Platform API prohibition scan.
5. Inspect the entire repository diff. Stage every added, modified, renamed, and deleted project file with `git add -A`, while confirming that `sources/.env`, `.codex-work/`, IDE files, caches, and virtual environments remain ignored.
6. If the tree changed, commit once with a concise collection-update message and push the current branch to `origin`. If nothing changed, do not create an empty commit. Never create a pull request.
7. Report collection counts, failures, catalog result, tests, commit hash, push result, and a short changelog derived from the committed diff. Do not analyze vacancies, create application packages, submit applications, contact employers, or create another scheduled task.

This task performs no model-dependent vacancy work, so configure it with GPT-5.6 Luna and low reasoning. Analysis and preparation are separate tasks because their configured models differ. Use CodexSandboxOnline for sandboxed command execution so collectors can reach external vacancy APIs over the network. Source API credentials must be provisioned as environment secrets for the scheduled task or host, not committed to the repository. Local runs may still use the ignored `sources/.env` fallback.
