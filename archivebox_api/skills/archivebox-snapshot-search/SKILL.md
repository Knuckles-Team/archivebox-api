---
name: archivebox-snapshot-search
skill_type: skill
description: >-
  Find and read archived pages in ArchiveBox through the archivebox-mcp server: list and filter snapshots by URL, tag, text, status or time, read one snapshot with its per-plugin archive results, list archive results, resolve any object by id, export a tag's URLs or snapshots, and read the RSS feed. Use when the agent must cite or inspect an archived page.
license: MIT
tags: [archivebox, search, snapshots, evidence, mcp]
metadata:
  author: Knuckles-Team
  version: '0.2.0'
---
# ArchiveBox snapshot search

Scope: Find and read archived pages in ArchiveBox through the archivebox-mcp server: list and filter snapshots by URL, tag, text, status or time, read one snapshot with its per-plugin archive results, list archive results, resolve any object by id, export a tag's URLs or snapshots, and read the RSS feed. Use when the agent must cite or inspect an archived page. Do NOT use to add or re-archive URLs (archivebox-web-archiving) or to ingest into the KG (archivebox-kg-ingestion).

All tools here are read-only.

| Tool | Use |
|------|-----|
| `archivebox_get_snapshots` | Filter snapshots: `url` (exact), `tag`, `search` (+ `search_mode` meta/contents/deep), `status`, `title`, `bookmarked_at__gte/__lt`, `with_archiveresults`, `limit/offset/page`. |
| `archivebox_get_snapshot` | One snapshot by `snapshot_id`, with its archive results. |
| `archivebox_get_archiveresults` | Results by `snapshot_id`, `snapshot_url`, `snapshot_tag`, `plugin`, `status`. |
| `archivebox_get_archiveresult` | One result by id. |
| `archivebox_get_any` | Resolve any id (snapshot, result, tag, crawl). |
| `archivebox_cli_search` | Index search with `filter_patterns` + `filter_type` (exact, substring, domain, regex, tag, search) and JSON/CSV/HTML export. |
| `archivebox_get_tags` / `archivebox_get_tag` / `archivebox_search_tags` / `archivebox_tags_autocomplete` | Tags and their snapshot counts. |
| `archivebox_get_tag_urls` / `archivebox_get_tag_snapshots_jsonl` | Export a tag's URLs (text) or snapshots (JSON Lines). |
| `archivebox_get_crawls` / `archivebox_get_crawl` | Crawls and the snapshots they produced. |
| `archivebox_get_crawl_file` / `_folder_file` / `_subfolder_file` | A file in a crawl's output directory. |
| `archivebox_get_snapshots_rss` | Recent snapshots as RSS. |

## Steps

1. Find candidates with `archivebox_get_snapshots`(url, tag, search). Verify the result contains at least one snapshot.
2. Pick the newest snapshot whose status is `sealed`. Verify its `id`, `timestamp` and `archive_path` are present.
3. List what was kept with `archivebox_get_archiveresults`(snapshot_id, status="succeeded"). Verify the plugins you rely on are in the list.
4. Cite `id`, `url`, `timestamp` and `archive_path`. Verify the cited fields come from the tool result, not memory.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| No snapshot found | The URL differs or the page was never archived | Search with `archivebox_get_snapshots`(search, search_mode="contents") or `archivebox_cli_search`(filter_type="domain"). |
| Only unsealed snapshots | Capture is incomplete | Report the status and check again with `archivebox_get_snapshot`(snapshot_id). |
| Page text not matched | `search` matches metadata by default | Use `search_mode="contents"` in `archivebox_get_snapshots`. |

## Procedure: cite an archived page

1. `archivebox_get_snapshots(url="<exact url>")` (or `tag=` / `search=`).
2. Take the newest `sealed` snapshot. Cite its `id`, `url`, `timestamp`,
   `bookmarked_at` and `archive_path`; the browsable copy is
   `<ARCHIVEBOX_BASE_URL>/<archive_path>`.
3. `archivebox_get_archiveresults(snapshot_id=<id>, status="succeeded")` lists
   what was kept (`plugin` = singlefile, wget, pdf, screenshot, readability,
   htmltotext, title, headers, ...). Cite the plugins you rely on.
4. A page captured more than once: compare `timestamp` and the `title` /
   readability output of each snapshot to show what changed.

## Gotchas

- Snapshot status: `queued` -> `started` -> `sealed`. Only `sealed` snapshots
  are complete; a sealed snapshot can still have failed plugins.
- `search` matches metadata by default; use `search_mode="contents"` for page text.
- Output files are served to a logged-in browser session, not the API token;
  cite the archive path, do not try to download files through the API.
