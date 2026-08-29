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


def _tag_name(tag: Any) -> str | None:
    """Resolve one raw tag entry (dict or scalar) to its name, or None to skip it."""
    if isinstance(tag, dict):
        name = tag.get("name") or tag.get("slug")
        return str(name) if name else None
    return str(tag) if tag else None


def _tag_names_from_csv(raw: str) -> list[str]:
    """Split a comma-separated tag string into trimmed, non-empty names."""
    return [t.strip() for t in raw.split(",") if t.strip()]


def _tag_names_from_list(tags: list[Any]) -> list[str]:
    """Resolve a list of raw tag entries (dicts or scalars) into names."""
    names: list[str] = []
    for tag in tags:
        name = _tag_name(tag)
        if name:
            names.append(name)
    return names


def _tags_of(snap: dict[str, Any]) -> list[str]:
    """Normalize a snapshot's tags into a list of tag names."""
    tags = snap.get("tags")
    if isinstance(tags, str):
        return _tag_names_from_csv(tags)
    if isinstance(tags, list):
        return _tag_names_from_list(tags)
    return []


def _snapshot_entity(snap: dict[str, Any], sid: Any, snap_id: str) -> dict[str, Any]:
    """Build the ``:Snapshot`` node payload for one snapshot record."""
    return {
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


def _snapshot_tags(
    snap: dict[str, Any], snap_id: str
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Build ``:Tag`` nodes + ``hasTag`` links for one snapshot's tags."""
    entities: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []
    for tag in _tags_of(snap):
        tag_id = f"archivebox:tag:{tag}"
        entities.append({"id": tag_id, "node_type": "Tag", "name": tag})
        relationships.append(
            {"source": snap_id, "target": tag_id, "relationship": "hasTag"}
        )
    return entities, relationships


def _snapshot_document(
    snap: dict[str, Any], snap_id: str, sid: Any
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Build the ``:Document`` (+ ``hasPageText`` link) for one snapshot, if titled/URLed."""
    title = snap.get("title")
    url = snap.get("url")
    if not (title or url):
        return None, None
    doc_id = f"archivebox:document:{sid}"
    document = {
        "id": doc_id,
        "text": title or url,
        "title": title or url,
        "source_uri": url,
        "snapshot_id": snap_id,
    }
    relationship = {"source": snap_id, "target": doc_id, "relationship": "hasPageText"}
    return document, relationship


def _map_one_snapshot(
    snap: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Map one snapshot record → (entities, relationships, documents)."""
    sid = _ext_id(snap)
    if sid is None:
        return [], [], []
    snap_id = f"archivebox:snapshot:{sid}"
    entities = [_snapshot_entity(snap, sid, snap_id)]
    relationships: list[dict[str, Any]] = []
    documents: list[dict[str, Any]] = []

    tag_entities, tag_relationships = _snapshot_tags(snap, snap_id)
    entities.extend(tag_entities)
    relationships.extend(tag_relationships)

    document, doc_relationship = _snapshot_document(snap, snap_id, sid)
    if document is not None and doc_relationship is not None:
        documents.append(document)
        relationships.append(doc_relationship)

    for res in snap.get("archiveresults") or []:
        ents, rels = _map_one_archiveresult(res, snapshot_node=snap_id)
        entities.extend(ents)
        relationships.extend(rels)

    return entities, relationships, documents


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
        ents, rels, docs = _map_one_snapshot(snap)
        entities.extend(ents)
        relationships.extend(rels)
        documents.extend(docs)
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
        rels.append(
            {"source": snap_ref, "target": res_id, "relationship": "hasArchiveResult"}
        )
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


def _resolve_media_store(media_store: Any | None) -> Any | None:
    """Return the injected store, or lazily resolve the authoritative one."""
    if media_store is not None:
        return media_store
    try:
        return globals()["media_store"]()
    except Exception as e:  # noqa: BLE001 — no reachable engine is non-fatal
        logger.warning("Operation failed: error_type=%s", type(e).__name__)
        return None


def _media_type_for(mime_type: str) -> str:
    """Classify a MIME type into the coarse media-type buckets the store expects."""
    if mime_type.startswith("image"):
        return "image"
    if mime_type == "application/pdf":
        return "document"
    return "web_snapshot"


def _blob_provenance(snapshot: dict[str, Any], extractor: str) -> dict[str, Any]:
    """Build the non-null provenance fields (source URL/abid/timestamp/extractor)."""
    return {
        k: v
        for k, v in {
            "source_url": snapshot.get("url"),
            "abid": snapshot.get("abid"),
            "timestamp": snapshot.get("timestamp"),
            "extractor": extractor or None,
        }.items()
        if v is not None
    }


def _store_blob(
    store: Any,
    data: bytes,
    media_type: str,
    mime_type: str,
    name: str,
    extra: dict[str, Any],
) -> Any | None:
    """Persist bytes via the media store, returning None on any store failure."""
    try:
        return store.store_media(
            data,
            media_type=media_type,
            mime_type=mime_type,
            source=_SOURCE,
            name=name,
            extra=extra,
        )
    except Exception as e:  # noqa: BLE001 — engine/store failure is non-fatal
        logger.warning("Operation failed: error_type=%s", type(e).__name__)
        return None


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
    store = _resolve_media_store(media_store)
    if store is None:
        return None
    snapshot = snapshot or {}
    media_type = _media_type_for(mime_type)
    extra = _blob_provenance(snapshot, extractor)
    name = str(
        snapshot.get("title") or snapshot.get("url") or (snapshot.get("abid") or "")
    )
    stored = _store_blob(store, data, media_type, mime_type, name, extra)
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
