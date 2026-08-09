# Prepare one to 10 application packages

1. Read `config/codex-workflows.yaml`. Confirm the task uses workflow `prepare` and that
   the explicit selection does not exceed `prepare_batch_size` (hard maximum: 10).
2. Require one to 10 vacancy IDs or registry directories explicitly named in the chat
   request. Preserve that sealed selection. Do not run `pending prepare all`, query an
   automatic preparation queue, or add another vacancy based on score or similarity.
3. Verify the complete selection with
   `python run.py pending prepare <selector-1> [<selector-2> ...] --workflow prepare`.
   The command prints only vacancies that are analyzed, fresh, score-eligible, and not
   already current. Do not draft a selected vacancy whose path is absent; report it as
   having no pending preparation work.
4. Process each printed vacancy independently. For the current vacancy, read its
   `meta.yaml`, `job.md`, optional `company.md`, the configured candidate sources, and
   `prompts/vacancy-application.md`. Do not read non-selected vacancies, compare selected
   vacancies, or carry company research, requirements, keywords, or wording from one
   package into another.
5. Use Codex web research when available. Keep research scoped to the current company
   and vacancy. Put direct source links and fact/inference/unknown labels in that
   vacancy's analysis. The repository must not call a model or web-search API on
   Codex's behalf.
6. After finalizing the vacancy-specific CV and company research, invoke
   `$write-cover-letter` in Draft mode. Supply only this vacancy, the configured
   candidate evidence, the final CV, and verified research for this company. Keep its
   requirement-to-evidence workbench internal, use two complementary supported examples,
   and run its final claim-grounding check. Put only the finished letter in
   `cover-letter.md`; put research sources and unresolved confirmation items in
   `analysis.md`. Do not invoke `stop-slop` as a routine cover-letter pass.
7. If `$write-cover-letter` is unavailable, stop and report that
   `agent-plugins@valentin-agent-plugins` version
   `9.0.0+codex.20260809175723` is required. Never substitute the old inline drafting
   rules or a generic letter.
8. For every vacancy, write exactly `cv.md`, `cover-letter.md`, `analysis.md`, and
   `interview-preparation.md` under
   `.codex-work/application/<vacancy-directory>/`. Never use one shared set of drafts.
9. Publish the verified batch with
   `python run.py prepare <selector-1> [<selector-2> ...] --input .codex-work/application --workflow prepare`.
   The deterministic publisher resolves every selector before publication and reads
   each package only from its matching vacancy-keyed draft directory. A legacy
   single-vacancy call may still pass that vacancy's draft directory directly.
10. If validation or DOCX conversion fails, correct only the failing vacancy's draft or
   the deterministic converter issue and retry the explicit selection. Current packages
   are skipped. Confirm each prepared vacancy has all six application artifacts, the
   upload-friendly CV copies, and `manifest.yaml`.
