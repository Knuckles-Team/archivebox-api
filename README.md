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

*Version: 0.13.0*

---

## Overview

**Archivebox Api** is a production-grade Agent and Model Context Protocol (MCP) server designed to interface directly with Pythonic ArchiveBox API Wrapper and Fast MCP Server for Agentic AI use!.

---

## Key Features

- **Consolidated Action-Routed MCP Tools:** Minimizes token overhead and eliminates tool bloat in LLM contexts by grouping methods into optimized, togglable tool modules.
- **Enterprise-Grade Security:** Comprehensive support for Eunomia policies, OIDC token delegation, and granular execution context tracking.
- **Integrated Graph Agent:** Built-in Pydantic AI agent supporting the Agent Control Protocol (ACP) and standard Web interfaces (AG-UI).
- **Native Telemetry & Tracing:** Out-of-the-box OpenTelemetry exports and native Langfuse tracing.

---

## CLI or API

This agent wraps the Pythonic ArchiveBox API Wrapper and Fast MCP Server for Agentic AI use! API. You can interact with it programmatically or via its integrated execution entrypoints.

Detailed instructions on how to use the underlying API wrappers, extended schema bindings, and developer SDK references are maintained in [docs/index.md](file:///home/apps/workspace/agent-packages/agents/archivebox-api/docs/index.md).

---

## MCP

This server utilizes dynamic Action-Routed tools to optimize token overhead and maximize IDE compatibility.

### Available MCP Tools
| Tool Module | Toggle Env Var | Enabled by Default | Description & Nested Methods |
|-------------|----------------|--------------------|------------------------------|
| **Authentication** | `AUTHENTICATIONTOOL` | `True` | Manage archivebox authentication operations. Action-routed methods: `get_api_token`, `check_api_token`. |
| **Core** | `CORETOOL` | `True` | Manage archivebox core operations. Action-routed methods: `get_snapshots`, `get_snapshot`, `get_archiveresults`, `get_tag`, `get_any`. |
| **Cli** | `CLITOOL` | `True` | Manage archivebox cli operations. Action-routed methods: `cli_add`, `cli_update`, `cli_schedule`, `cli_list`, `cli_remove`. |

Detailed tool schemas, parameter shapes, and validation constraints are preserved in [docs/mcp.md](file:///home/apps/workspace/agent-packages/agents/archivebox-api/docs/mcp.md).

### MCP Configuration Examples

#### stdio Transport (Recommended for local IDEs e.g., Cursor, Claude Desktop)
Configure your IDE's `mcp.json` to launch the MCP server via `uvx`:

```json
{
  "mcpServers": {
    "archivebox-api": {
      "command": "uvx",
      "args": [
        "--from",
        "archivebox-api",
        "archivebox-mcp"
      ],
      "env": {
        "ARCHIVEBOX_BASE_URL": "your_archivebox_base_url_here",
        "ARCHIVEBOX_USERNAME": "your_archivebox_username_here",
        "ARCHIVEBOX_SSL_VERIFY": "your_archivebox_ssl_verify_here",
        "DEBUG": "your_debug_here",
        "PYTHONUNBUFFERED": "your_pythonunbuffered_here",
        "ARCHIVEBOX_API_KEY": "your_archivebox_api_key_here",
        "ARCHIVEBOX_TOKEN": "your_archivebox_token_here",
        "ARCHIVEBOX_PASSWORD": "your_archivebox_password_here"
      }
    }
  }
}
```

#### Streamable-HTTP Transport (Recommended for production deployments)
Configure your client's `mcp.json` to launch the Streamable-HTTP server via `uvx` with explicit host and port definition:

```json
{
  "mcpServers": {
    "archivebox-api": {
      "command": "uvx",
      "args": [
        "--from",
        "archivebox-api",
        "archivebox-mcp"
      ],
      "env": {
        "TRANSPORT": "streamable-http",
        "HOST": "0.0.0.0",
        "PORT": "8000",
        "ARCHIVEBOX_BASE_URL": "your_archivebox_base_url_here",
        "ARCHIVEBOX_USERNAME": "your_archivebox_username_here",
        "ARCHIVEBOX_SSL_VERIFY": "your_archivebox_ssl_verify_here",
        "DEBUG": "your_debug_here",
        "PYTHONUNBUFFERED": "your_pythonunbuffered_here",
        "ARCHIVEBOX_API_KEY": "your_archivebox_api_key_here",
        "ARCHIVEBOX_TOKEN": "your_archivebox_token_here",
        "ARCHIVEBOX_PASSWORD": "your_archivebox_password_here"
      }
    }
  }
}
```

Alternatively, connect to a pre-deployed remote or local Streamable-HTTP instance:

```json
{
  "mcpServers": {
    "archivebox-api": {
      "url": "http://localhost:8000/archivebox-api/mcp"
    }
  }
}
```

Deploying the Streamable-HTTP server via Docker:

```bash
docker run -d \
  --name archivebox-api-mcp \
  -p 8000:8000 \
  -e TRANSPORT=streamable-http \
  -e PORT=8000 \
  -e ARCHIVEBOX_BASE_URL="your_value" \
  -e ARCHIVEBOX_USERNAME="your_value" \
  -e ARCHIVEBOX_SSL_VERIFY="your_value" \
  -e DEBUG="your_value" \
  -e PYTHONUNBUFFERED="your_value" \
  -e ARCHIVEBOX_API_KEY="your_value" \
  -e ARCHIVEBOX_TOKEN="your_value" \
  -e ARCHIVEBOX_PASSWORD="your_value" \
  knucklessg1/archivebox-api:latest
```

---

## Agent

This repository features a fully integrated Pydantic AI Graph Agent. It communicates over the **Agent Control Protocol (ACP)** and interacts seamlessly with the **Agent Web UI (AG-UI)** and Terminal interface.

### Running the Agent CLI
To start the interactive command-line agent:

```bash
# Set credentials
export ARCHIVEBOX_BASE_URL="your_value"
export ARCHIVEBOX_USERNAME="your_value"
export ARCHIVEBOX_SSL_VERIFY="your_value"
export DEBUG="your_value"
export PYTHONUNBUFFERED="your_value"
export ARCHIVEBOX_API_KEY="your_value"
export ARCHIVEBOX_TOKEN="your_value"
export ARCHIVEBOX_PASSWORD="your_value"

# Run the agent server
archivebox-agent --provider openai --model-id gpt-4o
```

### Docker Compose Orchestration
The following `docker/agent.compose.yml` configures the Agent, Web UI, and Terminal Interface together:

```yaml
version: '3.8'

services:
  archivebox-api-mcp:
    image: knucklessg1/archivebox-api:latest
    container_name: archivebox-api-mcp
    hostname: archivebox-api-mcp
    restart: always
    env_file:
      - ../.env
    environment:
      - PYTHONUNBUFFERED=1
      - HOST=0.0.0.0
      - PORT=8000
      - TRANSPORT=streamable-http
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "python3", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

  archivebox-api-agent:
    image: knucklessg1/archivebox-api:latest
    container_name: archivebox-api-agent
    hostname: archivebox-api-agent
    restart: always
    depends_on:
      - archivebox-api-mcp
    env_file:
      - ../.env
    command: [ "archivebox-agent" ]
    environment:
      - PYTHONUNBUFFERED=1
      - HOST=0.0.0.0
      - PORT=9013
      - MCP_URL=http://archivebox-api-mcp:8000/mcp
      - PROVIDER=${PROVIDER:-openai}
      - MODEL_ID=${MODEL_ID:-gpt-4o}
      - ENABLE_WEB_UI=True
      - ENABLE_OTEL=True
    ports:
      - "9013:9013"
    healthcheck:
      test: ["CMD", "python3", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:9013/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

```

Detailed graph node architecture explanations, custom skill configurations, and agentic trace guides are available in [docs/agent.md](file:///home/apps/workspace/agent-packages/agents/archivebox-api/docs/agent.md).

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

## Repository Owners

<img width="100%" height="180em" src="https://github-readme-stats.vercel.app/api?username=Knucklessg1&show_icons=true&hide_border=true&&count_private=true&include_all_commits=true" />

![GitHub followers](https://img.shields.io/github/followers/Knucklessg1)
![GitHub User's stars](https://img.shields.io/github/stars/Knucklessg1)

---

## Contribute

Contributions are welcome! Please ensure code quality by executing local checks before submitting pull requests:
- Format code using `ruff format .`
- Lint code using `ruff check .`
- Validate type-safety with `mypy .`
- Execute test suites using `pytest`
