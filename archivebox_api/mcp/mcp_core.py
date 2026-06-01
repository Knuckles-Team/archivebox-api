"""MCP tools for core operations.

Auto-generated from mcp_server.py during ecosystem standardization.
"""

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from archivebox_api.auth import get_client


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
