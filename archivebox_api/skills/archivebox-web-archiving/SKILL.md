---
name: archivebox-web-archiving
skill_type: skill
description: >-
  Capture and re-archive web pages with ArchiveBox via the archivebox-api MCP
  server — add URLs (with tags, crawl depth, and chosen extractors), update /
  re-archive existing snapshots, and schedule recurring archiving with the
  domain-typed CLI tool. Use when the agent must permanently archive a URL,
  bulk-add a list of links, refresh stale captures, or set up a recurring
  archive job. Do NOT use for browsing/searching what is already archived
  (archivebox-snapshot-search) or for pushing archived data into the knowledge
  graph (archivebox-kg-ingestion); prefer those.
license: MIT
tags: [archivebox, web-archiving, snapshots, crawl, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---
# ArchiveBox Web Archiving

Domain-typed access to ArchiveBox's **CLI actions** (`add` / `update` / `schedule`)
for capturing and re-capturing web pages into durable, self-hosted snapshots.

## When to use
- Archive one URL or a batch of URLs (optionally with tags + a crawl `depth`).
- Choose which extractors run (e.g. `wget,screenshot,pdf,singlefile,dom`).
- Re-archive / refresh existing snapshots (`update`, `only_new`, `overwrite`).
- Set up a recurring archive job (`schedule`).

## When NOT to use
- Reading / searching / listing what is already archived → `archivebox-snapshot-search`.
- Ingesting snapshots + results into the epistemic-graph KG → `archivebox-kg-ingestion`.
- Deleting snapshots — use the `cli_remove` action directly (destructive; not part
  of this capture-oriented skill).

## Prerequisites & environment
Connect via the `mcp-client` skill against the **`archivebox-api`** MCP server.

| Variable | Required | Notes |
|----------|----------|-------|
| `ARCHIVEBOX_BASE_URL` | ✅ | Instance URL (alias `ARCHIVEBOX_URL`) |
| `ARCHIVEBOX_TOKEN` | one of | Bearer API token (alias `ARCHIVEBOX_API_KEY`) |
| `ARCHIVEBOX_USERNAME` / `ARCHIVEBOX_PASSWORD` | one of | Basic-auth → token exchange |
| `ARCHIVEBOX_SSL_VERIFY` | optional | TLS verification toggle (default off) |

`MCP_TOOL_MODE` (`condensed`|`verbose`|`both`) selects the condensed surface (used
below) vs. the one-to-one verbose tools.

## Tools & actions
Prefer the **condensed** tool; it takes `action` + a `params_json` **JSON string**
whose keys are passed straight to the client method.

| Condensed tool | Actions |
|----------------|---------|
| `archivebox_cli` | `cli_add`, `cli_update`, `cli_schedule` |

### Key parameters
- `urls` — **list of strings** to archive (`cli_add`).
- `tag` — comma-separated tags to apply.
- `depth` — crawl depth (`0` = just the URL, `1` = also linked pages).
- `extractors` — comma-separated extractor list; empty = the instance default set.
- `update` / `update_all` / `overwrite` — re-archive controls.
- `only_new`, `after`, `before`, `status`, `filter_patterns` — scope for `cli_update`.

## Recipes (`params_json`)
Archive a single URL with tags:
```json
{"urls":["https://example.com/article"],"tag":"research,to-read"}
```
Bulk-archive with a crawl depth of 1 and only screenshot + pdf + singlefile:
```json
{"urls":["https://a.example","https://b.example"],"depth":1,"extractors":"screenshot,pdf,singlefile"}
```
Re-archive only snapshots still marked unarchived:
```json
{"only_new":true,"status":"unarchived"}
```
Schedule a recurring archive job (see `cli_schedule` params for cadence fields):
```json
{"urls":["https://news.example/feed"],"tag":"daily"}
```

## Gotchas
- `params_json` is a **string** of JSON, not an object — serialize it.
- `urls` MUST be a list even for a single URL.
- `cli_add` triggers **server-side** archiving; it returns the command result, not
  the finished snapshot bytes. Poll with `archivebox-snapshot-search` to confirm
  the capture completed and see per-extractor status.
- `depth > 0` can fan out into many captures — set tags and watch instance load.
- Extractor names must match the instance's enabled extractors, or they are skipped.
- After a successful `get_snapshots` read, native KG auto-ingestion fires by default
  (disable with `ARCHIVEBOX_KG_AUTO_INGEST=0`) — see `archivebox-kg-ingestion`.

## Related
- **Read side:** `archivebox-snapshot-search` (list/get snapshots, results, tags).
- **KG side:** `archivebox-kg-ingestion` (push snapshots + results into the graph).
