# LinkedIn profile and Featured proof workflow

Use this only for an explicit LinkedIn profile/Skills/Featured request. Integrating
the workflow does not itself request a new personal profile or permit LinkedIn
publication. Read the project skill
[`linkedin-profile-workflow`](../.agents/skills/linkedin-profile-workflow/SKILL.md)
and [configuration](../config/linkedin-profile.yaml). The configuration is read by
the Codex workflow; it does not register a new `run.py` command or application mode.

## Resolve the request and load the selected skills

- Establish audit, rewrite, keyword map, proof plan, copy, or asset production;
  preserve any section-only scope. Determine audience, goal, language, and target
  roles from the user's context. Ask one compact question for missing essentials,
  while continuing work that does not depend on the answer.
- Load `linkedin-profile-optimizer` and/or `linkedin-featured-proof` according to
  the project skill. Record installed version or pinned-source revision. Read
  referenced evidence/platform/format guidance for the selected operation.
- Use the already selected Codex model. For this standalone workflow the repository
  default is GPT-6 Sol/medium unless the user selected another profile. Do not label
  this work as `prepare`, add a publisher model label, or claim to switch models.
- Read current project instructions and relevant available memory. Memory points
  to decisions and sources; it does not verify current facts. Do not write memory.
  If repository files will change, use an isolated worktree and the repository
  preflight/finalizer. Chat-only review or ignored drafts need no publication.

## Establish current evidence and voice

Read configured candidate context and the applicable candidate-source selection
(`CANDIDATE_PROFILE_PATHS` or the repository's default source selection). Do not
dump the credentials file to discover that setting. Open only the candidate files
needed for selected claims, including relevant later corrections.

`registry/candidate/linkedin-profile.md` is an immutable source snapshot, not an
output destination or proof of current live wording. Request a current export,
pasted text, or accessible profile view when that distinction affects the audit.
Mark unseen sections `not reviewed`; do not infer them from a handle or old CV.

Use `registry/evidence/achievements.yaml` as an index, check current primary-source
quotes/hashes, status, attribution, and public-use limits. Only verified entries
can support copy. Apply the current quality contract's evidence principles:
problem, personal contribution, scope, decision, consequence, delivery status, and
measurement context. Keep team ownership, units, time windows, and qualifiers.
Neither a working dependency nor a keyword establishes production experience.

Resolve `social-voice.md` through `config/application-review.yaml` and read its
relevant current sections. Employer-letter and comment-only procedures do not
become profile structure requirements. If a required voice source is unavailable,
report it and do not claim the personal voice check passed.

Keep an internal claim ledger with final text, exact `candidate_quote`, source
locator/hash, verification status, employer/role/period, measurement qualifications,
and public-use decision. Contradictions and unknown measurements stay unresolved;
omit disputed claims and continue supported work. Never add a plausible metric,
upgrade “helped” to “led,” or convert a demo into employment experience.

## Optional comparison with selected vacancies

No storage operation is needed for candidate-only work. When the user explicitly
selects vacancies for alignment, read current storage instructions, check relevant
same-project activity, and use the permitted read-only `storage doctor` and
`storage vacancy-context --selector <id-or-directory> --output <ignored-path>`
commands. Use the explicit selectors only. Do not read frozen registry job text as
a fallback or expand to an automatic queue. Stop only the affected comparison if
storage is unavailable; retain a clearly labeled candidate-only result if useful.

Keep each posting's `jd_quote` and source identity separate, with importance,
`stated|structural|inferred` basis, candidate match, and intended profile placement.
Inferences have no fabricated source quote. Multiple postings can inform this
profile study; never feed their pooled keywords into a selected vacancy's match or
application package. State the sample size and limits of any market inference.

Propose OpenTelemetry/OTel, eBPF, gRPC, resilience, or idempotency only with relevant
evidence. Check exact selectable Skills labels in current authorized UI or official
sources; otherwise mark taxonomy unverified. Do not replace core Go/PHP skills
merely to add niche terms or promise Recruiter priority. Check platform limits and
UI support before prescribing pinning, skill associations, or role-media links.

## Produce and check the selected result

Use the loaded library skills for profile structure and proof production. Preserve
source-backed titles and chronology without importing CV-only employer windows,
bullet quotas, application document minima, or cover-letter structure. Keep audit
findings visible when requested; a rewrite does not need a compulsory audit report.

Return chat copy by default. If files were requested, write only the selected
deliverables under `.codex-work/linkedin/<run-id>/`, preserving previous runs:

- `profile.md` or `audit.md` for the requested operation/sections;
- `keyword-map.yaml` when vacancy alignment was selected;
- private `claims.yaml` review notes and `review.yaml` provenance/check receipt;
- requested Featured editable source, exports, and text equivalents in `featured/`.

These are standalone profile artifacts, not schema-3 application claims or an
application manifest. Do not pass them to `publish-application`. A review receipt
records actual skill sources, source hashes, voice source/hash, observed coverage,
checked text counts, taxonomy status, link access, privacy checks, and export QA
only when performed. Never mark a check passed because a file exists.

Check every final assertion for support, attribution, uncertainty, and disclosure.
Inspect actual PDF/PNG renders and extracted text before marking produced assets
ready. Separate private excerpts and notes from public copy; exclude internal URLs,
unapproved client details, contacts, and private export metadata. Do not create
asset files for a plan/copy-only request. If tools are unavailable, label unfinished
exports and return usable copy without claiming completed asset production.

Do not modify candidate sources, evidence status, memory, vacancies, applications,
catalogs, notifications, or external accounts as a side effect. Sending requests,
posting, uploading, profile/visibility edits, or evidence persistence require the
user's explicit instruction for that action; retain existing authorization without
asking again. Repository publication of this integration is separate from publishing
personal profile content. No application packages or catalogs need regeneration
for this integration alone.
