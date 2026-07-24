# Greenhouse source

Greenhouse exposes public company job boards through a keyless Job Board API.
This collector fetches:

```text
https://boards-api.greenhouse.io/v1/boards/<token>/jobs?content=true
```

`content=true` includes the full HTML job description. The collector decodes that
HTML into Markdown, uses the Greenhouse job `id` as `source_job_id`, and keeps
board, department, office, requisition, update, and compliance metadata in
`source_metadata`.

Configure boards in `sources/greenhouse/config.yaml`:

```yaml
boards:
  - token: grafanalabs
    company: Grafana Labs
```

The token is the path segment from the public board URL. For example,
`https://job-boards.greenhouse.io/grafanalabs` uses `grafanalabs`.

Optional filters mirror the Ashby collector:

```yaml
filters:
  remote_only: true
  location_terms: [Germany, Europe, EMEA]
  title_terms: [backend, platform engineer, staff engineer]
```

Remote detection is deterministic and looks for `remote` in the job title or
primary Greenhouse location. Location filtering checks the primary location and
office names.
