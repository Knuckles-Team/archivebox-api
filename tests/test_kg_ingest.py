"""Native epistemic-graph typed-node ingestion for archivebox-api — Wire-First coverage.

Exercises the real ``ingest_entities`` / ``ingest_documents`` / ``ingest_snapshots`` /
``ingest_archiveresults`` seam with a fake engine client (no engine required), asserting
the single-transaction node/edge staging and commit and the ArchiveBox snapshot/result mappings.
CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

import pytest
from agent_utilities.knowledge_graph.memory.native_ingest import NativeIngestError

from archivebox_api.kg_ingest import (
    ingest_archiveresults,
    ingest_documents,
    ingest_entities,
    ingest_snapshots,
    map_archiveresults,
    map_snapshots,
)


class _FakeTxn:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.committed = False

    def begin(self, graph=None):
        self.graph = graph
        return "txn-1"

    def add_node(self, txn, node_id, props):
        self.nodes[node_id] = props

    def add_edge(self, txn, source, target, props):
        self.edges.append((source, target, props))

    def commit(self, txn):
        self.committed = True
        return True


class _FakeClient:
    def __init__(self):
        self.txn = _FakeTxn()


def test_ingest_entities_writes_nodes_and_edges():
    c = _FakeClient()
    res = ingest_entities(
        [
            {"id": "a", "node_type": "Snapshot", "sourceUrl": "https://x"},
            {"id": "b", "node_type": "Tag", "name": "research"},
        ],
        [{"source": "a", "target": "b", "relationship": "hasTag"}],
        client=c,
        graph="__commons__",
    )
    assert res == {"nodes": 2, "edges": 1}
    assert c.txn.committed is True
    assert set(c.txn.nodes) == {"a", "b"}
    # provenance is stamped
    assert c.txn.nodes["a"]["source"] == "archivebox-api"
    assert c.txn.nodes["a"]["domain"] == "archivebox"
    assert c.txn.edges == [("a", "b", {"relationship": "hasTag"})]


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


def test_ingest_snapshots_writes_nodes_and_docs():
    c = _FakeClient()
    res = ingest_snapshots(
        [
            {
                "abid": "snap1",
                "url": "https://a.example",
                "title": "A",
                "tags": ["research"],
            }
        ],
        client=c,
        graph="__commons__",
    )
    assert res is not None
    assert res["documents"] == 1
    assert c.txn.nodes["archivebox:snapshot:snap1"]["node_type"] == "Snapshot"
    assert c.txn.nodes["archivebox:document:snap1"]["node_type"] == "Document"
    assert c.txn.nodes["archivebox:document:snap1"]["text"] == "A"


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


def test_ingest_archiveresults_writes_nodes():
    c = _FakeClient()
    res = ingest_archiveresults(
        [{"abid": "res1", "extractor": "screenshot", "status": "succeeded"}],
        client=c,
        graph="__commons__",
    )
    assert res == {"nodes": 1, "edges": 0}
    assert c.txn.nodes["archivebox:archiveresult:res1"]["extractor"] == "screenshot"


def test_ingest_documents_writes_document_nodes():
    c = _FakeClient()
    res = ingest_documents(
        [{"id": "archivebox:document:d1", "text": "hello", "source_uri": "https://x"}],
        client=c,
        graph="__commons__",
    )
    assert res == {"nodes": 1, "edges": 0}
    node = c.txn.nodes["archivebox:document:d1"]
    assert node["node_type"] == "Document"
    assert node["text"] == "hello"
    assert "created_at" in node


def test_retired_structural_alias_is_rejected():
    with pytest.raises(NativeIngestError, match="canonical node_type"):
        ingest_entities([{"id": "a", "type": "Snapshot"}], client=_FakeClient())


def test_empty_native_ingest_is_rejected():
    with pytest.raises(NativeIngestError, match="at least one entity"):
        ingest_entities([], client=_FakeClient())
