"""ArchiveBox as the secondary web-source backend (CONN-ARCHIVEBOX-API-WEB-SOURCE-R001)."""

from __future__ import annotations

import hashlib
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

import pytest

from archivebox_api.web_source import (
    REFUSAL_REASONS,
    ArchiveSession,
    ArchiveWebSource,
    WebSourceRefused,
)

SNAPSHOT = "0b5c9f6e-1d2a-4c3b-9e8f-7a6b5c4d3e2f"
TEXT = "A pod disruption budget limits voluntary evictions.\n" * 20
ARTICLE = {
    "title": "PDB explained",
    "byline": "Ada",
    "publishedTime": "2026-09-01",
    "siteName": "Docs",
}


class _Archive(BaseHTTPRequestHandler):
    files: dict[str, tuple[str, bytes]] = {}
    logins = 0

    def _authed(self) -> bool:
        return "sessionid=ok" in (self.headers.get("Cookie") or "")

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/admin/login/":
            body = b'<form><input name="csrfmiddlewaretoken" value="tok"></form>'
            self.send_response(200)
            self.send_header("Set-Cookie", "csrftoken=tok; Path=/")
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(body)
            return
        if not self._authed():
            self.send_response(302)
            self.send_header("Location", "/admin/login/?next=" + self.path)
            self.end_headers()
            return
        found = self.files.get(self.path)
        if found is None:
            self.send_response(404)
            self.end_headers()
            return
        ctype, body = found
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length") or 0)
        form = self.rfile.read(length).decode()
        type(self).logins += 1
        if "password=secret" in form and "csrfmiddlewaretoken=tok" in form:
            self.send_response(302)
            self.send_header("Location", "/")
            self.send_header("Set-Cookie", "sessionid=ok; Path=/")
        else:
            self.send_response(302)
            self.send_header("Location", "/admin/login/")
        self.end_headers()

    def log_message(self, *args: object) -> None:
        return


@pytest.fixture
def archive() -> Any:
    base = f"/snapshot/{SNAPSHOT.replace('-', '')}/"
    _Archive.files = {
        base + "readability/content.txt": ("text/plain; charset=utf-8", TEXT.encode()),
        base + "readability/article.json": ("text/plain", json.dumps(ARTICLE).encode()),
        base + "htmltotext.txt": ("text/plain", b"plain text fallback"),
    }
    _Archive.logins = 0
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Archive)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}", base
    server.shutdown()


class FakeApi:
    """The ArchiveBox REST surface the web source uses."""

    def __init__(
        self, *, statuses: list[str] | None = None, existing: bool = False
    ) -> None:
        self.snapshots: dict[str, dict[str, Any]] = {}
        self.adds: list[list[str]] = []
        self.statuses = statuses or ["sealed"]
        if existing:
            self._store("https://a.example/pdb")

    def _store(self, url: str) -> None:
        self.snapshots[url] = {
            "id": SNAPSHOT,
            "url": url,
            "title": "Fallback",
            "status": "queued",
        }

    def get_snapshots(self, *, url: str, limit: int) -> dict[str, Any]:
        found = self.snapshots.get(url)
        return {"items": [found] if found else []}

    def cli_add(self, *, urls: list[str], tag: str, extractors: str) -> dict[str, Any]:
        self.adds.append(urls)
        for url in urls:
            self._store(url)
        return {"success": True}

    def get_snapshot(
        self, snapshot_id: str, with_archiveresults: bool
    ) -> dict[str, Any]:
        status = self.statuses.pop(0) if len(self.statuses) > 1 else self.statuses[0]
        snap = next(iter(self.snapshots.values()))
        return dict(snap, status=status, downloaded_at="2026-10-18T00:00:00Z")


def _source(
    base_url: str, api: FakeApi, *, password: str = "secret", timeout_s: float = 10.0
) -> ArchiveWebSource:
    now = [0.0]

    def sleep(seconds: float) -> None:
        now[0] += seconds

    return ArchiveWebSource(
        api=api,
        session=ArchiveSession(base_url, "admin", password),
        timeout_s=timeout_s,
        sleep=sleep,
        clock=lambda: now[0],
    )


@pytest.mark.spec("CONN-ARCHIVEBOX-API-WEB-SOURCE-R001.2")
def test_add_reuses_existing_snapshot(archive: Any) -> None:
    api = FakeApi()
    source = _source(archive[0], api)
    first = source.fetch("https://a.example/pdb")
    second = source.fetch("https://a.example/pdb")
    assert api.adds == [["https://a.example/pdb"]]
    assert first["snapshot_id"] == second["snapshot_id"] == SNAPSHOT
    assert first["added"] is True and second["added"] is False
    assert len(api.snapshots) == 1


