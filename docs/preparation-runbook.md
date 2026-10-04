# One-pass preparation and repository handoff

Use an isolated managed worktree. Run `python scripts/finalize_repository.py preflight`
before reading vacancy evidence or drafting. It refuses local changes and updates a
clean checkout to the remote head. Keep shared service files, open documents, and
parallel work in their existing checkouts.

For a selected CV batch, reuse a current match from any approved analysis profile
when the vacancy, candidate, and workflow inputs are unchanged. Reuse vacancy
research only when its posting, company sources, and candidate evidence have not
changed. Never reuse a
different vacancy's research or wording. Finalize all selected CV drafts under
`.codex-work/application/<directory>/` before validating any of them.

Before reading vacancy evidence or assigning an editor, run one fail-closed batch gate:

```text
python run.py prepare-preflight <selector-1> [<selector-2> ...] --workflow prepare --model-profile <profile> --document cv
```

It checks the selected explicit batch, the configured storage adapter, canonical selector
resolution, required MongoDB metadata, approved-profile match freshness, score eligibility,
and `hard_rejection`. For a MongoDB backend it writes a minimal `meta.yaml`, `job.md`,
`match.yaml`, and optional company view only under `.codex-work/vacancy-snapshots/`.
Its `shared_candidate_context` lists the immutable profile sources and a verified-only
evidence packet under ignored `.codex-work/preparation-shared/`. Read those shared
candidate facts once for the selected batch. Keep each vacancy's posting, match,
research, claims, CV, and quality receipt independent; never copy a vacancy-specific
judgment or paragraph into another package. For each CV, explicitly review every
relevant source role in the ten-year Experience window and record why it appears
or is omitted; role-depth checks alone cannot detect a missing employer.
Never copy metadata from a shared checkout. A nonzero preflight ends the run before any
draft, preview, conversion, or canonical package path is created.

For each final CV, run:

```text
python run.py validate-application <directory> --input .codex-work/application/<directory> --document cv
python run.py documents preview-cv .codex-work/application/<directory>/cv.md
```

`validate-application` first reports aggregate lint defects, including trailing
whitespace and stale quality hashes, then runs the full grounding contract. Fix
these defects before any DOCX or PDF conversion. The preview receipt includes
`layout_warnings` when a role heading or its bullets span pages; use them to
adjust the source before the required visual review. An empty warning list is
not a visual approval.

The preview uses the same Markdown-to-DOCX converter and options as publication.
It stores the DOCX, PDF, page images, and receipt under `.codex-work/previews/`.
The receipt reports page count and extractable Experience bullets. Open every page
image and check clipping, density, headings, breaks, and blank pages yourself;
`visual_review: required` is deliberately not an automated approval. A changed
draft or converter option gets a new preview. An open canonical DOCX is never used
as a preview target. Publication reuses the preview DOCX only when the staged
Markdown, converter implementation, script, options, and artifact hash still match its receipt;
the ordinary export validator still checks the copied document. The PDF check needs `pdfinfo` and `pdftoppm`; conversion uses
LibreOffice, or Word on Windows when LibreOffice is absent.

After all affected drafts pass their one validation, issue one explicit selected
batch `python run.py prepare ... --input .codex-work/application --workflow prepare
--model-profile <profile> --document cv` call. Fix and recheck only an affected
draft if an edit is needed. Run the catalog in its own process, the required full
suite, evidence checks, and the prohibited-API scan. Do not rerun the full suite
after a successful gate unless a relevant code change requires it.

CLI commands automatically record UTC boundaries and elapsed seconds for preflight,
lint, validation, preview, DOCX conversion, PDF export, page rendering, and publication
under ignored `.codex-work/preparation-timing/events/`. Mark model and human work
at its real boundaries with `python run.py timing start editorial_drafting --vacancy
<directory>` and `python run.py timing stop editorial_drafting --vacancy <directory>`;
the same commands accept `analysis`, `visual_review`, and `finalization`. Run
`python run.py timing report` to create `.codex-work/preparation-timing.json` with
events and stage totals. Never infer human drafting from command time. Include a
before/after table with the exact fixture or batch used and the slowest remaining
stage; note overlapping batch work rather than summing it as serial elapsed time.

For repository publication, run `python scripts/finalize_repository.py review`.
Inspect the complete binary-capable `.codex-work/finalization/review.patch` and its
listed paths. It stages only normal Git project changes, detects whitespace errors,
and records the reviewed blob IDs. Then run `python scripts/finalize_repository.py
publish --subject "<specific imperative sentence>" --body "<run metadata>"`.

Never construct a GitHub tree, commit, or branch-ref update directly with `gh api`.
The finalizer's `publish-api` command is the only permitted API fallback: it starts
from the current remote base tree, applies only reviewed paths, and verifies the
resulting tree still contains the workflow's required repository files.
This creates one local commit and makes a non-force push. A concurrent remote
advance is fetched and integrated into that unpublished commit; publication stops
for review if integration changes a reviewed blob or conflicts. On partial failure,
keep the isolated checkout and its review files for diagnosis. A transient fetch or
push failure can be retried with the same `publish` command after the condition is
fixed; it verifies the existing unpublished commit instead of creating a second one.
Verify the reported
remote SHA and clean local status. Never synchronize the dirty authoring checkout
with `gh repo sync`; a separate clean checkout may be synchronized without force.

If the host cannot push with Git, leave the clean local commit in place. Run
`python scripts/finalize_repository.py review-commit`, inspect the complete
`.codex-work/finalization/api-review.patch`, and run
`python scripts/finalize_repository.py publish-api`. This fallback uploads exact
reviewed blobs with `gh api`, builds one commit on the current remote tree, and
updates its ref without force. It refuses a remote change to a reviewed path.
Create or use a separate clean checkout at the published commit for local
synchronization and verification; do not sync the authoring checkout over its
distinct local commit.
