# Usage — API / CLI / MCP

`archivebox-api` exposes the same capability three ways: as **MCP tools** an agent
calls, as a **Python API** (`Api`) you import, and as a **CLI**. The ecosystem role
and full configuration matrix are in [Overview](overview.md).

## As an MCP server

Once [deployed](deployment.md), the server registers three consolidated,
action-routed tool modules. Each module is toggled by its own environment variable
and dispatches on an `action` argument plus a JSON `params` string.

| Tool | Toggle | Actions |
|---|---|---|
| `archivebox_authentication` | `AUTHENTICATIONTOOL` | `get_api_token`, `check_api_token` |
| `archivebox_core` | `CORETOOL` | `get_snapshots`, `get_snapshot`, `get_archiveresults`, `get_tag`, `get_any` |
| `archivebox_cli` | `CLITOOL` | `cli_add`, `cli_update`, `cli_schedule`, `cli_list`, `cli_remove` |

Example agent prompts that map onto these tools:

- *"List the most recent snapshots in the archive"* → `archivebox_core` (`get_snapshots`)
- *"Archive this URL: https://example.com"* → `archivebox_cli` (`cli_add`)
- *"Fetch an API token for the configured user"* → `archivebox_authentication` (`get_api_token`)

## As a Python API

`Api` is a `requests`-based REST client composed of the authentication, core, and CLI
mixins. Construct it directly with a base URL and credentials:

```python
from archivebox_api import Api

api = Api(
    url="http://your-archivebox:8000",
    username="admin",
    password="your-password",
    verify=False,                 # self-signed homelab cert
)

# Reads
snapshots = api.get_snapshots()              # paginated snapshot catalog
results = api.get_archiveresults()           # per-snapshot archive outputs
tags = api.get_tags()
one = api.get_snapshot(snapshot_id="<abid>")

for snapshot in snapshots.json().get("results", []):
    print(f"[{snapshot['timestamp']}] {snapshot['url']}")
```

Authentication and token verification:

```python
token = api.get_api_token(username="admin", password="your-password")
api.check_api_token(token=token)
```

The client accepts a pre-issued `token` or an `api_key` in place of a
username/password pair.

## As a CLI

The CLI tool module drives the ArchiveBox command line — adding, updating,
scheduling, listing, and removing archived URLs:

```python
api.cli_add(urls=["https://example.com"])    # archive a new URL
api.cli_list()                               # list archived entries
api.cli_update()                             # refresh existing snapshots
api.cli_remove(filter_patterns=["https://example.com"])
```

These same operations are exposed through the `archivebox_cli` MCP tool and through
the agent server, so an agent can request them conversationally.
</content>
