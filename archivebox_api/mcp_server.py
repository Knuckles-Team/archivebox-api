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
import os
import sys
from typing import Any

from agent_utilities.base_utilities import to_boolean
from agent_utilities.mcp_utilities import create_mcp_server
from dotenv import find_dotenv, load_dotenv
from starlette.requests import Request
from starlette.responses import JSONResponse

from archivebox_api.auth import get_client

__version__ = "0.25.0"

# Telemetry & Observability
logger = get_logger(name="archivebox-api")
logger.setLevel(logging.INFO)


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
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "get_api_token":
            return client.get_api_token(**kwargs)
        if action == "check_api_token":
            return client.check_api_token(**kwargs)
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
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "get_snapshots":
            return client.get_snapshots(**kwargs)
        if action == "get_snapshot":
            return client.get_snapshot(**kwargs)
        if action == "get_archiveresults":
            return client.get_archiveresults(**kwargs)
        if action == "get_tag":
            return client.get_tag(**kwargs)
        if action == "get_any":
            return client.get_any(**kwargs)
        raise ValueError(f"Unknown action: {action}")


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
            ctx.info("Executing tool...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "cli_add":
            return client.cli_add(**kwargs)
        if action == "cli_update":
            return client.cli_update(**kwargs)
        if action == "cli_schedule":
            return client.cli_schedule(**kwargs)
        if action == "cli_list":
            return client.cli_list(**kwargs)
        if action == "cli_remove":
            return client.cli_remove(**kwargs)
        raise ValueError(f"Unknown action: {action}")


def get_mcp_instance() -> tuple[Any, ...]:
    """Initialize and return the MCP instance."""
    load_dotenv(find_dotenv())
    args, mcp, middlewares = create_mcp_server(
        name="archivebox-api MCP",
        version=__version__,
        instructions="archivebox-api MCP Server — Condensed Action-Routed Tools.",
    )

    @mcp.custom_route("/health", methods=["GET"])
    async def health_check(request: Request) -> JSONResponse:
        return JSONResponse({"status": "OK"})

    DEFAULT_AUTHENTICATIONTOOL = to_boolean(os.getenv("AUTHENTICATIONTOOL", "True"))
    if DEFAULT_AUTHENTICATIONTOOL:
        register_authentication_tools(mcp)
    DEFAULT_CORETOOL = to_boolean(os.getenv("CORETOOL", "True"))
    if DEFAULT_CORETOOL:
        register_core_tools(mcp)
    DEFAULT_CLITOOL = to_boolean(os.getenv("CLITOOL", "True"))
    if DEFAULT_CLITOOL:
        register_cli_tools(mcp)

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
