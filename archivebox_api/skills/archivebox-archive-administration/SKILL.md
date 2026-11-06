---
name: archivebox-archive-administration
skill_type: skill
description: >-
  Administer an ArchiveBox archive through the archivebox-mcp server: create,
  rename and delete tags, add or remove tags on snapshots, delete test or
  unwanted snapshots and crawls with the narrowest selection, inspect capture
  workers, installed capture binaries and personas, and manage API tokens.
  Use for archive hygiene and capture troubleshooting. Do NOT use to capture
  pages (archivebox-web-archiving) or to search them (archivebox-snapshot-search).
license: MIT
tags: [archivebox, administration, tags, cleanup, troubleshooting, mcp]
metadata:
  author: Knuckles-Team
  version: '0.1.0'
---
# ArchiveBox archive administration

## Tags

| Tool | Use |
|------|-----|
| `archivebox_create_tag(name)` | Create (or return the existing) tag. |
| `archivebox_rename_tag(tag_id, name)` | Rename. |
| `archivebox_add_tag_to_snapshot(snapshot_id, tag_name)` | Tag one snapshot (creates the tag). |
| `archivebox_remove_tag_from_snapshot(snapshot_id, tag_name)` | Untag one snapshot. |
| `archivebox_delete_tag(tag_id)` | Delete a tag; snapshots stay. |

## Removing captures (destructive; the server asks for confirmation)

| Tool | Use |
|------|-----|
| `archivebox_delete_snapshot(snapshot_id)` | Delete one snapshot and its files. |
| `archivebox_delete_crawl(crawl_id)` | Delete one crawl. |
| `archivebox_cli_remove(filter_patterns=[...], filter_type="exact")` | Delete the snapshots a selection matches. It refuses an empty selection. |

Rules: remove only what you created for a test (named `zz-validation-<date>`)
or what the owner named. Read the selection first with
`archivebox_cli_search` using the same arguments, check every match, then
remove by exact URL or snapshot id. Never remove by a broad `search`,
`url__icontains` or a shared tag.

## Capture troubleshooting

| Tool | Use |
|------|-----|
| `archivebox_get_current_machine` / `archivebox_get_machines` / `archivebox_get_machine` | Workers, their OS and stats. |
| `archivebox_get_binaries(status=...)` / `archivebox_get_binary` / `archivebox_get_binaries_by_name(name)` | Installed capture tools and versions (for example why `ytdlp` or `chromium` results fail). |
| `archivebox_get_archiveresults(status="failed", plugin=...)` | Which plugin is failing and its `output_str`. |
| `archivebox_get_personas` | Personas captures run as. |

## Credentials (owner approval required)

- `archivebox_sync_persona` uploads cookies/auth for a persona. Only with
  owner-provided material; never copy cookies from elsewhere.
- `archivebox_get_api_token`, `archivebox_check_api_token`,
  `archivebox_browser_session` handle tokens and sessions; never print or store
  a token in output, notes or the knowledge graph.
