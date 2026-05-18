#!/usr/bin/python
import warnings

# Filter RequestsDependencyWarning early to prevent log spam
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    try:
        from requests.exceptions import RequestsDependencyWarning

        warnings.filterwarnings("ignore", category=RequestsDependencyWarning)
    except ImportError:
        pass

warnings.filterwarnings("ignore", message=".*urllib3.*or chardet.*")
warnings.filterwarnings("ignore", message=".*urllib3.*or charset_normalizer.*")

import logging
import os
import sys
from typing import Any

from agent_utilities.base_utilities import to_boolean
from agent_utilities.mcp_utilities import create_mcp_server
from dotenv import find_dotenv, load_dotenv
from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from fastmcp.utilities.logging import get_logger
from pydantic import Field
from starlette.requests import Request
from starlette.responses import JSONResponse

from archivebox_api.auth import get_client

__version__ = "0.11.0"

logger = get_logger(name="archivebox-api")
logger.setLevel(logging.INFO)


def register_authentication_tools(mcp: FastMCP):
    @mcp.tool(tags={"authentication"})
    async def archivebox_authentication(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_api_token', 'check_api_token'"
        ),
        username: str | None = Field(default=None, description="username"),
        password: str | None = Field(default=None, description="password"),
        token: str | None = Field(default=None, description="token"),
        client=Depends(get_client),
    ) -> dict:
        """Manage authentication operations.

        Actions:
          - 'get_api_token': Generate an API token for a given username & password
          - 'check_api_token': Validate an API token to make sure it's valid and non-expired
        """
        kwargs: dict[str, Any]
        if action == "get_api_token":
            kwargs = {"username": username, "password": password}
            kwargs = {k: v for k, v in kwargs.items() if v is not None}
            return client.get_api_token(**kwargs)
        if action == "check_api_token":
            kwargs = {"token": token}
            kwargs = {k: v for k, v in kwargs.items() if v is not None}
            return client.check_api_token(**kwargs)
        raise ValueError(
            f"Unknown action: {action}. Must be one of: get_api_token', 'check_api_token"
        )


