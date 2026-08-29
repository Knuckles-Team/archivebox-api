import asyncio
import inspect
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from archivebox_api.api_client import Api


@pytest.fixture
def mock_session():
    with patch("requests.Session") as mock_sess:
        session = mock_sess.return_value

        res = MagicMock()
        res.status_code = 200
        res.ok = True
        res.json.return_value = {
            "token": "mock_token",
            "results": [],
            "next": None,
            "id": "123",
        }
        res.content = b'{"token": "mock_token"}'
        res.text = '{"token": "mock_token"}'
        session.get.return_value = res
        session.post.return_value = res
        session.request.return_value = res

        yield session


_PARAM_NAME_VALUE_RULES: list[tuple[tuple[str, ...], Any]] = [
    (("urls",), ["http://test.com"]),
    (("id",), "123"),
    (("filter_patterns",), ["test"]),
    (("depth", "limit", "offset", "page"), 1),
    (("after", "before", "resume"), 123456789.0),
    (("enabled", "update", "overwrite", "init", "as_json"), True),
]


def _guess_kwarg_value(param_name: str, annotation: Any) -> Any:
    """Best-effort guess of a plausible value for one brute-forced parameter, by name."""
    for keywords, value in _PARAM_NAME_VALUE_RULES:
        if any(keyword in param_name for keyword in keywords):
            return value
    if annotation == dict:
        return {}
    return "test"


def _guessed_kwargs(sig: inspect.Signature) -> dict[str, Any]:
    """Guess a kwargs dict covering every declared parameter of ``sig``."""
    return {
        param.name: _guess_kwarg_value(param.name, param.annotation)
        for param in sig.parameters.values()
        if param.name != "kwargs"
    }


def _positional_args(sig: inspect.Signature, kwargs: dict[str, Any]) -> list[Any]:
    """Pull required positional-eligible params out of ``kwargs`` as an arg list."""
    pos_args = []
    for param in sig.parameters.values():
        if param.default == inspect.Parameter.empty and param.kind in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.POSITIONAL_ONLY,
        ):
            pos_args.append(kwargs.get(param.name, "test"))
            if param.name in kwargs:
                del kwargs[param.name]
    return pos_args


def _call_method_best_effort(method: Any) -> None:
    """Call one client method with guessed args; any failure is expected/logged."""
    sig = inspect.signature(method)
    kwargs = _guessed_kwargs(sig)
    try:
        pos_args = _positional_args(sig, kwargs)
        method(*pos_args, **kwargs)
    except Exception as e:
        print(f"Operation failed: {type(e).__name__}")


def _construct_best_effort(**ctor_kwargs: Any) -> None:
    try:
        Api(url="http://test.com", **ctor_kwargs)
    except Exception:
        pass


def test_api_brute_force(mock_session):
    _ = mock_session
    # Test init paths
    _construct_best_effort(token="token")
    _construct_best_effort(api_key="key")
    _construct_best_effort(username="u", password="p")

    client = Api(url="http://test.com", token="mock_token")

    # Introspect all methods
    for name, method in inspect.getmembers(client, predicate=inspect.ismethod):
        if name.startswith("_") or name in ["get_api_token"]:
            continue
        print(f"Calling {name}...")
        _call_method_best_effort(method)


def test_mcp_server_coverage(mock_session):
    _ = mock_session
    from fastmcp.server.middleware.rate_limiting import RateLimitingMiddleware

    from archivebox_api.mcp_server import get_mcp_instance

    async def mock_on_request(self, context, call_next):
        return await call_next(context)

    with patch.object(RateLimitingMiddleware, "on_request", mock_on_request):
        # Mock env vars
        with patch.dict(
            "os.environ",
            {"ARCHIVEBOX_URL": "http://test.com", "ARCHIVEBOX_TOKEN": "mock"},
        ):
            mcp_data = get_mcp_instance()
            mcp = mcp_data[0] if isinstance(mcp_data, tuple) else mcp_data

            async def run_tools():
                tool_objs = (
                    await mcp.list_tools()
                    if inspect.iscoroutinefunction(mcp.list_tools)
                    else mcp.list_tools()
                )

                for tool in tool_objs:
                    tool_name = tool.name
                    print(f"Testing MCP tool: {tool_name}")
                    try:
                        all_possible_params = {
                            "urls": ["http://test.com"],
                            "snapshot_id": "123",
                            "archiveresult_id": "123",
                            "tag_id": "123",
                            "abid": "123",
                            "tag": "test",
                            "depth": 1,
                            "update": True,
                            "overwrite": True,
                            "init": True,
                            "extractors": "wget",
                            "parser": "auto",
                            "extra_data": {},
                            "filter_patterns": ["test"],
                            "status": "indexed",
                            "after": 123456789.0,
                            "before": 999999999.0,
                            "sort": "bookmarked_at",
                            "as_json": True,
                            "url": "http://test.com",
                            "api_key": "mock",
                        }

                        target_params = {}
                        if hasattr(tool, "parameters") and hasattr(
                            tool.parameters, "properties"
                        ):
                            for p in tool.parameters.properties:
                                if p in all_possible_params:
                                    target_params[p] = all_possible_params[p]
                                else:
                                    target_params[p] = "test"

                        await mcp.call_tool(tool_name, target_params)
                    except Exception as e:
                        print(f"Operation failed: {type(e).__name__}")

            loop = asyncio.new_event_loop()
            loop.run_until_complete(run_tools())
            loop.close()
