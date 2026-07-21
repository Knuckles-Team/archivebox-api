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

*Version: 1.0.1*

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
| **`AU-OS.governance.wasm-micro-agent-sandbox`** | Agent OS Infrastructure | Telemetry & Observability | Delivers warning suppressions, JSON progress logging, and error tracing. |

---

## Environment Variables

<!-- ENV-VARS-TABLE:START -->

#### Package environment variables

| Variable | Example | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` |  |
| `PORT` | `8000` |  |
| `TRANSPORT` | `stdio` | options: stdio, streamable-http, sse |
| `ENABLE_OTEL` | `True` |  |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://localhost:8080/api/public/otel` |  |
| `OTEL_EXPORTER_OTLP_PUBLIC_KEY` | `pk-...` |  |
| `OTEL_EXPORTER_OTLP_SECRET_KEY` | `sk-...` |  |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | `http/protobuf` |  |
| `EUNOMIA_TYPE` | `none` | options: none, embedded, remote |
| `EUNOMIA_POLICY_FILE` | `mcp_policies.json` |  |
| `EUNOMIA_REMOTE_URL` | `http://eunomia-server:8000` |  |
| `ARCHIVEBOX_BASE_URL` | `http://localhost:8000` |  |
| `ARCHIVEBOX_URL` | `http://localhost:8000` | ARCHIVEBOX_URL is a fallback/alternative alias for ARCHIVEBOX_BASE_URL |
| `ARCHIVEBOX_USERNAME` | — |  |
| `ARCHIVEBOX_TLS_PROFILE` | — | Named runtime TLS profile |
| `ARCHIVEBOX_TLS_PROFILE_REF` | — | Secret reference containing a TLS profile |
| `DEBUG` | `False` |  |
| `PYTHONUNBUFFERED` | `1` |  |
| `ARCHIVEBOX_API_KEY` | `your_archivebox_api_key_here` |  |
| `ARCHIVEBOX_TOKEN` | `your_archivebox_token_here` |  |
| `ARCHIVEBOX_PASSWORD` | `your_archivebox_password_here` |  |
| `AUTHENTICATIONTOOL` | `True` |  |
| `CORETOOL` | `True` |  |
| `CLITOOL` | `True` |  |

#### Inherited agent-utilities variables (apply to every connector)

| Variable | Example | Description |
|----------|---------|-------------|
| `MCP_TOOL_MODE` | `condensed` | Tool surface: `condensed` | `verbose` | `both` |
| `MCP_ENABLED_TOOLS` | — | Comma-separated tool allow-list |
| `MCP_DISABLED_TOOLS` | — | Comma-separated tool deny-list |
| `MCP_ENABLED_TAGS` | — | Comma-separated tag allow-list |
| `MCP_DISABLED_TAGS` | — | Comma-separated tag deny-list |
| `MCP_CLIENT_AUTH` | — | Outbound MCP auth (`oidc-client-credentials` for fleet calls) |
| `OIDC_CLIENT_ID` | — | OIDC client id (service-account auth) |
| `OIDC_CLIENT_SECRET` | — | OIDC client secret (service-account auth) |
| `MCP_URL` | `http://localhost:8000/mcp` | URL of the MCP server the agent connects to |
| `PROVIDER` | `openai` | LLM provider for the agent |
| `MODEL_ID` | `gpt-4o` | Model id for the agent |
| `ENABLE_WEB_UI` | `True` | Serve the AG-UI web interface |

_23 package + 12 inherited variable(s). Auto-generated from `.env.example` + the shared agent-utilities set — do not edit._
<!-- ENV-VARS-TABLE:END -->


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
| `ARCHIVEBOX_TLS_PROFILE` | Named TLS profile for private PKI, mTLS, or proxy policy | — |
| `ARCHIVEBOX_TLS_PROFILE_REF` | Secret reference containing the TLS profile | — |

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
)

# Fetch snapshots
snapshots = client.get_snapshots()
for snapshot in snapshots.get("results", []):
    print(f"[{snapshot['timestamp']}] {snapshot['url']}")
