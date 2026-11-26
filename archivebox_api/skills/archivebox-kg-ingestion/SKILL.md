---
name: archivebox-kg-ingestion
skill_type: skill
description: >-
  Copy ArchiveBox snapshots, tags, page text and archive results into the knowledge graph through the archivebox-mcp ingest tools, as :WebSnapshot, :Tag, :Document and :ArchiveResult nodes linked by :hasTag, :hasPageText and :hasArchiveResult. Use to make archived pages queryable and searchable next to other sources, or to backfill a tag.
license: MIT
tags: [archivebox, knowledge-graph, ingest, mcp]
metadata:
  author: Knuckles-Team
  version: '0.2.0'
---
# ArchiveBox knowledge-graph ingest

Scope: Copy ArchiveBox snapshots, tags, page text and archive results into the knowledge graph through the archivebox-mcp ingest tools, as :WebSnapshot, :Tag, :Document and :ArchiveResult nodes linked by :hasTag, :hasPageText and :hasArchiveResult. Use to make archived pages queryable and searchable next to other sources, or to backfill a tag. Do NOT use to capture pages (archivebox-web-archiving) or for plain reads (archivebox-snapshot-search).

| Tool | Arguments | Writes |
|------|-----------|--------|
| `archivebox_ingest_snapshots` | `tag`, `search`, `url`, `limit` | `:WebSnapshot` + `:Tag`/`:hasTag` + `:Document`/`:hasPageText` + nested `:ArchiveResult`/`:hasArchiveResult` |
| `archivebox_ingest_archiveresults` | `snapshot_id`, `snapshot_tag`, `plugin`, `status`, `limit` | `:ArchiveResult` linked to its snapshot |

Node ids are stable (`archivebox:snapshot:<id>`, `archivebox:archiveresult:<id>`,
`archivebox:tag:<name>`, `archivebox:document:<id>`), so re-ingest is idempotent.

## Steps

1. Confirm the captures are finished with `archivebox_get_snapshots`(tag). Verify every snapshot status is `sealed`.
2. Ingest snapshots with `archivebox_ingest_snapshots`(tag). Verify the result reports `listed` greater than zero.
3. Optionally add failed-plugin evidence with `archivebox_ingest_archiveresults`(snapshot_tag, status="failed"). Verify `ingested` is reported.
4. Read `listed` and `ingested` from the result. Verify `ingested` is a number. If it is null, no engine was reachable and the archive itself is unaffected.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Nothing listed | The tag or filter matches no snapshot | Check the tag with `archivebox_get_tags` and ingest with the exact tag. |
| `ingested` is null | No engine is reachable from the connector | Report it, check the engine connection settings, and run the ingest again afterwards; the archive is unchanged. |
| Records invisible to other tenants | Ingested records start in quarantine | Have the owner admit them through pack governance before expecting them in other tenants. |

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
