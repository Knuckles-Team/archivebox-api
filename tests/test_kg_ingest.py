"""Native epistemic-graph typed-node ingestion for archivebox-api — Wire-First coverage.

Exercises the real ``ingest_entities`` / ``ingest_documents`` / ``ingest_snapshots`` /
``ingest_archiveresults`` seam against a fake transport boundary (no engine required),
letting the SDK's own ``agent_connector_sdk.ingest`` request builder run on top of it so
the test still exercises the SDK's validation contract rather than re-deriving it.
CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from agent_connector_sdk.ingest import IngestError, KnowledgeIngest

from archivebox_api.kg_ingest import (
    ingest_archiveresults,
    ingest_documents,
    ingest_entities,
    ingest_snapshots,
    map_archiveresults,
    map_snapshots,
)


class _FakeTransport:
    def __init__(self) -> None:
        self.requests: list[Any] = []

    async def source_status(self, connector: str, stream: str) -> Any:
        return SimpleNamespace(accepted_checkpoint=None)

    async def submit(self, request: Any) -> Any:
        self.requests.append(request)
        return SimpleNamespace(
            affected_count=len(request.records),
            relationship_count=len(request.relationships),
            raw_admissions=[],
        )

    async def store_blob(self, data: bytes) -> str:
        raise AssertionError("this test does not exercise blob storage")


@pytest.fixture
def ingest():
    transport = _FakeTransport()
    return KnowledgeIngest(transport, loop=None), transport


@pytest.mark.asyncio
async def test_ingest_entities_writes_nodes_and_edges(ingest):
    service, transport = ingest
    res = await ingest_entities(
        [
            {"id": "a", "node_type": "Snapshot", "sourceUrl": "https://x"},
            {"id": "b", "node_type": "Tag", "name": "research"},
        ],
        [{"source": "a", "target": "b", "relationship": "hasTag"}],
        ingest=service,
    )
    assert res == {"nodes": 2, "edges": 1}
    assert {r.record_id for r in transport.requests[0].records} == {"a", "b"}
    assert transport.requests[0].relationships[0].source.record_id == "a"
    assert transport.requests[0].relationships[0].target.record_id == "b"


def test_map_snapshots_builds_typed_nodes_docs_and_links():
    entities, rels, docs = map_snapshots(
        [
            {
                "id": 1,
                "abid": "snap_abc",
                "url": "https://example.com/a",
                "title": "Example A",
                "timestamp": "1700000000.1",
                "tags": "research,news",
                "archiveresults": [
                    {
                        "id": 9,
                        "abid": "res_x",
                        "extractor": "wget",
                        "status": "succeeded",
                    }
                ],
            }
        ]
    )
    ids = {e["id"]: e for e in entities}
    assert ids["archivebox:snapshot:snap_abc"]["node_type"] == "Snapshot"
    assert ids["archivebox:snapshot:snap_abc"]["sourceUrl"] == "https://example.com/a"
    assert ids["archivebox:snapshot:snap_abc"]["externalToolId"] == "snap_abc"
    assert ids["archivebox:tag:research"]["node_type"] == "Tag"
    assert ids["archivebox:archiveresult:res_x"]["node_type"] == "ArchiveResult"
    assert ids["archivebox:archiveresult:res_x"]["extractor"] == "wget"
    # doc carries the page text
    assert docs[0]["id"] == "archivebox:document:snap_abc"
    assert docs[0]["text"] == "Example A"
    # links: two hasTag, one hasPageText, one hasArchiveResult
    types = sorted(r["relationship"] for r in rels)
    assert types == ["hasArchiveResult", "hasPageText", "hasTag", "hasTag"]


@pytest.mark.asyncio
async def test_ingest_snapshots_writes_nodes_and_docs(ingest):
    service, transport = ingest
    res = await ingest_snapshots(
        [
            {
                "abid": "snap1",
                "url": "https://a.example",
                "title": "A",
                "tags": ["research"],
            }
        ],
        ingest=service,
    )
    assert res is not None
    assert res["documents"] == 1
    all_ids = {r.record_id for req in transport.requests for r in req.records}
    assert "archivebox:snapshot:snap1" in all_ids
    assert "archivebox:document:snap1" in all_ids


def test_map_archiveresults_links_to_snapshot():
    entities, rels = map_archiveresults(
        [
            {
                "abid": "res1",
                "extractor": "pdf",
                "status": "failed",
                "snapshot_abid": "snap1",
            }
        ]
    )
    assert entities[0]["id"] == "archivebox:archiveresult:res1"
    assert entities[0]["archiveStatus"] == "failed"
    assert rels == [
        {
            "source": "archivebox:snapshot:snap1",
            "target": "archivebox:archiveresult:res1",
            "relationship": "hasArchiveResult",
        }
    ]


@pytest.mark.asyncio
async def test_ingest_archiveresults_writes_nodes(ingest):
    service, transport = ingest
    res = await ingest_archiveresults(
        [{"abid": "res1", "extractor": "screenshot", "status": "succeeded"}],
        ingest=service,
    )
    assert res == {"nodes": 1, "edges": 0}
    assert transport.requests[0].records[0].record_id == "archivebox:archiveresult:res1"


@pytest.mark.asyncio
async def test_ingest_documents_writes_document_nodes(ingest):
    service, transport = ingest
    res = await ingest_documents(
        [{"id": "archivebox:document:d1", "text": "hello", "source_uri": "https://x"}],
        ingest=service,
    )
    assert res == {"nodes": 1, "edges": 0}
    record = transport.requests[0].records[0]
    assert record.record_id == "archivebox:document:d1"
    assert record.payload["text"] == "hello"


@pytest.mark.asyncio
async def test_retired_structural_alias_is_rejected(ingest):
    service, _ = ingest
    with pytest.raises(IngestError, match="id and a node_type"):
        await ingest_entities([{"id": "a", "type": "Snapshot"}], ingest=service)


@pytest.mark.asyncio
async def test_empty_native_ingest_is_rejected(ingest):
    service, _ = ingest
    with pytest.raises(IngestError, match="at least one entity"):
        await ingest_entities([], ingest=service)
