# CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT — Design and implementation plan

Governing spec: [spec.md](spec.md).

## Architecture

`pyproject.toml` declares `archivebox-mcp` as the connector identity. `create_mcp_server` resolves the packaged content of `archivebox_api` from it.
