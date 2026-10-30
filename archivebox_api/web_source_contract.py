"""archivebox-api's implementation of the SDK web-source contract.

CONN-ARCHIVEBOX-API-WEB-SOURCE-R001.1. ``web_fetch`` and ``web_extract`` are
served by :func:`scion_sdk.ports.web_source.register_web_source_tools`
over :class:`ArchiveboxSource`, so their names, schemas, refusal reasons and
output shape are the contract's, identical to the webarchiver connector's.
ArchiveBox archives the page; the connector applies robots.txt and the
per-domain rate limit before submitting a URL, then serves the archived page
(``web_fetch``) or its readability output (``web_extract``). ``backend`` is
``archivebox``.
"""

from __future__ import annotations

import asyncio
import json
import re
from typing import Any
from urllib.parse import urlsplit

import httpx
from scion_sdk.http.client import create_http_client
from scion_sdk.http.options import HttpClientOptions
from scion_sdk.ports.web_source import (
    DEFAULT_MIN_INTERVAL_S,
    DomainRateLimiter,
    RobotsRules,
    WebFetchRequest,
    WebOutboundLink,
    WebPageResult,
    WebSourceRefused,
    content_digest,
)

from archivebox_api import web_source

__all__ = ["BACKEND", "USER_AGENT", "ArchiveboxSource"]

#: The connector named in every page's provenance.
BACKEND = "archivebox"
#: The agent token robots.txt rules are evaluated for (ArchiveBox's own).
USER_AGENT = "ArchiveBox"

#: Archived copies of the page body, in order of preference.
_PAGE_FILES = ("singlefile.html", "output.html")
_HREF = re.compile(
    r"""<a\b[^>]*\bhref=["'](https?://[^"'#\s]+)["'][^>]*>(.*?)</a>""", re.I | re.S
)
_TAG = re.compile(r"<[^>]+>")


def _read_robots(url: str) -> tuple[int, str]:
    parts = urlsplit(url)
    try:
        with create_http_client(
            HttpClientOptions(
                base_url=f"{parts.scheme}://{parts.netloc}",
                timeout=15,
                headers={"User-Agent": USER_AGENT},
                allow_plaintext=True,
            )
        ) as client:
            response = client.get(url)
    except (httpx.HTTPError, ValueError) as exc:
        raise WebSourceRefused("upstream_failed", type(exc).__name__) from exc
    return response.status_code, response.text


def _links(html: str) -> tuple[WebOutboundLink, ...]:
    seen: dict[str, WebOutboundLink] = {}
    for href, text in _HREF.findall(html):
        if href not in seen:
            seen[href] = WebOutboundLink(
                url=href, text=" ".join(_TAG.sub(" ", text).split())[:300]
            )
    return tuple(seen.values())


def _refusal(exc: web_source.WebSourceRefused) -> WebSourceRefused:
    return WebSourceRefused(exc.reason, str(exc))


class ArchiveboxSource:
    """Archive pages in ArchiveBox and serve them under the contract."""

    def __init__(
        self,
        archive: web_source.ArchiveWebSource,
        *,
        min_interval_s: float = DEFAULT_MIN_INTERVAL_S,
        robots_loader: Any = None,
    ) -> None:
        self.archive = archive
        self.limiter = DomainRateLimiter(min_interval_s=min_interval_s)
        loader = robots_loader or (lambda url: asyncio.to_thread(_read_robots, url))
        self.robots = RobotsRules(loader, user_agent=USER_AGENT)

    async def _snapshot(self, request: WebFetchRequest) -> dict[str, Any]:
        await self.robots.check(request.url)
        await self.limiter.acquire(request.url)
        try:
            return await asyncio.to_thread(self.archive.snapshot, request.url)
        except web_source.WebSourceRefused as exc:
            raise _refusal(exc) from exc

    async def _file(self, path: str, max_bytes: int) -> tuple[str, bytes] | None:
        try:
            return await asyncio.to_thread(
                self.archive.session.get_file, path, max_bytes=max_bytes
            )
        except web_source.WebSourceRefused as exc:
            raise _refusal(exc) from exc

    async def _content_type(self, base: str, request: WebFetchRequest) -> str:
        found = await self._file(base + "headers.json", 1024 * 1024)
        headers: dict[str, Any] = {}
        if found is not None:
            try:
                headers = {k.lower(): v for k, v in json.loads(found[1]).items()}
            except ValueError:
                headers = {}
        ctype = str(headers.get("content-type") or "text/html")
        if ctype.split(";", 1)[0].strip().lower() not in {
            t.lower() for t in request.accepted_types
        }:
            raise WebSourceRefused("unsupported_type", ctype)
        return ctype

    def _result(
        self,
        request: WebFetchRequest,
        snapshot: dict[str, Any],
        *,
        ctype: str,
        size: int,
        text: str,
        **metadata: Any,
    ) -> WebPageResult:
        final = str(snapshot.get("url") or request.url)
        return WebPageResult(
            url=request.url,
            canonical_url=final,
            final_url=final,
            status=200,
            content_type=ctype,
            byte_count=size,
            content_digest=content_digest(text),
            retrieved_at=str(snapshot.get("downloaded_at") or web_source._now()),
            text_markdown=text,
            backend=BACKEND,
            **metadata,
        )

    async def fetch(self, request: WebFetchRequest) -> WebPageResult:
        """The archived page body as text."""
        snapshot = await self._snapshot(request)
        base = snapshot["base"]
        ctype = await self._content_type(base, request)
        for name in _PAGE_FILES:
            found = await self._file(base + name, request.max_bytes)
            if found is not None and found[1]:
                body = found[1]
                return self._result(
                    request,
                    snapshot,
                    ctype=ctype,
                    size=len(body),
                    text=body.decode("utf-8", "replace"),
                )
        raise WebSourceRefused("extract_empty", "no archived page")

    async def extract(self, request: WebFetchRequest) -> WebPageResult:
        """The archived page's readability text and metadata, as markdown."""
        snapshot = await self._snapshot(request)
        base = snapshot["base"]
        ctype = await self._content_type(base, request)
        size = 0
        for name in _PAGE_FILES:
            found = await self._file(base + name, request.max_bytes)
            if found is not None and found[1]:
                size = len(found[1])
                break
        text = ""
        for name in ("readability/content.txt", "htmltotext.txt"):
            found = await self._file(base + name, request.max_bytes)
            if found is not None and found[1].strip():
                text = found[1].decode("utf-8", "replace").strip()
                break
        if not text:
            raise WebSourceRefused("extract_empty", "no extracted text")
        meta: dict[str, Any] = {}
        article = await self._file(base + "readability/article.json", 1024 * 1024)
        if article is not None:
            try:
                meta = json.loads(article[1])
            except ValueError:
                meta = {}
        content = await self._file(base + "readability/content.html", request.max_bytes)
        return self._result(
            request,
            snapshot,
            ctype=ctype,
            size=size or len(text.encode("utf-8")),
            text=text,
            title=str(meta.get("title") or snapshot.get("title") or ""),
            author=str(meta.get("byline") or ""),
            published_at=str(meta.get("publishedTime") or ""),
            outbound_links=_links(content[1].decode("utf-8", "replace"))
            if content
            else (),
        )
