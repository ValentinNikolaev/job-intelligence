---
name: generate-vacancy-catalog
description: Generate or refresh the repository's human-readable vacancy catalog from canonical registry metadata and existing application artifacts. Use after collection, analysis, preparation, or a manual vacancy-status change, and whenever the user asks to list, index, summarize, or rebuild the vacancy catalog. Must run in a separate independent agent or process and may modify only generated files under catalog/.
---

# Generate Vacancy Catalog

Run the generator only as a separate operating-system process. A normal `python run.py catalog` invocation satisfies this isolation; do not import and call `jobintel.catalog.generate_catalog` from the workflow process. No model agent is needed for this deterministic step.

## Generate

1. Read `AGENTS.md` and preserve all user changes.
2. Treat `registry/jobs/*/meta.yaml` as canonical. The repository uses `meta.yaml`; never create a parallel `metadata.yaml`.
3. Run `python run.py catalog`. This deterministic command scans all vacancies, validates status history, sorts newest first, computes status totals, selects single-file or monthly output, and writes relative links to available artifacts.
4. Inspect `catalog/index.md` and any generated monthly files. Confirm totals, newest-first ordering, relative links, and missing-artifact markers.
5. Confirm the run changed no files outside `catalog/`. Report an error rather than repairing or modifying vacancy metadata.

## Boundaries

- Never modify `registry/`, vacancy content, `meta.yaml`, `job.md`, company research, match files, CVs, cover letters, application analysis, or interview preparation.
- Never infer or update a vacancy status. Status changes are manual and belong to the vacancy-management workflow.
- Keep existing status history untouched.
- Do not copy artifact content into the catalog; link to files when they exist and show unavailable artifacts as `—`.
- Do not add monthly files unless the deterministic generator selects monthly mode.