def register_core_tools(mcp: FastMCP):
    @mcp.tool(tags={"core"})
    async def archivebox_core(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_snapshots', 'get_snapshot', 'get_archiveresults', 'get_tag', 'get_any'"
        ),
        id: str | None = Field(default=None, description="id"),
        abid: Any | None = Field(default=None, description="abid"),
        created_by_id: str | None = Field(default=None, description="created by id"),
        created_by_username: str | None = Field(
            default=None, description="created by username"
        ),
        created_at__gte: str | None = Field(
            default=None, description="created at  gte"
        ),
        created_at__lt: str | None = Field(default=None, description="created at  lt"),
        created_at: str | None = Field(default=None, description="created at"),
        modified_at: str | None = Field(default=None, description="modified at"),
        modified_at__gte: str | None = Field(
            default=None, description="modified at  gte"
        ),
        modified_at__lt: str | None = Field(
            default=None, description="modified at  lt"
        ),
        search: str | None = Field(default=None, description="search"),
        url: str | None = Field(default=None, description="url"),
        tag: str | None = Field(default=None, description="tag"),
        title: str | None = Field(default=None, description="title"),
        timestamp: str | None = Field(default=None, description="timestamp"),
        bookmarked_at__gte: str | None = Field(
            default=None, description="bookmarked at  gte"
        ),
        bookmarked_at__lt: str | None = Field(
            default=None, description="bookmarked at  lt"
        ),
        with_archiveresults: bool | None = Field(
            default=None, description="with archiveresults"
        ),
        limit: int | None = Field(default=None, description="limit"),
        offset: int | None = Field(default=None, description="offset"),
        page: int | None = Field(default=None, description="page"),
        api_key: str | None = Field(default=None, description="api key"),
        snapshot_id: Any | None = Field(default=None, description="snapshot id"),
        snapshot_url: str | None = Field(default=None, description="snapshot url"),
        snapshot_tag: str | None = Field(default=None, description="snapshot tag"),
        status: str | None = Field(default=None, description="status"),
        output: str | None = Field(default=None, description="output"),
        extractor: str | None = Field(default=None, description="extractor"),
        cmd: str | None = Field(default=None, description="cmd"),
        pwd: str | None = Field(default=None, description="pwd"),
        cmd_version: str | None = Field(default=None, description="cmd version"),
        tag_id: str | None = Field(default=None, description="tag id"),
        with_snapshots: bool | None = Field(default=None, description="with snapshots"),
        client=Depends(get_client),
    ) -> dict:
        """Manage core operations.

        Actions:
          - 'get_snapshots': Retrieve list of snapshots
          - 'get_snapshot': Get a specific Snapshot by abid or id
          - 'get_archiveresults': List all ArchiveResult entries matching these filters
          - 'get_tag': Get a specific Tag by id or abid
          - 'get_any': Get a specific Snapshot, ArchiveResult, or Tag by abid
        """
        kwargs: dict[str, Any]
        if action == "get_snapshots":
            kwargs = {
                "id": id,
                "abid": abid,
                "created_by_id": created_by_id,
                "created_by_username": created_by_username,
                "created_at__gte": created_at__gte,
                "created_at__lt": created_at__lt,
                "created_at": created_at,
                "modified_at": modified_at,
                "modified_at__gte": modified_at__gte,
                "modified_at__lt": modified_at__lt,
                "search": search,
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
                "api_key": api_key,
            }
            kwargs = {k: v for k, v in kwargs.items() if v is not None}
            return client.get_snapshots(**kwargs)
        if action == "get_snapshot":
            kwargs = {
                "snapshot_id": snapshot_id,
                "with_archiveresults": with_archiveresults,
            }
            kwargs = {k: v for k, v in kwargs.items() if v is not None}
            return client.get_snapshot(**kwargs)
        if action == "get_archiveresults":
            kwargs = {
                "id": id,
                "search": search,
                "snapshot_id": snapshot_id,
                "snapshot_url": snapshot_url,
                "snapshot_tag": snapshot_tag,
                "status": status,
                "output": output,
                "extractor": extractor,
                "cmd": cmd,
                "pwd": pwd,
                "cmd_version": cmd_version,
                "created_at": created_at,
                "created_at__gte": created_at__gte,
                "created_at__lt": created_at__lt,
                "limit": limit,
                "offset": offset,
                "page": page,
                "api_key": api_key,
            }
            kwargs = {k: v for k, v in kwargs.items() if v is not None}
            return client.get_archiveresults(**kwargs)
        if action == "get_tag":
            kwargs = {
                "tag_id": tag_id,
                "with_snapshots": with_snapshots,
            }
            kwargs = {k: v for k, v in kwargs.items() if v is not None}
            return client.get_tag(**kwargs)
        if action == "get_any":
            kwargs = {"abid": abid}
            kwargs = {k: v for k, v in kwargs.items() if v is not None}
            return client.get_any(**kwargs)
        raise ValueError(
            f"Unknown action: {action}. Must be one of: get_snapshots', 'get_snapshot', 'get_archiveresults', 'get_tag', 'get_any"
        )


