"""Native epistemic-graph ingestion for ArchiveBox records (typed graph nodes + docs).

CONCEPT:AU-KG.ingest.enterprise-source-extractor. The archivebox-api package natively
pushes its data into the ONE epistemic-graph knowledge graph **from its own code**, in
every applicable modality (the "maximum ingestion" bar):

* **typed nodes** — snapshots + per-extractor archive results → OWL ``:Snapshot`` /
  ``:ArchiveResult`` / ``:Tag`` nodes + ``:hasArchiveResult`` / ``:hasTag`` links.
* **documents** — a snapshot's title/URL text → a ``:Document`` (``:hasPageText``) so the
  archived page becomes semantic-search fodder; hub-side enrichment chunks/embeds it.
* **blobs** — raw web-capture bytes (HTML, screenshot, PDF, WARC) → a content-addressed
  media record via :func:`ingest_snapshot_blob`.

Everything rides the shared ``agent_connector_sdk.ingest`` knowledge-ingest facade. Engine
failures are explicit; the connector never acknowledges a partial or absent write. Node ids
follow ``archivebox:<class>:<externalId>`` and ``node_type`` matches a class the package's
``connector_manifest.yml`` declares.
"""

from __future__ import annotations

import logging
from typing import Any

from agent_connector_sdk.ingest import (
    ChangeSet,
    Document,
    Entity,
    IngestBinding,
    IngestError,
    IngestUnavailableError,
    KnowledgeIngest,
    MediaAsset,
    Relationship,
    current_ingest,
)

logger = logging.getLogger("archivebox_api.kg")

_SOURCE = "archivebox-api"
_DOMAIN = "archivebox"

_BINDING = IngestBinding(connector="archivebox-api", stream=_DOMAIN)
# sanitize=False: the archived page's own source URL is the product data for a web
# archive, not incidental PII — the default PersistencePrivacyGuard redacts URL-shaped
# property values ("[REDACTED_LOCATION]"), which would destroy blob provenance here.
_BLOB_BINDING = IngestBinding(
    connector="archivebox-api",
    stream=_DOMAIN,
    media_type="AssetOccurrence",
    sanitize=False,
)


def _to_entity(record: dict[str, Any]) -> Entity:
    # id/node_type are intentionally read with .get(): a missing one must reach
    # the SDK's own request builder (agent_connector_sdk.ingest.request._record),
    # which raises IngestError("every entity needs an id and a node_type") —
    # don't duplicate that validation here.
    return Entity(
        id=record.get("id"),
        node_type=record.get("node_type"),
        properties={k: v for k, v in record.items() if k not in ("id", "node_type")},
    )


def _to_relationship(record: dict[str, Any]) -> Relationship:
    props = {
        k: v
        for k, v in record.items()
        if k not in ("source", "target", "relationship")
    }
    return Relationship(
        source=record["source"],
        target=record["target"],
        relationship=record["relationship"],
        properties=props or None,
    )


def _to_document(record: dict[str, Any]) -> Document:
    return Document(
        id=record["id"],
        text=record["text"],
        title=record.get("title"),
        source_uri=record.get("source_uri"),
        properties={
            k: v
            for k, v in record.items()
            if k not in ("id", "text", "title", "source_uri")
        },
    )


async def ingest_entities(
    entities: list[dict[str, Any]],
    relationships: list[dict[str, Any]] | None = None,
    *,
    ingest: KnowledgeIngest | None = None,
) -> dict[str, int]:
    """Write canonical typed nodes and relationships in one native transaction."""
    if not entities:
        raise IngestError("ingest_entities needs at least one entity")
    change_set = ChangeSet(
        entities=tuple(_to_entity(e) for e in entities),
        relationships=tuple(_to_relationship(r) for r in relationships or ()),
    )
    service = ingest or current_ingest()
    receipt = await service.submit(_BINDING, change_set)
    return {"nodes": receipt.affected_count, "edges": receipt.relationship_count}


