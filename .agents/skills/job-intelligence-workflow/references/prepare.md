# Prepare one application package

1. Read `config/codex-workflows.yaml`. Confirm the task uses workflow `prepare`.
2. Require the user's explicit vacancy ID or registry directory from the chat request. Do not run `pending prepare all` and do not select from an automatic preparation queue.
3. Run `python run.py pending prepare <vacancy-id-or-directory> --workflow prepare` to verify the selected vacancy is analyzed, fresh, score-eligible, and not already current. If no path is printed, report that this selected vacancy has no pending preparation work and stop.
4. After verification, do not read any other vacancy. Read the selected vacancy's `meta.yaml`, `job.md`, optional `company.md`, the configured candidate sources, and `prompts/vacancy-application.md`.
5. Use Codex web research when available. Put direct source links and fact/inference/unknown labels in the analysis. The repository must not call a model or web-search API on Codex's behalf.
6. Write exactly these files under `.codex-work/application/<vacancy-directory>/`: `cv.md`, `cover-letter.md`, `analysis.md`, and `interview-preparation.md`.
7. Publish with `python run.py prepare <vacancy-directory> --input <draft-directory> --workflow prepare`.
8. If validation or DOCX conversion fails, correct the draft or deterministic converter issue and retry. Confirm all six application artifacts and `manifest.yaml` exist.
