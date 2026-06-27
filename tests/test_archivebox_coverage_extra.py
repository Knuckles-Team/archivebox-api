import os
import sys
import importlib
import warnings
from typing import cast, Callable
from unittest.mock import MagicMock, patch

import pytest
import requests
from pydantic import ValidationError
from agent_utilities.core.exceptions import (
    AuthError,
    MissingParameterError,
    ParameterError,
)

# Core imports to test
import archivebox_api
from archivebox_api.api_client import Api

# =====================================================================
# 1. Tests for archivebox_api/__init__.py
# =====================================================================


@pytest.mark.concept("ECO-4.0")
def test_init_import_module_safely():
    from archivebox_api import _import_module_safely

    # Verify non-existent module returns None (ImportError handled)
    res = _import_module_safely("nonexistent_module_xyz")
    assert res is None


@pytest.mark.concept("ECO-4.0")
def test_init_getattr():
    # 1. Test _MCP_AVAILABLE and _AGENT_AVAILABLE
    assert hasattr(archivebox_api, "_MCP_AVAILABLE")
    assert hasattr(archivebox_api, "_AGENT_AVAILABLE")

    # 2. Test missing/fake optional modules
    with patch.dict(archivebox_api.OPTIONAL_MODULES, {"nonexistent_server": "fake"}):
        val = getattr(archivebox_api, "_MCP_AVAILABLE")
        assert isinstance(val, bool)

    # 3. Test empty/missing optional modules to hit line 52/57 of __init__.py
    with patch.dict(archivebox_api.OPTIONAL_MODULES, {}, clear=True):
        assert archivebox_api._MCP_AVAILABLE is False
        assert archivebox_api._AGENT_AVAILABLE is False

    # 4. Test retrieving existent attributes dynamically
    mcp_instance = getattr(archivebox_api, "get_mcp_instance")
    assert mcp_instance is not None

    # 5. Test nonexistent attribute raises AttributeError
    with pytest.raises(AttributeError):
        _ = archivebox_api.nonexistent_attribute_abc


@pytest.mark.concept("ECO-4.0")
def test_init_lazy_expose_members():
    # Remove attributes from module globals if already exposed to force __getattr__ invocation
    for name in [
        "get_mcp_instance",
        "mcp_server",
        "get_agent_instance",
        "agent_server",
    ]:
        if name in archivebox_api.__dict__:
            del archivebox_api.__dict__[name]
    # Clear mcp_server from loaded optional modules to force dynamic lookup
    if "archivebox_api.mcp_server" in archivebox_api._loaded_optional_modules:
        del archivebox_api._loaded_optional_modules["archivebox_api.mcp_server"]
    # Trigger hasattr and getattr via __getattr__ exposing dynamic members (covers line 69)
    assert archivebox_api.get_mcp_instance is not None


@pytest.mark.concept("ECO-4.0")
def test_init_dir():
    dir_list = dir(archivebox_api)
    assert "Api" in dir_list
    assert "get_mcp_instance" in dir_list


# =====================================================================
# 2. Tests for archivebox_api/auth.py
# =====================================================================


@pytest.mark.concept("OS-5.1")
def test_auth_get_client_errors(temp_env):
    from archivebox_api.auth import get_client

    # 1. Unset ARCHIVEBOX_BASE_URL should raise RuntimeError
    temp_env.clear()
    with pytest.raises(RuntimeError) as exc:
        get_client()
    assert "ARCHIVEBOX_BASE_URL not set" in str(exc.value)


