"""Tests for standardized action discovery via the shared agent-utilities helper.

CONCEPT:ECO-4.0 — Tool Interface & MCP Factory
"""

from collections.abc import Callable
from typing import cast

import pytest
from fastmcp import FastMCP


async def _get_tool(register, name) -> Callable:
    mcp = FastMCP("test")
    register(mcp)
    tool_obj = await mcp.get_tool(name)
    assert tool_obj is not None
    return cast(Callable, getattr(tool_obj, "fn", tool_obj))


@pytest.mark.asyncio
async def test_authentication_list_actions(mock_client):
    from archivebox_api.mcp_server import register_authentication_tools

    tool = await _get_tool(register_authentication_tools, "archivebox_authentication")
    res = await tool(
        action="list_actions", params_json="{}", client=mock_client, ctx=None
    )
    assert res["service"] == "archivebox-api"
    assert "get_api_token" in res["actions"]
    assert "check_api_token" in res["actions"]


@pytest.mark.asyncio
async def test_core_list_actions(mock_client):
    from archivebox_api.mcp_server import register_core_tools

    tool = await _get_tool(register_core_tools, "archivebox_core")
    res = await tool(
        action="list_actions", params_json="{}", client=mock_client, ctx=None
    )
    assert "get_snapshots" in res["actions"]


@pytest.mark.asyncio
async def test_cli_list_actions(mock_client):
    from archivebox_api.mcp_server import register_cli_tools

    tool = await _get_tool(register_cli_tools, "archivebox_cli")
    res = await tool(
        action="list_actions", params_json="{}", client=mock_client, ctx=None
    )
    assert "cli_add" in res["actions"]


@pytest.mark.asyncio
async def test_bogus_action_raises_did_you_mean(mock_client):
    from archivebox_api.mcp_server import register_core_tools

    tool = await _get_tool(register_core_tools, "archivebox_core")
    with pytest.raises(ValueError) as exc:
        await tool(
            action="get_snapshotz", params_json="{}", client=mock_client, ctx=None
        )
    msg = str(exc.value)
    assert "list_actions" in msg
    assert "get_snapshots" in msg
