"""ArchiveBox ``/api/v1/cli`` operations: add, update, schedule, search, remove.

One client method per upstream operation (CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R003).
"""

import httpx
from scion_sdk.exceptions import ParameterError, require_auth

from archivebox_api.api.api_client_base import BaseApiClient

_CLI = "/api/v1/cli"


def _selection(
    *,
    after: float | None,
    before: float | None,
    filter_type: str | None,
    filter_patterns: list[str] | None,
    status: str | None,
    url__icontains: str | None,
    url__istartswith: str | None,
    tag: str | None,
    crawl_id: str | None,
    limit: int | None,
    sort: str | None,
    search: str | None,
) -> dict[str, object]:
    """The snapshot-selection fields shared by update, search and remove."""
    return {
        "after": after,
        "before": before,
        "filter_type": filter_type,
        "filter_patterns": filter_patterns,
        "status": status,
        "url__icontains": url__icontains,
        "url__istartswith": url__istartswith,
        "tag": tag,
        "crawl_id": crawl_id,
        "limit": limit,
        "sort": sort,
        "search": search,
    }


class Api(BaseApiClient):
    @require_auth
    def cli_add(
        self,
        urls: list[str],
        tag: str = "",
        depth: int = 0,
        snapshot_ids: list[str] | None = None,
        max_urls: int = 0,
        crawl_max_size: int = 0,
        crawl_timeout: int = 0,
        snapshot_max_size: int = 0,
        parser: str = "auto",
        plugins: str = "",
        persona: str = "Default",
        only_new: bool | None = None,
        update: bool = False,
        overwrite: bool = False,
        index_only: bool = False,
    ) -> httpx.Response:
        """POST /api/v1/cli/add

        Add URLs to the archive (one crawl; one snapshot per URL) and queue them
        for capture.

        Args:
            urls: URLs (or text/feeds the parser extracts URLs from) to archive.
            tag: Comma-separated tag names applied to every new snapshot.
            depth: Crawl depth (0 = only these URLs, 1 = also their outlinks).
            snapshot_ids: Re-run capture on these existing snapshots instead.
            max_urls: Cap on URLs the crawl may queue (0 = unlimited).
            crawl_max_size: Cap on total crawl bytes (0 = unlimited).
            crawl_timeout: Crawl time limit in seconds (0 = unlimited).
            snapshot_max_size: Cap on bytes per snapshot (0 = unlimited).
            parser: Input parser (``auto``, ``txt``, ``rss``, ``html``, ...).
            plugins: Comma-separated plugins to run (empty = instance defaults),
                for example ``wget,singlefile,pdf,screenshot,readability``.
            persona: Browser persona (cookies/profile) to capture with.
            only_new: Skip URLs already in the archive.
            update: Re-archive URLs already in the archive.
            overwrite: Overwrite existing outputs on re-archive.
            index_only: Add to the index without capturing.
        """
        body = {
            "urls": urls,
            "snapshot_ids": snapshot_ids,
            "tag": tag,
            "depth": depth,
            "max_urls": max_urls,
            "crawl_max_size": crawl_max_size,
            "crawl_timeout": crawl_timeout,
            "snapshot_max_size": snapshot_max_size,
            "parser": parser,
            "plugins": plugins,
            "persona": persona,
            "only_new": only_new,
            "update": update,
            "overwrite": overwrite,
            "index_only": index_only,
        }
        return self._send("POST", f"{_CLI}/add", json=body)

    @require_auth
    def cli_update(
        self,
        after: float | None = 0,
        before: float | None = None,
        filter_type: str | None = "substring",
        filter_patterns: list[str] | None = None,
        status: str | None = None,
        url__icontains: str | None = None,
        url__istartswith: str | None = None,
        tag: str | None = None,
        crawl_id: str | None = None,
        limit: int | None = None,
        sort: str | None = None,
        search: str | None = None,
        resume: str | None = None,
        batch_size: int = 100,
        continuous: bool = False,
        index_only: bool = False,
        migrate_only: bool = False,
    ) -> httpx.Response:
        """POST /api/v1/cli/update

        Re-archive (or re-index) the snapshots the selection matches.

        Args:
            after: Only snapshots bookmarked after this Unix time.
            before: Only snapshots bookmarked before this Unix time.
            filter_type: How ``filter_patterns`` match (exact, substring,
                domain, regex, tag, search).
            filter_patterns: Patterns to match.
            status: Only snapshots with this status.
            url__icontains: URL contains.
            url__istartswith: URL starts with.
            tag: Only snapshots with this tag.
            crawl_id: Only snapshots of this crawl.
            limit: Maximum snapshots.
            sort: Sort field.
            search: Full-text search.
            resume: Resume from this snapshot timestamp.
            batch_size: Snapshots per batch.
            continuous: Keep running and pick up new snapshots.
            index_only: Rebuild the index only.
            migrate_only: Run data migrations only.
        """
        body = _selection(
            after=after,
            before=before,
            filter_type=filter_type,
            filter_patterns=filter_patterns,
            status=status,
            url__icontains=url__icontains,
            url__istartswith=url__istartswith,
            tag=tag,
            crawl_id=crawl_id,
            limit=limit,
            sort=sort,
            search=search,
        ) | {
            "resume": resume,
            "batch_size": batch_size,
            "continuous": continuous,
            "index_only": index_only,
            "migrate_only": migrate_only,
        }
        return self._send("POST", f"{_CLI}/update", json=body)

    @require_auth
    def cli_schedule(
        self,
        import_path: str | None = None,
        add: bool = False,
        show: bool = False,
        foreground: bool = False,
        run_all: bool = False,
        quiet: bool = False,
        every: str | None = None,
        tag: str = "",
        depth: int = 0,
        only_new: bool | None = None,
        update: bool = False,
        overwrite: bool = False,
        clear: bool = False,
    ) -> httpx.Response:
        """POST /api/v1/cli/schedule

        Create, list or clear recurring archive schedules.

        Args:
            import_path: URL or feed to re-import on each run.
            add: Create a schedule.
            show: List existing schedules.
            foreground: Run the scheduler in the foreground.
            run_all: Run every schedule now.
            quiet: Less output.
            every: Interval (``hour``, ``day``, ``week``, ``month`` or cron).
            tag: Comma-separated tags for snapshots the schedule adds.
            depth: Crawl depth for each run.
            only_new: Only add URLs not yet archived.
            update: Re-archive existing URLs on each run.
            overwrite: Overwrite outputs on re-archive.
            clear: Remove all schedules.
        """
        body = {
            "import_path": import_path,
            "add": add,
            "show": show,
            "foreground": foreground,
            "run_all": run_all,
            "quiet": quiet,
            "every": every,
            "tag": tag,
            "depth": depth,
            "only_new": only_new,
            "update": update,
            "overwrite": overwrite,
            "clear": clear,
        }
        return self._send("POST", f"{_CLI}/schedule", json=body)

    @require_auth
    def cli_search(
        self,
        after: float | None = 0,
        before: float | None = None,
        filter_type: str | None = "substring",
        filter_patterns: list[str] | None = None,
        status: str | None = None,
        url__icontains: str | None = None,
        url__istartswith: str | None = None,
        tag: str | None = None,
        crawl_id: str | None = None,
        limit: int | None = None,
        sort: str | None = None,
        search: str | None = None,
        as_json: bool = True,
        as_html: bool = False,
        as_csv: str | None = "timestamp,url",
        with_headers: bool = False,
    ) -> httpx.Response:
        """POST /api/v1/cli/search

        Search the archive index and export the matches (JSON, HTML or CSV).

        Args:
            after: Only snapshots bookmarked after this Unix time.
            before: Only snapshots bookmarked before this Unix time.
            filter_type: How ``filter_patterns`` match (exact, substring,
                domain, regex, tag, search).
            filter_patterns: Patterns to match.
            status: Only snapshots with this status.
            url__icontains: URL contains.
            url__istartswith: URL starts with.
            tag: Only snapshots with this tag.
            crawl_id: Only snapshots of this crawl.
            limit: Maximum snapshots.
            sort: Sort field.
            search: Full-text search.
            as_json: Export as JSON.
            as_html: Export as HTML.
            as_csv: Export as CSV with these columns.
            with_headers: Include headers in the export.
        """
        body = _selection(
            after=after,
            before=before,
            filter_type=filter_type,
            filter_patterns=filter_patterns,
            status=status,
            url__icontains=url__icontains,
            url__istartswith=url__istartswith,
            tag=tag,
            crawl_id=crawl_id,
            limit=limit,
            sort=sort,
            search=search,
        ) | {
            "as_json": as_json,
            "as_html": as_html,
            "as_csv": as_csv,
            "with_headers": with_headers,
        }
        return self._send("POST", f"{_CLI}/search", json=body)

    @require_auth
    def cli_remove(
        self,
        after: float | None = 0,
        before: float | None = None,
        filter_type: str = "exact",
        filter_patterns: list[str] | None = None,
        status: str | None = None,
        url__icontains: str | None = None,
        url__istartswith: str | None = None,
        tag: str | None = None,
        crawl_id: str | None = None,
        limit: int | None = None,
        sort: str | None = None,
        search: str | None = None,
        timeout: float = 60.0,
    ) -> httpx.Response:
        """POST /api/v1/cli/remove

        Delete the snapshots the selection matches, and their files. Destructive:
        always pass the narrowest selection (an exact URL, or one tag).

        Args:
            after: Only snapshots bookmarked after this Unix time.
            before: Only snapshots bookmarked before this Unix time.
            filter_type: How ``filter_patterns`` match (default ``exact``).
            filter_patterns: Patterns to match.
            status: Only snapshots with this status.
            url__icontains: URL contains.
            url__istartswith: URL starts with.
            tag: Only snapshots with this tag.
            crawl_id: Only snapshots of this crawl.
            limit: Maximum snapshots.
            sort: Sort field.
            search: Full-text search.
            timeout: Seconds to wait for the removal.
        """
        if not any(
            (filter_patterns, url__icontains, url__istartswith, tag, crawl_id, search)
        ):
            raise ParameterError(
                "cli_remove needs a selection (filter_patterns, tag, url__icontains,"
                " url__istartswith, crawl_id or search); it never removes everything"
            )
        body = _selection(
            after=after,
            before=before,
            filter_type=filter_type,
            filter_patterns=filter_patterns,
            status=status,
            url__icontains=url__icontains,
            url__istartswith=url__istartswith,
            tag=tag,
            crawl_id=crawl_id,
            limit=limit,
            sort=sort,
            search=search,
        ) | {"timeout": timeout}
        return self._send("POST", f"{_CLI}/remove", json=body)