@pytest.mark.concept("OS-5.1")
@patch("archivebox_api.auth.Api")
def test_auth_get_client_combinations(mock_api_class, temp_env):
    from archivebox_api.auth import get_client

    # 2. Test get_client with different credentials in env vars
    temp_env.update(
        {
            "ARCHIVEBOX_URL": "http://localhost:8000",
            "ARCHIVEBOX_BASE_URL": "http://localhost:8000",
            "ARCHIVEBOX_TOKEN": "some-token",
            "ARCHIVEBOX_USERNAME": "some-username",
            "ARCHIVEBOX_PASSWORD": "some-password",
            "ARCHIVEBOX_API_KEY": "some-api-key",
            "ARCHIVEBOX_SSL_VERIFY": "True",
        }
    )
    client = get_client()
    mock_api_class.assert_called_with(
        url="http://localhost:8000",
        token="some-token",
        username="some-username",
        password="some-password",
        api_key="some-token",
        verify=True,
    )


# =====================================================================
# 3. Tests for archivebox_api/api/api_client_base.py
# =====================================================================


@pytest.mark.concept("OS-5.1")
def test_base_api_missing_url():
    with pytest.raises(MissingParameterError):
        Api(url=None)


@pytest.mark.concept("OS-5.4")
@patch("requests.Session.get")
def test_base_api_ssl_verify_false(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    # Verify False triggers warnings disable
    with patch("urllib3.disable_warnings") as mock_disable:
        Api(url="http://test.com", verify=False)
        assert mock_disable.called


@pytest.mark.concept("OS-5.1")
@patch("requests.Session.get")
@patch("requests.Session.post")
def test_base_api_username_password_auth_failures(mock_post, mock_get):
    # 1. Success return but no token key
    mock_token_resp = MagicMock()
    mock_token_resp.status_code = 200
    mock_token_resp.json.return_value = {}  # missing "token"
    mock_post.return_value = mock_token_resp

    mock_probe_resp = MagicMock()
    mock_probe_resp.status_code = 200
    mock_get.return_value = mock_probe_resp

    with pytest.raises(AuthError) as exc:
        Api(url="http://test.com", username="u", password="p")
    assert "Failed to retrieve API token" in str(exc.value)

    # 2. Authentication non-200 error
    mock_token_resp.status_code = 400
    mock_token_resp.content = b"Bad Auth"
    mock_post.return_value = mock_token_resp

    with pytest.raises(AuthError):
        Api(url="http://test.com", username="u", password="p")


# CONCEPT:OS-5.1 — Security & Auth
# CONCEPT:OS-5.4 — Telemetry & Observability
@pytest.mark.concept("OS-5.1")
@patch("requests.Session.get")
def test_base_api_no_eager_probe(mock_get):
    # The constructor must NOT issue any network request: it only configures auth
    # headers. An eager probe made construction raise before any tool ran, which
    # FastMCP surfaced as "Failed to resolve dependency 'client'".
    Api(url="http://test.com", token="token")
    assert not mock_get.called


@pytest.mark.concept("OS-5.1")
@patch("requests.Session.get")
def test_base_api_api_key_header(mock_get):
    # An api_key (with no token) sets the X-ArchiveBox-API-Key header and still
    # performs no network I/O at construction time.
    api = Api(url="http://test.com", api_key="my-key")
    assert api.headers["X-ArchiveBox-API-Key"] == "my-key"
    assert not mock_get.called


@pytest.mark.concept("OS-5.1")
def test_base_api_client_not_implemented_stub():
    from archivebox_api.api.api_client_base import BaseApiClient

    class DummyClient(BaseApiClient):
        def get_api_token(
            self, username: str | None = None, password: str | None = None
        ) -> requests.Response:
            raise NotImplementedError()

    # Patch requests.Session.get inside constructor so initialization probe succeeds
    with patch("requests.Session.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_get.return_value = mock_resp
        client = DummyClient(url="http://test.com", token="my-token")
        with pytest.raises(NotImplementedError):
            client.get_api_token()


# =====================================================================
# 4. Tests for ValidationError Catching in Clients
# =====================================================================


def _create_pydantic_validation_error():
    return ValidationError.from_exception_data(
        "DummyModel",
        [
            {
                "type": "value_error",
                "loc": ("dummy",),
                "input": None,
                "ctx": {"error": "dummy"},
            }
        ],
    )


@pytest.mark.concept("OS-5.4")
@patch("requests.Session.get")
@patch("requests.Session.post")
def test_client_validation_errors(mock_post, mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_get.return_value = mock_resp

    api = Api(url="http://test.com", token="token")

    # Inject ValidationError raising into session methods
    val_error = _create_pydantic_validation_error()
    mock_get.side_effect = val_error
    mock_post.side_effect = val_error

    # Test api_client_auth methods
    with pytest.raises(ParameterError):
        api.get_api_token(username="u")
    with pytest.raises(ParameterError):
        api.check_api_token(token="token")

    # Test api_client_core methods
    with pytest.raises(ParameterError):
        api.get_snapshots()
    with pytest.raises(ParameterError):
        api.get_snapshot(snapshot_id="123")
    with pytest.raises(ParameterError):
        api.get_archiveresults()
    with pytest.raises(ParameterError):
        api.get_archiveresult(archiveresult_id="123")
    with pytest.raises(ParameterError):
        api.get_tags()
    with pytest.raises(ParameterError):
        api.get_tag(tag_id="123")
    with pytest.raises(ParameterError):
        api.get_any(abid="123")

    # Test api_client_cli methods
    with pytest.raises(ParameterError):
        api.cli_add(urls=["http://example.com"])
    with pytest.raises(ParameterError):
        api.cli_update()
    with pytest.raises(ParameterError):
        api.cli_schedule()
    with pytest.raises(ParameterError):
        api.cli_list()
    with pytest.raises(ParameterError):
        api.cli_remove()


# =====================================================================
# 5. Tests for archivebox_api/mcp_server.py
# =====================================================================


@pytest.mark.concept("ECO-4.0")
@pytest.mark.asyncio
async def test_mcp_authentication_tool(mock_client, mock_context):
    from archivebox_api.mcp_server import register_authentication_tools
    from fastmcp import FastMCP

    mcp = FastMCP("test")
    register_authentication_tools(mcp)

    tool_obj = await mcp.get_tool("archivebox_authentication")
    assert tool_obj is not None
    tool = cast(Callable, getattr(tool_obj, "fn", tool_obj))

    # 1. Test progress reporting (ctx is not None)
    res = await tool(
        action="get_api_token",
        params_json='{"username": "u"}',
        client=mock_client,
        ctx=mock_context,
    )
    assert res == {"token": "mock-token-123"}
    mock_context.info.assert_called_with("Executing tool...")

    # 2. Test invalid JSON handling
    res = await tool(
        action="get_api_token",
        params_json="{invalid-json",
        client=mock_client,
        ctx=None,
    )
    assert "error" in res
    assert "Invalid params_json" in res["error"]

    # 3. Test check_api_token action
    res = await tool(
        action="check_api_token",
        params_json='{"token": "t"}',
        client=mock_client,
        ctx=None,
    )
    assert res == {"ok": True}

    # 4. Test unknown action raises ValueError
    with pytest.raises(ValueError) as exc:
        await tool(action="unknown", params_json="{}", client=mock_client, ctx=None)
    assert "Unknown action" in str(exc.value)


@pytest.mark.concept("ECO-4.0")
@pytest.mark.asyncio
async def test_mcp_core_tool(mock_client, mock_context):
    from archivebox_api.mcp_server import register_core_tools
    from fastmcp import FastMCP

    mcp = FastMCP("test")
    register_core_tools(mcp)

    tool_obj = await mcp.get_tool("archivebox_core")
    assert tool_obj is not None
    tool = cast(Callable, getattr(tool_obj, "fn", tool_obj))

    # 1. Test progress reporting (ctx is not None)
    res = await tool(
        action="get_snapshots", params_json="{}", client=mock_client, ctx=mock_context
    )
    assert res == {"snapshots": []}
    mock_context.info.assert_called_with("Executing tool...")

    # 2. Test invalid JSON handling
    res = await tool(
        action="get_snapshots", params_json="{invalid", client=mock_client, ctx=None
    )
    assert "error" in res
    assert "Invalid params_json" in res["error"]

    # 3. Test core actions mapping
    actions_mapping = {
        "get_snapshots": mock_client.get_snapshots,
        "get_snapshot": mock_client.get_snapshot,
        "get_archiveresults": mock_client.get_archiveresults,
        "get_tag": mock_client.get_tag,
        "get_any": mock_client.get_any,
    }

    for action, mock_func in actions_mapping.items():
        res = await tool(action=action, params_json="{}", client=mock_client, ctx=None)
        assert res == mock_func.return_value

    # Test unknown action
    with pytest.raises(ValueError):
        await tool(action="unknown", params_json="{}", client=mock_client, ctx=None)


@pytest.mark.concept("ECO-4.0")
@pytest.mark.asyncio
async def test_mcp_cli_tool(mock_client, mock_context):
    from archivebox_api.mcp_server import register_cli_tools
    from fastmcp import FastMCP

    mcp = FastMCP("test")
    register_cli_tools(mcp)

    tool_obj = await mcp.get_tool("archivebox_cli")
    assert tool_obj is not None
    tool = cast(Callable, getattr(tool_obj, "fn", tool_obj))

    # 1. Test progress reporting (ctx is not None)
    res = await tool(
        action="cli_list", params_json="{}", client=mock_client, ctx=mock_context
    )
    assert res == {"status": "listed"}
    mock_context.info.assert_called_with("Executing tool...")

    # 2. Test invalid JSON handling
    res = await tool(
        action="cli_list", params_json="{invalid", client=mock_client, ctx=None
    )
    assert "error" in res
    assert "Invalid params_json" in res["error"]

    # 3. Test cli actions mapping
    actions_mapping = {
        "cli_add": mock_client.cli_add,
        "cli_update": mock_client.cli_update,
        "cli_schedule": mock_client.cli_schedule,
        "cli_list": mock_client.cli_list,
        "cli_remove": mock_client.cli_remove,
    }

    for action, mock_func in actions_mapping.items():
        res = await tool(action=action, params_json="{}", client=mock_client, ctx=None)
        assert res == mock_func.return_value

    # Test unknown action
    with pytest.raises(ValueError):
        await tool(action="unknown", params_json="{}", client=mock_client, ctx=None)


@pytest.mark.concept("ECO-4.0")
@pytest.mark.asyncio
async def test_mcp_health_check():
    from archivebox_api.mcp_server import get_mcp_instance
    from starlette.requests import Request
    from starlette.datastructures import Headers

    mcp_data = get_mcp_instance()
    mcp = mcp_data[0] if isinstance(mcp_data, tuple) else mcp_data

    app = mcp.http_app()
    route_handler = None
    for route in app.routes:
        if route.path == "/health":
            route_handler = route.endpoint
            break

    assert route_handler is not None

    mock_scope = {
        "type": "http",
        "method": "GET",
        "path": "/health",
        "headers": Headers().raw,
    }
    mock_request = Request(scope=mock_scope)
    response = await route_handler(mock_request)
    assert response.status_code == 200
    assert b"ok" in response.body.lower()


@pytest.mark.concept("ECO-4.0")
@patch("archivebox_api.mcp_server.get_mcp_instance")
def test_mcp_server_run_options(mock_get_mcp):
    from archivebox_api.mcp_server import mcp_server

    mock_mcp = MagicMock()
    mock_args = MagicMock()
    mock_get_mcp.return_value = (mock_mcp, mock_args, [])

    # 1. Test stdio transport
    mock_args.transport = "stdio"
    mcp_server()
    mock_mcp.run.assert_called_with(transport="stdio")

    # 2. Test streamable-http transport
    mock_args.transport = "streamable-http"
    mock_args.host = "127.0.0.1"
    mock_args.port = 8000
    mcp_server()
    mock_mcp.run.assert_called_with(
        transport="streamable-http", host="127.0.0.1", port=8000
    )

    # 3. Test sse transport
    mock_args.transport = "sse"
    mcp_server()
    mock_mcp.run.assert_called_with(transport="sse", host="127.0.0.1", port=8000)

    # 4. Test invalid transport handles exit
    mock_args.transport = "invalid-transport"
    with pytest.raises(SystemExit) as sys_exit:
        mcp_server()
    assert sys_exit.value.code == 1


@pytest.mark.concept("OS-5.4")
def test_mcp_server_import_error_handling():
    import builtins

    original_import = builtins.__import__

    def mock_import(name, *args, **kwargs):
        if name == "requests.exceptions":
            raise ImportError("Simulated import error")
        return original_import(name, *args, **kwargs)

    mod = sys.modules.get("archivebox_api.mcp_server")
    with patch("builtins.__import__", side_effect=mock_import):
        if mod:
            importlib.reload(mod)


@pytest.mark.concept("ECO-4.0")
@patch("archivebox_api.mcp_server.get_mcp_instance")
def test_mcp_server_main_execution(mock_get_mcp):
    mock_args = MagicMock()
    mock_args.transport = "stdio"
    mock_args.host = "localhost"
    mock_args.port = 8000
    mock_args.auth_type = "none"

    mock_mcp = MagicMock()
    mock_mcp.custom_route.return_value = lambda x: x
    mock_get_mcp.return_value = (mock_mcp, mock_args, [])

    with (
        patch(
            "agent_utilities.mcp_utilities.create_mcp_server",
            return_value=(mock_args, mock_mcp, []),
        ),
        patch("sys.exit"),
    ):
        import runpy

        runpy.run_module("archivebox_api.mcp_server", run_name="__main__")
        mock_mcp.run.assert_called_with(transport="stdio")


# =====================================================================
# 6. Tests for archivebox_api/agent_server.py & __main__.py
# =====================================================================


@pytest.mark.concept("ECO-4.1")
@patch("agent_utilities.create_agent_server")
def test_agent_server_run(mock_create):
    from archivebox_api.agent_server import agent_server

    # Test running server with --debug enabled in args
    with patch("sys.argv", ["agent_server.py", "--debug"]):
        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            agent_server()

            assert mock_logger.setLevel.called
            assert mock_create.called


@pytest.mark.concept("ECO-4.1")
def test_agent_server_main_execution():
    import runpy

    with (
        patch("agent_utilities.initialize_workspace"),
        patch("agent_utilities.load_identity", return_value={"name": "test"}),
        patch(
            "agent_utilities.build_system_prompt_from_workspace", return_value="prompt"
        ),
        patch("agent_utilities.create_agent_server") as mock_server,
        patch("agent_utilities.create_agent_parser") as mock_parser,
        patch("sys.argv", ["agent_server.py"]),
    ):
        mock_args = MagicMock()
        mock_args.debug = False
        mock_args.mcp_url = None
        mock_args.mcp_config = None
        mock_args.host = "localhost"
        mock_args.port = 8000
        mock_args.provider = "openai"
        mock_args.model_id = "gpt-4"
        mock_args.base_url = None
        mock_args.api_key = "test"
        mock_args.custom_skills_directory = None
        mock_args.web = False
        mock_args.otel = False
        mock_args.otel_endpoint = None
        mock_args.otel_headers = None
        mock_args.otel_public_key = None
        mock_args.otel_secret_key = None
        mock_args.otel_protocol = "http/protobuf"
        mock_parser.return_value.parse_args.return_value = mock_args

        runpy.run_module("archivebox_api.agent_server", run_name="__main__")
        assert mock_server.called


@pytest.mark.concept("ECO-4.1")
def test_main_block_import():
    # Programmatic check of __main__.py import
    import runpy

    with patch("archivebox_api.agent_server.agent_server") as mock_agent_server:
        runpy.run_module("archivebox_api.__main__", run_name="__main__")
        mock_agent_server.assert_called_once()
