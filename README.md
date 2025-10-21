# ArchiveBox API

![PyPI - Version](https://img.shields.io/pypi/v/archivebox-api)
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

*Version: 0.0.4*

ArchiveBox API Python Wrapper & Fast MCP Server!

This repository provides a Python wrapper for interacting with the ArchiveBox API, enabling programmatic access to web archiving functionality. It includes a Model Context Protocol (MCP) server for Agentic AI, enhanced with various authentication mechanisms, middleware for observability and control, and optional Eunomia authorization for policy-based access control.

Contributions are welcome!

All API Response objects are customized for the response call. You can access return values in a `parent.value.nested_value` format, or use `parent.json()` to get the response as a dictionary.

#### API Calls:
- Authentication
- Core Model (Snapshots, ArchiveResults, Tags)
- CLI Commands (add, update, schedule, list, remove)

If your API call isn't supported, you can extend the functionality by adding custom endpoints or modifying the existing wrapper.

[These are the API endpoints currently supported](https://demo.archivebox.io/api/v1/docs)

#### Features:
- **Authentication**: Supports multiple authentication types including none (disabled), static (internal tokens), JWT, OAuth Proxy, OIDC Proxy, and Remote OAuth for external identity providers.
- **Middleware**: Includes logging, timing, rate limiting, and error handling for robust server operation.
- **Eunomia Authorization**: Optional policy-based authorization with embedded or remote Eunomia server integration.
- **Resources**: Provides `instance_config` for ArchiveBox configuration.
- **Prompts**: Includes `cli_add_prompt` for AI-driven interactions.

<details>
  <summary><b>Usage:</b></summary>

### MCP CLI

| Short Flag | Long Flag                          | Description                                                                 |
|------------|------------------------------------|-----------------------------------------------------------------------------|
| -h         | --help                             | Display help information                                                    |
| -t         | --transport                        | Transport method: 'stdio', 'http', or 'sse' [legacy] (default: stdio)       |
| -s         | --host                             | Host address for HTTP transport (default: 0.0.0.0)                          |
| -p         | --port                             | Port number for HTTP transport (default: 8000)                              |
|            | --auth-type                        | Authentication type: 'none', 'static', 'jwt', 'oauth-proxy', 'oidc-proxy', 'remote-oauth' (default: none) |
|            | --token-jwks-uri                   | JWKS URI for JWT verification                                              |
|            | --token-issuer                     | Issuer for JWT verification                                                |
|            | --token-audience                   | Audience for JWT verification                                              |
|            | --oauth-upstream-auth-endpoint     | Upstream authorization endpoint for OAuth Proxy                             |
|            | --oauth-upstream-token-endpoint    | Upstream token endpoint for OAuth Proxy                                    |
|            | --oauth-upstream-client-id         | Upstream client ID for OAuth Proxy                                         |
|            | --oauth-upstream-client-secret     | Upstream client secret for OAuth Proxy                                     |
|            | --oauth-base-url                   | Base URL for OAuth Proxy                                                   |
|            | --oidc-config-url                  | OIDC configuration URL                                                     |
|            | --oidc-client-id                   | OIDC client ID                                                             |
|            | --oidc-client-secret               | OIDC client secret                                                         |
|            | --oidc-base-url                    | Base URL for OIDC Proxy                                                    |
|            | --remote-auth-servers              | Comma-separated list of authorization servers for Remote OAuth             |
|            | --remote-base-url                  | Base URL for Remote OAuth                                                  |
|            | --allowed-client-redirect-uris     | Comma-separated list of allowed client redirect URIs                       |
|            | --eunomia-type                     | Eunomia authorization type: 'none', 'embedded', 'remote' (default: none)   |
|            | --eunomia-policy-file              | Policy file for embedded Eunomia (default: mcp_policies.json)              |
|            | --eunomia-remote-url               | URL for remote Eunomia server                                              |

### Using as an MCP Server

The MCP Server can be run in two modes: `stdio` (for local testing) or `http` (for networked access). To start the server, use the following commands:

#### Run in stdio mode (default):
```bash
archivebox-mcp --transport "stdio"
```

#### Run in HTTP mode:
```bash
archivebox-mcp --transport "http" --host "0.0.0.0" --port "8000"
```

### Basic API Usage

**Token Authentication**

```python
#!/usr/bin/python
# coding: utf-8
import archivebox_api

archivebox_url = "<ARCHIVEBOX_URL>"
token = "<ARCHIVEBOX_TOKEN>"

client = archivebox_api.Api(
    url=archivebox_url,
    token=token
)

snapshots = client.get_snapshots()
print(f"Snapshots: {snapshots.json()}")
```

**Basic Authentication**

```python
#!/usr/bin/python
# coding: utf-8
import archivebox_api

username = "<ARCHIVEBOX_USERNAME>"
password = "<ARCHIVEBOX_PASSWORD>"
archivebox_url = "<ARCHIVEBOX_URL>"

client = archivebox_api.Api(
    url=archivebox_url,
    username=username,
    password=password
)

snapshots = client.get_snapshots()
print(f"Snapshots: {snapshots.json()}")
```

**API Key Authentication**

```python
#!/usr/bin/python
# coding: utf-8
import archivebox_api

archivebox_url = "<ARCHIVEBOX_URL>"
api_key = "<ARCHIVEBOX_API_KEY>"

client = archivebox_api.Api(
    url=archivebox_url,
    api_key=api_key
)

snapshots = client.get_snapshots()
print(f"Snapshots: {snapshots.json()}")
```

**SSL Verify**

```python
#!/usr/bin/python
# coding: utf-8
import archivebox_api

username = "<ARCHIVEBOX_USERNAME>"
password = "<ARCHIVEBOX_PASSWORD>"
archivebox_url = "<ARCHIVEBOX_URL>"

client = archivebox_api.Api(
    url=archivebox_url,
    username=username,
    password=password,
    verify=False
)

snapshots = client.get_snapshots()
print(f"Snapshots: {snapshots.json()}")
```

### Deploy MCP Server as a Service

The ArchiveBox MCP server can be deployed using Docker, with configurable authentication, middleware, and Eunomia authorization.

#### Using Docker Run

```bash
docker pull archivebox/archivebox:latest

docker run -d \
  --name archivebox-mcp \
  -p 8004:8004 \
  -e HOST=0.0.0.0 \
  -e PORT=8004 \
  -e TRANSPORT=http \
  -e AUTH_TYPE=none \
  -e EUNOMIA_TYPE=none \
  -e ARCHIVEBOX_URL=https://yourinstance.archivebox.com \
  -e ARCHIVEBOX_USERNAME=user \
  -e ARCHIVEBOX_PASSWORD=pass \
  -e ARCHIVEBOX_TOKEN=token \
  -e ARCHIVEBOX_API_KEY=api_key \
  -e ARCHIVEBOX_VERIFY=False \
  archivebox/archivebox:latest
```

For advanced authentication (e.g., JWT, OAuth Proxy, OIDC Proxy, Remote OAuth) or Eunomia, add the relevant environment variables:

```bash
docker run -d \
  --name archivebox-mcp \
  -p 8004:8004 \
  -e HOST=0.0.0.0 \
  -e PORT=8004 \
  -e TRANSPORT=http \
  -e AUTH_TYPE=oidc-proxy \
  -e OIDC_CONFIG_URL=https://provider.com/.well-known/openid-configuration \
  -e OIDC_CLIENT_ID=your-client-id \
  -e OIDC_CLIENT_SECRET=your-client-secret \
  -e OIDC_BASE_URL=https://your-server.com \
  -e ALLOWED_CLIENT_REDIRECT_URIS=http://localhost:*,https://*.example.com/* \
  -e EUNOMIA_TYPE=embedded \
  -e EUNOMIA_POLICY_FILE=/app/mcp_policies.json \
  -e ARCHIVEBOX_URL=https://yourinstance.archivebox.com \
  -e ARCHIVEBOX_USERNAME=user \
  -e ARCHIVEBOX_PASSWORD=pass \
  -e ARCHIVEBOX_TOKEN=token \
  -e ARCHIVEBOX_API_KEY=api_key \
  -e ARCHIVEBOX_VERIFY=False \
  archivebox/archivebox:latest
```

#### Using Docker Compose

Create a `docker-compose.yml` file:

```yaml
services:
  archivebox-mcp:
    image: archivebox/archivebox:latest
    environment:
      - HOST=0.0.0.0
      - PORT=8004
      - TRANSPORT=http
      - AUTH_TYPE=none
      - EUNOMIA_TYPE=none
      - ARCHIVEBOX_URL=https://yourinstance.archivebox.com
      - ARCHIVEBOX_USERNAME=user
      - ARCHIVEBOX_PASSWORD=pass
      - ARCHIVEBOX_TOKEN=token
      - ARCHIVEBOX_API_KEY=api_key
      - ARCHIVEBOX_VERIFY=False
    ports:
      - 8004:8004
```

For advanced setups with authentication and Eunomia:

```yaml
services:
  archivebox-mcp:
    image: archivebox/archivebox:latest
    environment:
      - HOST=0.0.0.0
      - PORT=8004
      - TRANSPORT=http
      - AUTH_TYPE=oidc-proxy
      - OIDC_CONFIG_URL=https://provider.com/.well-known/openid-configuration
      - OIDC_CLIENT_ID=your-client-id
      - OIDC_CLIENT_SECRET=your-client-secret
      - OIDC_BASE_URL=https://your-server.com
      - ALLOWED_CLIENT_REDIRECT_URIS=http://localhost:*,https://*.example.com/*
      - EUNOMIA_TYPE=embedded
      - EUNOMIA_POLICY_FILE=/app/mcp_policies.json
      - ARCHIVEBOX_URL=https://yourinstance.archivebox.com
      - ARCHIVEBOX_USERNAME=user
      - ARCHIVEBOX_PASSWORD=pass
      - ARCHIVEBOX_TOKEN=token
      - ARCHIVEBOX_API_KEY=api_key
      - ARCHIVEBOX_VERIFY=False
    ports:
      - 8004:8004
    volumes:
      - ./mcp_policies.json:/app/mcp_policies.json
```

Run the service:

```bash
docker-compose up -d
```

#### Configure `mcp.json` for AI Integration

Recommended: Store secrets in environment variables with lookup in the JSON file.

For Testing Only: Plain text storage will also work, although **not** recommended.

```json
{
  "mcpServers": {
    "archivebox": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "archivebox-api",
        "archivebox-mcp",
        "--transport",
        "${TRANSPORT}",
        "--host",
        "${HOST}",
        "--port",
        "${PORT}",
        "--auth-type",
        "${AUTH_TYPE}",
        "--eunomia-type",
        "${EUNOMIA_TYPE}"
      ],
      "env": {
        "ARCHIVEBOX_URL": "https://yourinstance.archivebox.com",
        "ARCHIVEBOX_USERNAME": "user",
        "ARCHIVEBOX_PASSWORD": "pass",
        "ARCHIVEBOX_TOKEN": "token",
        "ARCHIVEBOX_API_KEY": "api_key",
        "ARCHIVEBOX_VERIFY": "False",
        "TOKEN_JWKS_URI": "${TOKEN_JWKS_URI}",
        "TOKEN_ISSUER": "${TOKEN_ISSUER}",
        "TOKEN_AUDIENCE": "${TOKEN_AUDIENCE}",
        "OAUTH_UPSTREAM_AUTH_ENDPOINT": "${OAUTH_UPSTREAM_AUTH_ENDPOINT}",
        "OAUTH_UPSTREAM_TOKEN_ENDPOINT": "${OAUTH_UPSTREAM_TOKEN_ENDPOINT}",
        "OAUTH_UPSTREAM_CLIENT_ID": "${OAUTH_UPSTREAM_CLIENT_ID}",
        "OAUTH_UPSTREAM_CLIENT_SECRET": "${OAUTH_UPSTREAM_CLIENT_SECRET}",
        "OAUTH_BASE_URL": "${OAUTH_BASE_URL}",
        "OIDC_CONFIG_URL": "${OIDC_CONFIG_URL}",
        "OIDC_CLIENT_ID": "${OIDC_CLIENT_ID}",
        "OIDC_CLIENT_SECRET": "${OIDC_CLIENT_SECRET}",
        "OIDC_BASE_URL": "${OIDC_BASE_URL}",
        "REMOTE_AUTH_SERVERS": "${REMOTE_AUTH_SERVERS}",
        "REMOTE_BASE_URL": "${REMOTE_BASE_URL}",
        "ALLOWED_CLIENT_REDIRECT_URIS": "${ALLOWED_CLIENT_REDIRECT_URIS}",
        "EUNOMIA_TYPE": "${EUNOMIA_TYPE}",
        "EUNOMIA_POLICY_FILE": "${EUNOMIA_POLICY_FILE}",
        "EUNOMIA_REMOTE_URL": "${EUNOMIA_REMOTE_URL}"
      },
      "timeout": 200000
    }
  }
}
```

#### CLI Parameters

The `archivebox-mcp` command supports the following CLI options for configuration:

- `--transport`: Transport method (`stdio`, `http`, `sse`) [default: `http`]
- `--host`: Host address for HTTP transport [default: `0.0.0.0`]
- `--port`: Port number for HTTP transport [default: `8000`]
- `--auth-type`: Authentication type (`none`, `static`, `jwt`, `oauth-proxy`, `oidc-proxy`, `remote-oauth`) [default: `none`]
- `--token-jwks-uri`: JWKS URI for JWT verification
- `--token-issuer`: Issuer for JWT verification
- `--token-audience`: Audience for JWT verification
- `--oauth-upstream-auth-endpoint`: Upstream authorization endpoint for OAuth Proxy
- `--oauth-upstream-token-endpoint`: Upstream token endpoint for OAuth Proxy
- `--oauth-upstream-client-id`: Upstream client ID for OAuth Proxy
- `--oauth-upstream-client-secret`: Upstream client secret for OAuth Proxy
- `--oauth-base-url`: Base URL for OAuth Proxy
- `--oidc-config-url`: OIDC configuration URL
- `--oidc-client-id`: OIDC client ID
- `--oidc-client-secret`: OIDC client secret
- `--oidc-base-url`: Base URL for OIDC Proxy
- `--remote-auth-servers`: Comma-separated list of authorization servers for Remote OAuth
- `--remote-base-url`: Base URL for Remote OAuth
- `--allowed-client-redirect-uris`: Comma-separated list of allowed client redirect URIs
- `--eunomia-type`: Eunomia authorization type (`none`, `embedded`, `remote`) [default: `none`]
- `--eunomia-policy-file`: Policy file for embedded Eunomia [default: `mcp_policies.json`]
- `--eunomia-remote-url`: URL for remote Eunomia server

#### Middleware

The MCP server includes the following built-in middleware for enhanced functionality:

- **ErrorHandlingMiddleware**: Provides comprehensive error logging and transformation.
- **RateLimitingMiddleware**: Limits request frequency with a token bucket algorithm (10 requests/second, burst capacity of 20).
- **TimingMiddleware**: Tracks execution time of requests.
- **LoggingMiddleware**: Logs all requests and responses for observability.

#### Eunomia Authorization

The server supports optional Eunomia authorization for policy-based access control:

- **Disabled (`none`)**: No authorization checks.
- **Embedded (`embedded`)**: Runs an embedded Eunomia server with a local policy file (`mcp_policies.json` by default).
- **Remote (`remote`)**: Connects to an external Eunomia server for centralized policy decisions.

To configure Eunomia policies:

```bash
# Initialize a default policy file
eunomia-mcp init

# Validate the policy file
eunomia-mcp validate mcp_policies.json
```

</details>

<details>
  <summary><b>Installation Instructions:</b></summary>

Install Python Package

```bash
python -m pip install archivebox-api eunomia-mcp
```

</details>


<img width="100%" height="180em" src="https://github-readme-stats.vercel.app/api?username=Knucklessg1&show_icons=true&hide_border=true&&count_private=true&include_all_commits=true" />

![GitHub followers](https://img.shields.io/github/followers/Knucklessg1)

![GitHub User's stars](https://img.shields.io/github/stars/Knucklessg1)
