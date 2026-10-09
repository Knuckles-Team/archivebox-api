#!/usr/bin/python
"""ArchiveBox MCP Server.

Tool Interface & MCP Factory
Provides dynamic tool registration and stdio/SSE/http interfaces using FastMCP.
"""

import warnings

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from fastmcp.utilities.logging import get_logger
from pydantic import Field

# Filter RequestsDependencyWarning early to prevent log spam
# Telemetry & Observability
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    try:
        from requests.exceptions import RequestsDependencyWarning

        warnings.filterwarnings("ignore", category=RequestsDependencyWarning)
    except ImportError:
        pass

warnings.filterwarnings("ignore", message=".*urllib3.*or chardet.*")
warnings.filterwarnings("ignore", message=".*urllib3.*or charset_normalizer.*")

import logging
import sys
from typing import Any

from agent_connector_sdk.config import load_config
from agent_connector_sdk.mcp.action_dispatch import resolve_action
from agent_connector_sdk.mcp.concurrency import run_blocking
from agent_connector_sdk.mcp.server import create_mcp_server
from agent_connector_sdk.mcp.tool_surface import register_tool_surface
from starlette.requests import Request
from starlette.responses import JSONResponse

from archivebox_api.api_client import Api
from archivebox_api.auth import get_client

__version__ = "2.1.0"

# Telemetry & Observability
logger = get_logger(name="archivebox-api")
logger.setLevel(logging.INFO)


AUTHENTICATION_ACTIONS = ("get_api_token", "check_api_token")
CORE_ACTIONS = (
    "get_snapshots",
    "get_snapshot",
    "get_archiveresults",
    "get_tag",
    "get_any",
)
CLI_ACTIONS = ("cli_add", "cli_update", "cli_schedule", "cli_list", "cli_remove")


def _parse_action_kwargs(params_json: str) -> dict[str, Any] | None:
    """Parse a tool's ``params_json`` blob into filtered kwargs, or None if invalid."""
    import json

    try:
        kwargs = json.loads(params_json)
    except Exception:  # noqa: BLE001 — any parse failure is reported the same way
        return None
    return {k: v for k, v in kwargs.items() if v is not None}


async def _dispatch_core_action(
    client: Any, action: str, kwargs: dict[str, Any]
) -> dict:
    """Call the client method matching a resolved core action; ``action`` is
    already validated by ``resolve_action`` against ``CORE_ACTIONS``, and every
    core action name equals its client method name."""
    if action not in CORE_ACTIONS:
        raise ValueError(f"Unknown action: {action}")
    resp = await run_blocking(getattr(client, action), **kwargs)
    if action == "get_snapshots":
        await _auto_ingest_snapshots(resp)
    return resp


async def _dispatch_cli_action(
    client: Any, action: str, kwargs: dict[str, Any]
) -> dict:
    """Call the client method matching a resolved cli action; ``action`` is
    already validated by ``resolve_action`` against ``CLI_ACTIONS``, and every
    cli action name equals its client method name."""
    if action not in CLI_ACTIONS:
        raise ValueError(f"Unknown action: {action}")
    return await run_blocking(getattr(client, action), **kwargs)


