---
name: archivebox-kg-ingestion
skill_type: skill
description: >-
  Natively ingest an ArchiveBox archive into the epistemic-graph knowledge graph
  via the archivebox-api MCP server — push snapshots as typed :Snapshot nodes
  (with :Tag + :hasTag links and per-snapshot :Document page-text) and archive
  results as :ArchiveResult nodes, best-effort, with the Wire-First ingest tools.
  Use when the agent must make the web archive queryable/semantic-searchable in
  the KG, backfill existing snapshots, or wire a recurring sync. Do NOT use for
  adding/re-archiving URLs (archivebox-web-archiving) or plain read/search of the
  archive (archivebox-snapshot-search); prefer those.
license: MIT
tags: [archivebox, knowledge-graph, ingestion, blob, mcp]
metadata:
  author: Genius
  version: '0.1.0'
---
# ArchiveBox → Knowledge Graph Ingestion

Wire-First native ingestion of ArchiveBox into the ONE epistemic-graph engine. Maps
records to the classes federated by this package's `archivebox.ttl`
(`:Snapshot`, `:ArchiveResult`, shared `:Tag` / `:Document` / `:MediaAsset` / `:Blob`).

## When to use
- Backfill or refresh the KG with snapshots (typed `:Snapshot` + `:Tag` + page-text
  `:Document` nodes) so the archive is queryable and semantic-searchable.
- Ingest `ArchiveResult`s (extractor/status/output) linked to their `:Snapshot`.
- Wire a recurring sync of an ArchiveBox instance into the graph.

## When NOT to use
- Capturing / re-archiving URLs → `archivebox-web-archiving`.
- Plain reading or searching the archive → `archivebox-snapshot-search`.

## Prerequisites & environment
Connect via the `mcp-client` skill against the **`archivebox-api`** MCP server, and a
reachable epistemic-graph engine (else ingestion **no-ops** best-effort).

| Variable | Required | Notes |
|----------|----------|-------|
| `ARCHIVEBOX_BASE_URL` | ✅ | Instance URL (alias `ARCHIVEBOX_URL`) |
| `ARCHIVEBOX_TOKEN` | one of | Bearer API token (alias `ARCHIVEBOX_API_KEY`) |
| `ARCHIVEBOX_USERNAME` / `ARCHIVEBOX_PASSWORD` | one of | Basic-auth → token exchange |
| `ARCHIVEBOX_KG_AUTO_INGEST` | optional | `0` disables default-on auto-ingest after `get_snapshots` |

## Tools & actions
These are dedicated **kg** tools (not action-routed): each lists via the real client
and pushes into the graph. `params_json` is a JSON **string** of `get_*` filters.

| Tool | What it ingests |
|------|-----------------|
| `archivebox_ingest_snapshots` | `:Snapshot` (+ `:Tag`, `:hasTag`, page-text `:Document` via `:hasPageText`) |
| `archivebox_ingest_archiveresults` | `:ArchiveResult` (+ `:hasArchiveResult` link to its snapshot) |

Node ids are `archivebox:<class>:<abid|id>`. In-code, `archivebox_api.kg_ingest`
also exposes `ingest_snapshot_blob(...)` to store raw web-capture bytes (HTML,
screenshot, PDF, WARC) as a `:Blob` + `:MediaAsset`.

## Recipes (`params_json`)
Ingest snapshots matching a search term:
```json
{"search":"climate","limit":200}
```
Ingest every snapshot tagged `research`:
```json
{"tag":"research","limit":500}
```
Ingest archive results for one snapshot:
```json
{"snapshot_id":"<abid_or_id>"}
```
Ingest all failed captures for triage:
```json
{"status":"failed","limit":500}
```

## Gotchas
- `params_json` is a **string** of JSON, not an object — serialize it.
- Ingestion is **best-effort**: with no reachable engine every call returns
  `{"ingested": null}` and never raises — the connector still works.
- A `get_snapshots` read (via `archivebox-snapshot-search`) already auto-ingests by
  default; use these tools for explicit backfills or archive-result ingestion.
- Ids key on `abid` when present (stable), else the numeric/uuid `id`; re-ingesting
  the same records MERGEs, it does not duplicate.
- Raw-blob ingestion (`ingest_snapshot_blob`) needs the actual capture bytes fetched
  first — the list/read API returns output *paths*, not the bytes.

## Related
- **Read side:** `archivebox-snapshot-search` (source records for ingestion).
- **Write side:** `archivebox-web-archiving` (produce the snapshots to ingest).
- **Ontology:** `archivebox_api/ontology/archivebox.ttl` (the federated class model).
