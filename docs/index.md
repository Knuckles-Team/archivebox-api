# archivebox-api

A Pythonic **ArchiveBox API wrapper, MCP Server, and A2A Agent** for the
agent-utilities ecosystem — programmatic access to an ArchiveBox web-archiving
instance for agentic AI.

!!! info "Official documentation"
    This site is the canonical reference for `archivebox-api`, maintained alongside
    every release.

[![PyPI](https://img.shields.io/pypi/v/archivebox-api)](https://pypi.org/project/archivebox-api/)
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')
[![License](https://img.shields.io/pypi/l/archivebox-api)](https://github.com/Knuckles-Team/archivebox-api/blob/main/LICENSE)
[![GitHub](https://img.shields.io/badge/source-GitHub-181717?logo=github)](https://github.com/Knuckles-Team/archivebox-api)

## Overview

`archivebox-api` wraps the [ArchiveBox](https://archivebox.io/) REST and CLI surface
with typed, deterministic MCP tools, and ships a Pydantic-AI agent for conversational
operation. It provides:

- **`Api`** — a `requests`-based REST client over the ArchiveBox API, organized by
  capability (authentication, core catalog, CLI), built on `agent-utilities`.
- **Action-routed MCP tools** — three consolidated, togglable tool modules
  (`archivebox_authentication`, `archivebox_core`, `archivebox_cli`) that minimize
  token overhead in an LLM context.
- **An integrated graph agent** — a Pydantic-AI agent server (console script
  `archivebox-agent`) exposing the same capability over A2A and the Agent Web UI.

## Explore the documentation

<div class="grid cards" markdown>

- :material-rocket-launch: **[Installation](installation.md)** — pip, source, extras, and the prebuilt Docker image.
- :material-server-network: **[Deployment](deployment.md)** — run the MCP and agent servers, Docker Compose, Caddy + Technitium.
- :material-console: **[Usage](usage.md)** — the MCP tools, the `Api` client, and the CLI.
- :material-database-cog: **[Backing Platform](platform.md)** — deploy ArchiveBox with Docker.
- :material-sitemap: **[Overview](overview.md)** — ecosystem role, configuration, and architecture.
- :material-tag-multiple: **[Concepts](concepts.md)** — the `CONCEPT:ABOX-*` registry.

</div>

## Quick start

```bash
pip install "archivebox-api[mcp]"
archivebox-mcp                   # stdio MCP server (default transport)
```

Connect it to an ArchiveBox instance:

```bash
export ARCHIVEBOX_BASE_URL=http://your-archivebox:8000
export ARCHIVEBOX_USERNAME=admin
export ARCHIVEBOX_PASSWORD=your-password
archivebox-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

See **[Installation](installation.md)** and **[Deployment](deployment.md)** for the
full matrix (PyPI extras, Docker image, all transports, the agent server, reverse
proxy, DNS).
</content>
