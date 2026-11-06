"""ArchiveBox ``/api/v1/crawls``, ``/api/v1/machine`` and ``/api/v1/personas``.

One client method per upstream operation (CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R003).
"""

from typing import Any

import httpx
from scion_sdk.exceptions import require_auth

from archivebox_api.api.api_client_base import BaseApiClient

_CRAWLS = "/api/v1/crawls"
_MACHINE = "/api/v1/machine"
_PERSONAS = "/api/v1/personas"


class Api(BaseApiClient):
    # -- crawls ------------------------------------------------------------

    @require_auth
    def get_crawls(self) -> httpx.Response:
        """GET /api/v1/crawls/crawls

        List crawls (one crawl per add/schedule run, holding its snapshots).
        """
        return self._send("GET", f"{_CRAWLS}/crawls")

    @require_auth
    def create_crawl(
        self,
        urls: list[str],
        max_depth: int = 0,
        tags: list[str] | None = None,
        tags_str: str = "",
        label: str = "",
        notes: str = "",
        config: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """POST /api/v1/crawls/crawls

        Create a crawl over seed URLs (queued; the orchestrator snapshots them).

        Args:
            urls: Seed URLs.
            max_depth: Outlink depth to follow.
            tags: Tag names for the crawl's snapshots.
            tags_str: Comma-separated tag names (alternative to ``tags``).
            label: Human label for the crawl.
            notes: Free-text notes (for example why it was captured).
            config: Per-crawl config overrides (for example plugin toggles).
        """
        body = {
            "urls": urls,
            "max_depth": max_depth,
            "tags": tags,
            "tags_str": tags_str,
            "label": label,
            "notes": notes,
            "config": config or {},
        }
        return self._send("POST", f"{_CRAWLS}/crawls", json=body)

    @require_auth
    def get_crawl(
        self,
        crawl_id: str,
        as_rss: bool = False,
        with_snapshots: bool = False,
        with_archiveresults: bool = False,
    ) -> httpx.Response:
        """GET /api/v1/crawls/crawl/{crawl_id}

        Read one crawl, optionally with its snapshots and archive results.

        Args:
            crawl_id: The crawl id.
            as_rss: Return the crawl's snapshots as an RSS feed.
            with_snapshots: Embed the crawl's snapshots.
            with_archiveresults: Embed each snapshot's archive results.
        """
        params = {
            "as_rss": as_rss,
            "with_snapshots": with_snapshots,
            "with_archiveresults": with_archiveresults,
        }
        return self._send("GET", f"{_CRAWLS}/crawl/{crawl_id}", params=params)

    @require_auth
    def patch_crawl(
        self,
        crawl_id: str,
        crawl_action: str | None = None,
        status: str | None = None,
        retry_at: str | None = None,
        tags: list[str] | None = None,
        tags_str: str | None = None,
    ) -> httpx.Response:
        """PATCH /api/v1/crawls/crawl/{crawl_id}

        Update a crawl: change status, reschedule, retag, or run an action.

        Args:
            crawl_id: The crawl id.
            crawl_action: Crawl action to run (sent as ``action``).
            status: New status.
            retry_at: Next retry time (ISO 8601 date-time).
            tags: Replacement tag names.
            tags_str: Replacement tags, comma-separated.
        """
        body = {
            "action": crawl_action,
            "status": status,
            "retry_at": retry_at,
            "tags": tags,
            "tags_str": tags_str,
        }
        return self._send("PATCH", f"{_CRAWLS}/crawl/{crawl_id}", json=body)

    @require_auth
    def delete_crawl(self, crawl_id: str) -> httpx.Response:
        """DELETE /api/v1/crawls/crawl/{crawl_id}

        Delete a crawl.

        Args:
            crawl_id: The crawl id.
        """
        return self._send("DELETE", f"{_CRAWLS}/crawl/{crawl_id}")

    @require_auth
    def get_crawl_file(self, crawl_id: str, filename: str) -> httpx.Response:
        """GET /api/v1/crawls/crawl/{crawl_id}/files/{filename}

        Read a file at the root of a crawl's output directory.

        Args:
            crawl_id: The crawl id.
            filename: File name.
        """
        return self._send("GET", f"{_CRAWLS}/crawl/{crawl_id}/files/{filename}")

    @require_auth
    def get_crawl_folder_file(
        self, crawl_id: str, folder: str, filename: str
    ) -> httpx.Response:
        """GET /api/v1/crawls/crawl/{crawl_id}/files/{folder}/{filename}

        Read a file one folder deep in a crawl's output directory.

        Args:
            crawl_id: The crawl id.
            folder: Folder name.
            filename: File name.
        """
        return self._send(
            "GET", f"{_CRAWLS}/crawl/{crawl_id}/files/{folder}/{filename}"
        )

    @require_auth
    def get_crawl_subfolder_file(
        self, crawl_id: str, folder: str, subfolder: str, filename: str
    ) -> httpx.Response:
        """GET /api/v1/crawls/crawl/{crawl_id}/files/{folder}/{subfolder}/{filename}

        Read a file two folders deep in a crawl's output directory.

        Args:
            crawl_id: The crawl id.
            folder: Folder name.
            subfolder: Subfolder name.
            filename: File name.
        """
        return self._send(
            "GET",
            f"{_CRAWLS}/crawl/{crawl_id}/files/{folder}/{subfolder}/{filename}",
        )

    # -- machine -----------------------------------------------------------

    @require_auth
    def get_machines(
        self,
        id: str | None = None,
        hostname: str | None = None,
        os_platform: str | None = None,
        os_arch: str | None = None,
        hw_in_docker: bool | None = None,
        hw_in_vm: bool | None = None,
        bin_providers: str | None = None,
        limit: int = 200,
        offset: int = 0,
        page: int = 0,
    ) -> httpx.Response:
        """GET /api/v1/machine/machines

        List the machines (workers) that have run archiving.

        Args:
            id: Machine id.
            hostname: Hostname.
            os_platform: OS platform.
            os_arch: CPU architecture.
            hw_in_docker: Running in a container.
            hw_in_vm: Running in a VM.
            bin_providers: Binary providers.
            limit: Page size.
            offset: Page offset.
            page: Page number.
        """
        params = {
            "id": id,
            "hostname": hostname,
            "os_platform": os_platform,
            "os_arch": os_arch,
            "hw_in_docker": hw_in_docker,
            "hw_in_vm": hw_in_vm,
            "bin_providers": bin_providers,
            "limit": limit,
            "offset": offset,
            "page": page,
        }
        return self._send("GET", f"{_MACHINE}/machines", params=params)

    @require_auth
    def get_current_machine(self) -> httpx.Response:
        """GET /api/v1/machine/machine/current

        Read the machine serving this API.
        """
        return self._send("GET", f"{_MACHINE}/machine/current")

    @require_auth
    def get_machine(self, machine_id: str) -> httpx.Response:
        """GET /api/v1/machine/machine/{machine_id}

        Read one machine.

        Args:
            machine_id: The machine id.
        """
        return self._send("GET", f"{_MACHINE}/machine/{machine_id}")

    @require_auth
    def get_binaries(
        self,
        id: str | None = None,
        name: str | None = None,
        binprovider: str | None = None,
        status: str | None = None,
        machine_id: str | None = None,
        version: str | None = None,
        limit: int = 200,
        offset: int = 0,
        page: int = 0,
    ) -> httpx.Response:
        """GET /api/v1/machine/binaries

        List the capture binaries (chromium, wget, yt-dlp, ...) and their status.

        Args:
            id: Binary id.
            name: Binary name.
            binprovider: Provider (apt, pip, npm, env, ...).
            status: Install status.
            machine_id: Machine id.
            version: Version.
            limit: Page size.
            offset: Page offset.
            page: Page number.
        """
        params = {
            "id": id,
            "name": name,
            "binprovider": binprovider,
            "status": status,
            "machine_id": machine_id,
            "version": version,
            "limit": limit,
            "offset": offset,
            "page": page,
        }
        return self._send("GET", f"{_MACHINE}/binaries", params=params)

    @require_auth
    def get_binary(self, binary_id: str) -> httpx.Response:
        """GET /api/v1/machine/binary/{binary_id}

        Read one binary.

        Args:
            binary_id: The binary id.
        """
        return self._send("GET", f"{_MACHINE}/binary/{binary_id}")

    @require_auth
    def get_binaries_by_name(self, name: str) -> httpx.Response:
        """GET /api/v1/machine/binary/by-name/{name}

        List the installed binaries with this name.

        Args:
            name: Binary name.
        """
        return self._send("GET", f"{_MACHINE}/binary/by-name/{name}")

    # -- personas ----------------------------------------------------------

    @require_auth
    def get_personas(
        self, limit: int = 200, offset: int = 0, page: int = 0
    ) -> httpx.Response:
        """GET /api/v1/personas/personas

        List browser personas (named cookie/profile sets used for capture).

        Args:
            limit: Page size.
            offset: Page offset.
            page: Page number.
        """
        return self._send(
            "GET",
            f"{_PERSONAS}/personas",
            params={"limit": limit, "offset": offset, "page": page},
        )

    @require_auth
    def sync_persona(
        self,
        extension_persona_id: str,
        name: str,
        settings: dict[str, Any] | None = None,
        cookies_txt: str = "",
        auth_json: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """POST /api/v1/personas/sync

        Create or update a browser persona from the browser extension's export.
        The cookies and auth data are credentials: only sync personas the owner
        provided.

        Args:
            extension_persona_id: The extension's persona id.
            name: Persona name.
            settings: Browser settings.
            cookies_txt: Netscape cookies.txt content.
            auth_json: Auth/session storage export.
        """
        body = {
            "extension_persona_id": extension_persona_id,
            "name": name,
            "settings": settings,
            "cookies_txt": cookies_txt,
            "auth_json": auth_json or {},
        }
        return self._send("POST", f"{_PERSONAS}/sync", json=body)