async def ingest_documents(
    docs: list[dict[str, Any]],
    *,
    ingest: KnowledgeIngest | None = None,
) -> dict[str, int]:
    """Write text records as canonical ``:Document`` nodes."""
    if not docs:
        raise IngestError("ingest_documents needs at least one document")
    change_set = ChangeSet(documents=tuple(_to_document(d) for d in docs))
    service = ingest or current_ingest()
    receipt = await service.submit(_BINDING, change_set)
    return {"nodes": receipt.affected_count, "edges": receipt.relationship_count}


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
async def ingest_snapshots(
    snapshots: list[dict[str, Any]],
    *,
    ingest: KnowledgeIngest | None = None,
) -> dict[str, int] | None:
    """Ingest snapshot records as ``:Snapshot`` (+ ``:Tag`` + ``:Document``) nodes.

    Returns merged ``{"nodes":n, "edges":m, "documents":d}``, or ``None`` best-effort
    when no engine is reachable.
    """
    entities, relationships, documents = map_snapshots(snapshots)
    try:
        node_res = (
            await ingest_entities(entities, relationships, ingest=ingest)
            if entities
            else None
        )
        doc_res = await ingest_documents(documents, ingest=ingest) if documents else None
    except IngestUnavailableError as e:
        logger.debug("Operation failed: error_type=%s", type(e).__name__)
        return None
    if node_res is None and doc_res is None:
        return None
    return {
        "nodes": (node_res or {}).get("nodes", 0),
        "edges": (node_res or {}).get("edges", 0),
        "documents": (doc_res or {}).get("nodes", 0),
    }


async def ingest_archiveresults(
    results: list[dict[str, Any]],
    *,
    ingest: KnowledgeIngest | None = None,
) -> dict[str, int] | None:
    """Ingest ArchiveResult records as ``:ArchiveResult`` nodes + snapshot links."""
    entities, relationships = map_archiveresults(results)
    if not entities:
        return None
    try:
        return await ingest_entities(entities, relationships, ingest=ingest)
    except IngestUnavailableError as e:
        logger.debug("Operation failed: error_type=%s", type(e).__name__)
        return None


def _media_type_for(mime_type: str) -> str:
    """Classify a MIME type into the coarse media-type buckets used for provenance."""
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


def ingest_snapshot_blob(
    data: bytes | None,
    *,
    snapshot: dict[str, Any] | None = None,
    mime_type: str = "application/octet-stream",
    extractor: str = "",
    ingest: KnowledgeIngest | None = None,
) -> dict[str, Any] | None:
    """Store raw web-capture bytes as a content-addressed media record in the graph.

    ``snapshot`` supplies provenance (source URL, abid, extractor). Returns
    ``{asset_id, digest, size_bytes, media_type}`` on success, or ``None`` (no
    bytes, or no reachable engine). This path has no async caller today, so it
    stays synchronous via ``KnowledgeIngest.submit_blocking`` rather than forcing
    every caller to ``await``.
    """
    if not data:
        return None
    snapshot = snapshot or {}
    media_kind = _media_type_for(mime_type)
    extra = _blob_provenance(snapshot, extractor)
    extra["media_kind"] = media_kind
    name = str(
        snapshot.get("title") or snapshot.get("url") or (snapshot.get("abid") or "")
    )
    asset = MediaAsset(data=data, mime_type=mime_type, name=name, properties=extra)
    change_set = ChangeSet(media=(asset,))
    try:
        service = ingest or current_ingest()
        receipt = service.submit_blocking(_BLOB_BINDING, change_set)
    except (IngestUnavailableError, IngestError) as e:  # noqa: BLE001 — best-effort
        logger.warning("Operation failed: error_type=%s", type(e).__name__)
        return None
    admission = receipt.raw_admissions[-1] if receipt.raw_admissions else None
    asset_id = admission.record_id if admission else None
    digest = admission.raw_digest if admission else None
    logger.info(
        "KG blob ingest: stored web snapshot %s (%s bytes) as asset %s",
        name,
        len(data),
        asset_id or "?",
    )
    return {
        "asset_id": asset_id,
        "digest": digest,
        "size_bytes": len(data),
        "media_type": media_kind,
    }