def register_cli_tools(mcp: FastMCP):
    @mcp.tool(tags={"cli"})
    async def archivebox_cli(
        action: str = Field(
            description="Action to perform. Must be one of: 'cli_add', 'cli_update', 'cli_schedule', 'cli_list', 'cli_remove'"
        ),
        urls: list[str] | None = Field(default=None, description="urls"),
        tag: str | None = Field(default=None, description="tag"),
        depth: int | None = Field(default=None, description="depth"),
        update: bool | None = Field(default=None, description="update"),
        update_all: bool | None = Field(default=None, description="update all"),
        index_only: bool | None = Field(default=None, description="index only"),
        overwrite: bool | None = Field(default=None, description="overwrite"),
        init: bool | None = Field(default=None, description="init"),
        extractors: Any | None = Field(default=None, description="extractors"),
        parser: str | None = Field(default=None, description="parser"),
        extra_data: dict | None = Field(default=None, description="extra data"),
        resume: float | None = Field(default=None, description="resume"),
        only_new: bool | None = Field(default=None, description="only new"),
        after: float | None = Field(default=None, description="after"),
        before: float | None = Field(default=None, description="before"),
        status: str | None = Field(default=None, description="status"),
        filter_type: Any | None = Field(default=None, description="filter type"),
        filter_patterns: list[str] | None = Field(
            default=None, description="filter patterns"
        ),
        import_path: str | None = Field(default=None, description="import path"),
        add: bool | None = Field(default=None, description="add"),
        every: str | None = Field(default=None, description="every"),
        clear: bool | None = Field(default=None, description="clear"),
        sort: str | None = Field(default=None, description="sort"),
        as_json: bool | None = Field(default=None, description="as json"),
        as_html: bool | None = Field(default=None, description="as html"),
        as_csv: str | bool | None = Field(default=None, description="as csv"),
        with_headers: bool | None = Field(default=None, description="with headers"),
        delete: bool | None = Field(default=None, description="delete"),
        client=Depends(get_client),
    ) -> dict:
        """Manage cli operations.

        Actions:
          - 'cli_add': Execute archivebox add command
          - 'cli_update': Execute archivebox update command
          - 'cli_schedule': Execute archivebox schedule command
          - 'cli_list': Execute archivebox list command
          - 'cli_remove': Execute archivebox remove command
        """
        kwargs: dict[str, Any]
        if action == "cli_add":
            kwargs = {
                "urls": urls,
                "tag": tag,
                "depth": depth,
                "update": update,
                "update_all": update_all,
                "index_only": index_only,
                "overwrite": overwrite,
                "init": init,
                "extractors": extractors,
                "parser": parser,
                "extra_data": extra_data,
            }
            kwargs = {k: v for k, v in kwargs.items() if v is not None}
            return client.cli_add(**kwargs)
        if action == "cli_update":
            kwargs = {
                "resume": resume,
                "only_new": only_new,
                "index_only": index_only,
                "overwrite": overwrite,
                "after": after,
                "before": before,
                "status": status,
                "filter_type": filter_type,
                "filter_patterns": filter_patterns,
                "extractors": extractors,
                "extra_data": extra_data,
            }
            kwargs = {k: v for k, v in kwargs.items() if v is not None}
            return client.cli_update(**kwargs)
        if action == "cli_schedule":
            kwargs = {
                "import_path": import_path,
                "add": add,
                "every": every,
                "tag": tag,
                "depth": depth,
                "overwrite": overwrite,
                "update": update,
                "clear": clear,
                "extra_data": extra_data,
            }
            kwargs = {k: v for k, v in kwargs.items() if v is not None}
            return client.cli_schedule(**kwargs)
        if action == "cli_list":
            kwargs = {
                "filter_patterns": filter_patterns,
                "filter_type": filter_type,
                "status": status,
                "after": after,
                "before": before,
                "sort": sort,
                "as_json": as_json,
                "as_html": as_html,
                "as_csv": as_csv,
                "with_headers": with_headers,
                "extra_data": extra_data,
            }
            kwargs = {k: v for k, v in kwargs.items() if v is not None}
            return client.cli_list(**kwargs)
        if action == "cli_remove":
            kwargs = {
                "delete": delete,
                "after": after,
                "before": before,
                "filter_type": filter_type,
                "filter_patterns": filter_patterns,
                "extra_data": extra_data,
            }
            kwargs = {k: v for k, v in kwargs.items() if v is not None}
            return client.cli_remove(**kwargs)
        raise ValueError(
            f"Unknown action: {action}. Must be one of: cli_add', 'cli_update', 'cli_schedule', 'cli_list', 'cli_remove"
        )


def get_mcp_instance() -> tuple[Any, ...]:
    """Initialize and return the MCP instance."""
    load_dotenv(find_dotenv())
    args, mcp, middlewares = create_mcp_server(
        name="archivebox-api MCP",
        version=__version__,
        instructions="archivebox-api MCP Server — Condensed Action-Routed Tools.",
    )

    @mcp.custom_route("/health", methods=["GET"])
    async def health_check(request: Request) -> JSONResponse:
        return JSONResponse({"status": "OK"})

    DEFAULT_AUTHENTICATIONTOOL = to_boolean(os.getenv("AUTHENTICATIONTOOL", "True"))
    if DEFAULT_AUTHENTICATIONTOOL:
        register_authentication_tools(mcp)
    DEFAULT_CORETOOL = to_boolean(os.getenv("CORETOOL", "True"))
    if DEFAULT_CORETOOL:
        register_core_tools(mcp)
    DEFAULT_CLITOOL = to_boolean(os.getenv("CLITOOL", "True"))
    if DEFAULT_CLITOOL:
        register_cli_tools(mcp)

    for mw in middlewares:
        mcp.add_middleware(mw)
    return mcp, args, middlewares


def mcp_server() -> None:
    mcp, args, middlewares = get_mcp_instance()
    print(f"archivebox-api MCP v{__version__}", file=sys.stderr)
    print("\nStarting MCP Server", file=sys.stderr)
    print(f"  Transport: {args.transport.upper()}", file=sys.stderr)
    print(f"  Auth: {args.auth_type}", file=sys.stderr)

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    elif args.transport == "streamable-http":
        mcp.run(transport="streamable-http", host=args.host, port=args.port)
    elif args.transport == "sse":
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        logger.error("Invalid transport", extra={"transport": args.transport})
        sys.exit(1)


if __name__ == "__main__":
    mcp_server()
