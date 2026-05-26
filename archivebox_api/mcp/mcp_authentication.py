"""MCP tools for authentication operations.

Auto-generated from mcp_server.py during ecosystem standardization.
"""

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from archivebox_api.auth import get_client


def register_authentication_tools(mcp: FastMCP):
    """Register authentication management tools.

    CONCEPT:OS-5.1 — Security & Auth
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
