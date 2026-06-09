# Installation

`archivebox-api` is a standard Python package and a prebuilt container image. Pick the
path that matches how you want to run it.

## Requirements

- **Python 3.11 – 3.14**.
- A reachable **ArchiveBox** instance — see [Backing Platform](platform.md) to deploy
  one locally.

## From PyPI (recommended)

```bash
pip install archivebox-api
```

### Optional extras

The base install is intentionally minimal. Install the extra for what you need:

| Extra | Install | Pulls in |
|---|---|---|
| `mcp` | `pip install "archivebox-api[mcp]"` | FastMCP MCP-server runtime (`agent-utilities[mcp]`) |
| `agent` | `pip install "archivebox-api[agent]"` | Pydantic-AI agent + Logfire tracing (`agent-utilities[agent,logfire]`) |
| `all` | `pip install "archivebox-api[all]"` | Everything above |

```bash
# Typical: run the MCP server and the graph agent
pip install "archivebox-api[all]"
```

## From source

```bash
git clone https://github.com/Knuckles-Team/archivebox-api.git
cd archivebox-api
pip install -e ".[all]"          # editable install with every extra
```

With [`uv`](https://docs.astral.sh/uv/):

```bash
uv pip install -e ".[all]"
uv run archivebox-mcp
```

## Prebuilt Docker image

A multi-stage, slim image is published on every release (installs
`archivebox-api[all]`, entrypoint `archivebox-mcp`):

```bash
docker pull knucklessg1/archivebox-api:latest

docker run --rm -i \
  -e ARCHIVEBOX_BASE_URL=http://your-archivebox:8000 \
  -e ARCHIVEBOX_USERNAME=admin \
  -e ARCHIVEBOX_PASSWORD=your-password \
  knucklessg1/archivebox-api:latest        # stdio transport (default)
```

For an HTTP server with a published port and the agent server, see
[Deployment](deployment.md).

## Verify the install

```bash
archivebox-mcp --help
python -c "import archivebox_api; print(archivebox_api.__version__)"
```

## Next steps

- **[Deployment](deployment.md)** — run it as a long-lived MCP server and agent behind Caddy + DNS.
- **[Usage](usage.md)** — call the tools, the `Api` client, and the CLI.
- **[Configuration](deployment.md#configuration-environment)** — every environment variable.
</content>
