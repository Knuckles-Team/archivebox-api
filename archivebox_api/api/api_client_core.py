"""ArchiveBox ``/api/v1/core`` operations: snapshots, archive results and tags.

One client method per upstream operation (CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R003);
each docstring opens with its ``VERB /path`` so the served tool carries the
right read-only / destructive annotation.
"""

import httpx
from scion_sdk.exceptions import require_auth

from archivebox_api.api.api_client_base import BaseApiClient

_CORE = "/api/v1/core"


class Api(BaseApiClient):
    # -- snapshots ---------------------------------------------------------

    @require_auth
    def get_snapshots(
        self,
        id: str | None = None,
        created_by_id: str | None = None,
        created_by_username: str | None = None,
        created_at__gte: str | None = None,
        created_at__lt: str | None = None,
        created_at: str | None = None,
        modified_at: str | None = None,
        modified_at__gte: str | None = None,
        modified_at__lt: str | None = None,
        search: str | None = None,
        search_mode: str | None = None,
        status: str | None = None,
        url: str | None = None,
        tag: str | None = None,
        title: str | None = None,
        timestamp: str | None = None,
        bookmarked_at__gte: str | None = None,
        bookmarked_at__lt: str | None = None,
        with_archiveresults: bool = False,
        limit: int = 200,
        offset: int = 0,
        page: int = 0,
        api_key: str | None = None,
    ) -> httpx.Response:
        """GET /api/v1/core/snapshots

        List snapshots matching these filters (paginated).

        Args:
            id: Filter by snapshot id (prefix match).
            created_by_id: Filter by creator id.
            created_by_username: Filter by creator username.
            created_at__gte: Created at or after (ISO 8601).
            created_at__lt: Created before (ISO 8601).
            created_at: Exact creation time (ISO 8601).
            modified_at: Exact modification time (ISO 8601).
            modified_at__gte: Modified at or after (ISO 8601).
            modified_at__lt: Modified before (ISO 8601).
            search: Search url, title, tags, id and timestamp (and page text in
                ``search_mode`` content/deep).
            search_mode: Search mode: ``meta`` (default), ``contents`` or ``deep``.
            status: Snapshot status (queued, started, sealed).
            url: Exact URL.
            tag: Exact tag name.
            title: Title contains.
            timestamp: Timestamp prefix.
            bookmarked_at__gte: Bookmarked at or after (ISO 8601).
            bookmarked_at__lt: Bookmarked before (ISO 8601).
            with_archiveresults: Embed each snapshot's archive results.
            limit: Page size.
            offset: Page offset.
            page: Page number.
            api_key: API key passed as a query parameter (optional).
        """
        params = {
            "id": id,
            "created_by_id": created_by_id,
            "created_by_username": created_by_username,
            "created_at__gte": created_at__gte,
            "created_at__lt": created_at__lt,
            "created_at": created_at,
            "modified_at": modified_at,
            "modified_at__gte": modified_at__gte,
            "modified_at__lt": modified_at__lt,
            "search": search,
            "search_mode": search_mode,
            "status": status,
            "url": url,
            "tag": tag,
            "title": title,
            "timestamp": timestamp,
            "bookmarked_at__gte": bookmarked_at__gte,
            "bookmarked_at__lt": bookmarked_at__lt,
            "with_archiveresults": with_archiveresults,
            "limit": limit,
            "offset": offset,
            "page": page,
        }
        return self._send("GET", f"{_CORE}/snapshots", params=params, api_key=api_key)

    @require_auth
    def create_snapshot(
        self,
        url: str,
        crawl_id: str | None = None,
        depth: int = 0,
        title: str | None = None,
        tags: list[str] | None = None,
        status: str | None = None,
    ) -> httpx.Response:
        """POST /api/v1/core/snapshots

        Create one snapshot for a URL (queued for archiving).

        Args:
            url: The URL to snapshot.
            crawl_id: Attach the snapshot to an existing crawl.
            depth: Crawl depth of this snapshot.
            title: Initial title.
            tags: Tag names to apply.
            status: Initial status (default queued).
        """
        body = {
            "url": url,
            "crawl_id": crawl_id,
            "depth": depth,
            "title": title,
            "tags": tags,
            "status": status,
        }
        return self._send("POST", f"{_CORE}/snapshots", json=body)

    @require_auth
    def get_snapshots_rss(
        self,
        crawl_id: str | None = None,
        created_by: str | None = None,
        limit: int | None = None,
        before: str | None = None,
    ) -> httpx.Response:
        """GET /api/v1/core/snapshots.rss

        RSS feed of recent snapshots.

        Args:
            crawl_id: Only snapshots of this crawl.
            created_by: Only snapshots created by this user.
            limit: Maximum feed items.
            before: Only snapshots before this time (ISO 8601).
        """
        params = {
            "crawl_id": crawl_id,
            "created_by": created_by,
            "limit": limit,
            "before": before,
        }
        return self._send("GET", f"{_CORE}/snapshots.rss", params=params)

    @require_auth
    def get_snapshot(
        self, snapshot_id: str, with_archiveresults: bool = True
    ) -> httpx.Response:
        """GET /api/v1/core/snapshot/{snapshot_id}

        Read one snapshot by id, optionally with its archive results.

        Args:
            snapshot_id: The snapshot id.
            with_archiveresults: Embed the snapshot's archive results.
        """
        return self._send(
            "GET",
            f"{_CORE}/snapshot/{snapshot_id}",
            params={"with_archiveresults": with_archiveresults},
        )

    @require_auth
    def patch_snapshot(
        self,
        snapshot_id: str,
        snapshot_action: str | None = None,
        status: str | None = None,
        retry_at: str | None = None,
        tags: list[str] | None = None,
    ) -> httpx.Response:
        """PATCH /api/v1/core/snapshot/{snapshot_id}

        Update a snapshot: change status, reschedule, replace its tags, or run
        an action (for example ``seal``).

        Args:
            snapshot_id: The snapshot id.
            snapshot_action: Snapshot action to run (sent as ``action``).
            status: New status.
            retry_at: Next retry time (ISO 8601 date-time).
            tags: Replacement tag names.
        """
        body = {
            "action": snapshot_action,
            "status": status,
            "retry_at": retry_at,
            "tags": tags,
        }
        return self._send("PATCH", f"{_CORE}/snapshot/{snapshot_id}", json=body)

    @require_auth
    def delete_snapshot(self, snapshot_id: str) -> httpx.Response:
        """DELETE /api/v1/core/snapshot/{snapshot_id}

        Delete one snapshot and its archive results.

        Args:
            snapshot_id: The snapshot id.
        """
        return self._send("DELETE", f"{_CORE}/snapshot/{snapshot_id}")

    # -- archive results ---------------------------------------------------

    @require_auth
    def get_archiveresults(
        self,
        id: str | None = None,
        search: str | None = None,
        snapshot_id: str | None = None,
        snapshot_url: str | None = None,
        snapshot_tag: str | None = None,
        status: str | None = None,
        output_str: str | None = None,
        plugin: str | None = None,
        hook_name: str | None = None,
        process_id: str | None = None,
        cmd: str | None = None,
        pwd: str | None = None,
        cmd_version: str | None = None,
        created_at: str | None = None,
        created_at__gte: str | None = None,
        created_at__lt: str | None = None,
        limit: int = 200,
        offset: int = 0,
        page: int = 0,
        api_key: str | None = None,
    ) -> httpx.Response:
        """GET /api/v1/core/archiveresults

        List archive results (one per plugin run on a snapshot).

        Args:
            id: Filter by result id.
            search: Search snapshot url/title/tags, plugin, output and id.
            snapshot_id: Results of this snapshot.
            snapshot_url: Results of the snapshot with this URL.
            snapshot_tag: Results of snapshots with this tag.
            status: Result status (queued, started, succeeded, failed, skipped,
                noresults).
            output_str: Output text contains.
            plugin: Plugin name (for example ``wget``, ``singlefile``, ``pdf``).
            hook_name: Hook name.
            process_id: Worker process id.
            cmd: Command contains.
            pwd: Working directory.
            cmd_version: Tool version.
            created_at: Exact creation time (ISO 8601).
            created_at__gte: Created at or after (ISO 8601).
            created_at__lt: Created before (ISO 8601).
            limit: Page size.
            offset: Page offset.
            page: Page number.
            api_key: API key passed as a query parameter (optional).
        """
        params = {
            "id": id,
            "search": search,
            "snapshot_id": snapshot_id,
            "snapshot_url": snapshot_url,
            "snapshot_tag": snapshot_tag,
            "status": status,
            "output_str": output_str,
            "plugin": plugin,
            "hook_name": hook_name,
            "process_id": process_id,
            "cmd": cmd,
            "pwd": pwd,
            "cmd_version": cmd_version,
            "created_at": created_at,
            "created_at__gte": created_at__gte,
            "created_at__lt": created_at__lt,
            "limit": limit,
            "offset": offset,
            "page": page,
        }
        return self._send(
            "GET", f"{_CORE}/archiveresults", params=params, api_key=api_key
        )

    @require_auth
    def create_archiveresult(
        self,
        snapshot_id: str,
        plugin: str,
        output_str: str = "",
        hook_name: str | None = None,
        status: str = "succeeded",
        output_json: str = "",
        files: dict[str, str] | None = None,
    ) -> httpx.Response:
        """POST /api/v1/core/archiveresults

        Create (or update) an archive result produced outside the server, for
        example evidence captured by another web connector, with optional
        output files.

        Args:
            snapshot_id: The snapshot the result belongs to.
            plugin: Plugin name to file the result under.
            output_str: Output summary text.
            hook_name: Hook name (server default when omitted).
            status: Result status (default ``succeeded``).
            output_json: Structured output as a JSON string.
            files: Output path -> base64 content, written under the plugin dir.
        """
        fields = {
            "snapshot_id": snapshot_id,
            "plugin": plugin,
            "output_str": output_str,
            "hook_name": hook_name,
            "status": status,
            "output_json": output_json,
        }
        return self._send_form(
            "POST", f"{_CORE}/archiveresults", fields=fields, files=files
        )

    @require_auth
    def get_archiveresult(self, archiveresult_id: str) -> httpx.Response:
        """GET /api/v1/core/archiveresult/{archiveresult_id}

        Read one archive result.

        Args:
            archiveresult_id: The archive result id.
        """
        return self._send("GET", f"{_CORE}/archiveresult/{archiveresult_id}")

    @require_auth
    def patch_archiveresult(
        self,
        archiveresult_id: str,
        status: str | None = None,
        output_str: str | None = None,
        output_json: str | None = None,
        files: dict[str, str] | None = None,
    ) -> httpx.Response:
        """PATCH /api/v1/core/archiveresult/{archiveresult_id}

        Append or replace output files on an archive result and update its
        status, output text or structured output.

        Args:
            archiveresult_id: The archive result id.
            status: New status.
            output_str: New output text.
            output_json: New structured output as a JSON string.
            files: Output path -> base64 content to add or replace.
        """
        fields = {
            "status": status,
            "output_str": output_str,
            "output_json": output_json,
        }
        return self._send_form(
            "PATCH",
            f"{_CORE}/archiveresult/{archiveresult_id}",
            fields=fields,
            files=files,
        )

    # -- tags --------------------------------------------------------------

    @require_auth
    def get_tags(
        self, limit: int = 200, offset: int = 0, page: int = 0
    ) -> httpx.Response:
        """GET /api/v1/core/tags

        List tags (paginated).

        Args:
            limit: Page size.
            offset: Page offset.
            page: Page number.
        """
        return self._send(
            "GET",
            f"{_CORE}/tags",
            params={"limit": limit, "offset": offset, "page": page},
        )

    @require_auth
    def get_tag(self, tag_id: str, with_snapshots: bool = True) -> httpx.Response:
        """GET /api/v1/core/tag/{tag_id}

        Read one tag by id or slug, optionally with its snapshots.

        Args:
            tag_id: Tag id or slug.
            with_snapshots: Embed the tag's snapshots.
        """
        return self._send(
            "GET",
            f"{_CORE}/tag/{tag_id}",
            params={"with_snapshots": with_snapshots},
        )

    @require_auth
    def delete_tag(self, tag_id: str) -> httpx.Response:
        """DELETE /api/v1/core/tag/{tag_id}

        Delete a tag (snapshots keep existing, untagged).

        Args:
            tag_id: Tag id.
        """
        return self._send("DELETE", f"{_CORE}/tag/{tag_id}")

    @require_auth
    def get_any(self, id: str) -> httpx.Response:
        """GET /api/v1/core/any/{id}

        Resolve any object (snapshot, archive result, tag, crawl) by its id;
        follows the server's redirect to the object's own endpoint.

        Args:
            id: The object id.
        """
        return self._send("GET", f"{_CORE}/any/{id}", follow_redirects=True)

    @require_auth
    def search_tags(
        self,
        q: str | None = None,
        sort: str | None = None,
        created_by: str | None = None,
        year: str | None = None,
        has_snapshots: str | None = None,
    ) -> httpx.Response:
        """GET /api/v1/core/tags/search/

        Search tags with snapshot counts.

        Args:
            q: Name contains.
            sort: Sort order (for example ``name``, ``-snapshots``).
            created_by: Only tags created by this user.
            year: Only tags created in this year.
            has_snapshots: ``yes``/``no`` filter on tags with snapshots.
        """
        params = {
            "q": q,
            "sort": sort,
            "created_by": created_by,
            "year": year,
            "has_snapshots": has_snapshots,
        }
        return self._send("GET", f"{_CORE}/tags/search/", params=params)

    @require_auth
    def tags_autocomplete(self, q: str = "") -> httpx.Response:
        """GET /api/v1/core/tags/autocomplete/

        Tag-name suggestions for a prefix.

        Args:
            q: Name prefix.
        """
        return self._send("GET", f"{_CORE}/tags/autocomplete/", params={"q": q})

    @require_auth
    def create_tag(self, name: str) -> httpx.Response:
        """POST /api/v1/core/tags/create/

        Create a tag (returns the existing tag when the name is taken).

        Args:
            name: Tag name.
        """
        return self._send("POST", f"{_CORE}/tags/create/", json={"name": name})

    @require_auth
    def rename_tag(self, tag_id: str, name: str) -> httpx.Response:
        """POST /api/v1/core/tag/{tag_id}/rename

        Rename a tag.

        Args:
            tag_id: Tag id.
            name: New name.
        """
        return self._send("POST", f"{_CORE}/tag/{tag_id}/rename", json={"name": name})

    @require_auth
    def get_tag_urls(self, tag_id: str) -> httpx.Response:
        """GET /api/v1/core/tag/{tag_id}/urls.txt

        Export a tag's snapshot URLs as plain text, one per line.

        Args:
            tag_id: Tag id.
        """
        return self._send("GET", f"{_CORE}/tag/{tag_id}/urls.txt")

    @require_auth
    def get_tag_snapshots_jsonl(self, tag_id: str) -> httpx.Response:
        """GET /api/v1/core/tag/{tag_id}/snapshots.jsonl

        Export a tag's snapshots as JSON Lines.

        Args:
            tag_id: Tag id.
        """
        return self._send("GET", f"{_CORE}/tag/{tag_id}/snapshots.jsonl")

    @require_auth
    def add_tag_to_snapshot(
        self, snapshot_id: str, tag_name: str | None = None, tag_id: int | None = None
    ) -> httpx.Response:
        """POST /api/v1/core/tags/add-to-snapshot/

        Add a tag (by name, created when missing, or by id) to a snapshot.

        Args:
            snapshot_id: The snapshot id.
            tag_name: Tag name.
            tag_id: Tag id.
        """
        body = {"snapshot_id": snapshot_id, "tag_name": tag_name, "tag_id": tag_id}
        return self._send("POST", f"{_CORE}/tags/add-to-snapshot/", json=body)

    @require_auth
    def remove_tag_from_snapshot(
        self, snapshot_id: str, tag_name: str | None = None, tag_id: int | None = None
    ) -> httpx.Response:
        """POST /api/v1/core/tags/remove-from-snapshot/

        Remove a tag (by name or id) from a snapshot; the tag itself remains.

        Args:
            snapshot_id: The snapshot id.
            tag_name: Tag name.
            tag_id: Tag id.
        """
        body = {"snapshot_id": snapshot_id, "tag_name": tag_name, "tag_id": tag_id}
        return self._send("POST", f"{_CORE}/tags/remove-from-snapshot/", json=body)
