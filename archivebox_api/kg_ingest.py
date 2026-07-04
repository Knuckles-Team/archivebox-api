"""Native epistemic-graph ingestion for ArchiveBox records (typed graph nodes + docs).

CONCEPT:AU-KG.ingest.enterprise-source-extractor. The archivebox-api package natively
pushes its data into the ONE epistemic-graph knowledge graph **from its own code**, in
every applicable modality (the "maximum ingestion" bar):

* **typed nodes** — snapshots + per-extractor archive results → OWL ``:Snapshot`` /
  ``:ArchiveResult`` / ``:Tag`` nodes + ``:hasArchiveResult`` / ``:hasTag`` links.
* **documents** — a snapshot's title/URL text → a ``:Document`` (``:hasPageText``) so the
  archived page becomes semantic-search fodder; hub-side enrichment chunks/embeds it.
* **blobs** — raw web-capture bytes (HTML, screenshot, PDF, WARC) → ``:Blob`` +
  ``:MediaAsset`` via :class:`MediaStore` (:func:`ingest_snapshot_blob`).

Everything rides the lightweight engine client (``GraphComputeEngine()._client`` + ``txn``)
via the shared ``agent_utilities.knowledge_graph.memory.native_ingest`` primitive when it is
present. That primitive is not yet in the installed agent-utilities, so this module imports
it **guarded** (try/except) and otherwise falls back to a self-contained txn write over the
same fast client. With no KG stack or no reachable engine every entry point **no-ops**
(returns ``None``), so the connector runs with zero KG infrastructure. Node ids follow
``archivebox:<class>:<externalId>`` and ``type`` matches a class the package's
``ontology_providers`` ``archivebox.ttl`` federates.
"""

from __future__ import annotations

import logging
import time
from typing import Any

logger = logging.getLogger("archivebox_api.kg")

_SOURCE = "archivebox-api"
_DOMAIN = "archivebox"
_DEFAULT_GRAPH = "__commons__"


# --------------------------------------------------------------------------- #
# engine client / write path — prefer the shared primitive, else self-contained
# --------------------------------------------------------------------------- #
def _shared():  # -> module | None
    """Return the shared ``native_ingest`` module, or ``None`` when absent."""
    try:
        from agent_utilities.knowledge_graph.memory import native_ingest
    except Exception as e:  # noqa: BLE001 — primitive not in installed agent-utilities
        logger.debug("native_ingest primitive unavailable: %s", e)
        return None
    return native_ingest


def _client() -> tuple[Any | None, str]:
    """Return ``(engine_client, graph_name)`` or ``(None, "")`` when unavailable."""
    try:
        from agent_utilities.knowledge_graph.core.graph_compute import (
            GraphComputeEngine,
        )
    except Exception as e:  # noqa: BLE001 — KG stack absent
        logger.debug("KG ingest unavailable (import): %s", e)
        return None, ""
    try:
        engine = GraphComputeEngine()
        client = getattr(engine, "_client", None)
        if client is None:
            return None, ""
        return client, (getattr(engine, "graph_name", None) or _DEFAULT_GRAPH)
    except Exception as e:  # noqa: BLE001 — engine unreachable
        logger.debug("KG ingest: engine unreachable: %s", e)
        return None, ""


def _fallback_write(
    entities: list[dict[str, Any]],
    relationships: list[dict[str, Any]] | None,
    *,
    client: Any | None,
    graph: str | None,
) -> dict[str, int] | None:
    """Self-contained txn write (used only when the shared primitive is absent)."""
    entities = [e for e in (entities or []) if e.get("id")]
    if not entities:
        return None
    if client is None:
        client, graph = _client()
    if client is None:
        return None
    graph = graph or _DEFAULT_GRAPH
    try:
        txn = client.txn.begin(graph=graph)
        for ent in entities:
            props = {k: v for k, v in ent.items() if k != "id" and v is not None}
            props.setdefault("source", _SOURCE)
            props.setdefault("domain", _DOMAIN)
            client.txn.add_node(txn, ent["id"], props)
        committed = client.txn.commit(txn)
    except Exception as e:  # noqa: BLE001 — engine/txn failure is non-fatal
        logger.warning("KG ingest: txn failed: %s", e)
        return None
    if not committed:
        logger.warning("KG ingest: txn not committed (conflict)")
        return None
    edges = 0
    for rel in relationships or []:
        try:
            client.edges.add(
                rel["source"], rel["target"], {"type": rel.get("type", "RELATED")}
            )
            edges += 1
        except Exception as e:  # noqa: BLE001 — pure edge link, best-effort
            logger.debug("KG ingest: edge skipped: %s", e)
    logger.info("KG ingest: wrote %d nodes, %d edges", len(entities), edges)
    return {"nodes": len(entities), "edges": edges}


