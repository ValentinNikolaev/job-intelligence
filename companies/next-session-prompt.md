# Prompt for the next Codex task

Use GPT-5.6 Luna with low reasoning, following this repository's `AGENTS.md` and `$job-intelligence-workflow` boundaries. Work only inside the new `companies/` directory and related documentation; do not add any company to `sources/custom/config.yaml` or another vacancy source. The user will handle source registration in a separate session.

The initial ReadyToTouch snapshot is in `companies/README.md`, one company card per entry under `companies/records/`, and `companies/dev-blogs.md`. There are 291 companies whose ReadyToTouch `remote` flag is true. Treat ReadyToTouch as discovery metadata, not as verification of current company links or current remote hiring policy.

For each company card:

1. Verify the official company domain, careers link, company/about page, and developer blog from the company's own website. Keep source URLs and the date checked. Preserve ReadyToTouch's original links in provenance when correcting them.
2. Follow the careers link and identify the recruitment platform/ATS (for example Greenhouse, Ashby, Lever, Workable, SmartRecruiters, Factorial, or a custom careers system). Record the observed engine and evidence URL. Distinguish confirmed engine from an unresolved or inaccessible page; do not infer it from URL text alone.
3. Verify social profile links from official company pages or other strong primary evidence. Do not treat ReadyToTouch's `verified` flag as independent live verification. Leave missing or ambiguous fields blank and explain uncertainty briefly.
4. Update `companies/dev-blogs.md` as a clean subscription list with verified developer-blog URLs, company names, and a concise type/platform hint where evident. Keep it useful for manually subscribing; do not subscribe, log in, or create accounts.
5. Keep one Markdown card per company and the directory separate from all vacancy-source configuration. This work is research only: do not collect/post vacancies, add custom sources, alter MongoDB, or initiate applications.

Use deterministic browsing/fetching for the obvious official pages and reserve model reasoning for resolving ambiguous identity, URL, or careers-engine cases. Keep a concise checkpoint so the work can continue in small batches without repeating completed verification. Report totals for verified careers links, identified engines by type, developer blogs, and unresolved cases. Before any repository publication, follow the repository's required checks and GitHub CLI finalization rules.
