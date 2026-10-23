"""Capabilities through the SDK (CONN-ARCHIVEBOX-API-SDK-CENTRALIZATION-R001)."""

from __future__ import annotations

import dataclasses
import pathlib
import re
from unittest.mock import MagicMock

import httpx
import pytest

from archivebox_api.web_source import ArchiveSession, WebSourceRefused

ID = "CONN-ARCHIVEBOX-API-SDK-CENTRALIZATION-R001"
ROOT = pathlib.Path(__file__).resolve().parents[1]


@pytest.mark.spec(f"{ID}.1")
def test_package_uses_the_governed_client() -> None:
    sources = {p: p.read_text() for p in (ROOT / "archivebox_api").rglob("*.py")}
    assert not [
        p
        for p, s in sources.items()
        if re.search(r"^\s*(import|from) requests\b", s, re.M)
    ]
    base = (ROOT / "archivebox_api/api/api_client_base.py").read_text()
    assert "create_http_client(" in base
    assert "create_http_client(" in (ROOT / "archivebox_api/web_source.py").read_text()
    assert (
        "create_http_client("
        in (ROOT / "archivebox_api/web_source_contract.py").read_text()
    )


@pytest.mark.spec(f"{ID}.2")
def test_archive_session_takes_trust_from_the_profile() -> None:
    assert "verify" not in {f.name for f in dataclasses.fields(ArchiveSession)}
    session = ArchiveSession("https://archive.example", "u", "p")
    assert isinstance(session.session, httpx.Client)
    session.session.close()


def _session(responses: list[httpx.Response]) -> ArchiveSession:
    client = MagicMock()
    client.get.side_effect = responses
    session = ArchiveSession("https://archive.example", "u", "p", session=client)
    session._logged_in = True
    session.login = MagicMock()  # type: ignore[method-assign]
    return session


def _login_redirect() -> httpx.Response:
    return httpx.Response(302, headers={"location": "/admin/login/?next=/x"})


@pytest.mark.spec(f"{ID}.3")
def test_expired_session_refreshes_once() -> None:
    ok = httpx.Response(200, headers={"content-type": "text/plain"}, content=b"hi")
    session = _session([_login_redirect(), ok])
    assert session.get_file("/x") == ("text/plain", b"hi")
    assert session.login.call_count == 1  # type: ignore[attr-defined]
    stuck = _session([_login_redirect(), _login_redirect()])
    with pytest.raises(WebSourceRefused) as refused:
        stuck.get_file("/x")
    assert refused.value.reason == "upstream_failed"


@pytest.mark.spec(f"{ID}.4")
def test_dependencies_come_from_the_sdk() -> None:
    text = (ROOT / "pyproject.toml").read_text()
    assert "requests" not in text.split("[project.optional-dependencies]")[0]
    floor = re.search(r"agent-connector-sdk\[mcp\]>=(\d+)\.(\d+)\.(\d+)", text)
    assert floor and tuple(map(int, floor.groups())) >= (0, 3, 11)
