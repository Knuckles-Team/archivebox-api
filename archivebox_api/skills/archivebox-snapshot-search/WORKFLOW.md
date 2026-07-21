# Archivebox Snapshot Search

Browse and search an ArchiveBox archive via the archivebox-api MCP server — list/filter snapshots, read one snapshot (with its per-extractor archive results), list archive results by extractor/status, and read tags with the domain-typed core tool. Use when the agent must find an archived URL, inspect what was captured for a page, check extractor success/failure, or resolve a snapshot/result/tag by its abid. Do NOT use for adding or re-archiving URLs (archivebox-web-archiving) or for pushing data into the knowledge graph (archivebox-kg-ingestion); prefer those.

# ArchiveBox Snapshot Search

Domain-typed **read** access to an ArchiveBox archive: snapshots, their per-extractor
archive results, and tags. Prefer these over raw HTTP — they return archive-shaped
records.

## When to use
- Find / filter snapshots by `search`, `url`, `tag`, `title`, or date window.
- Read one snapshot by `snapshot_id` (id or abid), optionally with archive results.
- List `ArchiveResult`s filtered by `extractor`, `status`, `snapshot_url`, etc.
- Read tags, or resolve any object (snapshot/result/tag) by its `abid`.

## When NOT to use
- Adding, updating, or scheduling captures → `archivebox-web-archiving`.
- Loading snapshots/results into the epistemic-graph KG → `archivebox-kg-ingestion`.

## Prerequisites & environment
Connect via the `mcp-client` skill against the **`archivebox-api`** MCP server.

| Variable | Required | Notes |
|----------|----------|-------|
| `ARCHIVEBOX_BASE_URL` | ✅ | Instance URL (alias `ARCHIVEBOX_URL`) |
| `ARCHIVEBOX_TOKEN` | one of | Bearer API token (alias `ARCHIVEBOX_API_KEY`) |
| `ARCHIVEBOX_USERNAME` / `ARCHIVEBOX_PASSWORD` | one of | Basic-auth → token exchange |
| `ARCHIVEBOX_TLS_PROFILE[_REF]` | optional | Runtime TLS profile for private PKI, mTLS, or proxy policy |

`MCP_TOOL_MODE` (`condensed`|`verbose`|`both`) selects the condensed surface (used
below) vs. the one-to-one verbose tools.

## Tools & actions
Prefer the **condensed** tool; it takes `action` + a `params_json` **JSON string**.

| Condensed tool | Actions |
|----------------|---------|
| `archivebox_core` | `get_snapshots`, `get_snapshot`, `get_archiveresults`, `get_tag`, `get_any` |
| `archivebox_cli`  | `cli_list` (JSON/CSV export of the index) |

### Key parameters
- `search` — matches url, title, tags, id, abid, timestamp (`get_snapshots`).
- `tag`, `url`, `title`, `timestamp` — exact/`icontains`/`startswith` filters.
- `created_at__gte` / `created_at__lt`, `bookmarked_at__gte` / `__lt` — date windows.
- `with_archiveresults` — include per-extractor results on a snapshot read.
- `snapshot_id` — id or abid for `get_snapshot`; `abid` for `get_any`.
- `extractor`, `status`, `snapshot_url`, `snapshot_tag` — `get_archiveresults` filters.
- `limit`, `offset`, `page` — pagination.

## Recipes (`params_json`)
Search snapshots for a term, newest first, small page:
```json
{"search":"climate","limit":25,"page":0}
```
Read one snapshot with its archive results:
```json
{"snapshot_id":"<abid_or_id>","with_archiveresults":true}
```
Find failed screenshot captures:
```json
{"extractor":"screenshot","status":"failed","limit":50}
```
List all snapshots tagged `research`:
```json
{"tag":"research","limit":100}
```

## Gotchas
- `params_json` is a **string** of JSON, not an object — serialize it.
- `tag` is an **exact** tag-name match; use `search` for fuzzy matching across fields.
- `timestamp` filters `startswith`, not equality — ArchiveBox timestamps are the
  snapshot directory keys (epoch-like), not ISO dates.
- Always set a sane `limit`; unbounded reads over a large archive are slow.
- A `get_snapshots` read triggers default-on native KG ingestion (best-effort, no-op
  without a live engine; disable with `ARCHIVEBOX_KG_AUTO_INGEST=0`).

## Related
- **Write side:** `archivebox-web-archiving` (add/update/schedule captures).
- **KG side:** `archivebox-kg-ingestion` (typed nodes + page-text docs + blobs).
