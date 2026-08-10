# Project instructions

## OpenAI Platform API prohibition

- Never add or restore calls from project code to the OpenAI Platform API or an OpenAI-compatible model endpoint.
- Never add the OpenAI SDK, `OPENAI_API_KEY`, requests to `api.openai.com`, Responses API payloads, Chat Completions payloads, or a proxy whose purpose is to call an OpenAI model for this project.
- Run model-dependent work inside an interactive or scheduled Codex task. Passing a Codex-produced local draft to deterministic project code for validation and publication is allowed.
- External vacancy-source APIs such as Adzuna, Jooble, Ashby, Arbeitnow, Himalayas, and Jobicy remain allowed.
- If requested functionality cannot be implemented without project code calling the OpenAI Platform API, stop before implementing it and tell the user exactly why Codex execution, deterministic local code, or an allowed external source cannot satisfy the requirement.
- Do not silently weaken this rule for tests, prototypes, fallbacks, optional integrations, or environment-specific code.

## Codex workflow models

Treat `config/codex-workflows.yaml` as the project model-routing policy. The file is advisory because a repository cannot switch the model of its current Codex task. Select the configured model and reasoning level when creating each Codex task or Scheduled Task, and pass the matching `--workflow` when publishing; project code derives the only allowed model label from policy.

## Workflow boundaries

- Keep collection, normalization, deduplication, hashing, validation, atomic publishing, DOCX conversion, and index generation deterministic and covered by tests.
- Process preparation as an explicitly selected batch of one to 10 vacancies per Codex
  task. Key every application package to its vacancy directory; research, draft,
  validate, and publish each package independently without reusing vacancy-specific
  content. Automatic `all` selection remains prohibited. Analysis may use the sealed
  batch contract (up to 15 vacancies) when every result is keyed to its input directory,
  evaluated independently, and published only after deterministic validation.
- Treat `registry/candidate/*.md` as immutable source-of-truth evidence. Never invent candidate claims.
- Use the repo skill `$job-intelligence-workflow` for collection, match analysis, and application preparation.
- Treat user approval as the mandatory preparation gateway: research, adapted CV,
  cover letter, interview preparation, and any later application-process artifacts
  may be generated only after the user explicitly asks to prepare a named vacancy
  (by vacancy ID, registry directory, or equivalent clear identifier). A manually
  supplied vacancy URL or pasted vacancy text authorizes intake and analysis only;
  it does not by itself authorize preparation.
- For every prepared cover letter, invoke `$write-cover-letter` from the highest
  installed version of `agent-plugins@valentin-agent-plugins` available in the active
  Codex task. If that skill is unavailable, stop before drafting; never fall back to
  the retired inline cover-letter logic.
- For CV preparation, do not include roles or employment experience older than 10 years in the generated CV `Experience` section. Older evidence may support skills, chronology, or interview preparation only when relevant.
- Change vacancy status only after an explicit user request, through `python run.py status`; never infer status from artifacts or external events.
- Before finishing code changes, run `python -m unittest discover -v` with an available Python 3.11+ runtime and search project code/configuration for prohibited API integrations.

## Required Git finalization

- At the end of every successful task that changes repository files, regenerate the vacancy catalog when the workflow requires it, run the relevant checks, and inspect the complete Git diff.
- Stage every added, modified, renamed, and deleted project file with `git add -A`. Never stage ignored secrets, `.codex-work/`, IDE files, caches, or virtual environments.
- Every Job Intelligence task must finish by inspecting `git status` and the complete diff, staging every real project change with `git add -A`, committing once, and pushing the current branch to `origin` when the tree has changes. Never leave real project changes unstaged or uncommitted. Preserve only ignored secrets, `.codex-work/`, IDE files, caches, and virtual environments.
- Commit the complete task as the final repository mutation with a concise message, then push the current branch to `origin`.
- For Codex-authored commits, derive the subject from the final staged diff and write a
  natural, specific imperative sentence that names the actual outcome. Include useful
  counts or vacancy context when they distinguish the run. Do not select from the
  GitHub Actions templates, and avoid generic subjects such as `update files`, `update
  data`, `workflow changes`, or `automated update`; keep execution metadata in the
  commit body instead.
- If there are no repository changes, do not create an empty commit; report that no push was needed.
- End the user-facing report with a short changelog derived from the committed diff, followed by the commit hash and push result.
- Do not open a pull request unless the user explicitly asks for one.
