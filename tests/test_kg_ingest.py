"""Native epistemic-graph typed-node ingestion for archivebox-api — Wire-First coverage.

Exercises the real ``ingest_entities`` / ``ingest_documents`` / ``ingest_snapshots`` /
``ingest_archiveresults`` seam with a fake engine client (no engine required), asserting
the txn add_node/commit + edge calls and the ArchiveBox snapshot/result mappings.
CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

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
        self.committed = False

    def begin(self, graph=None):
        self.graph = graph
        return "txn-1"

    def add_node(self, txn, node_id, props):
        self.nodes[node_id] = props

    def commit(self, txn):
        self.committed = True
        return True


class _FakeEdges:
    def __init__(self):
        self.edges = []

    def add(self, src, dst, props):
        self.edges.append((src, dst, props))


class _FakeClient:
    def __init__(self):
        self.txn = _FakeTxn()
        self.edges = _FakeEdges()


def test_ingest_entities_writes_nodes_and_edges():
    c = _FakeClient()
    res = ingest_entities(
        [
            {"id": "a", "type": "Snapshot", "sourceUrl": "https://x"},
            {"id": "b", "type": "Tag", "name": "research"},
        ],
        [{"source": "a", "target": "b", "type": "hasTag"}],
        client=c,
        graph="__commons__",
    )
    assert res == {"nodes": 2, "edges": 1}
    assert c.txn.committed is True
    assert set(c.txn.nodes) == {"a", "b"}
    # provenance is stamped
    assert c.txn.nodes["a"]["source"] == "archivebox-api"
    assert c.txn.nodes["a"]["domain"] == "archivebox"
    assert c.edges.edges == [("a", "b", {"type": "hasTag"})]


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
    assert ids["archivebox:snapshot:snap_abc"]["type"] == "Snapshot"
    assert ids["archivebox:snapshot:snap_abc"]["sourceUrl"] == "https://example.com/a"
    assert ids["archivebox:snapshot:snap_abc"]["externalToolId"] == "snap_abc"
    assert ids["archivebox:tag:research"]["type"] == "Tag"
    assert ids["archivebox:archiveresult:res_x"]["type"] == "ArchiveResult"
    assert ids["archivebox:archiveresult:res_x"]["extractor"] == "wget"
    # doc carries the page text
    assert docs[0]["id"] == "archivebox:document:snap_abc"
    assert docs[0]["text"] == "Example A"
    # links: two hasTag, one hasPageText, one hasArchiveResult
    types = sorted(r["type"] for r in rels)
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
    assert c.txn.nodes["archivebox:snapshot:snap1"]["type"] == "Snapshot"
    assert c.txn.nodes["archivebox:document:snap1"]["type"] == "Document"
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
            "type": "hasArchiveResult",
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
    assert node["type"] == "Document"
    assert node["text"] == "hello"
    assert "created_at" in node


def test_ingest_noops_without_engine():
    # No injected client + no reachable engine -> clean no-op.
    assert ingest_entities([{"id": "a", "type": "Snapshot"}]) is None


def test_ingest_empty_is_noop():
    assert ingest_entities([], client=_FakeClient()) is None
    assert ingest_snapshots([], client=_FakeClient()) is None
    assert ingest_archiveresults([], client=_FakeClient()) is None
