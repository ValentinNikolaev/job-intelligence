# Prepare one to 10 application packages

1. Read `prompts/job-intelligence-workflow.md` and `config/codex-workflows.yaml`.
   Confirm the task uses workflow `prepare`, the selected model profile, and that the
   explicit selection does not exceed `prepare_batch_size` (hard maximum: 10).
2. Require one to 10 vacancy IDs or registry directories explicitly named in the chat
   request. Preserve that sealed selection. Do not run `pending prepare all`, query an
   automatic preparation queue, or add another vacancy based on score or similarity.
3. Verify the complete selection with
   `python run.py pending prepare <selector-1> [<selector-2> ...] --workflow prepare --model-profile <selected-profile>`.
   The command prints only vacancies that are analyzed, fresh, score-eligible, and not
   already current. Do not draft a selected vacancy whose path is absent; report it as
   having no pending preparation work.
4. Process each printed vacancy independently. For the current vacancy, read its
   `meta.yaml`, `job.md`, optional `company.md`, the configured candidate sources, and
   `prompts/vacancy-application.md`. Do not read non-selected vacancies, compare selected
   vacancies, or carry company research, requirements, keywords, or wording from one
   package into another.
5. Create `.codex-work/application/<vacancy-directory>/parts/`, then run Wave 1 with
   three independent roles in parallel when subagent slots are available. Route only
   the minimum inputs below and assign exactly one handoff file:
   - research: read this vacancy's `meta.yaml`, `job.md`, optional `company.md`, and only
     the minimal candidate motivation hooks needed for fit; do not read the full source
     CV. Verify company identity, role context, and one motivation point within the
     research budget, then write only `parts/research.md` with links and
     fact/inference/unknown labels;
   - CV/evidence: read this vacancy and the configured candidate sources, perform no web
     research, and write only `parts/evidence-map.md`. Include the evidence mapping and
     a complete proposed CV draft with supported headline, summary, skills, and bullets;
   - requirements/risks: read this vacancy and configured candidate evidence, extract
     explicit and inferred requirements, gaps, ATS terms, recruiter risks, and likely
     interview probes, then write only `parts/requirements-risks.md`.
   Wave 1 roles must not publish, run deterministic project commands, or write `cv.md`,
   `cover-letter.md`, `analysis.md`, or `interview-preparation.md`.
6. The research role must use the vacancy posting plus at most two primary company
   sources in one pass. Exceed that budget only for a critical unresolved eligibility
   or company-identity fact and record the reason in its handoff. After all three Wave 1
   handoffs finish, the main agent must reconcile conflicts, reject unsupported claims,
   and synthesize the final vacancy-specific `cv.md` without repeating the research.
7. Start Wave 2 only after `cv.md` is final. Run three independent roles in parallel
   when slots are available, with exclusive ownership of one final file each:
   - cover letter: receive this vacancy, final CV, verified `parts/research.md`, and only
     the candidate evidence required to ground the selected stories; invoke the
     highest installed version of `$write-cover-letter` in Draft mode and write only
     `cover-letter.md`;
   - interview preparation: receive this vacancy, final CV,
     `parts/requirements-risks.md`, and verified `parts/research.md`; write only
     `interview-preparation.md` without repeating company research;
   - application analysis: receive this vacancy, final CV, and all three Wave 1
     handoffs; synthesize the required audit, research, requirements, gaps, changes,
     scores, and recommendation and write only `analysis.md`.
   No role may edit another role's file. Keep the
   `$write-cover-letter` workbench internal and run its claim-grounding check. If that
   skill is unavailable, stop; never substitute generic or retired inline letter logic.
8. The main agent must perform one cross-file consistency and claim-grounding pass after
   Wave 2. Resolve contradictions against candidate evidence and the final CV without
   starting another broad drafting loop. If subagents or enough slots are unavailable,
   execute the same Wave 1 roles, main CV synthesis, and Wave 2 roles sequentially with
   the same file ownership and boundaries. Do not claim that the repository or current
   task switched models.
9. Do not let a role reread unneeded candidate sources, other handoffs, the full
   registry, or another vacancy directory. For a batch, each role still owns exactly
   one vacancy-keyed file. Agents may be
   distributed across vacancies, but no agent may combine evidence, research, handoffs,
   or final artifacts from different vacancies. Complete all four final drafts for each
   vacancy under its own `.codex-work/application/<vacancy-directory>/`.
10. After the main consistency pass, run the vacancy's single combined deterministic
   draft check:
   `python run.py validate-application <vacancy-directory> --input .codex-work/application/<vacancy-directory>`.
   Do this once per selected vacancy after drafting is complete, not after each wave or
   file.
   If it fails, correct only that vacancy and rerun its validator.
11. After every selected draft passes, publish the verified batch once with
    `python run.py prepare <selector-1> [<selector-2> ...] --input .codex-work/application --workflow prepare --model-profile <selected-profile>`.
    The deterministic publisher resolves every selector before publication and reads
    each package only from its matching vacancy-keyed draft directory. A legacy
    single-vacancy call may still pass that vacancy's draft directory directly. If DOCX
    conversion fails, correct only that deterministic issue and rerun publication.
    Current packages are skipped. Confirm each prepared vacancy has all six application
    artifacts, the upload-friendly CV copies, and `manifest.yaml`.
