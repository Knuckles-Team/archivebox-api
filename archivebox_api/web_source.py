"""ArchiveBox as a web-source backend (CONN-ARCHIVEBOX-API-WEB-SOURCE-R001).

Two operations serve the web-source contract:

* ``web_fetch`` adds a URL through ``cli_add``, or reuses the snapshot that
  already archives it, and reports the snapshot.
* ``web_extract`` does the same, polls ``get_snapshot`` until the snapshot is
  complete, then reads the extracted text: the main-content (readability)
  output first, then the plain-text (htmltotext) output.

ArchiveBox serves extractor output files only to a logged-in session; the
REST token is refused there. :class:`ArchiveSession` therefore logs in through
the Django admin form with a CSRF token, keeps the session cookie, and logs in
again when a read is redirected to the login page.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import re
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, cast

import httpx
from scion_sdk.http.client import create_http_client
from scion_sdk.http.options import HttpClientOptions
from scion_sdk.tls.resolve import resolve_tls_profile

__all__ = [
    "REFUSAL_REASONS",
    "ArchiveSession",
    "ArchiveWebSource",
    "WebSourceRefused",
]

REFUSAL_REASONS = frozenset(
    {
        "robots_disallowed",
        "rate_limited",
        "size_exceeded",
        "unsupported_type",
        "egress_denied",
        "policy_refused",
        "extract_empty",
        "upstream_failed",
    }
)

_CSRF_RE = re.compile(r'name="csrfmiddlewaretoken" value="([^"]+)"')
_LOGIN_PATH = "/admin/login/"
_COMPLETE = frozenset({"sealed", "succeeded", "complete"})
_TEXT_SOURCES = (
    ("readability", "readability/content.txt"),
    ("htmltotext", "htmltotext.txt"),
)
_MAX_TEXT_BYTES = 5 * 1024 * 1024


class WebSourceRefused(Exception):
    """A closed web-source refusal for one URL."""

    def __init__(self, reason: str, url: str, detail: str = "") -> None:
        if reason not in REFUSAL_REASONS:
            raise ValueError(f"unknown refusal reason {reason!r}")
        self.reason = reason
        self.url = url
        super().__init__(f"{reason}: {url}" + (f" ({detail})" if detail else ""))


@dataclass
class ArchiveSession:
    """A Django admin session for reading extractor output files."""

    base_url: str
    username: str
    password: str
    timeout_s: float = 30.0
    session: httpx.Client = field(default=cast("httpx.Client", None))
    _logged_in: bool = field(default=False, init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)

    def __post_init__(self) -> None:
        if self.session is None:
            self.session = create_http_client(
                HttpClientOptions(
                    base_url=self.base_url.rstrip("/"),
                    timeout=self.timeout_s,
                    tls=resolve_tls_profile("archivebox"),
                    allow_plaintext=self.base_url.startswith("http://"),
                )
            )

    def _url(self, path: str) -> str:
        return self.base_url.rstrip("/") + path

    def login(self) -> None:
        if not self.username or not self.password:
            raise WebSourceRefused(
                "upstream_failed", self.base_url, "archive login is not configured"
            )
        page = self.session.get(self._url(_LOGIN_PATH))
        match = _CSRF_RE.search(page.text)
        if match is None:
            raise WebSourceRefused("upstream_failed", self.base_url, "no login form")
        response = self.session.post(
            self._url(_LOGIN_PATH),
            data={
                "username": self.username,
                "password": self.password,
                "csrfmiddlewaretoken": match.group(1),
                "next": "/",
            },
            headers={"Referer": self._url(_LOGIN_PATH)},
        )
        location = response.headers.get("location", "")
        if response.status_code != 302 or _LOGIN_PATH in location:
            raise WebSourceRefused("upstream_failed", self.base_url, "login refused")
        self._logged_in = True

    def _is_login_redirect(self, response: httpx.Response) -> bool:
        return response.is_redirect and _LOGIN_PATH in response.headers.get(
            "location", ""
        )

    def get_text(self, path: str) -> str | None:
        """The text at ``path``, or ``None`` when it is absent or not text."""
        found = self.get_file(path)
        if found is None:
            return None
        ctype, body = found
        if not ctype.startswith(("text/plain", "application/json")):
            return None
        return body.decode("utf-8", "replace")

    def get_file(
        self, path: str, *, max_bytes: int = _MAX_TEXT_BYTES
    ) -> tuple[str, bytes] | None:
        """``(content type, bytes)`` of the archive file at ``path``, or ``None``."""
        with self._lock:
            if not self._logged_in:
                self.login()
        response = self.session.get(self._url(path))
        if self._is_login_redirect(response):
            # The archive session expired: log in again and read once more.
            with self._lock:
                self.login()
            response = self.session.get(self._url(path))
            if self._is_login_redirect(response):
                raise WebSourceRefused("upstream_failed", path, "session expired")
        if response.status_code == 404:
            return None
        if response.status_code != 200:
            raise WebSourceRefused(
                "upstream_failed", path, f"HTTP {response.status_code}"
            )
        if len(response.content) > max_bytes:
            raise WebSourceRefused("size_exceeded", path)
        return response.headers.get("content-type", ""), response.content


def _json(response: Any) -> Any:
    if isinstance(response, (dict, list)):
        return response
    status = getattr(response, "status_code", 200)
    if status >= 400:
        raise WebSourceRefused("upstream_failed", "archivebox", f"HTTP {status}")
    return response.json()


def _now() -> str:
    return _dt.datetime.now(_dt.UTC).isoformat()


@dataclass
class ArchiveWebSource:
    """Add, poll and read one archived page through the ArchiveBox API."""

    api: Any
    session: ArchiveSession
    poll_interval_s: float = 2.0
    timeout_s: float = 120.0
    sleep: Callable[[float], None] = time.sleep
    clock: Callable[[], float] = time.monotonic

    def _existing(self, url: str) -> dict[str, Any] | None:
        data = _json(self.api.get_snapshots(url=url, limit=1))
        items = data.get("items", data) if isinstance(data, dict) else data
        return items[0] if items else None

    def fetch(self, url: str) -> dict[str, Any]:
        """Archive ``url`` once and return its snapshot; an archived URL is reused."""
        snapshot = self._existing(url)
        added = False
        if snapshot is None:
            _json(
                self.api.cli_add(
                    urls=[url],
                    tag="research.web",
                    extractors="readability,htmltotext,title",
                )
            )
            added = True
            snapshot = self._queued(url)
        return {
            "backend": "archivebox",
            "url": url,
            "snapshot_id": str(snapshot["id"]),
            "status": str(snapshot.get("status") or ""),
            "added": added,
        }

    def _queued(self, url: str) -> dict[str, Any]:
        """The snapshot ``cli_add`` queued; ArchiveBox creates it asynchronously."""
        deadline = self.clock() + self.timeout_s
        while True:
            snapshot = self._existing(url)
            if snapshot is not None:
                return snapshot
            if self.clock() >= deadline:
                raise WebSourceRefused("upstream_failed", url, "no snapshot after add")
            self.sleep(self.poll_interval_s)

    def _wait(self, url: str, snapshot_id: str) -> dict[str, Any]:
        deadline = self.clock() + self.timeout_s
        while True:
            snapshot = _json(
                self.api.get_snapshot(snapshot_id, with_archiveresults=False)
            )
            if str(snapshot.get("status") or "") in _COMPLETE:
                return snapshot
            if self.clock() >= deadline:
                raise WebSourceRefused(
                    "upstream_failed", url, "snapshot did not complete"
                )
            self.sleep(self.poll_interval_s)

    def snapshot(self, url: str) -> dict[str, Any]:
        """The completed snapshot archiving ``url`` and its archive path."""
        fetched = self.fetch(url)
        snapshot_id = fetched["snapshot_id"]
        snapshot = self._wait(url, snapshot_id)
        return {
            **snapshot,
            "snapshot_id": snapshot_id,
            "base": f"/snapshot/{snapshot_id.replace('-', '')}/",
        }

    def extract(self, url: str) -> dict[str, Any]:
        """The extracted text and metadata of ``url``'s completed snapshot."""
        fetched = self.fetch(url)
        snapshot_id = fetched["snapshot_id"]
        snapshot = self._wait(url, snapshot_id)
        base = f"/snapshot/{snapshot_id.replace('-', '')}/"
        text = ""
        extractor = ""
        for name, path in _TEXT_SOURCES:
            found = self.session.get_text(base + path)
            if found and found.strip():
                text, extractor = found.strip(), name
                break
        if not text:
            raise WebSourceRefused("extract_empty", url, "no extracted text")
        meta: dict[str, Any] = {}
        if extractor == "readability":
            raw = self.session.get_text(base + "readability/article.json")
            if raw:
                try:
                    meta = json.loads(raw)
                except ValueError:
                    meta = {}
        return {
            "backend": "archivebox",
            "url": url,
            "canonical_url": str(snapshot.get("url") or url),
            "final_url": str(snapshot.get("url") or url),
            "snapshot_id": snapshot_id,
            "extractor": extractor,
            "title": str(meta.get("title") or snapshot.get("title") or ""),
            "author": str(meta.get("byline") or ""),
            "published_at": str(meta.get("publishedTime") or ""),
            "site_name": str(meta.get("siteName") or ""),
            "text": text,
            "byte_count": len(text.encode("utf-8")),
            "content_digest": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "archived_at": str(
                snapshot.get("downloaded_at") or snapshot.get("modified_at") or ""
            ),
            "retrieved_at": _now(),
        }
