"""MCP tools for core operations.

Auto-generated from mcp_server.py during ecosystem standardization.
"""

from agent_utilities.mcp_utilities import resolve_action, run_blocking
from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from archivebox_api.auth import get_client

CORE_ACTIONS = (
    "get_snapshots",
    "get_snapshot",
    "get_archiveresults",
    "get_tag",
    "get_any",
)


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
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        resolved = resolve_action(action, CORE_ACTIONS, service="archivebox-api")
        if isinstance(resolved, dict):
            return resolved
        action = resolved

        if action == "get_snapshots":
            return await run_blocking(client.get_snapshots, **kwargs)
        if action == "get_snapshot":
            return await run_blocking(client.get_snapshot, **kwargs)
        if action == "get_archiveresults":
            return await run_blocking(client.get_archiveresults, **kwargs)
        if action == "get_tag":
            return await run_blocking(client.get_tag, **kwargs)
        if action == "get_any":
            return await run_blocking(client.get_any, **kwargs)
        raise ValueError(f"Unknown action: {action}")
