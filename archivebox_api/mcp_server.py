#!/usr/bin/python
"""ArchiveBox MCP Server.

Tool Interface & MCP Factory
Provides dynamic tool registration and stdio/SSE/http interfaces using FastMCP.
"""

# Telemetry & Observability
import logging
from typing import Any

import httpx
from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from fastmcp.utilities.logging import get_logger
from pydantic import Field
from scion_sdk.mcp.concurrency import run_blocking
from scion_sdk.mcp.method_tools import jsonable_result

from archivebox_api.auth import get_client

# Telemetry & Observability
logger = get_logger(name="archivebox-api")
logger.setLevel(logging.INFO)


def _records_from_dict(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Pull a record list out of a Ninja pagination envelope, or wrap a lone record."""
    for key in ("items", "results", "data", "snapshots"):
        value = data.get(key)
        if isinstance(value, list):
            return [r for r in value if isinstance(r, dict)]
    return [data] if data.get("id") or data.get("abid") else []


def _records_from_list(data: list[Any]) -> list[dict[str, Any]]:
    """Keep only the dict entries of a bare list response."""
    return [r for r in data if isinstance(r, dict)]


def _records_from_response(resp: Any) -> list[dict[str, Any]]:
    """Best-effort: pull a list of record dicts out of an ArchiveBox API response.

    Accepts a ``requests.Response``, a Ninja pagination envelope
    (``{"items"|"results"|"data": [...]}``), a bare list, or a single dict.
    """
    data: Any = resp
    if hasattr(resp, "json"):
        try:
            data = resp.json()
        except Exception:  # noqa: BLE001 — non-JSON body
            return []
    if isinstance(data, dict):
        return _records_from_dict(data)
    if isinstance(data, list):
        return _records_from_list(data)
    return []


def coerce_result(result: Any) -> Any:
    """Turn an ArchiveBox HTTP response into the tool result.

    CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R004: a 2xx JSON body is returned as-is; a 2xx
    text body (RSS, ``urls.txt``, JSON Lines) as ``{status_code, content_type,
    text}``; any other status as ``{status_code, error}`` with the upstream
    message, so a failed call is never reported as a bare status code.
    """
    if not isinstance(result, httpx.Response):
        return jsonable_result(result)
    status = result.status_code
    ctype = result.headers.get("content-type", "")
    if 200 <= status < 300:
        if "json" in ctype and "jsonl" not in ctype and "ndjson" not in ctype:
            try:
                return result.json()
            except ValueError:
                pass
        return {"status_code": status, "content_type": ctype, "text": result.text}
    try:
        detail: Any = result.json()
    except ValueError:
        detail = result.text[:4000]
    return {"status_code": status, "error": detail}


def register_kg_tools(mcp: FastMCP):
    """Wire-First native-ingestion tools (CONCEPT:AU-KG.ingest.enterprise-source-extractor)."""

    @mcp.tool(tags={"kg"})
    async def archivebox_ingest_snapshots(
        tag: str | None = Field(
            default=None, description="Only snapshots with this tag."
        ),
        search: str | None = Field(default=None, description="Full-text/meta search."),
        url: str | None = Field(default=None, description="Exact snapshot URL."),
        limit: int = Field(default=200, description="Maximum snapshots to ingest."),
        client=Depends(get_client),
        ctx: Context | None = None,
    ) -> dict:
        """List ArchiveBox snapshots and natively ingest them into the knowledge graph.

        Pushes :Snapshot (+ :Tag + :hasTag) nodes and per-snapshot :Document page-text,
        plus nested :ArchiveResult links, via the fast engine client. Best-effort:
        returns ``{"ingested": None}`` when no engine is reachable.
        """
        from archivebox_api.kg_ingest import ingest_snapshots

        if ctx:
            await ctx.info("Ingesting snapshots into the knowledge graph...")
        resp = await run_blocking(
            client.get_snapshots,
            tag=tag,
            search=search,
            url=url,
            limit=limit,
            with_archiveresults=True,
        )
        records = _records_from_response(resp)
        result = await ingest_snapshots(records)
        return {"listed": len(records), "ingested": result}

    @mcp.tool(tags={"kg"})
    async def archivebox_ingest_archiveresults(
        snapshot_id: str | None = Field(
            default=None, description="Results of this snapshot."
        ),
        snapshot_tag: str | None = Field(
            default=None, description="Results of snapshots with this tag."
        ),
        plugin: str | None = Field(
            default=None, description="Only this plugin's results."
        ),
        status: str | None = Field(
            default=None, description="Only results with this status."
        ),
        limit: int = Field(default=200, description="Maximum results to ingest."),
        client=Depends(get_client),
        ctx: Context | None = None,
    ) -> dict:
        """List ArchiveBox archive results and ingest them as :ArchiveResult nodes.

        Best-effort: returns ``{"ingested": None}`` when no engine is reachable.
        """
        from archivebox_api.kg_ingest import ingest_archiveresults

        if ctx:
            await ctx.info("Ingesting archive results into the knowledge graph...")
        resp = await run_blocking(
            client.get_archiveresults,
            snapshot_id=snapshot_id,
            snapshot_tag=snapshot_tag,
            plugin=plugin,
            status=status,
            limit=limit,
        )
        records = _records_from_response(resp)
        result = await ingest_archiveresults(records)
        return {"listed": len(records), "ingested": result}


_WEB_SOURCE: Any = None


def get_web_source() -> Any:
    """The process-wide ArchiveBox web source (CONN-ARCHIVEBOX-API-WEB-SOURCE-R001)."""
    global _WEB_SOURCE
    if _WEB_SOURCE is None:
        from scion_sdk.config import setting

        from archivebox_api.web_source import ArchiveSession, ArchiveWebSource

        base_url = setting("ARCHIVEBOX_URL") or setting("ARCHIVEBOX_BASE_URL")
        if not base_url:
            raise RuntimeError("ARCHIVEBOX_BASE_URL not set")
        _WEB_SOURCE = ArchiveWebSource(
            api=get_client(),
            session=ArchiveSession(
                base_url=base_url,
                username=setting("ARCHIVEBOX_USERNAME", "") or "",
                password=setting("ARCHIVEBOX_PASSWORD", "") or "",
            ),
            timeout_s=float(setting("ARCHIVEBOX_EXTRACT_TIMEOUT_S", 120.0)),
        )
    return _WEB_SOURCE


_CONTRACT_SOURCE: Any = None


def get_contract_source() -> Any:
    """The web-source contract's source over the configured ArchiveBox."""
    global _CONTRACT_SOURCE
    if _CONTRACT_SOURCE is None:
        from scion_sdk.config import setting

        from archivebox_api.web_source_contract import ArchiveboxSource

        _CONTRACT_SOURCE = ArchiveboxSource(
            get_web_source(),
            min_interval_s=float(setting("ARCHIVEBOX_MIN_INTERVAL_S", 1.0)),
        )
    return _CONTRACT_SOURCE


def register_web_tools(mcp: FastMCP):
    """web_fetch and web_extract: the SDK web-source contract's tools.

    CONN-ARCHIVEBOX-API-WEB-SOURCE-R001.1. The same names, schemas, refusal
    reasons and output shape as every other page connector's.
    """
    from scion_sdk.ports.web_source import register_web_source_tools

    register_web_source_tools(mcp, get_contract_source)
