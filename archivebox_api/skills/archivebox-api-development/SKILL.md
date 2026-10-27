---
name: archivebox-api-development
skill_type: skill
description: >-
  Develop and maintain the ArchiveBox connector while preserving its governed
  API actions, web-source contract, credential boundary, package resources, and
  public-first release evidence.
license: MIT
tags: [archivebox, connector, mcp, sdk, web-source, knowledge-graph]
metadata:
  author: Genius
  version: '0.1.0'
---
# ArchiveBox API Development

This is the repository development skill for `archivebox-api`. The owning central
delivery row is `PIPE-CONNSPEC-R103.4`; use this skill with the repository
`AGENTS.md`, the connector-content and web-source specifications, and the
focused tests.

## Repository and runtime map

- `archivebox_api/mcp_server.py` registers authentication, core, CLI, KG,
  and web-source tools. Keep action names and the SDK Connector boundary stable.
- `archivebox_api/api_client.py` composes the authentication, core, and CLI
  API wrappers. `archivebox_api/auth.py` injects endpoint credentials and the
  SDK TLS profile through `get_client`; it must not persist secret values.
- `archivebox_api/connector_sources.py` is the live source and schema
  declaration. Change declarations there rather than duplicating source IDs or
  mappings in tool code.
- `archivebox_api/web_source.py` implements the SDK web-source contract:
  keyless web discovery is separate from ArchiveBox REST authentication, while
  extractor files use a logged-in Django session and bounded reads.
- `archivebox_api/kg_ingest.py` owns best-effort typed Snapshot, ArchiveResult,
  Document, Chunk, Tag, and Blob ingestion through the SDK/epistemic-graph
  boundary. Preserve stable IDs and no-op behavior when the engine is absent.
- `archivebox_api/skills/**`, `prompts/**`, `ontology/**`, and
  `connectors/**` are package data. A skill change therefore needs a package
  inclusion check before publication.

## Connection and security contract

The REST client uses `ARCHIVEBOX_BASE_URL` with the `ARCHIVEBOX_URL` alias.
Bearer/API-key and basic-auth values come from injected `ARCHIVEBOX_TOKEN`,
`ARCHIVEBOX_API_KEY`, `ARCHIVEBOX_USERNAME`, and `ARCHIVEBOX_PASSWORD`
settings. Keep secrets out of source, skills, fixtures, logs, and test output.

Use the SDK TLS policy selected by `ARCHIVEBOX_TLS_PROFILE` and
`ARCHIVEBOX_TLS_PROFILE_REF`; `ArchiveSession` must keep certificate and
hostname verification governed by the shared resolver. Preserve the supported
`stdio`, `streamable-http`, and `sse` transports, the
`MCP_TOOL_MODE` surface selection, `WEBTOOL`/`WEB_SOURCETOOL` toggles,
and the `ARCHIVEBOX_KG_AUTO_INGEST` opt-out. Do not add a provider-specific
credential store or a TLS bypass.

## Rapid delivery: the 5-minute contract

1. Read the owning connector-content and web-source specs, this skill,
   `AGENTS.md`, and the directly bound tests before changing a surface.
2. Inspect the SDK `Connector`, action lists and dispatchers, API wrappers,
   `ArchiveWebSource` session/refusal behavior, source declarations, KG
   mappings, and package-data rules.
3. Make the smallest connector-owned change. Preserve public action/tool names,
   source IDs and mappings, keyless web fallbacks, injected credentials, TLS
   verification, bounded extractor reads, stable KG IDs, and canonical/legacy
   server paths.
4. Run the smallest directly bound tests with
   `uv run --locked --extra test pytest`, then run the repository hooks. Use
   the approved narrow wrapper when the lane requires it; never bypass a hook or
   failing gate.
5. If package content changes, advance the version with the repository's normal
   release metadata, refresh `uv.lock`, and inspect the built wheel and sdist
   for the intended `archivebox_api/skills/**` bytes before publication.
6. Treat Pages and containers as separate evidence. After the exact main commit
   publishes, verify the Pages revision and `/spec-delivery/` artifacts. The
   container workflow must wait for the exact public wheel guard; never move an
   image pin before package proof.

## Focused validation

For client, action, source, or KG changes, run only the smallest relevant test
file and keep keyless, credentialed, unavailable-authority, and refusal paths
distinct. For this skill/package-data change, verify frontmatter, the required
rapid-delivery heading, ArchiveBox-specific source references, package-data
inclusion, and absence of token-like material without contacting an external
provider.

Use repository commands from `AGENTS.md`:

```bash
uv sync --locked
uv run --locked --extra test pytest -q tests/test_archivebox_development_skill.py
uvx pre-commit run --all-files
```

## Publication and Pages

`.github/workflows/pipeline.yml` publishes the package through
`Knuckles-Team/pipelines/.github/workflows/python_pipeline.yml@main` with
`connector: true`, then invokes the container pipeline with
`render_connector: true`. `.github/workflows/pages.yml` delegates the
README/docs path to `pages_pipeline.yml@main`. Keep package publication before
the generated connector image and preserve the public wheel/source fences.

A successful local test or workflow run is not package, Pages, or image proof.
Record the exact merged source, public wheel/sdist hashes, skill bytes, Pages
revision, and image digest separately. Do not hand-edit central Pipelines status,
promote a rollup from this skill change, or put credentials, provider data,
generated release artifacts, or bypass instructions in this skill.
