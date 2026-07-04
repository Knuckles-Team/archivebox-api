"""Native blob ingestion of ArchiveBox web-capture bytes — Wire-First coverage.

Exercises ``ingest_snapshot_blob`` with a fake :class:`MediaStore` (no engine required),
asserting the store_media call, media-type inference, and the provenance ``extra`` map.
CONCEPT:AU-KG.ingest.list-durable-media.
"""

from __future__ import annotations

from archivebox_api.kg_ingest import ingest_snapshot_blob


class _Stored:
    def __init__(self, asset_id, digest):
        self.asset_id = asset_id
        self.digest = digest


class _FakeMediaStore:
    def __init__(self):
        self.calls = []

    def store_media(self, data, *, media_type, mime_type, source, name, extra):
        self.calls.append(
            {
                "size": len(data),
                "media_type": media_type,
                "mime_type": mime_type,
                "source": source,
                "name": name,
                "extra": extra,
            }
        )
        return _Stored(asset_id="archivebox:asset:1", digest="deadbeef" * 8)


def test_ingest_snapshot_blob_stores_web_snapshot():
    store = _FakeMediaStore()
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
        media_store=store,
    )
    assert res is not None
    assert res["asset_id"] == "archivebox:asset:1"
    assert res["size_bytes"] == len(b"<html>captured</html>")
    call = store.calls[0]
    assert call["media_type"] == "web_snapshot"
    assert call["source"] == "archivebox-api"
    assert call["name"] == "Example A"
    assert call["extra"]["source_url"] == "https://example.com/a"
    assert call["extra"]["extractor"] == "singlefile"
    assert call["extra"]["abid"] == "snap1"


def test_ingest_snapshot_blob_infers_image_and_pdf():
    store = _FakeMediaStore()
    ingest_snapshot_blob(b"\x89PNG", mime_type="image/png", media_store=store)
    ingest_snapshot_blob(b"%PDF-1.4", mime_type="application/pdf", media_store=store)
    assert store.calls[0]["media_type"] == "image"
    assert store.calls[1]["media_type"] == "document"


def test_ingest_snapshot_blob_noops_without_bytes_or_store():
    assert ingest_snapshot_blob(b"", media_store=_FakeMediaStore()) is None
    # No injected store + no reachable engine -> clean no-op.
    assert ingest_snapshot_blob(b"data", snapshot={"url": "x"}) is None