```

Refer to [docs/index.md](docs/index.md) for full developer SDK and class references.

---

## MCP Server Setup

> **Install the connector-focused `[mcp]` extra.** Examples use `archivebox-api[mcp]` to add
> FastMCP / FastAPI through `agent-utilities[mcp]`; the required Agent Utilities core
> still carries `epistemic-graph[full]`. The `[agent]` extra additionally
> enables model orchestration.

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
| `archivebox-api[mcp]` | Connector-focused MCP server (`agent-utilities[mcp]` — FastMCP/FastAPI + `epistemic-graph[full]`) | You only run the **MCP server** (smallest install / image) |
| `archivebox-api[agent]` | Agent runtime (`agent-utilities[agent-runtime,logfire]` — model orchestration + `epistemic-graph[full]`) | You run the **integrated agent** |
| `archivebox-api[all]` | Everything (`mcp` + `agent` + `logfire`) | Development / both surfaces |

```bash
# Connector-focused MCP server (includes the shared graph engine)
uv pip install "archivebox-api[mcp]"

# Agent runtime (adds model orchestration to the shared graph engine)
uv pip install "archivebox-api[agent]"

# Everything (development)
uv pip install "archivebox-api[all]"      # or: python -m pip install "archivebox-api[all]"
```

### Container images (`:mcp` vs `:agent`)

One multi-stage `docker/Dockerfile` builds two right-sized images, selected by `--target`:

| Image tag | Build target | Contents | Entrypoint |
|-----------|--------------|----------|------------|
| `example/archivebox-api:mcp` | `--target mcp` | `archivebox-api[mcp]` — **connector-focused**, includes `epistemic-graph[full]`; no model-orchestration stack | `archivebox-mcp` |
| `example/archivebox-api@sha256:<digest>` | `--target agent` (default) | `archivebox-api[agent]` — **agent runtime**, model orchestration + `epistemic-graph[full]` | `archivebox-agent` |

```bash
docker build --target mcp   -t example/archivebox-api:mcp    docker/   # connector-focused MCP server
docker build --target agent -t example/archivebox-api:agent-local docker/   # agent runtime
```

`docker/mcp.compose.yml` runs the connector-focused `:mcp` server; `docker/agent.compose.yml` runs the
agent (`immutable agent digest`) with a co-located `:mcp` sidecar.

### Knowledge-graph database (`epistemic-graph`)

Both `[mcp]` and `[agent]` carry the **epistemic-graph** engine through the required
Agent Utilities core dependency (`epistemic-graph[full]`). The `[mcp]` extra keeps
the server connector-focused; `[agent]` additionally enables model orchestration. Local
deployments can use the bundled engine. For production or shared state, run
**epistemic-graph as a dedicated database service** and configure the runtime to use it.
Deployment recipes (single-node + Raft HA), connection configuration, and architecture
diagrams are documented in the
[epistemic-graph deployment guide](https://knuckles-team.github.io/epistemic-graph/deployment/).

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

#### Condensed action-routed tools (default — `MCP_TOOL_MODE=condensed`)

| MCP Tool | Toggle Env Var | Description |
|----------|----------------|-------------|
| `archivebox_authentication` | `AUTHENTICATIONTOOL` | Manage archivebox authentication operations. |
| `archivebox_cli` | `CLITOOL` | Manage archivebox cli operations. |
| `archivebox_core` | `CORETOOL` | Manage archivebox core operations. |

#### Verbose 1:1 API-mapped tools (`MCP_TOOL_MODE=verbose` or `both`)

<details>
<summary>14 per-operation tools — one per public API method (click to expand)</summary>

| MCP Tool | Toggle Env Var | Description |
|----------|----------------|-------------|
| `archivebox_check_api_token` | `APITOOL` | Validate an API token to make sure it's valid and non-expired |
| `archivebox_cli_add` | `APITOOL` | Execute archivebox add command |
| `archivebox_cli_list` | `APITOOL` | Execute archivebox list command |
| `archivebox_cli_remove` | `APITOOL` | Execute archivebox remove command |
| `archivebox_cli_schedule` | `APITOOL` | Execute archivebox schedule command |
| `archivebox_cli_update` | `APITOOL` | Execute archivebox update command |
| `archivebox_get_any` | `APITOOL` | Get a specific Snapshot, ArchiveResult, or Tag by abid |
| `archivebox_get_api_token` | `APITOOL` | Generate an API token for a given username & password |
| `archivebox_get_archiveresult` | `APITOOL` | Get a specific ArchiveResult by id or abid |
| `archivebox_get_archiveresults` | `APITOOL` | List all ArchiveResult entries matching these filters |
| `archivebox_get_snapshot` | `APITOOL` | Get a specific Snapshot by abid or id |
| `archivebox_get_snapshots` | `APITOOL` | Retrieve list of snapshots |
| `archivebox_get_tag` | `APITOOL` | Get a specific Tag by id or abid |
| `archivebox_get_tags` | `APITOOL` | Retrieve list of tags |

</details>

_3 action-routed tool(s) (default) · 14 verbose 1:1 tool(s). Each is enabled unless its `<DOMAIN>TOOL` toggle is set false; `MCP_TOOL_MODE` selects the surface (`condensed` default · `verbose` 1:1 · `both`). Auto-generated — do not edit._
<!-- MCP-TOOLS-TABLE:END -->

<!-- BEGIN GENERATED: additional-deployment-options -->
### Additional Deployment Options

`archivebox-api` can run as a local stdio process or container, or behind a remote
network boundary. The
[Deployment guide](https://knuckles-team.github.io/archivebox-api/deployment/) carries
the detailed transport contract.

- **Local container** — launch a reviewed immutable image as a least-privilege
  stdio child with no listener or published port.
- **Remote URL** — connect through an operator-supplied authenticated HTTPS
  ingress. Keep its URL, outbound identity references, trust profile, and exact
  `MCP_ALLOWED_HOSTS` in `AgentConfig`.
<!-- END GENERATED: additional-deployment-options -->


<!-- BEGIN agent-utilities-deployment (generated; do not edit between markers) -->

## Deploy with `agent-utilities-deployment`

Provision this package with the consolidated **`agent-utilities-deployment`**
workflow. It selects an installed-package, editable-source, or immutable-container
path; records only runtime secret and TLS-profile references in `AgentConfig`; and
runs doctor, registration, policy, observability, and rollback gates. Ask your agent
to **"deploy `archivebox-api` with agent-utilities-deployment"**.

| Install mode | Command |
|------|---------|
| Installed package | `uv tool install "archivebox-api[mcp]"`, then run `archivebox-mcp` |
| Editable source | `uv pip install -e ".[agent]"`, then run `archivebox-mcp` |
| Immutable container | deploy `registry.example.invalid/archivebox-api@sha256:<digest>` through the operator-selected orchestrator |

The repository embeds no deployment profile, credential value, certificate path, or
environment-specific endpoint. Supply those at runtime through `AgentConfig` and the
configured secret provider.

<!-- END agent-utilities-deployment -->

<!-- GOVERNED-CAPABILITY:START -->
## Governed capability contract

This package ships a compact canonical skill surface with specialist procedures
kept as referenced workflows. The current MCP tools, skill metadata,
`connector_manifest.yml`, ontology, mappings, shapes, fixtures, migrations,
tool-schema fingerprints, and certification metadata form one versioned
capability contract. Validate them together; do not rely on stale tool names or
historical per-task skill wrappers.

Runtime endpoints, credentials, certificate trust, tenant identity, retention,
and observability policy are deployment inputs and are never packaged values.
See [Configuration, trust, and privacy](docs/configuration.md) before enabling a
network transport, connector ingestion, GraphOS delegation, or trace export.
<!-- GOVERNED-CAPABILITY:END -->
