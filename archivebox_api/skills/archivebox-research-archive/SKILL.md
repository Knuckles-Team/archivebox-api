---
name: archivebox-research-archive
skill_type: skill
description: >-
  Keep a durable, tagged, re-checkable archive of competitor and market
  research and cite it as evidence. The web fetch connector (webarchiver-mcp)
  captures and extracts each page; archivebox-mcp files a durable copy under
  research tags, confirms the capture, and later answers "what did this page
  say on that date" with snapshot ids, timestamps and plugin results. Use for
  any competitor, pricing, product or market research run that must be
  evidenced or repeated. Do NOT use for one-off reads that need no durable copy
  (use webarchiver-mcp alone) or for archive cleanup
  (archivebox-archive-administration).
license: MIT
tags: [archivebox, research, competitors, market, evidence, archive]
metadata:
  author: Knuckles-Team
  version: '0.1.0'
---
# Research archive: competitor and market evidence

Business goal: every page a competitor or market brief relies on has a durable
archive copy, found again by tag, so claims can be re-checked and changes over
time shown.

## Roles of the two connectors

- **webarchiver-mcp (primary capture, read-only):** `web_links`, `web_crawl`,
  `web_extract`, `web_render`, `web_screenshot` find and read the pages now.
  Follow its `webarchiver-market-research-capture` skill.
- **archivebox-mcp (durable archive):** keeps the copy (HTML, singlefile,
  PDF, screenshot, WARC, text) and its history.

## Tag scheme

Every page of one run gets three tags: `market-research`, the subject slug
(for example `acme-corp` or `crm-market`) and the run date `YYYY-MM-DD`.
Test runs use `zz-validation-<YYYY-MM-DD>` instead and are removed afterwards.

## Procedure

1. **Scope and capture (webarchiver-mcp).** Select the pages (pricing, plans,
   product, features, about, news) and `web_extract` each. Keep each page's
   `canonical_url` and `retrieved_at`.
2. **Archive (one call).**
   `archivebox_cli_add(urls=[<canonical urls>], tag="market-research,<subject>,<YYYY-MM-DD>", depth=0)`.
   No more than 50 URLs per run without owner approval. Use `depth=0`; the
   page list comes from step 1, not from an archive crawl.
3. **Confirm.** Poll `archivebox_get_snapshots(tag="<YYYY-MM-DD>", search="<subject>")`
   (or `tag="<subject>"`) until every URL has a `sealed` snapshot. For each,
   `archivebox_get_archiveresults(snapshot_id=<id>, status="succeeded")` must
   include at least one of `singlefile`, `wget` or `pdf` (the durable copy) and
   `readability` or `htmltotext` (the text). A page with none: report it as
   not archived with the failed plugins' `output_str`.
4. **Attach the extract (optional).** File the webarchiver extract on the
   snapshot so the exact text used is archived with it:
   `archivebox_create_archiveresult(snapshot_id=<id>, plugin="webarchiver", output_str="<canonical_url> <retrieved_at>", files={"extract.md": <base64 markdown>})`.
5. **Index (optional).** `archivebox_ingest_snapshots(tag="<subject>")` so
   the knowledge graph can answer cross-source questions about the subject.
6. **Cite.** For each fact: quote, `canonical_url`, `retrieved_at`, snapshot
   `id`, snapshot `timestamp`, and the archive path
   `<ARCHIVEBOX_BASE_URL>/<archive_path>`.

## Re-check and compare a later run

1. List earlier runs: `archivebox_get_snapshots(tag="<subject>", limit=200)`
   and group by URL; the date tag tells runs apart.
2. For the same URL, compare the `title` and the readability/htmltotext output
   of the latest two sealed snapshots; report what changed (prices, plans,
   features, claims) with both snapshot ids.
3. Refresh a whole subject on demand: `archivebox_cli_update(tag="<subject>")`,
   or keep a page under watch:
   `archivebox_cli_schedule(add=true, every="week", import_path="<url>", tag="market-research,<subject>")`
   (owner approval for schedules).

## Guardrails

- Public pages only: no logins, personas with cookies, forms, paywalls or
  robots.txt bypass. Never contact competitors or post anything.
- Never remove research snapshots; removal of anything but `zz-validation-*`
  test captures needs the owner.
- Quote exactly from captured text; label inferences.

## Output

A research brief section per page (canonical URL, retrieved_at, snapshot id,
timestamp, archive path, plugins kept, quoted facts), a list of pages not
archived with reasons, and a change list against the previous run.
