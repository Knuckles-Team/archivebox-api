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

*Version: 0.26.0*

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

Configure the runtime environment by creating a `.env` file based on `.env.example`:

| Env Variable | Type | Default | Description |
|--------------|------|---------|-------------|
| `ARCHIVEBOX_BASE_URL` | String | `http://localhost:8000` | Canonical endpoint URL for the backend ArchiveBox API. |
| `ARCHIVEBOX_URL` | String | `http://localhost:8000` | Fallback alias/alternative for `ARCHIVEBOX_BASE_URL`. |
| `ARCHIVEBOX_USERNAME` | String | *None* | Username for authentication. |
| `ARCHIVEBOX_PASSWORD` | String | *None* | Password for authentication. |
| `ARCHIVEBOX_API_KEY` | String | *None* | API Key for token-less header authentication. |
| `ARCHIVEBOX_TOKEN` | String | *None* | Pre-configured authentication token. |
| `ARCHIVEBOX_SSL_VERIFY`| Boolean| `False` | Enable/disable SSL certificate validation. |
| `AUTHENTICATIONTOOL` | Boolean| `True` | Toggle to enable/disable the Authentication MCP toolset. |
| `CORETOOL` | Boolean| `True` | Toggle to enable/disable the Core ArchiveBox MCP toolset. |
| `CLITOOL` | Boolean| `True` | Toggle to enable/disable the CLI command MCP toolset. |
| `EUNOMIA_TYPE` | String | `none` | Policy mode: `none`, `embedded`, or `remote`. |
| `EUNOMIA_POLICY_FILE` | String | `mcp_policies.json` | Path to the local policy file when using `embedded` mode. |
| `ENABLE_OTEL` | Boolean| `True` | Enable/disable OpenTelemetry metrics/traces exporter. |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | String | *None* | Endpoint for the OpenTelemetry collector. |

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

This server utilizes dynamic Action-Routed tools to optimize token overhead and maximize IDE compatibility.

### Available MCP Tools
- **`archivebox_authentication`** (`AUTHENTICATIONTOOL=True`): Manage token exchanges and validation (`get_api_token`, `check_api_token`).
- **`archivebox_core`** (`CORETOOL=True`): Manage core collections (`get_snapshots`, `get_snapshot`, `get_archiveresults`, `get_tag`).
- **`archivebox_cli`** (`CLITOOL=True`): Directly execute ArchiveBox command line functions (`cli_add`, `cli_list`, `cli_update`).

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

Install the Python package locally:

```bash
# Using uv (highly recommended)
uv pip install archivebox-api[all]

# Using standard pip
python -m pip install archivebox-api[all]
```

---

## Contribute

Contributions are welcome! Please ensure code quality by executing local checks before submitting pull requests:
- Format code using `ruff format .`
- Lint code using `ruff check .`
- Validate type-safety with `mypy .`
- Execute test suites using `pytest`


### Available MCP Tools
| Tool Module | Toggle Env Var | Enabled by Default | Description & Nested Methods |
|-------------|----------------|--------------------|------------------------------|
| **Authentication** | `AUTHENTICATION_TOOL` | `True` | Register authentication management tools.

    CONCEPT:OS-5.1 — Security & Auth Action-routed methods: `check_api_token`, `get_api_token`. |
| **Core** | `CORE_TOOL` | `True` | Manage archivebox core operations. Action-routed methods: `get_any`, `get_archiveresults`, `get_snapshot`, `get_snapshots`, `get_tag`. |
| **Cli** | `CLI_TOOL` | `True` | Manage archivebox cli operations. Action-routed methods: `cli_add`, `cli_list`, `cli_remove`, `cli_schedule`, `cli_update`. |
