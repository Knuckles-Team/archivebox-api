"""MCP tools for cli operations.

Auto-generated from mcp_server.py during ecosystem standardization.
"""

from agent_utilities.mcp_utilities import resolve_action
from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from archivebox_api.auth import get_client

CLI_ACTIONS = ("cli_add", "cli_update", "cli_schedule", "cli_list", "cli_remove")


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
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        resolved = resolve_action(action, CLI_ACTIONS, service="archivebox-api")
        if isinstance(resolved, dict):
            return resolved
        action = resolved

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
