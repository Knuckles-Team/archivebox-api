"""Native epistemic-graph ingestion for ArchiveBox records (typed graph nodes + docs).

CONCEPT:AU-KG.ingest.enterprise-source-extractor. The archivebox-api package natively
pushes its data into the ONE epistemic-graph knowledge graph **from its own code**, in
every applicable modality (the "maximum ingestion" bar):

* **typed nodes** — snapshots + per-extractor archive results → OWL ``:Snapshot`` /
  ``:ArchiveResult`` / ``:Tag`` nodes + ``:hasArchiveResult`` / ``:hasTag`` links.
* **documents** — a snapshot's title/URL text → a ``:Document`` (``:hasPageText``) so the
  archived page becomes semantic-search fodder; hub-side enrichment chunks/embeds it.
* **blobs** — raw web-capture bytes (HTML, screenshot, PDF, WARC) → ``:Blob`` +
  ``:AssetOccurrence`` via :class:`MediaStore` (:func:`ingest_snapshot_blob`).

Everything rides the required shared
``agent_utilities.knowledge_graph.memory.native_ingest`` transaction primitive. Engine
failures are explicit; the connector never acknowledges a partial or absent write. Node ids
follow ``archivebox:<class>:<externalId>`` and ``node_type`` matches a class the package's
``ontology_providers`` ``archivebox.ttl`` federates.
"""

from __future__ import annotations

import logging
from typing import Any

from agent_utilities.knowledge_graph.memory.native_ingest import (
    ingest_documents as _native_ingest_documents,
)
from agent_utilities.knowledge_graph.memory.native_ingest import (
    ingest_entities as _native_ingest_entities,
)
from agent_utilities.knowledge_graph.memory.native_ingest import (
    media_store as _native_media_store,
)

logger = logging.getLogger("archivebox_api.kg")

_SOURCE = "archivebox-api"
_DOMAIN = "archivebox"
def ingest_entities(
    entities: list[dict[str, Any]],
    relationships: list[dict[str, Any]] | None = None,
    *,
    source: str = _SOURCE,
    domain: str = _DOMAIN,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int]:
    """Write canonical typed nodes and relationships in one native transaction."""
    return _native_ingest_entities(
        entities,
        relationships,
        source=source,
        domain=domain,
        client=client,
        graph=graph,
    )


def ingest_documents(
    docs: list[dict[str, Any]],
    *,
    source: str = _SOURCE,
    domain: str = _DOMAIN,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int]:
    """Write text records as canonical ``:Document`` nodes."""
    return _native_ingest_documents(
        docs, source=source, domain=domain, client=client, graph=graph
    )


def media_store() -> Any:
    """Return the authoritative native media store."""
    return _native_media_store()


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
                "node_type": "Snapshot",
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
            entities.append({"id": tag_id, "node_type": "Tag", "name": tag})
            relationships.append(
                {"source": snap_id, "target": tag_id, "relationship": "hasTag"}
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
                {"source": snap_id, "target": doc_id, "relationship": "hasPageText"}
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
        "node_type": "ArchiveResult",
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
        rels.append({"source": snap_ref, "target": res_id, "relationship": "hasArchiveResult"})
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
    """Store raw web-capture bytes as a ``:Blob`` + ``:AssetOccurrence`` in the graph.

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
        logger.warning("Operation failed: error_type=%s", type(e).__name__)
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