def register_authentication_tools(mcp: FastMCP):
    """Register authentication management tools.

    Security & Auth
    """

    @mcp.tool(tags={"authentication"})
    async def archivebox_authentication(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_api_token', 'check_api_token'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage archivebox authentication operations."""
        if ctx:
            await ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception:
            return {"error": "Operation failed"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        resolved = resolve_action(
            action, AUTHENTICATION_ACTIONS, service="archivebox-api"
        )
        if isinstance(resolved, dict):
            return resolved
        action = resolved

        if action == "get_api_token":
            return await run_blocking(client.get_api_token, **kwargs)
        if action == "check_api_token":
            return await run_blocking(client.check_api_token, **kwargs)
        raise ValueError(f"Unknown action: {action}")


def register_core_tools(mcp: FastMCP):
    @mcp.tool(tags={"core"})
    async def archivebox_core(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_snapshots', 'get_snapshot', 'get_archiveresults', 'get_tag', 'get_any'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage archivebox core operations."""
        if ctx:
            await ctx.info("Executing tool...")
        kwargs = _parse_action_kwargs(params_json)
        if kwargs is None:
            return {"error": "Operation failed"}

        resolved = resolve_action(action, CORE_ACTIONS, service="archivebox-api")
        if isinstance(resolved, dict):
            return resolved

        return await _dispatch_core_action(client, resolved, kwargs)


def register_cli_tools(mcp: FastMCP):
    @mcp.tool(tags={"cli"})
    async def archivebox_cli(
        action: str = Field(
            description="Action to perform. Must be one of: 'cli_add', 'cli_update', 'cli_schedule', 'cli_list', 'cli_remove'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters to pass to the action."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Manage archivebox cli operations."""
        if ctx:
            await ctx.info("Executing tool...")
        kwargs = _parse_action_kwargs(params_json)
        if kwargs is None:
            return {"error": "Operation failed"}

        resolved = resolve_action(action, CLI_ACTIONS, service="archivebox-api")
        if isinstance(resolved, dict):
            return resolved

        return await _dispatch_cli_action(client, resolved, kwargs)


def _records_from_dict(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Pull a record list out of a Ninja pagination envelope, or wrap a lone record."""
    for key in ("items", "results", "data", "snapshots"):
        value = data.get(key)
        if isinstance(value, list):
            return [r for r in value if isinstance(r, dict)]
    return [data] if data.get("id") or data.get("abid") else []


def _records_from_list(data: list[Any]) -> list[dict[str, Any]]:
    """Keep only the dict entries of a bare list response."""
    return [r for r in data if isinstance(r, dict)]


def _records_from_response(resp: Any) -> list[dict[str, Any]]:
    """Best-effort: pull a list of record dicts out of an ArchiveBox API response.

    Accepts a ``requests.Response``, a Ninja pagination envelope
    (``{"items"|"results"|"data": [...]}``), a bare list, or a single dict.
    """
    data: Any = resp
    if hasattr(resp, "json"):
        try:
            data = resp.json()
        except Exception:  # noqa: BLE001 — non-JSON body
            return []
    if isinstance(data, dict):
        return _records_from_dict(data)
    if isinstance(data, list):
        return _records_from_list(data)
    return []


async def _auto_ingest_snapshots(resp: Any) -> None:
    """Default-on, best-effort native KG ingestion after a snapshot fetch.

    No-ops unless a live epistemic-graph engine is reachable. Disable by setting
    ``ARCHIVEBOX_KG_AUTO_INGEST=0``. Never raises into the tool path.
    """
    import os

    if os.environ.get("ARCHIVEBOX_KG_AUTO_INGEST", "1") == "0":
        return
    try:
        records = _records_from_response(resp)
        if not records:
            return
        from archivebox_api.kg_ingest import ingest_snapshots

        await ingest_snapshots(records)
    except Exception as e:  # noqa: BLE001 — ingestion is best-effort
        logger.debug("Operation failed: error_type=%s", type(e).__name__)


def register_kg_tools(mcp: FastMCP):
    """Wire-First native-ingestion tools (CONCEPT:AU-KG.ingest.enterprise-source-extractor)."""

    @mcp.tool(tags={"kg"})
    async def archivebox_ingest_snapshots(
        params_json: str = Field(
            default="{}",
            description="JSON string of get_snapshots filters (e.g. tag, search, limit).",
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """List ArchiveBox snapshots and natively ingest them into epistemic-graph.

        Pushes :Snapshot (+ :Tag + :hasTag) nodes and per-snapshot :Document page-text,
        plus any nested :ArchiveResult links, via the fast engine client. Best-effort:
        returns ``{"ingested": None}`` when no engine is reachable.
        """
        import json

        from archivebox_api.kg_ingest import ingest_snapshots

        if ctx:
            await ctx.info("Ingesting snapshots into the knowledge graph...")
        try:
            kwargs = json.loads(params_json) if params_json else {}
        except Exception:  # noqa: BLE001
            return {"error": "Operation failed"}
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        resp = await run_blocking(client.get_snapshots, **kwargs)
        records = _records_from_response(resp)
        result = await ingest_snapshots(records)
        return {"listed": len(records), "ingested": result}

    @mcp.tool(tags={"kg"})
    async def archivebox_ingest_archiveresults(
        params_json: str = Field(
            default="{}",
            description="JSON string of get_archiveresults filters (e.g. snapshot_id, extractor, status).",
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """List ArchiveBox archive results and ingest them as :ArchiveResult nodes.

        Best-effort: returns ``{"ingested": None}`` when no engine is reachable.
        """
        import json

        from archivebox_api.kg_ingest import ingest_archiveresults

        if ctx:
            await ctx.info("Ingesting archive results into the knowledge graph...")
        try:
            kwargs = json.loads(params_json) if params_json else {}
        except Exception:  # noqa: BLE001
            return {"error": "Operation failed"}
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        resp = await run_blocking(client.get_archiveresults, **kwargs)
        records = _records_from_response(resp)
        result = await ingest_archiveresults(records)
        return {"listed": len(records), "ingested": result}


def get_mcp_instance() -> tuple[Any, ...]:
    """Initialize and return the MCP instance."""
    load_config()
    args, mcp, middlewares = create_mcp_server(
        name="archivebox-api MCP",
        version=__version__,
        instructions="archivebox-api MCP Server — Condensed Action-Routed Tools.",
    )

    @mcp.custom_route("/health", methods=["GET"])
    async def health_check(request: Request) -> JSONResponse:
        return JSONResponse({"status": "OK"})

    register_tool_surface(
        mcp,
        client_cls=Api,
        get_client=get_client,
        service="archivebox-api",
        tools_module=sys.modules[__name__],
    )

    for mw in middlewares:
        mcp.add_middleware(mw)
    return mcp, args, middlewares


def mcp_server() -> None:
    mcp, args, middlewares = get_mcp_instance()
    print(f"archivebox-api MCP v{__version__}", file=sys.stderr)
    print("\nStarting MCP Server", file=sys.stderr)
    print(f"  Transport: {args.transport.upper()}", file=sys.stderr)
    print(f"  Auth: {args.auth_type}", file=sys.stderr)

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    elif args.transport == "streamable-http":
        mcp.run(transport="streamable-http", host=args.host, port=args.port)
    elif args.transport == "sse":
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        logger.error("Invalid transport", extra={"transport": args.transport})
        sys.exit(1)


if __name__ == "__main__":
    mcp_server()
