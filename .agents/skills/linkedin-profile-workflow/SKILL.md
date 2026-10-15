---
name: linkedin-profile-workflow
description: Run Job Intelligence LinkedIn profile audits, rewrites, Skills alignment, and Featured proof tasks using current candidate evidence and the published LinkedIn skills. Not vacancy intake, CV or letter preparation, feed content, or automatic LinkedIn publication.
---

# LinkedIn Profile Workflow

Read repository `AGENTS.md`, the
[LinkedIn prompt](../../../prompts/linkedin-profile.md), and
[integration configuration](../../../config/linkedin-profile.yaml) first.

Use `linkedin-profile-optimizer` for the requested profile audit, rewrite, or
keyword map. Use `linkedin-featured-proof` only for requested proof plans, copy,
or asset files. Prefer the highest installed `agent-plugins@valentin-agent-plugins`
version that contains the selected skill. Read its full SKILL.md and relevant
references; a skill name in the prompt is not evidence it was loaded.

If the active plugin lacks a selected skill, use GitHub CLI to read that skill's
generated Codex package and needed references from the repository and exact
revision in the configuration. A verified local checkout of that revision is
also suitable. Record the actual source and revision; do not pretend the active
chat's plugin was upgraded. Do not install packages, execute fetched scripts,
vendor copies into this project, or silently substitute generic drafting.
If neither source can be read, stop only the dependent operation and report what
is unavailable. The unaffected audit or asset work can continue when possible.

Follow the prompt's candidate and vacancy boundaries. Read relevant memory as
source-discovery context, then verify current primary evidence. Keep sources
immutable and drafts private under `.codex-work/linkedin/`. Never route profile
work through the application publisher or apply CV-only employer windows and
bullet quotas. No model API calls or automatic external writes are part of this
workflow.

Return the requested result, coverage and unresolved evidence issues, actual skill
provenance, and checks performed. Do not mark an unseen profile section or an
unrendered export as reviewed. Existing explicit authorization for a specific
external action remains valid; preparation alone does not authorize publication.
