# Deployment

This page covers running `archivebox-api` as a long-lived service: the transports, a
Docker Compose stack, the optional agent server, putting it behind a Caddy reverse
proxy, and giving it a DNS name with Technitium. To provision the **ArchiveBox
instance** it connects to, see [Backing Platform](platform.md).

> `archivebox-api` ships both an **MCP server** (console script `archivebox-mcp`) and
> an **A2A agent server** (console script `archivebox-agent`). The MCP server is the
> typed, deterministic tool surface; the agent server wraps it behind a Pydantic-AI
> graph agent and the Agent Web UI.

## Run the MCP server

The transport is selected with `--transport` (or the `TRANSPORT` env var):

=== "stdio (default)"

    ```bash
    archivebox-mcp
    ```
    For IDE / desktop MCP clients that launch the server as a subprocess.

=== "streamable-http"

    ```bash
    archivebox-mcp --transport streamable-http --host 0.0.0.0 --port 8000
    ```
    A network server with a `/health` endpoint and `/mcp` route.

=== "sse"

    ```bash
    archivebox-mcp --transport sse --host 0.0.0.0 --port 8000
    ```

Health check (HTTP transports):

```bash
curl -s http://localhost:8000/health        # {"status":"OK"}
```

## Configuration (environment)

`archivebox-api` is configured entirely from the environment. The **required** set:

| Var | Default | Meaning |
|---|---|---|
| `ARCHIVEBOX_BASE_URL` | `http://localhost:8000` | ArchiveBox API base URL |
| `ARCHIVEBOX_URL` | `http://localhost:8000` | Fallback alias for `ARCHIVEBOX_BASE_URL` |
| `ARCHIVEBOX_USERNAME` | _(unset)_ | Username for authentication |
| `ARCHIVEBOX_PASSWORD` | _(unset)_ | Password for authentication |
| `ARCHIVEBOX_API_KEY` | _(unset)_ | API key for header authentication |
| `ARCHIVEBOX_TOKEN` | _(unset)_ | Pre-configured authentication token |
| `ARCHIVEBOX_SSL_VERIFY` | `False` | Verify TLS (self-signed homelab) |
| `AUTHENTICATIONTOOL` | `True` | Register the authentication tool set |
| `CORETOOL` | `True` | Register the core catalog tool set |
| `CLITOOL` | `True` | Register the CLI tool set |

Plus `HOST` / `PORT` / `TRANSPORT` for HTTP transports, and the optional telemetry
(`ENABLE_OTEL`, `OTEL_EXPORTER_OTLP_*`) and access-governance (`EUNOMIA_TYPE`,
`EUNOMIA_POLICY_FILE`) settings. The full set is documented in
[`.env.example`](https://github.com/Knuckles-Team/archivebox-api/blob/main/.env.example).
Copy it to `.env` and populate only what you use; the client remains inactive against
endpoints whose credentials are absent.

## Docker Compose

The repo ships [`docker/mcp.compose.yml`](https://github.com/Knuckles-Team/archivebox-api/blob/main/docker/mcp.compose.yml).
It reads a sibling `.env` and publishes the HTTP server on `:8000`:

```yaml
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
```

```bash
cp .env.example .env          # then edit ARCHIVEBOX_* values
docker compose -f docker/mcp.compose.yml up -d
docker compose -f docker/mcp.compose.yml logs -f
```

## Agent server

For conversational and A2A operation, `archivebox-api` ships a Pydantic-AI graph
agent (console script `archivebox-agent`). It connects to the MCP server over
`MCP_URL` and exposes its own HTTP surface, including the Agent Web UI, on `:9013`.

```bash
export MCP_URL=http://localhost:8000/mcp
export PROVIDER=openai
export MODEL_ID=gpt-4o
archivebox-agent --host 0.0.0.0 --port 9013
```

The repo ships [`docker/agent.compose.yml`](https://github.com/Knuckles-Team/archivebox-api/blob/main/docker/agent.compose.yml),
which deploys the MCP server and the agent together and wires the agent to the MCP
server by container name:

```yaml
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
    ports:
      - "9013:9013"
```

```bash
docker compose -f docker/agent.compose.yml up -d
```

## Behind a Caddy reverse proxy

Expose the HTTP server on a hostname with automatic TLS. Add to your `Caddyfile`:

```caddy
# Internal (self-signed) — homelab .arpa zone
archivebox-api.arpa {
    tls internal
    reverse_proxy archivebox-api-mcp:8000
}
```

```caddy
# Public — automatic Let's Encrypt
archivebox-api.example.com {
    reverse_proxy archivebox-api-mcp:8000
}
```

Reload Caddy:

```bash
docker compose -f services/caddy/compose.yml exec caddy caddy reload --config /etc/caddy/Caddyfile
```

## DNS with Technitium

Point the hostname at the host running Caddy. Via the Technitium API:

```bash
curl -s "http://technitium.arpa:5380/api/zones/records/add" \
  --data-urlencode "token=$TECHNITIUM_DNS_TOKEN" \
  --data-urlencode "domain=archivebox-api.arpa" \
  --data-urlencode "zone=arpa" \
  --data-urlencode "type=A" \
  --data-urlencode "ipAddress=10.0.0.10" \
  --data-urlencode "ttl=3600"
```

…or add an **A record** `archivebox-api.arpa → <caddy-host-ip>` in the Technitium web
console (`http://technitium.arpa:5380`). The ecosystem
[`technitium-dns-mcp`](https://knuckles-team.github.io/technitium-dns-mcp/) automates
this as a tool.

## Register with an MCP client

Add to your client's `mcp_config.json`:

```json
{
  "mcpServers": {
    "archivebox-api": {
      "command": "uv",
      "args": ["run", "--package", "archivebox-api", "archivebox-mcp"],
      "env": {
        "ARCHIVEBOX_BASE_URL": "http://your-archivebox:8000",
        "ARCHIVEBOX_USERNAME": "admin",
        "ARCHIVEBOX_PASSWORD": "your-password"
      }
    }
  }
}
```

For a remote HTTP server, point the client at `http://archivebox-api.arpa/mcp` instead.
</content>
