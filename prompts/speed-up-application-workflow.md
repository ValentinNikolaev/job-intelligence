# Speed up application preparation and make repository synchronization reliable

Improve the Job Intelligence preparation workflow end to end, with priority on the
six-CV editorial rebuild path. Read `AGENTS.md`, `config/codex-workflows.yaml`,
`prompts/job-intelligence-workflow.md`, the `$job-intelligence-workflow` skill, and
the existing publication and document-conversion code before changing anything.
Measure the current stages once so that the result can be compared with a real
baseline. The recent six-CV run spent about 20 seconds on the full unit suite;
focus on repeated drafting/publication, document preview, diff construction, and
repository synchronization rather than weakening tests.

## Repository finalization

The current sequence creates a commit on GitHub through `gh api` while the same
files remain uncommitted in the authoring checkout. A subsequent non-force
`gh repo sync` therefore refuses to overwrite those local files. Remove this
structural conflict. Prefer an isolated managed worktree with a local commit and
non-force push, after explicitly updating the repository's `gh`-only policy in
`AGENTS.md` to permit the narrowly scoped local Git operations this requires.
Continue using `gh` for remote inspection. If a local push is not viable, retain
`gh api` publication but synchronize only a separate clean checkout; never treat a
dirty authoring checkout as a failed publication.

- Preserve concurrent remote changes. On a changed remote head, integrate them
  safely and retry without a force push or destructive reset.
- Never discard, stash, delete, or overwrite unrelated staged, unstaged, untracked,
  ignored, or parallel-session work. Keep task output isolated from shared service
  files and open documents.
- Update every affected instruction, skill reference, and automation prompt so the
  preflight and finalization procedures agree. Keep one reviewed commit containing
  all real project changes and a clear remote publication result.
- Make the finalization path reusable and deterministic. Handle Windows long paths,
  CRLF-only differences, binary files, ignored work directories, concurrent branch
  advances, and partial failures. Do not rebuild an ad hoc comparison/publisher in
  each Codex task.

## One-pass CV preparation and review

- Add or document a draft preview path that uses the same Markdown-to-DOCX options
  as publication, writes previews under `.codex-work/`, and checks page count and
  extractable Experience text before the canonical package is published. Keep the
  human visual review of rendered pages. An open canonical DOCX must not prevent
  preview or cause a silent overwrite.
- Validate each finalized vacancy draft once, then publish the selected batch once.
  After a real edit, recheck only affected drafts and previews. Reuse fresh,
  approved-profile match evidence and completed vacancy research when their inputs have
  not changed; never relabel an old match or reuse another vacancy's content.
- Record elapsed time for analysis, editorial drafting, validation, conversion,
  visual review, diff review, and publication. Report before/after timings from a
  representative run and identify any remaining bottleneck. Keep the full required
  test suite, evidence checks, catalog generation, and prohibited-API scan.

## Acceptance

Demonstrate a complete preparation or realistic fixture run from an isolated
checkout: preview, validation, one publication, remote-head verification, and a
clean local state or an explicitly separate clean synchronization checkout. Test
the refusal/concurrency paths without damaging the shared checkout. Verify that
unrelated files survive and that the resulting remote commit contains exactly the
reviewed project changes. Do not alter vacancy statuses, candidate facts, or
application content merely to exercise this workflow. Do not add any OpenAI
Platform API integration. Publish the workflow change under the repository rules
in force at the time of the change; do not open a PR unless requested.
