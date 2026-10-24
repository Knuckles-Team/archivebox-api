"""archivebox-api passes the SDK web-source conformance kit (CONN-ARCHIVEBOX-API-WEB-SOURCE-R001.1)."""

from __future__ import annotations

import importlib
import json
import re
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

import pytest
from agent_connector_sdk.testing.web_source_conformance import (
    check_web_source,
    fastmcp_caller,
    fixture_site,
    served_tool_schemas,
)
from fastmcp import Client

from archivebox_api.web_source import ArchiveSession, ArchiveWebSource
from archivebox_api.web_source_contract import ArchiveboxSource
from agent_connector_sdk.connector import build_server

INTERVAL = 0.3


class _Archive(BaseHTTPRequestHandler):
    """A logged-in-only archive file server, as ArchiveBox serves snapshots."""

    files: dict[str, tuple[str, bytes]] = {}

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/admin/login/":
            body = b'<input name="csrfmiddlewaretoken" value="tok">'
            self.send_response(200)
            self.send_header("Set-Cookie", "csrftoken=tok; Path=/")
            self.end_headers()
            self.wfile.write(body)
            return
        if "sessionid=ok" not in (self.headers.get("Cookie") or ""):
            self.send_response(302)
            self.send_header("Location", "/admin/login/")
            self.end_headers()
            return
        found = self.files.get(self.path)
        if found is None:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", found[0])
        self.send_header("Content-Length", str(len(found[1])))
        self.end_headers()
        self.wfile.write(found[1])

    def do_POST(self) -> None:  # noqa: N802
        self.rfile.read(int(self.headers.get("Content-Length") or 0))
        self.send_response(302)
        self.send_header("Location", "/")
        self.send_header("Set-Cookie", "sessionid=ok; Path=/")
        self.end_headers()

    def log_message(self, *args: object) -> None:
        return


class ArchivingApi:
    """An ArchiveBox REST fake that archives each added URL by fetching it."""

    def __init__(self) -> None:
        self.snapshots: dict[str, dict[str, Any]] = {}

    def get_snapshots(self, *, url: str, limit: int) -> dict[str, Any]:
        found = self.snapshots.get(url)
        return {"items": [found] if found else []}

    def get_snapshot(
        self, snapshot_id: str, with_archiveresults: bool
    ) -> dict[str, Any]:
        return next(s for s in self.snapshots.values() if s["id"] == snapshot_id)

    def cli_add(self, *, urls: list[str], tag: str, extractors: str) -> dict[str, Any]:
        for url in urls:
            snapshot_id = f"{len(self.snapshots) + 1:032x}"
            base = f"/snapshot/{snapshot_id}/"
            try:
                with urllib.request.urlopen(url, timeout=10) as response:  # noqa: S310
                    ctype = response.headers.get("content-type", "")
                    body = response.read()
            except urllib.error.HTTPError as error:
                ctype, body = "text/plain", error.read()
            paragraphs = re.findall(rb"<p>(.*?)</p>", body, re.S)
            text = b"\n\n".join(re.sub(rb"<[^>]+>", b"", p) for p in paragraphs)
            _Archive.files.update(
                {
                    base + "headers.json": (
                        "application/json",
                        json.dumps({"Content-Type": ctype}).encode(),
                    ),
                    base + "singlefile.html": ("text/html", body),
                    base + "readability/content.txt": ("text/plain", text),
                    base + "readability/content.html": (
                        "text/html",
                        b"".join(paragraphs),
                    ),
                    base + "readability/article.json": (
                        "application/json",
                        json.dumps(
                            {"title": "Disruption budgets", "byline": "Fixture Author"}
                        ).encode(),
                    ),
                }
            )
            self.snapshots[url] = {
                "id": snapshot_id,
                "url": url,
                "title": "Disruption budgets",
                "status": "sealed",
                "downloaded_at": "2026-10-18T00:00:00+00:00",
            }
        return {"success": True}


@pytest.fixture
def archive() -> Any:
    _Archive.files = {}
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Archive)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()


@pytest.mark.spec("CONN-ARCHIVEBOX-API-WEB-SOURCE-R001.1")
@pytest.mark.spec("CONN-ARCHIVEBOX-API-WEB-SOURCE-R001.8")
async def test_archivebox_conforms_to_the_web_source_contract(
    archive: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    server_module = importlib.import_module("archivebox_api.mcp_server")
    source = ArchiveboxSource(
        ArchiveWebSource(
            api=ArchivingApi(), session=ArchiveSession(archive, "admin", "secret")
        ),
        min_interval_s=INTERVAL,
    )
    monkeypatch.setattr(server_module, "_CONTRACT_SOURCE", source)
    monkeypatch.setattr("sys.argv", ["archivebox-mcp"])
    _, mcp = build_server("archivebox_api", command_args=[])
    with fixture_site() as site:
        async with Client(mcp) as client:
            report = await check_web_source(
                fastmcp_caller(client),
                site,
                backend="archivebox",
                served_tools=await served_tool_schemas(client),
                min_interval_s=INTERVAL,
            )
    assert report.ok, report.results
