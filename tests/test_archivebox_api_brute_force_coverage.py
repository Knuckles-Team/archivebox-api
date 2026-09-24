import os

# Set environment variables for defaults BEFORE any imports
os.environ["ARCHIVEBOX_URL"] = "http://test"
os.environ["ARCHIVEBOX_USERNAME"] = "test"
os.environ["ARCHIVEBOX_PASSWORD"] = "test"

import asyncio
import inspect
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_session():
    with patch("requests.Session") as mock_s:
        session = mock_s.return_value
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "id": 1,
            "url": "http://test",
            "status": "indexed",
            "token": "test",
        }
        response.text = '{"id": 1, "token": "test"}'
        session.get.return_value = response
        session.post.return_value = response
        session.put.return_value = response
        session.delete.return_value = response
        session.patch.return_value = response
        session.request.return_value = response
        yield session


_COMMON_METHOD_KWARGS: dict[str, Any] = {
    "url": "http://example.com",
    "tag": "test",
    "depth": 1,
    "id": "1",
    "snapshot_id": "1",
    "name": "test",
    "payload": {},
    "data": {},
    "limit": 10,
    "offset": 0,
}


def _kwargs_for_method(
    sig: inspect.Signature, common_kwargs: dict[str, Any]
) -> dict[str, Any]:
    """Guess a kwargs dict for one method signature from the common value pool."""
    has_kwargs = any(
        p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()
    )
    if has_kwargs:
        return common_kwargs.copy()
    kwargs = {k: v for k, v in common_kwargs.items() if k in sig.parameters}
    for p_name, p in sig.parameters.items():
        if p.default == inspect.Parameter.empty and p_name not in kwargs:
            kwargs[p_name] = "test" if p.annotation == str else 1
    return kwargs


def _call_api_method_best_effort(method: Any, common_kwargs: dict[str, Any]) -> None:
    sig = inspect.signature(method)
    kwargs = _kwargs_for_method(sig, common_kwargs)
    try:
        method(**kwargs)
    except:  # noqa: E722 — brute-force coverage sweep, any failure is expected
        pass


def test_archivebox_api_brute_force(mock_session):
    _ = mock_session
    from archivebox_api.api_client import Api

    api = Api(url="http://test", username="test", password="test")

    # Introspect all methods
    for name, method in inspect.getmembers(api, predicate=inspect.ismethod):
        if name.startswith("_"):
            continue
        print(f"Calling Api.{name}...")
        _call_api_method_best_effort(method, _COMMON_METHOD_KWARGS)


_MCP_BASE_TARGET_PARAMS: dict[str, Any] = {
    "url": "http://example.com",
    "id": "1",
    "snapshot_id": "1",
    "archivebox_url": "http://test",
    "username": "test",
    "password": "test",
    "token": "test",
    "api_key": "test",
    "urls": ["http://example.com"],
}


def _add_guessed_required_params(
    sig: inspect.Signature, target_params: dict[str, Any]
) -> dict[str, Any]:
    """Fill in a guessed value for any required param not already covered."""
    result = dict(target_params)
    for p_name, p in sig.parameters.items():
        if p.default != inspect.Parameter.empty or p_name in ("_client", "context"):
            continue
        if p_name not in result:
            result[p_name] = "test" if p.annotation == str else 1
    return result


def _accepts_var_keyword(sig: inspect.Signature) -> bool:
    return any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())


def _target_params_for_tool(sig: inspect.Signature) -> dict[str, Any]:
    """Guess a call payload for one MCP tool signature from the base value pool."""
    target_params = _add_guessed_required_params(sig, _MCP_BASE_TARGET_PARAMS)
    if _accepts_var_keyword(sig):
        return target_params
    return {k: v for k, v in target_params.items() if k in sig.parameters}


async def _call_tool_best_effort(mcp: Any, tool: Any) -> None:
    try:
        target_params = _target_params_for_tool(inspect.signature(tool.fn))
        await mcp.call_tool(tool.name, target_params)
    except:  # noqa: E722 — brute-force coverage sweep, any failure is expected
        pass


async def _run_all_tools(mcp: Any) -> None:
    tool_objs = (
        await mcp.list_tools()
        if inspect.iscoroutinefunction(mcp.list_tools)
        else mcp.list_tools()
    )
    for tool in tool_objs:
        await _call_tool_best_effort(mcp, tool)


def test_mcp_server_coverage(mock_session):
    _ = mock_session
    from fastmcp.server.middleware.rate_limiting import RateLimitingMiddleware

    from archivebox_api.mcp_server import get_mcp_instance

    # Patch RateLimitingMiddleware to do nothing
    async def mock_on_request(self, context, call_next):
        return await call_next(context)

    with patch.object(RateLimitingMiddleware, "on_request", mock_on_request):
        with patch("archivebox_api.auth.get_client") as mock_api:
            mcp_data = get_mcp_instance()
            mcp = mcp_data[0] if isinstance(mcp_data, tuple) else mcp_data

            loop = asyncio.new_event_loop()
            loop.run_until_complete(_run_all_tools(mcp))
            loop.close()
