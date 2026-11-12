import sys
from typing import Callable, cast
from unittest.mock import MagicMock, patch

import pytest
import httpx
from scion_sdk.exceptions import (
    AuthError,
    MissingParameterError,
    ParameterError,
)
from pydantic import ValidationError

# Core imports to test
from archivebox_api.api_client import Api

# =====================================================================
# 1. Tests for archivebox_api/__init__.py
# =====================================================================


@pytest.mark.concept("AU-ECO.messaging.native-backend-abstraction")
def test_init_import_module_safely():
    from archivebox_api import _import_module_safely

    # Verify non-existent module returns None (ImportError handled)
    res = _import_module_safely("nonexistent_module_xyz")
    assert res is None


# =====================================================================
# 2. Tests for archivebox_api/auth.py
# =====================================================================


@pytest.mark.concept("AU-OS.config.secrets-authentication")
def test_auth_get_client_errors(temp_env):
    from archivebox_api.auth import get_client

    # 1. Unset ARCHIVEBOX_BASE_URL should raise RuntimeError
    temp_env.clear()
    with pytest.raises(RuntimeError) as exc:
        get_client()
    assert "ARCHIVEBOX_BASE_URL not set" in str(exc.value)


@pytest.mark.concept("AU-OS.config.secrets-authentication")
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
        }
    )
    with patch("archivebox_api.auth.resolve_tls_profile") as resolve_profile:
        get_client()
        mock_api_class.assert_called_with(
            url="http://localhost:8000",
            token="some-token",
            username="some-username",
            password="some-password",
            api_key="some-token",
            tls_profile=resolve_profile.return_value,
        )


# =====================================================================
# 3. Tests for archivebox_api/api/api_client_base.py
# =====================================================================


@pytest.mark.concept("AU-OS.config.secrets-authentication")
def test_base_api_missing_url():
    with pytest.raises(MissingParameterError):
        Api(url=None)


@pytest.mark.concept("AU-OS.governance.wasm-micro-agent-sandbox")
def test_base_api_applies_tls_profile():
    profile = MagicMock()

    with patch("archivebox_api.api.api_client_base.build_http_client") as create:
        client = Api(url="http://test.com", tls_profile=profile)

    create.assert_called_once()
    assert create.call_args.args[0].tls is profile
    assert client._session is create.return_value


@pytest.mark.concept("AU-OS.config.secrets-authentication")
@patch("httpx.Client.get")
@patch("httpx.Client.post")
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


# CONCEPT:AU-OS.config.secrets-authentication — Security & Auth
# CONCEPT:AU-OS.governance.wasm-micro-agent-sandbox — Telemetry & Observability
@pytest.mark.concept("AU-OS.config.secrets-authentication")
@patch("httpx.Client.get")
def test_base_api_no_eager_probe(mock_get):
    # The constructor must NOT issue any network request: it only configures auth
    # headers. An eager probe made construction raise before any tool ran, which
    # FastMCP surfaced as "Failed to resolve dependency 'client'".
    Api(url="http://test.com", token="token")
    assert not mock_get.called


@pytest.mark.concept("AU-OS.config.secrets-authentication")
@patch("httpx.Client.get")
def test_base_api_api_key_header(mock_get):
    # An api_key (with no token) sets the X-ArchiveBox-API-Key header and still
    # performs no network I/O at construction time.
    api = Api(url="http://test.com", api_key="my-key")
    assert api.headers["X-ArchiveBox-API-Key"] == "my-key"
    assert not mock_get.called


@pytest.mark.concept("AU-OS.config.secrets-authentication")
def test_base_api_client_not_implemented_stub():
    from archivebox_api.api.api_client_base import BaseApiClient

    class DummyClient(BaseApiClient):
        def get_api_token(
            self, username: str | None = None, password: str | None = None
        ) -> httpx.Response:
            raise NotImplementedError()

    # Patch httpx.Client.get inside constructor so initialization probe succeeds
    with patch("httpx.Client.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_get.return_value = mock_resp
        client = DummyClient(url="http://test.com", token="my-token")
        with pytest.raises(NotImplementedError):
            client.get_api_token()


# =====================================================================
# 4. Tests for ValidationError Catching in Clients
# =====================================================================
