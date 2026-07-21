"""Native epistemic-graph typed-node ingestion for archivebox-api — Wire-First coverage.

Exercises the real ``ingest_entities`` / ``ingest_documents`` / ``ingest_snapshots`` /
``ingest_archiveresults`` seam with a fake ChangeEnvelope-capable engine client (no engine
required), asserting the apply()'d add_node/add_edge operations and the ArchiveBox
snapshot/result mappings. Mirrors agent-utilities' own canonical
``tests/knowledge_graph/test_native_ingest.py`` fakes — the retired raw ``txn``-only fake is
deliberately rejected by ``native_ingest`` now. CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

from typing import Any

import msgpack
import pytest
from agent_utilities.knowledge_graph.core.session import GraphSession, use_session
from agent_utilities.knowledge_graph.memory.native_ingest import NativeIngestError
from agent_utilities.models.company_brain import ActorType
from agent_utilities.security.brain_context import ActorContext, use_actor

from archivebox_api.kg_ingest import (
    ingest_archiveresults,
    ingest_documents,
    ingest_entities,
    ingest_snapshots,
    map_archiveresults,
    map_snapshots,
)


@pytest.fixture(autouse=True)
def _governed_session():
    """Every native_ingest write requires a verified ambient GraphSession
    (CONCEPT:AU-P0-1) — no development bypass exists by design. Mint a
    synthetic, scoped session the same way agent-utilities' own
    ``tests/knowledge_graph/test_native_ingest.py`` does."""
    actor = ActorContext(
        actor_id="subject:opaque:synthetic",
        actor_type=ActorType.AUTOMATED_SERVICE,
        roles=(),
        tenant_id="tenant:opaque:synthetic",
        authenticated=True,
    )
    session = GraphSession(
        actor=actor,
        tenant=actor.tenant_id,
        scopes=frozenset({"kg:write"}),
        graph="graph:opaque:synthetic",
        policy_version="policy:opaque:synthetic",
        audience="epistemic-graph",
    )
    with use_actor(actor), use_session(session):
        yield


class _FakeNodes:
    def __init__(self) -> None:
        self.values: dict[str, dict[str, Any]] = {}

    def properties(self, node_id: str) -> dict[str, Any] | None:
        return self.values.get(node_id)

    def list(self) -> list[tuple[str, dict[str, Any]]]:
        return list(self.values.items())


class _FakeChanges:
    def __init__(self, nodes: _FakeNodes) -> None:
        self.nodes = nodes
        self.edges: list[tuple[str, str, dict[str, Any]]] = []
        self.applied: list[dict[str, Any]] = []
        self.records: dict[str, dict[str, Any]] = {}
        self.versions: dict[str, dict[str, Any]] = {}

    def get(self, envelope_id: str) -> dict[str, Any] | None:
        return self.records.get(envelope_id)

    def content_version(self, object_id: str) -> dict[str, Any] | None:
        return self.versions.get(object_id)

    def cursor(self, _source: str, _partition: str = "") -> None:
        return None

    def apply(self, envelope: dict[str, Any]) -> dict[str, Any]:
        self.applied.append(envelope)
        mutation = envelope["mutation"]
        for operation in mutation["operations"]:
            method = operation["method"]
            params = method["params"]
            properties = msgpack.unpackb(params["properties_msgpack"], raw=False)
            if method["method"] == "AddNode":
                self.nodes.values[params["node_id"]] = properties
            elif method["method"] == "AddEdge":
                self.edges.append(
                    (params["source_id"], params["target_id"], properties)
                )
        version = envelope["content_version"]
        self.versions[version["object_id"]] = version
        self.records[envelope["envelope_id"]] = envelope
        return {
            "batch_id": mutation["batch_id"],
            "replayed": False,
            "projection_pending": False,
        }


class _FakeRdf:
    def validate_shacl(self, _shapes: str, _data_graph: str) -> dict[str, Any]:
        return {"conforms": True, "results": []}


class _FakeClient:
    def __init__(self) -> None:
        self.nodes = _FakeNodes()
        self.changes = _FakeChanges(self.nodes)
        self.rdf = _FakeRdf()

    @staticmethod
    def supports(operation: str) -> bool:
        return operation == "ApplyChangeEnvelope"


def test_ingest_entities_writes_nodes_and_edges():
    c = _FakeClient()
    res = ingest_entities(
        [
            {"id": "a", "node_type": "Snapshot", "sourceUrl": "https://x"},
            {"id": "b", "node_type": "Tag", "name": "research"},
        ],
        [{"source": "a", "target": "b", "relationship": "hasTag"}],
        client=c,
    )
    assert res == {"nodes": 2, "edges": 1}
    assert c.changes.applied
    assert set(c.nodes.values) == {"a", "b"}
    # provenance is stamped
    assert c.nodes.values["a"]["source"] == "archivebox-api"
    assert c.nodes.values["a"]["domain"] == "archivebox"
    assert c.changes.edges == [("a", "b", {"relationship": "hasTag"})]


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
    )
    assert res is not None
    assert res["documents"] == 1
    assert c.nodes.values["archivebox:snapshot:snap1"]["node_type"] == "Snapshot"
    assert c.nodes.values["archivebox:document:snap1"]["node_type"] == "Document"
    assert c.nodes.values["archivebox:document:snap1"]["text"] == "A"


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
    )
    assert res == {"nodes": 1, "edges": 0}
    assert c.nodes.values["archivebox:archiveresult:res1"]["extractor"] == "screenshot"


def test_ingest_documents_writes_document_nodes():
    c = _FakeClient()
    res = ingest_documents(
        [{"id": "archivebox:document:d1", "text": "hello", "source_uri": "https://x"}],
        client=c,
    )
    assert res == {"nodes": 1, "edges": 0}
    node = c.nodes.values["archivebox:document:d1"]
    assert node["node_type"] == "Document"
    assert node["text"] == "hello"
    assert node["source"] == "archivebox-api"


def test_retired_structural_alias_is_rejected():
    with pytest.raises(NativeIngestError, match="canonical node_type"):
        ingest_entities([{"id": "a", "type": "Snapshot"}], client=_FakeClient())


def test_empty_native_ingest_is_rejected():
    with pytest.raises(NativeIngestError, match="at least one entity"):
        ingest_entities([], client=_FakeClient())
