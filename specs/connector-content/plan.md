# CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT — Implementation plan

Governing spec: [spec.md](spec.md). Rows: [requirements.md](requirements.md).

## Summary

`pyproject.toml` declares `archivebox-mcp` as the connector identity. `create_mcp_server` resolves the packaged content of `archivebox_api` from it.

## Technical Context

- **Language/Version**: Python 3.14 (floor 3.12)
- **Primary Dependencies**: scion-sdk, fastmcp
- **Storage**: N/A; the connector stores nothing
- **Testing**: pytest; the proof level each row names
- **Target Platform**: Linux containers
- **Project Type**: connector (MCP server)
- **Performance Goals**: N/A
- **Constraints**: one tool per API operation; shared capabilities come from the SDK
- **Scale/Scope**: 2 rows

## Constitution Check

- One owner per concept: pass. The connector owns one external system's calls, mappings and tools only.
- Connectors depend on the SDK and are called through arbora: pass.
- No ratchets: pass. The rows add no suppression.

## Project Structure

```text
pyproject.toml  existing
```

## Phase 0: Research

No unknowns. Each row names the code it touches.

## Phase 1: Design

The rows are delivered in place; the design is the caller chain below.

## Phase 2: Task approach

`tasks.md` holds one task line per row, producer first.

## Complexity Tracking

None. The constitution check passed.

## Build contract

The repository pre-commit hooks apply: `ruff-format`, `connector-standard`, `secrets`, `tests-fast`. Each row names its proving test. No suppression and no duplicate implementation.

## Production caller chain

1. `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R001`: the `archivebox-mcp` console script (pyproject.toml, scion_sdk.cli:serve) loads the `scion_sdk.connector` entry point `archivebox_api:connector` -> archivebox_api/__init__.py::connector (a Connector with no content= argument) -> the SDK default content registration serves skill:// and ontology:// resources and prompts.
2. `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R002`: arbora fleet.call -> the served read tools `archivebox_get_snapshots`, `archivebox_get_archiveresults`, `archivebox_get_crawls` (SDK operation tools over archivebox_api/api/api_client_core.py and api_client_crawls.py) -> archivebox_api/ontology/access_contracts.ttl names each as the class's route.
3. `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R003`: scion_sdk register_tool_surface -> register_method_tools over archivebox_api/api_client.py::Api (auth, cli, core, crawls mixins) -> one tool per public method, verb from the `VERB /path` docstring line; archivebox_api/mcp_server.py keeps only the kg and web registrars.
4. `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R004`: archivebox_api/__init__.py::connector(result_coercer=coerce_result) -> archivebox_api/mcp_server.py::coerce_result on every operation result.
5. `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R005`: archivebox_cli_remove -> archivebox_api/api/api_client_cli.py::cli_remove selection guard, after the SDK destructive confirmation.
6. `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R006`: SDK content registration serves archivebox_api/ontology/pack.ttl and archivebox_api/prompts/*.json; arbora's onboarding capture reads them.
7. `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R007`: archivebox_api/ontology/archivebox.ttl, mappings/source.yaml, archivebox_api/connector_sources.py.
8. `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R008`: SDK skills provider serves archivebox_api/skills/archivebox-research-archive/SKILL.md as skill://.

## Cross-repo seams

none. The cited owner rows are library capabilities the connector calls in process; spec.md names them.