@pytest.mark.spec("CONN-ARCHIVEBOX-API-WEB-SOURCE-R001.3")
def test_status_poll_and_timeout(archive: Any) -> None:
    done = _source(archive[0], FakeApi(statuses=["queued", "started", "sealed"]))
    assert done.extract("https://a.example/pdb")["snapshot_id"] == SNAPSHOT
    stalled = _source(archive[0], FakeApi(statuses=["started"]), timeout_s=5.0)
    with pytest.raises(WebSourceRefused) as refused:
        stalled.extract("https://a.example/pdb")
    assert refused.value.reason == "upstream_failed"


@pytest.mark.spec("CONN-ARCHIVEBOX-API-WEB-SOURCE-R001.4")
def test_extract_reads_archive_results(archive: Any) -> None:
    result = _source(archive[0], FakeApi()).extract("https://a.example/pdb")
    assert result["text"] == TEXT.strip()
    assert result["extractor"] == "readability"
    assert result["title"] == "PDB explained"
    assert result["author"] == "Ada"
    assert result["published_at"] == "2026-09-01"
    assert result["content_digest"] == hashlib.sha256(TEXT.strip().encode()).hexdigest()
    # Without the main-content output the plain-text output is read.
    del _Archive.files[archive[1] + "readability/content.txt"]
    plain = _source(archive[0], FakeApi()).extract("https://a.example/pdb")
    assert plain["extractor"] == "htmltotext" and plain["text"] == "plain text fallback"


@pytest.mark.spec("CONN-ARCHIVEBOX-API-WEB-SOURCE-R001.5")
def test_refusals_and_provenance(archive: Any) -> None:
    result = _source(archive[0], FakeApi()).extract("https://a.example/pdb")
    assert result["backend"] == "archivebox"
    assert result["snapshot_id"] == SNAPSHOT
    assert result["retrieved_at"].endswith("+00:00")
    assert len(result["content_digest"]) == 64
    for name in ("readability/content.txt", "htmltotext.txt"):
        del _Archive.files[archive[1] + name]
    with pytest.raises(WebSourceRefused) as empty:
        _source(archive[0], FakeApi()).extract("https://a.example/pdb")
    assert empty.value.reason == "extract_empty"
    with pytest.raises(WebSourceRefused) as login:
        _source(archive[0], FakeApi(), password="wrong").extract(
            "https://a.example/pdb"
        )
    assert login.value.reason == "upstream_failed"
    assert {empty.value.reason, login.value.reason} <= REFUSAL_REASONS
    with pytest.raises(ValueError):
        WebSourceRefused("not_a_reason", "u")


@pytest.mark.spec("CONN-ARCHIVEBOX-API-WEB-SOURCE-R001.4")
def test_session_logs_in_again_after_expiry(archive: Any) -> None:
    session = ArchiveSession(archive[0], "admin", "secret")
    assert session.get_text(archive[1] + "htmltotext.txt") == "plain text fallback"
    session.session.cookies.clear()
    session.session.cookies.set("sessionid", "expired")
    assert session.get_text(archive[1] + "htmltotext.txt") == "plain text fallback"
    assert _Archive.logins == 2


@pytest.mark.spec("CONN-ARCHIVEBOX-API-WEB-SOURCE-R001.7")
async def test_served_manifest_maps_document_and_chunk(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """SourceIngest resolves manifest:<connector>#schema_mappings/Document and /Chunk."""
    import importlib

    from fastmcp import Client

    monkeypatch.setattr("sys.argv", ["archivebox-mcp"])
    server_module = importlib.import_module("archivebox_api.mcp_server")
    mcp, *_ = server_module.get_mcp_instance()
    async with Client(mcp) as client:
        uris = {str(r.uri) for r in await client.list_resources()}
        body = await client.read_resource("manifest://connector")
    assert "manifest://connector" in uris
    text = body[0].text if hasattr(body[0], "text") else str(body[0])
    manifest = (
        json.loads(text)
        if text.lstrip().startswith("{")
        else __import__("yaml").safe_load(text)
    )
    for record_type in ("Document", "Chunk"):
        assert manifest["schema_mappings"][record_type]["ontology_class"] == record_type
