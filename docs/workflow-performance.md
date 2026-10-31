# Workflow performance review — 2026-10-31

This review covers collection, normalization and deduplication, operational storage,
analysis and preparation handoffs, indexing, catalog generation, archival,
notifications, backup, and repository publication. The implementation targets
repeatable excess work found in those paths. It does not claim that every source
collector or production workload has been profiled.

The baseline is commit `c90369369e4d8580e5bcede00cd633b7b9964b01`.
Three separate Quick council advisors assessed the options, followed by anonymized
peer review. Their agreement guided prioritization; code traces, measurements, and
regression checks supply the evidence. Two non-author reviewers reviewed the code.

## Observed pipeline and decisions

The successful [collection run 41175346968](https://github.com/ValentinNikolaev/job-intelligence/actions/runs/41175346968)
provides the following step durations. These are sequential step timings, not an
attribution of all time to Python or MongoDB. In particular, the 26-second reindex
step is separate from the 108-second collection step.

| Flow | Evidence and decision |
| --- | --- |
| Collection — 108 s | Source fetching already runs concurrently and persistence uses batches of 50 with a writer lease. Preserve concurrency, batch limits, source ranking, and source failure handling. Use existing fetch/store timing events before tuning remote calls. |
| Normalization and deduplication | Exact source and fingerprint indexes already exist. Cached URL matching still scanned every cached vacancy, and cache replacement scanned every index bucket. Add a canonical URL index and update only the old/new keys. Keep company/title guards and refuse ambiguous merges. |
| MongoDB storage | Preserve revision checks, transactions, writer fencing, and batch invalidation. Reuse documents only within the current read operation; introduce no cross-operation document cache. |
| Index — 26 s | The full vacancy query already contains matches, but index generation reread each match one or two times. Validate and render the embedded matches from the same query. |
| Triage — 7 s; catalog — 3 s; report — 8 s | These paths already reuse batch/catalog snapshots. Preserve existing behavior; no measured justification for redesign. |
| Analysis | Exact ID resolution could enumerate the registry and then fetch individual metadata records. Route it through the canonical selector query, preserving direct-directory priority. Sealed packs, freshness checks, scores, and prompts are unchanged. |
| Preparation and document validation | Each explicit selector previously fetched all active records. Use an indexed ID/directory query. Materialize the four operational fields from one MongoDB document to avoid eight reads and mixed revisions. Keep eligibility and document quality gates. |
| Archival — 15 s across four steps | Logical archival already checks revisions and retains artifacts. Keep the existing categories, retention policy, and leases. Combining stages requires a separate failure/retry design and workload evidence. |
| Notifications | Delivery suppression scans receipts and maintains delivery identity. No measured bottleneck justifies changing that durable contract. No messages were sent during this review. |
| Backup and recovery | Backup holds the writer lease while snapshotting and verifying artifacts. It materializes payloads in memory before writing ZIP parts; the part size is not a peak-memory bound. Measure memory and lease duration before a streaming redesign. |
| Tests — 41 s in CI; publication | Keep full deterministic checks and the reviewed finalizer. Local Windows timings are not comparable to CI runner timings. |

## Controlled measurements

Measurements used Python 3.14.6 on Windows and an isolated local MongoDB 8.0 replica
set with randomized disposable databases. No production database was queried or
modified. Index fixtures contained 100 active records with valid matches; the URL
fixture contained 1,000 records from one company and performed 100 role lookups.

| Operation | Baseline | Changed implementation |
| --- | --- | --- |
| Index, 100 matched vacancies | 1 list + 200 document reads; 1.655 s | 1 list + 0 document reads; 0.012–0.013 s |
| Four-field vacancy snapshot | 8 document reads; 0.075 s | 1 document read; 0.012–0.015 s |
| 100 URL lookups over 1,000 cached records | 1.009 s | 0.0010–0.0018 s, plus 0.010–0.014 s to build the URL index |
| One exact selector in 100 MongoDB records | Full active-record enumeration | Query execution stats: 1 document and 1 index key examined, 1 result |

These small local samples demonstrate reduced work. They are not production
speedup promises: remote latency, source response sizes, cold caches, and shared
board URLs change the result. URL lookup still inspects every candidate sharing a
canonical URL, as required to detect ambiguity. MongoDB collection already uses
bounded candidate batches, so its end-to-end gain may be smaller than the isolated
lookup gain.

## Verification and preserved contracts

- Index output is byte-identical across YAML and MongoDB fixtures, including an
  absent match, escaped title, sorting, and unchanged-file detection. Invalid
  match scores or recommendations leave the previous index intact. A new MongoDB
  scan overrides an older registry cache, including when the result is empty.
- Snapshot tests check a single revision, content-addressed reuse, changed-input
  separation, absent fields, and refusal to use frozen operational files.
- Selector tests cover ID/directory collisions, matching's directory priority,
  active/archive filtering, batch behavior, missing records, and real MongoDB queries.
- URL tests cover canonical aliases, official apply URLs, shared-board guards,
  ambiguous matches, removal of obsolete keys, and creation/update paths. After
  index construction, 100 lookups normalize 100 incoming URLs rather than the
  entire registry repeatedly.
- Two regression checks were also run against the unchanged baseline modules in
  an isolated Python process. They failed on the intended excess-read assertions
  and pass with the changes. The authoring worktree was not reverted for this check.

The baseline full suite passed 928 tests with 20 integration tests skipped.
The final suite passed all 962 tests in 164.921 seconds with the disposable
replica set and no skips. `python run.py doctor --ci` passed, and the runtime/config
scan found no prohibited model API integration. The independent match-policy gate
passed all 28 pair comparisons / 56 judgments with no failures or unresolved ties.
Run the complete suite with a disposable replica set to include MongoDB behavior:

```powershell
$env:JOBINTEL_TEST_MONGODB_URI = 'mongodb://127.0.0.1:27028/?replicaSet=rs0&directConnection=true'
python -m unittest discover -v
```

The focused checks are `tests.test_registry_lookup`,
`tests.test_storage_read_efficiency`, and `tests.test_vacancy_selectors`.
Changing `jobintel/matching.py` also invokes the finalizer's independent synthetic
match-policy evaluation gate, even when the change only affects selector lookup.
Production catalog regeneration is unnecessary for these output-preserving code
changes; catalog and index behavior are exercised by the tests.

## Next measurements, in priority order

1. Compare the next scheduled reindex step and collection fetch/store events with
   the linked baseline. Capture workload counts alongside durations; one faster
   run alone does not establish a general speedup.
2. Profile analysis pack assembly if it becomes material. It currently reloads
   profile/vacancy inputs for freshness and pack creation. Any reuse must bind
   one pack to one profile version and preserve publication-time revalidation.
3. Measure peak backup memory and writer-lease duration against representative
   artifact sizes before streaming payloads. Require restore/hash parity and
   interrupted-write recovery before changing that path.
4. Revisit receipt indexing or consolidated archive scans only when their measured
   cost warrants the extra invalidation and recovery rules.
