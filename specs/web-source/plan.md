# CONN-ARCHIVEBOX-API-WEB-SOURCE — Implementation plan

Governing spec: [spec.md](spec.md). Rows: [requirements.md](requirements.md).

## Summary

`cli_add` at `archivebox_api/api/api_client_cli.py:15` adds a URL. `get_snapshot` at `archivebox_api/api/api_client_core.py:110` reads the snapshot status. `get_archiveresults` at line 137 reads the extractor output. `archivebox_api/kg_ingest.py` stays the bulk snapshot ingest path; the web-source tools do not replace it. Call path: arbora `research.web` -> engine work item of kind `WebPage` -> SDK ingest worker -> `WebFetchSourceAdapter.extract` -> this connector `web_extract` -> engine `SourceIngest`. The connector holds no store and no selection rule. It returns one page result or one typed refusal per call.

## Technical Context

- **Language/Version**: Python 3.14 (floor 3.12)
- **Primary Dependencies**: scion-sdk, fastmcp
- **Storage**: N/A; the connector stores nothing
- **Testing**: pytest; the proof level each row names
- **Target Platform**: Linux containers
- **Project Type**: connector (MCP server)
- **Performance Goals**: N/A
- **Constraints**: one tool per API operation; shared capabilities come from the SDK
- **Scale/Scope**: 10 rows

## Constitution Check

- One owner per concept: pass. The connector owns one external system's calls, mappings and tools only.
- Connectors depend on the SDK and are called through arbora: pass.
- No ratchets: pass. The rows add no suppression.

## Project Structure

```text
archivebox_api/web_source_contract.py  existing
archivebox_api/web_source.py  existing
archivebox_api/mcp_server.py  existing
archivebox_api/kg_ingest.py  existing
```

## Phase 0: Research

No unknowns. Each row names the code it touches.

## Phase 1: Design

### Interfaces and data model

The tool arguments and results are the SDK contract types of `SCION-SOURCE-INGEST-R005.40.1`. No connector-local result type exists.

### Live integration path

The production caller is `WebFetchSourceAdapter.extract` in the SDK. arbora reaches it through the engine work item of `ARBORA-OPS-R067.2`.

### Quality and release gates

The SDK conformance kit of `SCION-SOURCE-INGEST-R005.40.2` must pass against the served connector.

### Risks, alternatives, and decisions

A spec-only change on `main` must not publish a release. Merge commits for spec text carry `[skip ci]`.

## Phase 2: Task approach

`tasks.md` holds one task line per row, producer first.

## Complexity Tracking

None. The constitution check passed.

## Build contract

The repository pre-commit hooks apply: `ruff-format`, `connector-standard`, `secrets`, `tests-fast`. Each row names its proving test. No suppression and no duplicate implementation.

## Production caller chain

1. `CONN-ARCHIVEBOX-API-WEB-SOURCE-R001.1`: arbora fleet.call -> web_fetch or web_extract (archivebox_api/mcp_server.py::register_web_tools:340, register_web_source_tools from scion_sdk.ports.web_source) -> archivebox_api/mcp_server.py::get_contract_source:325 -> archivebox_api/web_source_contract.py::ArchiveboxSource.fetch:154 and ::extract:172 over ArchiveWebSource (web_source.py:180).
2. `CONN-ARCHIVEBOX-API-WEB-SOURCE-R001.2`: arbora fleet.call -> web_fetch or web_extract (archivebox_api/mcp_server.py::register_web_tools:340, register_web_source_tools from scion_sdk.ports.web_source) -> archivebox_api/mcp_server.py::get_contract_source:325 -> ArchiveboxSource._snapshot:98 -> archivebox_api/web_source.py::ArchiveWebSource.snapshot:242 -> fetch:195 -> _existing:190 and api.cli_add (archivebox_api/api/api_client_cli.py:15).
3. `CONN-ARCHIVEBOX-API-WEB-SOURCE-R001.3`: arbora fleet.call -> web_fetch or web_extract (archivebox_api/mcp_server.py::register_web_tools:340, register_web_source_tools from scion_sdk.ports.web_source) -> archivebox_api/mcp_server.py::get_contract_source:325 -> ArchiveboxSource._snapshot:98 -> archivebox_api/web_source.py::ArchiveWebSource.snapshot:242 -> _wait:228 -> api.get_snapshot (archivebox_api/api/api_client_core.py:110).
4. `CONN-ARCHIVEBOX-API-WEB-SOURCE-R001.4`: arbora fleet.call -> web_fetch or web_extract (archivebox_api/mcp_server.py::register_web_tools:340, register_web_source_tools from scion_sdk.ports.web_source) -> archivebox_api/mcp_server.py::get_contract_source:325 -> ArchiveboxSource.extract:172 -> ArchiveSession.get_file:140 and get_text:130 (archivebox_api/web_source.py:76) -> login:101 with the admin form.
5. `CONN-ARCHIVEBOX-API-WEB-SOURCE-R001.5`: arbora fleet.call -> web_fetch or web_extract (archivebox_api/mcp_server.py::register_web_tools:340, register_web_source_tools from scion_sdk.ports.web_source) -> archivebox_api/mcp_server.py::get_contract_source:325 -> ArchiveboxSource.fetch:154 and extract:172, which raise WebSourceRefused("extract_empty") when no text exists and return results through ArchiveboxSource._result:129.
6. `CONN-ARCHIVEBOX-API-WEB-SOURCE-R001.6`: arbora served run of ARBORA-OPS-R067.7 -> fleet.call web_fetch/web_extract (archivebox_api/mcp_server.py::register_web_tools:340) -> ArchiveboxSource (archivebox_api/web_source_contract.py:83); tests/test_web_source_served.py does not exist yet (planned).
7. `CONN-ARCHIVEBOX-API-WEB-SOURCE-R001.7`: (planned) archivebox_api/__init__.py::connector (Connector, no manifest today) serves manifest://connector through the SDK content registration, which SourceIngest reads for schema_mappings; archivebox_api/connector_manifest.yml does not exist yet.
8. `CONN-ARCHIVEBOX-API-WEB-SOURCE-R001.8`: arbora fleet.call -> web_fetch or web_extract (archivebox_api/mcp_server.py::register_web_tools:340, register_web_source_tools from scion_sdk.ports.web_source) -> archivebox_api/mcp_server.py::get_contract_source:325 -> ArchiveboxSource._snapshot:98 which runs RobotsRules.check (robots loader _read_robots:52) and the DomainRateLimiter, then ArchiveboxSource._content_type:114 and _file:106 apply content type and max_bytes.
9. `CONN-ARCHIVEBOX-API-WEB-SOURCE-R001.9`: `archivebox-mcp` entry point -> archivebox_api/__init__.py::connector -> archivebox_api/kg_ingest.py::ingest_snapshots:323 and ingest_snapshot_blob:394 submit through _BINDING:44 and _BLOB_BINDING:48, both already IngestBinding(connector="archivebox-mcp"); ConnectorContent and connector_manifest.yml are not present in archivebox_api/mcp_server.py today (planned).

## Cross-repo seams

none. The cited owner rows are library capabilities the connector calls in process; spec.md names them.
