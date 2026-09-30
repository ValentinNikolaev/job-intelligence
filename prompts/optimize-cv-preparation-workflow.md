# Optimize CV preparation throughput without weakening evidence gates

## Objective

Reduce elapsed time and failed reruns for an explicitly selected CV-only preparation
batch while preserving every existing safety boundary: MongoDB-only metadata,
candidate-evidence grounding, per-vacancy isolation, the five-year role-depth rule,
DOCX fidelity, and non-force publication.

Work from an isolated managed worktree at the current remote `main` head. Do not
prepare, modify, submit, or change the lifecycle status of any vacancy. This task
improves the process and its deterministic checks only.

## Baseline problem to address

The six-CV batch on 2026-09-27 spent substantial time on avoidable stop-and-retry
cycles:

1. The isolated worktree had no usable `MONGODB_URI`, so workflow execution failed
   before the database health check.
2. Drafts reached the combined validator before simple structural defects were caught:
   missing handoff headings, evidence-role incompatibilities, stale artifact hashes,
   and candidate quotes that did not match the source text byte-for-byte.
3. PDF rendering capability was discovered after DOCX generation. A missing renderer
   made visual page-budget review impossible in that environment.
4. Repository finalization repeatedly rebuilt large binary DOCX patches and then
   encountered an upstream conflict in files changed by the preview/finalizer work.

Do not turn these into weaker checks, silent fallbacks, or a permission to use YAML
metadata. The improvement is earlier deterministic feedback and less duplicated work.

## Required design

Implement and document the following bounded flow.

### 1. One preflight command

Add one deterministic, read-only preflight command for selected preparation batches.
It must complete before agents draft any document and report machine-readable JSON.
It must check, at minimum:

- the selected IDs are explicit, unique, and within the configured batch maximum;
- the selected workflow/model profile is valid and every match is fresh for it;
- MongoDB configuration is available to this worktree and `storage doctor` succeeds;
- the DOCX converter, its options, and the configured preview renderer are available;
- the preview command can report a clear `unavailable` result without writing a
  canonical package when rendering support is absent;
- the worktree is isolated and its remote base is current before model work starts.

The command must fail closed before drafting if a required gate is unavailable. It may
write only ignored work files. It must never print credentials or read a frozen YAML
metadata fallback.

The command is `python run.py prepare-preflight <selector-1> [<selector-2> ...]
--workflow prepare [--model-profile <profile>] [--document cv]`. Its MongoDB context
snapshot belongs only under `.codex-work/vacancy-snapshots/`; it is not a publication
target or a fallback to a shared checkout.

### 2. Draft-lint before the combined validator

Add a fast, deterministic lint command for one draft directory. It should reuse the
same parser and evidence indexes as publication rather than duplicate business rules.
Before `validate-application`, it must identify all of these in one report where
possible:

- required evidence-map markers and final-CV linkage;
- malformed, missing, or stale artifact hashes and CV audit anchors;
- claim employer/role values incompatible with any referenced evidence entry;
- candidate and job quotes that are not exact source substrings;
- Experience bullet counts at the five-year cutoff, duplicate normalized bullets, and
  Technologies lines incorrectly relied on as bullets;
- references to unverified, retracted, or cannot-confirm evidence.

The combined validator remains authoritative. The lint only moves predictable errors
earlier and must have output stable enough for a Codex task to repair without
guesswork.

### 3. Preview and publication reuse

Keep the preview receipt bound to the exact Markdown, converter code, and DOCX options.
Make the operator-facing result explicit: page count, render availability, source and
DOCX hashes, and whether publication reused the preview. Do not reuse a preview after
any relevant input changes. Preserve the two-page limit and require a visual review
when a renderer is available.

### 4. Finalization efficiency and conflict safety

Keep one reviewed commit and non-force publication. Improve the finalizer so it:

- obtains the remote head once before expensive binary patch generation;
- reports the exact paths overlapping with a remote advance before attempting a rebase;
- avoids recomputing an unchanged binary patch during `review`, `publish`, and
  `publish-api` by reusing a hash-bound review record;
- stops with actionable conflict information rather than leaving an ambiguous
  interrupted rebase; and
- never stages ignored files, secrets, caches, or unrelated worktree changes.

Do not optimize by omitting DOCX blobs, bypassing a diff review, force pushing, or
silently choosing one side of a conflict.

## Verification

Add focused unit tests for each new deterministic gate, including missing MongoDB
configuration, unavailable renderer, invalid batch selection, all listed draft-lint
diagnostics, preview invalidation, cached-patch reuse, and remote-overlap reporting.
Keep existing tests green. Run the full suite and the prohibited-API scan. Update the
workflow skill and relevant operator documentation with the exact command order.

## Completion report

Report measured before/after command counts and elapsed-time categories from a
representative selected test batch. State which optimizations are verified, which
remain environmental prerequisites, and why no evidence, approval, lifecycle, or
publication safety rule was weakened.
