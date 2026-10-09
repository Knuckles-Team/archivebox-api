"""Native blob ingestion of ArchiveBox web-capture bytes — Wire-First coverage.

Exercises ``ingest_snapshot_blob`` against a fake transport boundary (no engine
required), asserting the content-addressed media record, media-kind inference, and
the provenance properties carried on it. CONCEPT:AU-KG.ingest.list-durable-media.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from agent_connector_sdk.ingest import KnowledgeIngest

from archivebox_api.kg_ingest import ingest_snapshot_blob


class _FakeTransport:
    """A synchronous-looking fake, driven over its own event loop via submit_blocking."""

    def __init__(self) -> None:
        self.stored: list[bytes] = []
        self.requests: list[Any] = []

    async def source_status(self, connector: str, stream: str) -> Any:
        return SimpleNamespace(accepted_checkpoint=None)

    async def store_blob(self, data: bytes) -> str:
        self.stored.append(data)
        return f"digest-{len(self.stored)}"

    async def submit(self, request: Any) -> Any:
        self.requests.append(request)
        record = request.records[0]
        return SimpleNamespace(
            affected_count=len(request.records),
            relationship_count=len(request.relationships),
            raw_admissions=[
                SimpleNamespace(
                    record_id=record.record_id,
                    raw_digest="a" * 64,
                    stream=request.records[0].stream,
                    deduplicated=False,
                )
            ],
        )


def _service_with_loop():
    """A KnowledgeIngest bound to a running background loop, for submit_blocking."""
    import asyncio
    import threading

    loop = asyncio.new_event_loop()
    thread = threading.Thread(target=loop.run_forever, daemon=True)
    thread.start()
    transport = _FakeTransport()
    service = KnowledgeIngest(transport, loop=loop)
    return service, transport, loop


def test_ingest_snapshot_blob_stores_web_snapshot():
    service, transport, loop = _service_with_loop()
    try:
        snap = {
            "abid": "snap1",
            "url": "https://example.com/a",
            "title": "Example A",
            "timestamp": "1700000000.1",
        }
        res = ingest_snapshot_blob(
            b"<html>captured</html>",
            snapshot=snap,
            mime_type="text/html",
            extractor="singlefile",
            ingest=service,
        )
        assert res is not None
        assert res["asset_id"] is not None
        assert res["size_bytes"] == len(b"<html>captured</html>")
        assert res["media_type"] == "web_snapshot"
        assert transport.stored == [b"<html>captured</html>"]
        record = transport.requests[0].records[0]
        assert record.payload["source_url"] == "https://example.com/a"
        assert record.payload["extractor"] == "singlefile"
        assert record.payload["abid"] == "snap1"
    finally:
        loop.call_soon_threadsafe(loop.stop)


def test_ingest_snapshot_blob_infers_image_and_pdf():
    service, transport, loop = _service_with_loop()
    try:
        res_image = ingest_snapshot_blob(b"\x89PNG", mime_type="image/png", ingest=service)
        res_pdf = ingest_snapshot_blob(
            b"%PDF-1.4", mime_type="application/pdf", ingest=service
        )
        assert res_image["media_type"] == "image"
        assert res_pdf["media_type"] == "document"
    finally:
        loop.call_soon_threadsafe(loop.stop)


def test_ingest_snapshot_blob_noops_without_bytes_or_engine():
    service, _, loop = _service_with_loop()
    try:
        assert ingest_snapshot_blob(b"", ingest=service) is None
    finally:
        loop.call_soon_threadsafe(loop.stop)
    # No injected service + no reachable engine -> clean no-op.
    assert ingest_snapshot_blob(b"data", snapshot={"url": "x"}) is None
