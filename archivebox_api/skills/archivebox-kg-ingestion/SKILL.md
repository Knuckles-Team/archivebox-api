---
name: archivebox-kg-ingestion
skill_type: skill
description: >-
  Copy ArchiveBox snapshots, tags, page text and archive results into the
  knowledge graph through the archivebox-mcp ingest tools, as :WebSnapshot,
  :Tag, :Document and :ArchiveResult nodes linked by :hasTag, :hasPageText and
  :hasArchiveResult. Use to make archived pages queryable and searchable next
  to other sources, or to backfill a tag. Do NOT use to capture pages
  (archivebox-web-archiving) or for plain reads (archivebox-snapshot-search).
license: MIT
tags: [archivebox, knowledge-graph, ingest, mcp]
metadata:
  author: Knuckles-Team
  version: '0.2.0'
---
# ArchiveBox knowledge-graph ingest

| Tool | Arguments | Writes |
|------|-----------|--------|
| `archivebox_ingest_snapshots` | `tag`, `search`, `url`, `limit` | `:WebSnapshot` + `:Tag`/`:hasTag` + `:Document`/`:hasPageText` + nested `:ArchiveResult`/`:hasArchiveResult` |
| `archivebox_ingest_archiveresults` | `snapshot_id`, `snapshot_tag`, `plugin`, `status`, `limit` | `:ArchiveResult` linked to its snapshot |

Node ids are stable (`archivebox:snapshot:<id>`, `archivebox:archiveresult:<id>`,
`archivebox:tag:<name>`, `archivebox:document:<id>`), so re-ingest is idempotent.

## Procedure

1. Ingest after capture completes (snapshots `sealed`), scoped by tag:
   `archivebox_ingest_snapshots(tag="<tag>")`.
2. Optionally add failed-plugin evidence:
   `archivebox_ingest_archiveresults(snapshot_tag="<tag>", status="failed")`.
3. Report `listed` and `ingested`. `ingested: null` means no engine was
   reachable from the connector; the archive itself is unaffected.

## Gotchas

- Ingested records start with ACL `quarantine` (pack governance); they are
  not visible to other tenants until admitted.
- The archive stays the system of record (see access_contracts.ttl); the
  engine copy is a projection for search and cross-source questions.
