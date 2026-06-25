# Archivebox Api
## CLI or API | MCP | Agent

![PyPI - Version](https://img.shields.io/pypi/v/archivebox-api)
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')
![PyPI - Downloads](https://img.shields.io/pypi/dd/archivebox-api)
![GitHub Repo stars](https://img.shields.io/github/stars/Knuckles-Team/archivebox-api)
![GitHub forks](https://img.shields.io/github/forks/Knuckles-Team/archivebox-api)
![GitHub contributors](https://img.shields.io/github/contributors/Knuckles-Team/archivebox-api)
![PyPI - License](https://img.shields.io/pypi/l/archivebox-api)
![GitHub](https://img.shields.io/github/license/Knuckles-Team/archivebox-api)
![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/Knuckles-Team/archivebox-api)
![GitHub pull requests](https://img.shields.io/github/issues-pr/Knuckles-Team/archivebox-api)
![GitHub closed pull requests](https://img.shields.io/github/issues-pr-closed/Knuckles-Team/archivebox-api)
![GitHub issues](https://img.shields.io/github/issues/Knuckles-Team/archivebox-api)
![GitHub top language](https://img.shields.io/github/languages/top/Knuckles-Team/archivebox-api)
![GitHub language count](https://img.shields.io/github/languages/count/Knuckles-Team/archivebox-api)
![GitHub repo size](https://img.shields.io/github/repo-size/Knuckles-Team/archivebox-api)
![GitHub repo file count (file type)](https://img.shields.io/github/directory-file-count/Knuckles-Team/archivebox-api)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/archivebox-api)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/archivebox-api)

*Version: 0.34.0*

> **Documentation** — Installation, deployment, usage across the API, CLI, MCP, and
> A2A agent interfaces, and guidance for provisioning the ArchiveBox platform are
> maintained in the [official documentation](https://knuckles-team.github.io/archivebox-api/).

---

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Concept Registry](#concept-registry)
- [Environment Variables](#environment-variables)
- [CLI or API Usage](#cli-or-api-usage)
- [MCP Server Setup](#mcp-server-setup)
- [Agentic AI Graph Agent](#agentic-ai-graph-agent)
- [Security & Governance](#security--governance)
- [Installation](#installation)
- [Contribute](#contribute)

---

## Overview

**Archivebox Api** is a production-grade Agent and Model Context Protocol (MCP) server designed to interface directly with the Pythonic ArchiveBox API Wrapper and Fast MCP Server for Agentic AI use!

---

## Key Features

- **Consolidated Action-Routed MCP Tools:** Minimizes token overhead and eliminates tool bloat in LLM contexts by grouping methods into optimized, togglable tool modules.
- **Enterprise-Grade Security:** Comprehensive support for Eunomia policies, OIDC token delegation, and granular execution context tracking.
- **Integrated Graph Agent:** Built-in Pydantic AI agent supporting the Agent Control Protocol (ACP) and standard Web interfaces (AG-UI).
- **Native Telemetry & Tracing:** Out-of-the-box OpenTelemetry exports and native Langfuse tracing.

---

## Concept Registry

This codebase is aligned with the **5 Core Pillars Architecture** of the `agent-utilities` ecosystem:

| Concept ID | Pillar Name | Domain | Implementation Details in archivebox-api |
|------------|-------------|--------|-----------------------------------------|
| **`ECO-4.0`** | Ecosystem & Peripherals | Tool Interface & MCP Factory | Provides FastMCP server wrapper, action routing tools, and dynamic schema exposures. |
| **`ECO-4.1`** | Ecosystem & Peripherals | A2A Network & Consensus | Manages agent peer discovery, routing tables, and consensus. |
| **`OS-5.1`** | Agent OS Infrastructure | Security & Auth | Implements token-based OIDC access control, JWT filters, and Eunomia validation. |
| **`OS-5.4`** | Agent OS Infrastructure | Telemetry & Observability | Delivers warning suppressions, JSON progress logging, and error tracing. |

---

## Environment Variables

Configure the runtime environment by creating a `.env` file based on `.env.example`.
Every variable the server reads, grouped by concern.

### Connection & Credentials
| Variable | Description | Default |
|----------|-------------|---------|
| `ARCHIVEBOX_BASE_URL` | Canonical endpoint URL for the backend ArchiveBox API | `http://localhost:8000` |
| `ARCHIVEBOX_URL` | Fallback alias/alternative for `ARCHIVEBOX_BASE_URL` | `http://localhost:8000` |
| `ARCHIVEBOX_USERNAME` | Username for authentication | — |
| `ARCHIVEBOX_PASSWORD` | Password for authentication | — |
| `ARCHIVEBOX_API_KEY` | API key for token-less header authentication | — |
| `ARCHIVEBOX_TOKEN` | Pre-configured authentication token | — |
| `ARCHIVEBOX_SSL_VERIFY` (alias `ARCHIVEBOX_VERIFY`) | Enable/disable SSL certificate validation | `False` |

### MCP server / transport
| Variable | Description | Default |
|----------|-------------|---------|
| `TRANSPORT` | `stdio`, `streamable-http`, or `sse` | `stdio` |
| `HOST` | Bind host (HTTP transports) | `0.0.0.0` |
| `PORT` | Bind port (HTTP transports) | `8000` |
| `MCP_TOOL_MODE` | Tool surface: `condensed`, `verbose`, or `both` | `condensed` |
| `MCP_ENABLED_TOOLS` / `MCP_DISABLED_TOOLS` | Comma-separated tool allow/deny list | — |
| `MCP_ENABLED_TAGS` / `MCP_DISABLED_TAGS` | Comma-separated tag allow/deny list | — |
| `DEBUG` | Verbose logging | `False` |
| `PYTHONUNBUFFERED` | Unbuffered stdout (recommended in containers) | `1` |

### Tool toggles
Each action-routed tool can be disabled individually via its toggle env var (set to `false`):
`AUTHENTICATIONTOOL`, `CORETOOL`, `CLITOOL` (see the [Available MCP Tools](#available-mcp-tools) table below).

### Telemetry & governance
| Variable | Description | Default |
|----------|-------------|---------|
| `ENABLE_OTEL` | Enable OpenTelemetry export | `True` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP collector endpoint | — |
| `OTEL_EXPORTER_OTLP_PUBLIC_KEY` / `OTEL_EXPORTER_OTLP_SECRET_KEY` | OTLP auth keys | — |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | OTLP protocol (e.g. `http/protobuf`) | — |
| `EUNOMIA_TYPE` | Authorization mode: `none`, `embedded`, `remote` | `none` |
| `EUNOMIA_POLICY_FILE` | Embedded policy file | `mcp_policies.json` |
| `EUNOMIA_REMOTE_URL` | Remote Eunomia server URL | — |

### Agent CLI (full `[agent]` runtime only)
| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_URL` | URL of the MCP server the agent connects to | `http://localhost:8000/mcp` |
| `PROVIDER` | LLM provider (e.g. `openai`) | `openai` |
| `MODEL_ID` | Model id (e.g. `gpt-4o`) | `gpt-4o` |
| `ENABLE_WEB_UI` | Serve the AG-UI web interface | `True` |

---

## CLI or API Usage

You can use the API client programmatically in Python to manage ArchiveBox snapshots:

```python
from archivebox_api import Api

# Initialize client
client = Api(
    url="http://localhost:8000",
    token="your-auth-token",
    verify=True
)

# Fetch snapshots
snapshots = client.get_snapshots()
for snapshot in snapshots.get("results", []):
    print(f"[{snapshot['timestamp']}] {snapshot['url']}")
```

Refer to [docs/index.md](docs/index.md) for full developer SDK and class references.

---

## MCP Server Setup

> **Install the slim `[mcp]` extra.** Install `archivebox-api[mcp]` — the MCP-server
> extra that pulls only the FastMCP / FastAPI tooling (`agent-utilities[mcp]`). It
> deliberately **excludes** the heavy agent runtime (the epistemic-graph engine,
> `pydantic-ai`, `dspy`, `llama-index`, `tree-sitter`), so `uvx`/container installs are
> dramatically smaller and faster. Use the full `[agent]` extra only when you need the
> integrated Pydantic AI agent (see [Installation](#installation)).

This server utilizes dynamic Action-Routed tools to optimize token overhead and maximize IDE compatibility.

### Tool Catalog

See the auto-generated [Available MCP Tools](#available-mcp-tools) table below for the full, live list of tools.

### Dynamic Tool Selection & Visibility

This MCP server supports dynamic toolset selection and visibility filtering at runtime. This allows you to restrict the set of exposed tools in order to prevent blowing up the LLM's context window.

You can configure tool filtering via multiple input channels:

- **CLI Arguments:** Pass `--tools` or `--toolsets` (or their disabled counterparts `--disabled-tools` and `--disabled-toolsets`) during startup.
- **Environment Variables:** Define standard environment variables:
  - `MCP_ENABLED_TOOLS` / `MCP_DISABLED_TOOLS`
  - `MCP_ENABLED_TAGS` / `MCP_DISABLED_TAGS`
- **HTTP SSE Request Headers:** Pass custom headers during transport initialization:
  - `x-mcp-enabled-tools` / `x-mcp-disabled-tools`
  - `x-mcp-enabled-tags` / `x-mcp-disabled-tags`
- **HTTP SSE Request Query Parameters:** Append query parameters directly to your transport connection URL:
  - `?tools=tool1,tool2`
  - `?tags=tag1`

When query strings or parameters are supplied, an LLM-free **Knowledge Graph resolution layer** (using `DynamicToolOrchestrator`) matches query intents against known tool tags, names, or descriptions, with safe fallback and automated 24-hour background cache refreshing.

---

### Local IDE Configuration (Cursor / Claude Desktop)
Add the following block to your `mcp.json` to configure stdio transport via `uvx`:

```json
{
  "mcpServers": {
    "archivebox-api": {
      "command": "uv",
      "args": [
        "run",
        "--package",
        "archivebox-api",
        "archivebox-mcp"
      ],
      "env": {
        "ARCHIVEBOX_BASE_URL": "http://localhost:8000",
        "ARCHIVEBOX_USERNAME": "admin",
        "ARCHIVEBOX_PASSWORD": "your-password"
      }
    }
  }
}
```

---

## Agentic AI Graph Agent

This repository features a fully integrated Pydantic AI Graph Agent. It communicates over the **Agent Control Protocol (ACP)** and interacts seamlessly with the **Agent Web UI (AG-UI)**.

### Running the Agent CLI
To start the interactive command-line agent:

```bash
# Export credentials
export ARCHIVEBOX_BASE_URL="http://localhost:8000"
export ARCHIVEBOX_USERNAME="admin"
export ARCHIVEBOX_PASSWORD="your-password"

# Run agent server
archivebox-agent --provider openai --model-id gpt-4o
```

Detailed graph node architecture explanations, custom skill configurations, and agentic trace guides are available in [docs/index.md](docs/index.md#agent-orchestration).

---

## Security & Governance

Built directly upon the enterprise-ready [`agent-utilities`](https://github.com/Knuckles-Team/agent-utilities) core, standard security parameters are fully supported:

### Access Control & Policy Enforcement
- **Eunomia Policies:** Fine-grained, policy-driven tool authorization. Supports `none`, local `embedded` (`mcp_policies.json`), or centralized `remote` modes.
- **OIDC Token Delegation:** Compliant with RFC 8693 token exchange for flowing authenticating user credentials from Web UI / ACP → Agent → MCP.
- **Scoped Credentials:** Execution context runs restricted to the specific caller identity.

### Runtime Security Grid
| Feature | Functionality | Enablement |
|---------|---------------|------------|
| **Tool Guard** | Sensitivity inspection with human-in-the-loop validation | Enabled by default |
| **Prompt Injection Defense** | Input scanning, repetition monitoring, and recursive loop blocks | Enabled by default |
| **Context Safety Guard** | Stuck-loop detectors and contextual overflow preemptive alerts | Enabled by default |

---

## Installation

Pick the extra that matches what you want to run:

| Extra | Installs | Use when |
|-------|----------|----------|
| `archivebox-api[mcp]` | Slim MCP server only (`agent-utilities[mcp]` — FastMCP/FastAPI) | You only run the **MCP server** (smallest install / image) |
| `archivebox-api[agent]` | Full agent runtime (`agent-utilities[agent,logfire]` — Pydantic AI + the epistemic-graph engine) | You run the **integrated agent** |
| `archivebox-api[all]` | Everything (`mcp` + `agent` + `logfire`) | Development / both surfaces |

```bash
# MCP server only (recommended for tool hosting — slim deps)
uv pip install "archivebox-api[mcp]"

# Full agent runtime (Pydantic AI + epistemic-graph engine)
uv pip install "archivebox-api[agent]"

# Everything (development)
uv pip install "archivebox-api[all]"      # or: python -m pip install "archivebox-api[all]"
```

### Container images (`:mcp` vs `:agent`)

One multi-stage `docker/Dockerfile` builds two right-sized images, selected by `--target`:

| Image tag | Build target | Contents | Entrypoint |
|-----------|--------------|----------|------------|
| `knucklessg1/archivebox-api:mcp` | `--target mcp` | `archivebox-api[mcp]` — **slim**, no engine/`pydantic-ai`/`dspy`/`llama-index`/`tree-sitter` | `archivebox-mcp` |
| `knucklessg1/archivebox-api:latest` | `--target agent` (default) | `archivebox-api[agent]` — **full** agent runtime + epistemic-graph engine | `archivebox-agent` |

```bash
docker build --target mcp   -t knucklessg1/archivebox-api:mcp    docker/   # slim MCP server
docker build --target agent -t knucklessg1/archivebox-api:latest docker/   # full agent
```

`docker/mcp.compose.yml` runs the slim `:mcp` server; `docker/agent.compose.yml` runs the
agent (`:latest`) with a co-located `:mcp` sidecar.

### Knowledge-graph database (`epistemic-graph`)

The **full agent** (`[agent]` / `:latest`) embeds the **epistemic-graph** engine (pulled in
transitively via `agent-utilities[agent]`). For production — or to share one knowledge graph
across multiple agents — run **epistemic-graph as its own database container** and point the
agent at it instead of embedding it. Deployment recipes (single-node + Raft HA), connection
config, and the full database architecture (with diagrams) are documented in the
[epistemic-graph deployment guide](https://knuckles-team.github.io/epistemic-graph/deployment/).
The slim `[mcp]` server does **not** require the database.

---

## Documentation

The complete documentation is published as the
[official documentation site](https://knuckles-team.github.io/archivebox-api/) and is
the recommended reference for installation, deployment, and day-to-day operation.

| Page | Contents |
|---|---|
| [Installation](https://knuckles-team.github.io/archivebox-api/installation/) | pip, source, extras, prebuilt Docker image |
| [Deployment](https://knuckles-team.github.io/archivebox-api/deployment/) | run the MCP and agent servers, Compose, Caddy + Technitium, env config |
| [Usage](https://knuckles-team.github.io/archivebox-api/usage/) | the MCP tools, the `Api` client, the CLI |
| [Backing Platform](https://knuckles-team.github.io/archivebox-api/platform/) | deploy ArchiveBox with Docker |
| [Overview](https://knuckles-team.github.io/archivebox-api/overview/) | ecosystem role, configuration, architecture |
| [Concepts](https://knuckles-team.github.io/archivebox-api/concepts/) | concept registry (`CONCEPT:ABOX-*`) |

`AGENTS.md` is the canonical contributor/agent guidance.

---

## Contribute

Contributions are welcome! Please ensure code quality by executing local checks before submitting pull requests:
- Format code using `ruff format .`
- Lint code using `ruff check .`
- Validate type-safety with `mypy .`
- Execute test suites using `pytest`


### Available MCP Tools

The table below is auto-generated from the live server — do not edit by hand.

<!-- MCP-TOOLS-TABLE:START -->

| MCP Tool | Toggle Env Var | Description |
|----------|----------------|-------------|
| `archivebox_authentication` | `AUTHENTICATIONTOOL` | Manage archivebox authentication operations. |
| `archivebox_cli` | `CLITOOL` | Manage archivebox cli operations. |
| `archivebox_core` | `CORETOOL` | Manage archivebox core operations. |

_3 action-routed tools (default `MCP_TOOL_MODE=condensed`). Each is enabled unless its toggle is set false; set `MCP_TOOL_MODE=verbose` (or `both`) for the 1:1 per-operation surface. Auto-generated — do not edit._
<!-- MCP-TOOLS-TABLE:END -->

<!-- BEGIN GENERATED: additional-deployment-options -->
### Additional Deployment Options

`archivebox-api` can also run as a **local container** (Docker / Podman / `uv`) or be
consumed from a **remote deployment**. The
[Deployment guide](https://knuckles-team.github.io/archivebox-api/deployment/) has full, copy-paste
`mcp_config.json` for all four transports — **stdio**, **streamable-http**,
**local container / uv**, and **remote URL**:

- **Local container / uv** — launch the server from `mcp_config.json` via `uvx`,
  `docker run`, or `podman run`, or point at a local streamable-http container by `url`.
- **Remote URL** — connect to a server deployed behind Caddy at
  `http://archivebox-mcp.arpa/mcp` using the `"url"` key.
<!-- END GENERATED: additional-deployment-options -->


<!-- BEGIN agent-os-genesis-deploy (generated; do not edit between markers) -->

## Deploy with `agent-os-genesis`

This package can be provisioned for you — skill-guided — by the **`agent-os-genesis`**
universal skill (its *single-package deploy mode*): it picks your install method, seeds
secrets to OpenBao/Vault (or `.env`), trusts your enterprise CA, registers the MCP
server, and verifies it — the same machinery that stands up the whole Agent OS, narrowed
to just this package. Ask your agent to **"deploy `archivebox-api` with agent-os-genesis"**.

| Install mode | Command |
|------|---------|
| Bare-metal, prod (PyPI) | `uvx archivebox-mcp` · or `uv tool install archivebox-api` |
| Bare-metal, dev (editable) | `uv pip install -e ".[all]"` · or `pip install -e ".[all]"` |
| Container, prod | deploy `knucklessg1/archivebox-api:latest` via docker-compose / swarm / podman / podman-compose / kubernetes |
| Container, dev (editable) | deploy `docker/compose.dev.yml` (source-mounted at `/src`; edits live on restart) |

Secrets are read-existing + seeded via `vault_sync` — you are only prompted for what's missing.

<!-- END agent-os-genesis-deploy -->