def ingest_entities(
    entities: list[dict[str, Any]],
    relationships: list[dict[str, Any]] | None = None,
    *,
    source: str = _SOURCE,
    domain: str = _DOMAIN,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Write typed OWL nodes (+ edges) into epistemic-graph. Never raises."""
    if not entities:
        return None
    shared = _shared()
    if shared is not None and client is None:
        return shared.ingest_entities(
            entities, relationships, source=source, domain=domain
        )
    return _fallback_write(entities, relationships, client=client, graph=graph)


def ingest_documents(
    docs: list[dict[str, Any]],
    *,
    source: str = _SOURCE,
    domain: str = _DOMAIN,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Write text records as ``:Document`` nodes (semantic-search fodder). Never raises."""
    if not docs:
        return None
    shared = _shared()
    if shared is not None and client is None:
        return shared.ingest_documents(docs, source=source, domain=domain)
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    nodes: list[dict[str, Any]] = []
    for doc in docs:
        did = doc.get("id")
        text = doc.get("text") or doc.get("content")
        if not did or not text:
            continue
        node = {k: v for k, v in doc.items() if k != "content" and v is not None}
        node["id"] = did
        node["type"] = "Document"
        node["text"] = text
        node.setdefault("created_at", now)
        nodes.append(node)
    return _fallback_write(nodes, None, client=client, graph=graph)


def media_store() -> Any | None:
    """Return a :class:`MediaStore` over a live engine (raw-blob ingestion), or ``None``."""
    shared = _shared()
    if shared is not None:
        return shared.media_store()
    client, _ = _client()
    if client is None:
        return None
    try:
        from agent_utilities.knowledge_graph.core.graph_compute import (
            GraphComputeEngine,
        )
        from agent_utilities.knowledge_graph.memory.media_store import MediaStore

        return MediaStore(GraphComputeEngine())
    except Exception as e:  # noqa: BLE001
        logger.debug("KG ingest: media_store unavailable: %s", e)
        return None


# --------------------------------------------------------------------------- #
# record → node/document mappers
# --------------------------------------------------------------------------- #
def _ext_id(record: dict[str, Any]) -> str | None:
    """Prefer the stable ``abid``, else the numeric/uuid ``id``."""
    return record.get("abid") or record.get("id")


def _tags_of(snap: dict[str, Any]) -> list[str]:
    """Normalize a snapshot's tags into a list of tag names."""
    tags = snap.get("tags")
    if isinstance(tags, str):
        return [t.strip() for t in tags.split(",") if t.strip()]
    if isinstance(tags, list):
        out: list[str] = []
        for t in tags:
            if isinstance(t, dict):
                name = t.get("name") or t.get("slug")
                if name:
                    out.append(str(name))
            elif t:
                out.append(str(t))
        return out
    return []


def map_snapshots(
    snapshots: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Map snapshot records → (entities, relationships, documents).

    Emits ``:Snapshot`` (+ ``:Tag`` + ``:hasTag``) nodes and, when the snapshot has a
    title/URL, a ``:Document`` (+ ``:hasPageText``). Also folds any nested
    ``archiveresults`` into ``:ArchiveResult`` nodes + ``:hasArchiveResult`` links.
    """
    entities: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []
    documents: list[dict[str, Any]] = []
    for snap in snapshots or []:
        sid = _ext_id(snap)
        if sid is None:
            continue
        snap_id = f"archivebox:snapshot:{sid}"
        entities.append(
            {
                "id": snap_id,
                "type": "Snapshot",
                "abid": snap.get("abid"),
                "sourceUrl": snap.get("url"),
                "title": snap.get("title"),
                "timestamp": snap.get("timestamp"),
                "bookmarkedAt": snap.get("bookmarked_at"),
                "created_at": snap.get("created_at"),
                "modified_at": snap.get("modified_at"),
                "created_by_username": snap.get("created_by_username")
                or snap.get("created_by_id"),
                "externalToolId": str(sid),
            }
        )
        for tag in _tags_of(snap):
            tag_id = f"archivebox:tag:{tag}"
            entities.append({"id": tag_id, "type": "Tag", "name": tag})
            relationships.append(
                {"source": snap_id, "target": tag_id, "type": "hasTag"}
            )
        title = snap.get("title")
        url = snap.get("url")
        if title or url:
            doc_id = f"archivebox:document:{sid}"
            documents.append(
                {
                    "id": doc_id,
                    "text": title or url,
                    "title": title or url,
                    "source_uri": url,
                    "snapshot_id": snap_id,
                }
            )
            relationships.append(
                {"source": snap_id, "target": doc_id, "type": "hasPageText"}
            )
        for res in snap.get("archiveresults") or []:
            ents, rels = _map_one_archiveresult(res, snapshot_node=snap_id)
            entities.extend(ents)
            relationships.extend(rels)
    return entities, relationships, documents


def _map_one_archiveresult(
    res: dict[str, Any], *, snapshot_node: str | None
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rid = _ext_id(res)
    if rid is None:
        return [], []
    res_id = f"archivebox:archiveresult:{rid}"
    ent = {
        "id": res_id,
        "type": "ArchiveResult",
        "abid": res.get("abid"),
        "extractor": res.get("extractor"),
        "archiveStatus": res.get("status"),
        "output": res.get("output"),
        "cmd_version": res.get("cmd_version"),
        "created_at": res.get("created_at"),
        "externalToolId": str(rid),
    }
    rels: list[dict[str, Any]] = []
    snap_ref = snapshot_node
    if snap_ref is None:
        sref = res.get("snapshot_abid") or res.get("snapshot_id")
        if sref is not None:
            snap_ref = f"archivebox:snapshot:{sref}"
    if snap_ref is not None:
        rels.append({"source": snap_ref, "target": res_id, "type": "hasArchiveResult"})
    return [ent], rels


def map_archiveresults(
    results: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Map standalone ArchiveResult records → (:ArchiveResult entities, links)."""
    entities: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []
    for res in results or []:
        ents, rels = _map_one_archiveresult(res, snapshot_node=None)
        entities.extend(ents)
        relationships.extend(rels)
    return entities, relationships


# --------------------------------------------------------------------------- #
# high-level ingest entry points (called by the Wire-First MCP tool / fetch flow)
# --------------------------------------------------------------------------- #
def ingest_snapshots(
    snapshots: list[dict[str, Any]],
    *,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Ingest snapshot records as ``:Snapshot`` (+ ``:Tag`` + ``:Document``) nodes.

    Returns merged ``{"nodes":n, "edges":m, "documents":d}`` or ``None``.
    """
    entities, relationships, documents = map_snapshots(snapshots)
    node_res = ingest_entities(entities, relationships, client=client, graph=graph)
    doc_res = ingest_documents(documents, client=client, graph=graph)
    if node_res is None and doc_res is None:
        return None
    return {
        "nodes": (node_res or {}).get("nodes", 0),
        "edges": (node_res or {}).get("edges", 0),
        "documents": (doc_res or {}).get("nodes", 0),
    }


def ingest_archiveresults(
    results: list[dict[str, Any]],
    *,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Ingest ArchiveResult records as ``:ArchiveResult`` nodes + snapshot links."""
    entities, relationships = map_archiveresults(results)
    return ingest_entities(entities, relationships, client=client, graph=graph)


def ingest_snapshot_blob(
    data: bytes | None,
    *,
    snapshot: dict[str, Any] | None = None,
    mime_type: str = "application/octet-stream",
    extractor: str = "",
    media_store: Any | None = None,  # noqa: A002 — injectable for tests
) -> dict[str, Any] | None:
    """Store raw web-capture bytes as a ``:Blob`` + ``:MediaAsset`` in the graph.

    ``snapshot`` supplies provenance (source URL, abid, extractor). Returns
    ``{asset_id, digest, size_bytes}`` on success, or ``None`` (no engine / no bytes).
    """
    if not data:
        return None
    store = media_store if media_store is not None else globals()["media_store"]()
    if store is None:
        return None
    snapshot = snapshot or {}
    if mime_type.startswith("image"):
        media_type = "image"
    elif mime_type == "application/pdf":
        media_type = "document"
    else:
        media_type = "web_snapshot"
    extra = {
        k: v
        for k, v in {
            "source_url": snapshot.get("url"),
            "abid": snapshot.get("abid"),
            "timestamp": snapshot.get("timestamp"),
            "extractor": extractor or None,
        }.items()
        if v is not None
    }
    name = snapshot.get("title") or snapshot.get("url") or (snapshot.get("abid") or "")
    try:
        stored = store.store_media(
            data,
            media_type=media_type,
            mime_type=mime_type,
            source=_SOURCE,
            name=str(name),
            extra=extra,
        )
    except Exception as e:  # noqa: BLE001 — engine/store failure is non-fatal
        logger.warning("KG blob ingest: store_media failed: %s", e)
        return None
    if stored is None:
        return None
    logger.info(
        "KG blob ingest: stored web snapshot %s (%s bytes) as asset %s",
        name,
        len(data),
        getattr(stored, "asset_id", "?"),
    )
    return {
        "asset_id": stored.asset_id,
        "digest": stored.digest,
        "size_bytes": len(data),
        "media_type": media_type,
    }
