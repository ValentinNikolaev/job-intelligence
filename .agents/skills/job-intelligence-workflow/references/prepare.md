# Prepare one to 10 application packages

The default scope is the complete four-document package. If the user explicitly asks
for exactly one document, set `<document>` to `cv`, `cover-letter`, `analysis`, or
`interview-preparation`, run only the required evidence/drafting roles, and pass
`--document <document>` to pending, validation, and publication. Preserve existing
unselected artifacts. Never infer partial scope from casual emphasis; without an
explicit single-document request, use the full-package flow below.

1. Read `prompts/job-intelligence-workflow.md` and `config/codex-workflows.yaml`.
   Confirm the task uses workflow `prepare`, the selected model profile, and that the
   explicit selection does not exceed `prepare_batch_size` (hard maximum: 10).
2. Require one to 10 vacancy IDs or registry directories explicitly named in the chat
   request. Preserve that sealed selection. Do not run `pending prepare all`, query an
   automatic preparation queue, or add another vacancy based on score or similarity.
3. Verify the complete selection with
   `python run.py pending prepare <selector-1> [<selector-2> ...] --workflow prepare --model-profile <selected-profile> [--document <document>]`.
   The command prints only vacancies that are analyzed, fresh, score-eligible, and not
   already current. Match freshness is evaluated against the same selected model
   profile. If an explicitly selected vacancy is absent only because its current match
   was produced by another profile, do not relabel or reuse that judgment. Evaluate the
   vacancy in the active selected-profile Codex task, publish the new isolated draft
   with `python run.py analyze <vacancy-directory> --input <match-draft.yaml>
   --workflow analyze --model-profile <selected-profile> --force`, and rerun the pending
   check. Do not draft a vacancy that remains absent; report the actual eligibility or
   freshness reason.
4. Process each printed vacancy independently. For the current vacancy, read its
   `meta.yaml`, `job.md`, optional `company.md`, the configured candidate sources, and
   `prompts/vacancy-application.md`. Do not read non-selected vacancies, compare selected
   vacancies, or carry company research, requirements, keywords, or wording from one
   package into another.
5. For a full package, create `.codex-work/application/<vacancy-directory>/parts/`, then run Wave 1 with
   three independent roles in parallel when subagent slots are available. Route only
   the minimum inputs below and assign exactly one handoff file:
   - research: read this vacancy's `meta.yaml`, `job.md`, optional `company.md`, and only
     the minimal candidate motivation hooks needed for fit; do not read the full source
     CV. Verify company identity, role context, and one motivation point within the
     research budget, then write only `parts/research.md`, at least 100 words, with
     Fact, Inference, Unknown labels and at least one direct URL;
   - CV/evidence: read this vacancy and the configured candidate sources, perform no web
     research, and write only `parts/evidence-map.md`, at least 450 words. Include a
     requirement-to-evidence matrix and a complete proposed CV with Summary, Skills,
     Experience, Education, Languages, supported headline, and evidence-backed bullets;
   - requirements/risks: read this vacancy and configured candidate evidence, extract
     explicit and inferred requirements, gaps, ATS terms, recruiter risks, and likely
     interview probes, then write only `parts/requirements-risks.md`, at least 250
     words, separately covering explicit/inferred requirements, gaps, ATS terms,
     recruiter risks, and interview probes.
   Wave 1 roles must not publish, run deterministic project commands, or write `cv.md`,
   `cover-letter.md`, `analysis.md`, or `interview-preparation.md`.
   For `--document cv`, run only CV/evidence plus the main CV synthesis. For another
   single document, run only its necessary evidence/research handoffs and its owning
   final role; reuse an existing current CV only when that document depends on it.
6. The final CV must contain Summary, Skills, Experience, Education, and Languages;
   12–18 evidence-backed hard skills; the candidate's real LinkedIn and GitHub URLs;
   and at least 10 evidence-backed Experience bullets.
7. The research role must use the vacancy posting plus at most two primary company
   sources in one pass. Exceed that budget only for a critical unresolved eligibility
   or company-identity fact and record the reason in its handoff. After all three Wave 1
   handoffs finish, the main agent must reconcile conflicts, reject unsupported claims,
   and synthesize the final vacancy-specific `cv.md` without repeating the research.
8. Start Wave 2 only after `cv.md` is final. Run three independent roles in parallel
   when slots are available, with exclusive ownership of one final file each:
   - cover letter: receive this vacancy, final CV, verified `parts/research.md`, and only
     the candidate evidence required to ground the selected stories; invoke the
     highest installed version of `$write-cover-letter` in Draft mode and write only
     `cover-letter.md`. It must contain four to six body paragraphs, two distinct
     evidence stories, and a company-specific hook grounded in verified research;
   - interview preparation: receive this vacancy, final CV,
     `parts/requirements-risks.md`, and verified `parts/research.md`; write only
     `interview-preparation.md` without repeating company research;
   - application analysis: receive this vacancy, final CV, and all three Wave 1
     handoffs; synthesize the required audit, research, requirements, gaps, changes,
     scores, and recommendation and write only `analysis.md`.
   No role may edit another role's file. Keep the
   `$write-cover-letter` workbench internal and run its claim-grounding check. If that
   skill is unavailable, stop; never substitute generic or retired inline letter logic.
9. The main agent must perform one cross-file consistency and claim-grounding pass after
   Wave 2. Resolve contradictions against candidate evidence and the final CV without
   starting another broad drafting loop. If subagents or enough slots are unavailable,
   execute the same Wave 1 roles, main CV synthesis, and Wave 2 roles sequentially with
   the same file ownership and boundaries. Do not claim that the repository or current
   task switched models.
10. Do not let a role reread unneeded candidate sources, other handoffs, the full
   registry, or another vacancy directory. For a batch, each role still owns exactly
   one vacancy-keyed file. Agents may be
   distributed across vacancies, but no agent may combine evidence, research, handoffs,
   or final artifacts from different vacancies. Complete all four final drafts for the
   default scope, or only the explicitly selected draft, under its own
   `.codex-work/application/<vacancy-directory>/`.
11. Before validation, write `quality.yaml`, schema version 1, in the vacancy draft:
    `workflow: two-wave`; cover-letter skill name, version, and completed workbench;
    two evidence stories with candidate sources; company-motivation fact and source URL;
    and final claim grounding plus cross-file consistency results.
12. After the main consistency pass, run the vacancy's single combined deterministic
   draft check:
   `python run.py validate-application <vacancy-directory> --input .codex-work/application/<vacancy-directory> [--document <document>]`.
   Do this once per selected vacancy after drafting is complete, not after each wave or
   file.
   The validator checks the quality contract, required handoffs, structure, minimum word
   counts, provenance, and hashes before publication. If it fails, correct only that
   vacancy and rerun its validator.
13. After every selected draft passes, publish the verified batch once with
    `python run.py prepare <selector-1> [<selector-2> ...] --input .codex-work/application --workflow prepare --model-profile <selected-profile> [--document <document>]`.
    The deterministic publisher resolves every selector before publication and reads
    each package only from its matching vacancy-keyed draft directory. A legacy
    single-vacancy call may still pass that vacancy's draft directory directly. If DOCX
    conversion fails, correct only that deterministic issue and rerun publication.
    Current selected documents are skipped. For full scope, confirm all six application
    artifacts, upload-friendly CV copies, and `manifest.yaml`; for single-document
    scope, confirm only that document's canonical and derived outputs plus the manifest,
    and verify other existing artifacts were unchanged. Confirm the manifest retains the
    quality contract, provenance, word counts, and hashes.
