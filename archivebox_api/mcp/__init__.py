"""MCP tool registration modules for archivebox-api.

Auto-generated during ecosystem standardization.
Each domain has its own module with a register_*_tools function.
"""

from archivebox_api.mcp.mcp_authentication import register_authentication_tools
from archivebox_api.mcp.mcp_cli import register_cli_tools
from archivebox_api.mcp.mcp_core import register_core_tools

__all__ = [
    "register_authentication_tools",
    "register_cli_tools",
    "register_core_tools",
]
