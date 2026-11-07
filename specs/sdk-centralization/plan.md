# CONN-ARCHIVEBOX-API-SDK-CENTRALIZATION — Implementation plan

Governing spec: [spec.md](spec.md). Rows: [requirements.md](requirements.md).

## Summary

The SDK owns the capability rows cited in [requirements.md](requirements.md). The connector adds no transport code of its own. The connector builds on the SDK. HTTP goes through the SDK governed client, and TLS comes from `resolve_tls_profile` for the connector's settings prefix.

## Technical Context

- **Language/Version**: Python 3.14 (floor 3.12)
- **Primary Dependencies**: scion-sdk, fastmcp
- **Storage**: N/A; the connector stores nothing
- **Testing**: pytest; the proof level each row names
- **Target Platform**: Linux containers
- **Project Type**: connector (MCP server)
- **Performance Goals**: N/A
- **Constraints**: one tool per API operation; shared capabilities come from the SDK
- **Scale/Scope**: 5 rows

## Constitution Check

- One owner per concept: pass. The connector owns one external system's calls, mappings and tools only.
- Connectors depend on the SDK and are called through arbora: pass.
- No ratchets: pass. The rows add no suppression.

## Project Structure

```text
No file is added; the rows edit existing files.
```

## Phase 0: Research

No unknowns. Each row names the code it touches.

## Phase 1: Design

### Interfaces and data model

No tool, argument or result changes.

### Live integration path

Every tool reaches ArchiveBox through the connector client, which sends each request through the SDK.

### Quality and release gates

The focused tests in [test-spec.md](test-spec.md) must pass. The SDK floor must be the latest published release.

### Risks, alternatives, and decisions

A private certificate authority must be supplied through the TLS profile. A flag that disables verification must not return.

### Adoption of scion-sdk 0.10.0 (CONN-ARCHIVEBOX-API-SDK-CENTRALIZATION-R002)

- Owner. This repository, the import lines named in `CONN-ARCHIVEBOX-API-SDK-CENTRALIZATION-R002`. The paths belong to scion-sdk.
- Cohesion. The import edits, the pin and the lock change together and sit in one change.
- Dependency direction. The connector imports public modules of the SDK units; no import points to a private module.
- Interface depth. The connector uses the public surface only.
- Special cases. None. Every removed path takes the same replacement, with no alias.
- State. None.
- Environment. None. The pin is package metadata, not environment code.

## Phase 2: Task approach

`tasks.md` holds one task line per row, producer first.

## Complexity Tracking

None. The constitution check passed.

## Build contract

The repository pre-commit hooks apply: `ruff-format`, `connector-standard`, `secrets`, `tests-fast`. Each row names its proving test. No suppression and no duplicate implementation.

## Production caller chain

1. `CONN-ARCHIVEBOX-API-SDK-CENTRALIZATION-R001.1`: arbora fleet.call -> `archivebox_core` tool (archivebox_api/mcp_server.py::archivebox_core:120) -> archivebox_api/auth.py::get_client -> archivebox_api/api/api_client_base.py (ApiClientBase.__init__ calls create_http_client at line 30); web_fetch reaches archivebox_api/web_source.py::ArchiveSession.__post_init__:87 and web_source_contract.py::_read_robots:52.
2. `CONN-ARCHIVEBOX-API-SDK-CENTRALIZATION-R001.2`: archivebox-mcp console script -> archivebox_api/auth.py::get_client:28 passes resolve_tls_profile("archivebox") into Api -> archivebox_api/api/api_client_base.py:28; web_fetch builds ArchiveSession via archivebox_api/mcp_server.py::get_web_source:303 -> archivebox_api/web_source.py::ArchiveSession.__post_init__:87.
3. `CONN-ARCHIVEBOX-API-SDK-CENTRALIZATION-R001.3`: web_extract tool (archivebox_api/mcp_server.py::register_web_tools:340) -> web_source_contract.py::ArchiveboxSource.extract:172 -> archivebox_api/web_source.py::ArchiveSession.get_text:130 and get_file:140 -> login:101 on a redirect to /admin/login/.
4. `CONN-ARCHIVEBOX-API-SDK-CENTRALIZATION-R001.4`: dependency resolution of pyproject.toml (dependencies = scion-sdk[mcp]) for the `archivebox-mcp` console script and the `archivebox_api:connector` entry point; the only runtime path is every scion_sdk import in archivebox_api.

## Cross-repo seams

none. The cited owner rows are library capabilities the connector calls in process; spec.md names them.
