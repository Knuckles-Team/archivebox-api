---
name: archivebox-web-archiving
skill_type: skill
description: >-
  Capture and re-archive web pages with ArchiveBox through the archivebox-mcp
  server: add URLs (tags, depth, plugins), create single snapshots or crawls,
  re-archive existing snapshots, schedule recurring captures, and file evidence
  captured elsewhere as archive results. Use when a URL must be kept as a
  durable, re-checkable copy. Do NOT use to browse what is archived
  (archivebox-snapshot-search), to curate tags or remove captures
  (archivebox-archive-administration), or for KG ingest (archivebox-kg-ingestion).
license: MIT
tags: [archivebox, web-archiving, snapshots, crawl, mcp]
metadata:
  author: Knuckles-Team
  version: '0.2.0'
---
# ArchiveBox web archiving

One typed tool per ArchiveBox operation. Every tool takes its arguments
directly (no `action`, no `params_json`).

## Tools

| Tool | Use |
|------|-----|
| `archivebox_cli_add` | Add one or many URLs as one crawl; one snapshot per URL. |
| `archivebox_create_snapshot` | Create exactly one snapshot for a URL (optionally in a crawl). |
| `archivebox_create_crawl` | Create a crawl with seed URLs, depth, label, notes, tags. |
| `archivebox_cli_update` | Re-archive the snapshots a selection matches. |
| `archivebox_patch_snapshot` | Reschedule a snapshot, change status or replace its tags. |
| `archivebox_patch_crawl` | Retag, reschedule or run an action on a crawl. |
| `archivebox_cli_schedule` | Create, list (`show`) or clear recurring captures. |
| `archivebox_create_archiveresult` | File output captured by another tool (base64 files) on a snapshot. |
| `archivebox_patch_archiveresult` | Add files or change status/output of an archive result. |
| `web_fetch` / `web_extract` | Shared web-source contract: archive-then-read one page. |

## Procedure: archive URLs

1. Check for an existing capture: `archivebox_get_snapshots(url=<exact url>)`.
   Re-adding the same URL creates a second snapshot only with `update=true`.
2. `archivebox_cli_add(urls=[...], tag="<tag1>,<tag2>", depth=0)`.
   - `depth=1` also captures each page's outlinks; keep `max_urls` set when you
     use it (for example `max_urls=25`).
   - `plugins` limits capture to named plugins, for example
     `"wget,singlefile,pdf,screenshot,readability,htmltotext,title"`; empty runs
     the instance defaults.
3. Capture is asynchronous. Poll `archivebox_get_snapshots(tag=...)` until each
   snapshot's `status` is `sealed`, then read results
   (`archivebox_get_archiveresults(snapshot_id=..., status="succeeded")`).

## Procedure: refresh and schedule

- Re-capture a tag's pages: `archivebox_cli_update(tag="<tag>")`.
- Re-capture one snapshot: `archivebox_cli_add(urls=[], snapshot_ids=["<id>"], update=true)`.
- Recurring capture of a feed or page:
  `archivebox_cli_schedule(add=true, every="day", import_path="<url>", tag="<tag>")`;
  list with `show=true`.

## Gotchas

- Results come back as the upstream JSON; a failed call returns
  `{status_code, error}` with ArchiveBox's message.
- `urls` is always a list. Tags are a comma-separated string in `cli_add` and a
  list in `create_snapshot` / `create_crawl`.
- Writes are only accepted on the instance's configured hostname
  (`ARCHIVEBOX_BASE_URL`); a different host answers 403 "control plane disabled".
- Never add login-only, paywalled or private pages without the owner's approval:
  capture runs with the `Default` persona and stores what it sees.
