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
   When the candidate explicitly requests a CV-only refresh for a named vacancy
   whose existing application already has a CV, a fresh same-profile
   `possible_match` below the normal score threshold may be refreshed with
   `--document cv --allow-low-score-cv-refresh` on both `pending prepare` and
   `prepare`. State the score and material gaps to the candidate. This narrow
   override does not admit a `not_match`, hard rejection, new application, other
   document, or automatic preparation selection.
4. Process each printed vacancy independently. For the current vacancy, read its
   `meta.yaml`, `job.md`, optional `company.md`, the configured candidate sources, and
   `prompts/vacancy-application.md`. Do not read non-selected vacancies, compare selected
   vacancies, or carry company research, requirements, keywords, or wording from one
   package into another.
   Consult relevant `registry/candidate/*-experience-inventory-*.md` files during
   evidence review to discover work that may fit the vacancy. Keep delivered work,
   proposals, duties, and unconfirmed figures separate. An inventory note is not
   a verified achievement; anchor every CV claim in a reviewed evidence-bank entry
   backed by direct candidate source or a later candidate confirmation.
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
   and at least 10 evidence-backed Experience bullets (six in compact format). Its
   Summary must be one employer-facing paragraph of 50–110 words that opens with the
   candidate's professional identity. Strip all evidence IDs, source/verification
   commentary, confirmation notes, placeholders, and drafting language from the final
   CV; keep those only in handoffs, `claims.yaml`, and `quality.yaml`. Never duplicate
   or lightly paraphrase an Experience bullet to meet a count or word minimum.
   Apply the mandatory **recent-experience editorial gate** before the CV is final:
   - treat roles ending within the last five years as the primary employer-facing
     narrative; give each such role at least four distinct, evidence-backed bullets
     when the candidate source supports them, and explain any shortfall to the user
     instead of compensating with older experience;
   - ensure those recent roles contain at least 60% of all Experience bullets;
   - keep roles ending more than five years ago compact. For a Senior or Tech Lead
     CV, aim for three distinct, non-duplicative bullets for each displayed role
     within the ten-year window when the sources support them. A role with only one
     or two bullets needs a source review and a deliberate editorial decision; do
     not publish that shape by default or invent another achievement to fill it;
   - count bullets by role and read the finished Experience section as a hiring
     manager would. Reject a draft where a recent role has a single generic bullet,
     or where older roles carry the substantive detail that should describe recent
     work. Do this editorial review even when deterministic validation succeeds.
   For Senior or Tech Lead positioning, also apply the **impact and judgment gate**:
   - lead each Experience bullet with a supported result or consequential change;
     name the candidate's contribution, the system or people affected, and the
     outcome. Use scale or a numeric result only when the source supports it;
     otherwise state the concrete operational or delivery consequence;
   - rank the bullets within each role before finalizing: lead with the strongest
     vacancy-relevant outcome and scope, then architecture judgment, operational
     reliability or security, and cross-team influence as evidence permits. A
     technology implementation or duty should never displace a stronger result;
     record the reason for the chosen order in the CV audit;
   - prefer evidence of architecture decisions and their reason, reliability,
     observability, migrations, simplification, and cross-team influence over a
     list of technologies or planning duties. Never manufacture a trade-off,
     incident, cost saving, team reach, or learning story to satisfy this gate;
   - omit generic duties and repeated claims. If ten distinct outcome bullets
     cannot be grounded, choose `document_format: compact` when the user's
     requested format permits it, rather than padding the standard CV;
   - review every displayed role for senior-level signal: a concrete system or
     organizational consequence, ownership or judgment, and a distinct proof
     point. Reject generic planning, troubleshooting or tool-list bullets without
     a supported consequence. Never split one result into multiple bullets merely
     to satisfy the role count;
   - group Skills by domain, retain only defensible skills relevant to this
     vacancy, and check a rendered PDF against a two-page limit when PDF export
     is available. Keep the optional projects section only if it adds distinct,
     source-backed depth within that limit.
   Before finalizing, surface any additional relevant numbers found in candidate
   sources that have not been candidate-confirmed. Ask the candidate to select
   which figures they can substantiate and how they were measured. If the
   candidate says a question is unclear, explain the metric, scope, personal
   contribution, and measurement source in a focused follow-up; do not treat
   the request for clarification as a rejection. Keep genuinely unanswered or
   uncertain numbers out of the CV; an unattended scheduled task
   records the question and proceeds with supported qualitative outcomes.
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
     `cover-letter.md`. In standard format it must contain four to six body paragraphs (three to six in compact), two distinct
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
   starting another broad drafting loop. As part of that pass, read the final Summary
   as employer-facing copy and reject any evidence labels, audit commentary, gap list,
   source notes, placeholders, duplicated claims, or opening employer anecdote. If
   subagents or enough slots are unavailable,
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
11. Before validation, write `quality.yaml`, schema version 2, in the vacancy draft:
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
    `python run.py prepare <selector-1> [<selector-2> ...] --input .codex-work/application --workflow prepare --model-profile <selected-profile> [--document <document>] [--allow-low-score-cv-refresh]`.
    The deterministic publisher resolves every selector before publication and reads
    each package only from its matching vacancy-keyed draft directory. A legacy
    single-vacancy call may still pass that vacancy's draft directory directly. If DOCX
    conversion fails, correct only that deterministic issue and rerun publication.
    Current selected documents are skipped. For full scope, confirm all six application
    artifacts, upload-friendly CV copies, and `manifest.yaml`; for single-document
    scope, confirm only that document's canonical and derived outputs plus the manifest,
    and verify other existing artifacts were unchanged. Confirm the manifest retains the
    quality contract, provenance, word counts, and hashes.
14. In the user-facing result, include a package-location entry for every successfully
    prepared vacancy. Each entry must contain the vacancy/company label, its direct
    source vacancy URL, the absolute local path to
    `registry/jobs/<vacancy-directory>/application/`, and, when the files were committed
    remotely, a stable URL to that directory pinned to the published commit SHA. If the
    posting is no longer reachable, preserve the recorded direct URL and label it as
    unavailable instead of silently omitting it. For every selected vacancy that was
    skipped or failed, say explicitly that no package was produced and give the reason.
    Do not report only a shared parent directory, catalog link, commit link, list of
    artifact filenames, or vacancy ID: the source URL and per-vacancy package directory
    links are mandatory handoff information.

## Version 2 preparation contract

All new drafts use quality schema 2 and `docs/application-quality.md`. Include the
verified evidence bank, claims ledger, sourced requirement matrix, format selection,
final CV audit and hash-bound review. Read the compact-format overrides in the
application prompt before drafting. Legacy schema 1 stays readable with a migration
notice and does not become current v2 evidence by relabeling. Review actual exported
text and rendered pages; never mark an uninspected file visually reviewed.
