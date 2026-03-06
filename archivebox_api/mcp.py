#!/usr/bin/python
# coding: utf-8

from dotenv import load_dotenv, find_dotenv
import os
import sys
import logging
from typing import Optional, List, Dict, Union

from fastmcp.exceptions import ResourceError
from pydantic import Field
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastmcp import FastMCP, Context
from fastmcp.utilities.logging import get_logger
from archivebox_api.archivebox_api import Api
from agent_utilities.base_utilities import to_boolean
from agent_utilities.mcp_utilities import (
    create_mcp_server,
    config,
)

__version__ = "0.1.27"

logger = get_logger(name="TokenMiddleware")
logger.setLevel(logging.DEBUG)


def register_misc_tools(mcp: FastMCP):
    async def health_check(request: Request) -> JSONResponse:
        return JSONResponse({"status": "OK"})


def register_authentication_tools(mcp: FastMCP):
    @mcp.tool(
        exclude_args=[
            "archivebox_url",
            "username",
            "password",
            "token",
            "api_key",
            "verify",
        ],
        tags={"authentication"},
    )
    async def get_api_token(
        username: Optional[str] = Field(
            description="The username for authentication",
        ),
        password: Optional[str] = Field(
            description="The password for authentication",
        ),
        archivebox_url: str = Field(
            default=os.environ.get("ARCHIVEBOX_URL", None),
            description="The URL of the ArchiveBox instance (e.g., https://yourinstance.archivebox.com)",
        ),
        token: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_TOKEN", None),
            description="Bearer token for authentication",
        ),
        api_key: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_API_KEY", None),
            description="API key for authentication",
        ),
        verify: Optional[bool] = Field(
            default=to_boolean(os.environ.get("ARCHIVEBOX_VERIFY", "True")),
            description="Whether to verify SSL certificates",
        ),
    ) -> dict:
        """
        Generate an API token for a given username & password.
        """
        client = Api(
            url=archivebox_url,
            username=username,
            password=password,
            token=token,
            api_key=api_key,
            verify=verify,
        )
        response = client.get_api_token(username=username, password=password)
        return response.json()

    @mcp.tool(
        exclude_args=[
            "archivebox_url",
            "username",
            "password",
            "token",
            "api_key",
            "verify",
        ],
        tags={"authentication"},
    )
    async def check_api_token(
        token: str = Field(
            description="The API token to validate",
        ),
        archivebox_url: str = Field(
            default=os.environ.get("ARCHIVEBOX_URL", None),
            description="The URL of the ArchiveBox instance (e.g., https://yourinstance.archivebox.com)",
        ),
        username: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_USERNAME", None),
            description="Username for authentication",
        ),
        password: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_PASSWORD", None),
            description="Password for authentication",
        ),
        token_param: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_TOKEN", None),
            description="Bearer token for authentication",
        ),
        api_key: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_API_KEY", None),
            description="API key for authentication",
        ),
        verify: Optional[bool] = Field(
            default=to_boolean(os.environ.get("ARCHIVEBOX_VERIFY", "True")),
            description="Whether to verify SSL certificates",
        ),
    ) -> dict:
        """
        Validate an API token to make sure it's valid and non-expired.
        """
        client = Api(
            url=archivebox_url,
            username=username,
            password=password,
            token=token_param,
            api_key=api_key,
            verify=verify,
        )
        response = client.check_api_token(token=token)
        return response.json()


def register_core_tools(mcp: FastMCP):
    @mcp.tool(
        exclude_args=[
            "archivebox_url",
            "username",
            "password",
            "token",
            "api_key",
            "verify",
        ],
        tags={"core"},
    )
    async def get_snapshots(
        id: Optional[str] = Field(None, description="Filter by snapshot ID"),
        abid: Optional[str] = Field(None, description="Filter by snapshot abid"),
        created_by_id: Optional[str] = Field(None, description="Filter by creator ID"),
        created_by_username: Optional[str] = Field(
            None, description="Filter by creator username"
        ),
        created_at__gte: Optional[str] = Field(
            None, description="Filter by creation date >= (ISO 8601)"
        ),
        created_at__lt: Optional[str] = Field(
            None, description="Filter by creation date < (ISO 8601)"
        ),
        created_at: Optional[str] = Field(
            None, description="Filter by exact creation date (ISO 8601)"
        ),
        modified_at: Optional[str] = Field(
            None, description="Filter by exact modification date (ISO 8601)"
        ),
        modified_at__gte: Optional[str] = Field(
            None, description="Filter by modification date >= (ISO 8601)"
        ),
        modified_at__lt: Optional[str] = Field(
            None, description="Filter by modification date < (ISO 8601)"
        ),
        search: Optional[str] = Field(
            None, description="Search across url, title, tags, id, abid, timestamp"
        ),
        url: Optional[str] = Field(None, description="Filter by URL (exact)"),
        tag: Optional[str] = Field(None, description="Filter by tag name (exact)"),
        title: Optional[str] = Field(None, description="Filter by title (icontains)"),
        timestamp: Optional[str] = Field(
            None, description="Filter by timestamp (startswith)"
        ),
        bookmarked_at__gte: Optional[str] = Field(
            None, description="Filter by bookmark date >= (ISO 8601)"
        ),
        bookmarked_at__lt: Optional[str] = Field(
            None, description="Filter by bookmark date < (ISO 8601)"
        ),
        with_archiveresults: bool = Field(
            False, description="Include archiveresults in response"
        ),
        limit: int = Field(10, description="Number of results to return"),
        offset: int = Field(0, description="Offset for pagination"),
        page: int = Field(0, description="Page number for pagination"),
        api_key_param: Optional[str] = Field(
            None, description="API key for QueryParamTokenAuth"
        ),
        archivebox_url: str = Field(
            default=os.environ.get("ARCHIVEBOX_URL", None),
            description="The URL of the ArchiveBox instance",
        ),
        username: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_USERNAME", None),
            description="Username for authentication",
        ),
        password: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_PASSWORD", None),
            description="Password for authentication",
        ),
        token: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_TOKEN", None),
            description="Bearer token for authentication",
        ),
        api_key: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_API_KEY", None),
            description="API key for authentication",
        ),
        verify: Optional[bool] = Field(
            default=to_boolean(os.environ.get("ARCHIVEBOX_VERIFY", "True")),
            description="Whether to verify SSL certificates",
        ),
    ) -> dict:
        """
        Retrieve list of snapshots.
        """
        client = Api(
            url=archivebox_url,
            username=username,
            password=password,
            token=token,
            api_key=api_key,
            verify=verify,
        )
        response = client.get_snapshots(
            id=id,
            abid=abid,
            created_by_id=created_by_id,
            created_by_username=created_by_username,
            created_at__gte=created_at__gte,
            created_at__lt=created_at__lt,
            created_at=created_at,
            modified_at=modified_at,
            modified_at__gte=modified_at__gte,
            modified_at__lt=modified_at__lt,
            search=search,
            url=url,
            tag=tag,
            title=title,
            timestamp=timestamp,
            bookmarked_at__gte=bookmarked_at__gte,
            bookmarked_at__lt=bookmarked_at__lt,
            with_archiveresults=with_archiveresults,
            limit=limit,
            offset=offset,
            page=page,
            api_key=api_key_param,
        )
        return response.json()

    @mcp.tool(
        exclude_args=[
            "archivebox_url",
            "username",
            "password",
            "token",
            "api_key",
            "verify",
        ],
        tags={"core"},
    )
    async def get_snapshot(
        snapshot_id: str = Field(
            description="The ID or abid of the snapshot",
        ),
        with_archiveresults: bool = Field(
            True, description="Whether to include archiveresults"
        ),
        archivebox_url: str = Field(
            default=os.environ.get("ARCHIVEBOX_URL", None),
            description="The URL of the ArchiveBox instance",
        ),
        username: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_USERNAME", None),
            description="Username for authentication",
        ),
        password: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_PASSWORD", None),
            description="Password for authentication",
        ),
        token: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_TOKEN", None),
            description="Bearer token for authentication",
        ),
        api_key: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_API_KEY", None),
            description="API key for authentication",
        ),
        verify: Optional[bool] = Field(
            default=to_boolean(os.environ.get("ARCHIVEBOX_VERIFY", "True")),
            description="Whether to verify SSL certificates",
        ),
    ) -> dict:
        """
        Get a specific Snapshot by abid or id.
        """
        client = Api(
            url=archivebox_url,
            username=username,
            password=password,
            token=token,
            api_key=api_key,
            verify=verify,
        )
        response = client.get_snapshot(
            snapshot_id=snapshot_id,
            with_archiveresults=with_archiveresults,
        )
        return response.json()

    @mcp.tool(
        exclude_args=[
            "archivebox_url",
            "username",
            "password",
            "token",
            "api_key",
            "verify",
        ],
        tags={"core"},
    )
    async def get_archiveresults(
        id: Optional[str] = Field(None, description="Filter by ID"),
        search: Optional[str] = Field(
            None,
            description="Search across snapshot url, title, tags, extractor, output, id",
        ),
        snapshot_id: Optional[str] = Field(None, description="Filter by snapshot ID"),
        snapshot_url: Optional[str] = Field(None, description="Filter by snapshot URL"),
        snapshot_tag: Optional[str] = Field(None, description="Filter by snapshot tag"),
        status: Optional[str] = Field(None, description="Filter by status"),
        output: Optional[str] = Field(None, description="Filter by output"),
        extractor: Optional[str] = Field(None, description="Filter by extractor"),
        cmd: Optional[str] = Field(None, description="Filter by command"),
        pwd: Optional[str] = Field(None, description="Filter by working directory"),
        cmd_version: Optional[str] = Field(
            None, description="Filter by command version"
        ),
        created_at: Optional[str] = Field(
            None, description="Filter by exact creation date (ISO 8601)"
        ),
        created_at__gte: Optional[str] = Field(
            None, description="Filter by creation date >= (ISO 8601)"
        ),
        created_at__lt: Optional[str] = Field(
            None, description="Filter by creation date < (ISO 8601)"
        ),
        limit: int = Field(10, description="Number of results to return"),
        offset: int = Field(0, description="Offset for pagination"),
        page: int = Field(0, description="Page number for pagination"),
        api_key_param: Optional[str] = Field(
            None, description="API key for QueryParamTokenAuth"
        ),
        archivebox_url: str = Field(
            default=os.environ.get("ARCHIVEBOX_URL", None),
            description="The URL of the ArchiveBox instance",
        ),
        username: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_USERNAME", None),
            description="Username for authentication",
        ),
        password: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_PASSWORD", None),
            description="Password for authentication",
        ),
        token: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_TOKEN", None),
            description="Bearer token for authentication",
        ),
        api_key: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_API_KEY", None),
            description="API key for authentication",
        ),
        verify: Optional[bool] = Field(
            default=to_boolean(os.environ.get("ARCHIVEBOX_VERIFY", "True")),
            description="Whether to verify SSL certificates",
        ),
    ) -> dict:
        """
        List all ArchiveResult entries matching these filters.
        """
        client = Api(
            url=archivebox_url,
            username=username,
            password=password,
            token=token,
            api_key=api_key,
            verify=verify,
        )
        response = client.get_archiveresults(
            id=id,
            search=search,
            snapshot_id=snapshot_id,
            snapshot_url=snapshot_url,
            snapshot_tag=snapshot_tag,
            status=status,
            output=output,
            extractor=extractor,
            cmd=cmd,
            pwd=pwd,
            cmd_version=cmd_version,
            created_at=created_at,
            created_at__gte=created_at__gte,
            created_at__lt=created_at__lt,
            limit=limit,
            offset=offset,
            page=page,
            api_key=api_key_param,
        )
        return response.json()

    @mcp.tool(
        exclude_args=[
            "archivebox_url",
            "username",
            "password",
            "token",
            "api_key",
            "verify",
        ],
        tags={"core"},
    )
    async def get_tag(
        tag_id: str = Field(
            description="The ID or abid of the tag",
        ),
        with_snapshots: bool = Field(True, description="Whether to include snapshots"),
        archivebox_url: str = Field(
            default=os.environ.get("ARCHIVEBOX_URL", None),
            description="The URL of the ArchiveBox instance",
        ),
        username: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_USERNAME", None),
            description="Username for authentication",
        ),
        password: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_PASSWORD", None),
            description="Password for authentication",
        ),
        token: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_TOKEN", None),
            description="Bearer token for authentication",
        ),
        api_key: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_API_KEY", None),
            description="API key for authentication",
        ),
        verify: Optional[bool] = Field(
            default=to_boolean(os.environ.get("ARCHIVEBOX_VERIFY", "True")),
            description="Whether to verify SSL certificates",
        ),
    ) -> dict:
        """
        Get a specific Tag by id or abid.
        """
        client = Api(
            url=archivebox_url,
            username=username,
            password=password,
            token=token,
            api_key=api_key,
            verify=verify,
        )
        response = client.get_tag(
            tag_id=tag_id,
            with_snapshots=with_snapshots,
        )
        return response.json()

    @mcp.tool(
        exclude_args=[
            "archivebox_url",
            "username",
            "password",
            "token",
            "api_key",
            "verify",
        ],
        tags={"core"},
    )
    async def get_any(
        abid: str = Field(
            description="The abid of the Snapshot, ArchiveResult, or Tag",
        ),
        archivebox_url: str = Field(
            default=os.environ.get("ARCHIVEBOX_URL", None),
            description="The URL of the ArchiveBox instance",
        ),
        username: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_USERNAME", None),
            description="Username for authentication",
        ),
        password: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_PASSWORD", None),
            description="Password for authentication",
        ),
        token: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_TOKEN", None),
            description="Bearer token for authentication",
        ),
        api_key: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_API_KEY", None),
            description="API key for authentication",
        ),
        verify: Optional[bool] = Field(
            default=to_boolean(os.environ.get("ARCHIVEBOX_VERIFY", "True")),
            description="Whether to verify SSL certificates",
        ),
    ) -> dict:
        """
        Get a specific Snapshot, ArchiveResult, or Tag by abid.
        """
        client = Api(
            url=archivebox_url,
            username=username,
            password=password,
            token=token,
            api_key=api_key,
            verify=verify,
        )
        response = client.get_any(abid=abid)
        return response.json()


def register_cli_tools(mcp: FastMCP):
    @mcp.tool(
        exclude_args=[
            "archivebox_url",
            "username",
            "password",
            "token",
            "api_key",
            "verify",
        ],
        tags={"cli"},
    )
    async def cli_add(
        urls: List[str] = Field(
            description="List of URLs to archive",
        ),
        tag: str = Field("", description="Comma-separated tags"),
        depth: int = Field(0, description="Crawl depth"),
        update: bool = Field(False, description="Update existing snapshots"),
        update_all: bool = Field(False, description="Update all snapshots"),
        index_only: bool = Field(False, description="Index without archiving"),
        overwrite: bool = Field(False, description="Overwrite existing files"),
        init: bool = Field(False, description="Initialize collection if needed"),
        extractors: str = Field(
            "", description="Comma-separated list of extractors to use"
        ),
        parser: str = Field("auto", description="Parser type"),
        extra_data: Optional[Dict] = Field(
            None, description="Additional parameters as a dictionary"
        ),
        archivebox_url: str = Field(
            default=os.environ.get("ARCHIVEBOX_URL", None),
            description="The URL of the ArchiveBox instance",
        ),
        username: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_USERNAME", None),
            description="Username for authentication",
        ),
        password: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_PASSWORD", None),
            description="Password for authentication",
        ),
        token: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_TOKEN", None),
            description="Bearer token for authentication",
        ),
        api_key: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_API_KEY", None),
            description="API key for authentication",
        ),
        verify: Optional[bool] = Field(
            default=to_boolean(os.environ.get("ARCHIVEBOX_VERIFY", "True")),
            description="Whether to verify SSL certificates",
        ),
        ctx: Context = None,
    ) -> dict:
        """
        Execute archivebox add command.
        """
        if ctx:
            # Elicitation not supported by some clients, skipping confirmation
            pass

        client = Api(
            url=archivebox_url,
            username=username,
            password=password,
            token=token,
            api_key=api_key,
            verify=verify,
        )
        response = client.cli_add(
            urls=urls,
            tag=tag,
            depth=depth,
            update=update,
            update_all=update_all,
            index_only=index_only,
            overwrite=overwrite,
            init=init,
            extractors=extractors,
            parser=parser,
            extra_data=extra_data,
        )
        return response.json()

    @mcp.tool(
        exclude_args=[
            "archivebox_url",
            "username",
            "password",
            "token",
            "api_key",
            "verify",
        ],
        tags={"cli"},
    )
    async def cli_update(
        resume: Optional[float] = Field(0, description="Resume from timestamp"),
        only_new: bool = Field(True, description="Update only new snapshots"),
        index_only: bool = Field(False, description="Index without archiving"),
        overwrite: bool = Field(False, description="Overwrite existing files"),
        after: Optional[float] = Field(
            0, description="Filter snapshots after timestamp"
        ),
        before: Optional[float] = Field(
            999999999999999, description="Filter snapshots before timestamp"
        ),
        status: Optional[str] = Field("unarchived", description="Filter by status"),
        filter_type: Optional[str] = Field("substring", description="Filter type"),
        filter_patterns: Optional[List[str]] = Field(
            None, description="List of filter patterns"
        ),
        extractors: Optional[str] = Field(
            "", description="Comma-separated list of extractors"
        ),
        extra_data: Optional[Dict] = Field(
            None, description="Additional parameters as a dictionary"
        ),
        archivebox_url: str = Field(
            default=os.environ.get("ARCHIVEBOX_URL", None),
            description="The URL of the ArchiveBox instance",
        ),
        username: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_USERNAME", None),
            description="Username for authentication",
        ),
        password: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_PASSWORD", None),
            description="Password for authentication",
        ),
        token: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_TOKEN", None),
            description="Bearer token for authentication",
        ),
        api_key: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_API_KEY", None),
            description="API key for authentication",
        ),
        verify: Optional[bool] = Field(
            default=to_boolean(os.environ.get("ARCHIVEBOX_VERIFY", "True")),
            description="Whether to verify SSL certificates",
        ),
        ctx: Context = None,
    ) -> dict:
        """
        Execute archivebox update command.
        """
        if ctx:
            # Elicitation not supported by some clients, skipping confirmation
            pass

        client = Api(
            url=archivebox_url,
            username=username,
            password=password,
            token=token,
            api_key=api_key,
            verify=verify,
        )
        response = client.cli_update(
            resume=resume,
            only_new=only_new,
            index_only=index_only,
            overwrite=overwrite,
            after=after,
            before=before,
            status=status,
            filter_type=filter_type,
            filter_patterns=filter_patterns,
            extractors=extractors,
            extra_data=extra_data,
        )
        return response.json()

    @mcp.tool(
        exclude_args=[
            "archivebox_url",
            "username",
            "password",
            "token",
            "api_key",
            "verify",
        ],
        tags={"cli"},
    )
    async def cli_schedule(
        import_path: Optional[str] = Field(None, description="Path to import file"),
        add: bool = Field(False, description="Enable adding new URLs"),
        every: Optional[str] = Field(
            None, description="Schedule frequency (e.g., 'daily')"
        ),
        tag: str = Field("", description="Comma-separated tags"),
        depth: int = Field(0, description="Crawl depth"),
        overwrite: bool = Field(False, description="Overwrite existing files"),
        update: bool = Field(False, description="Update existing snapshots"),
        clear: bool = Field(False, description="Clear existing schedules"),
        extra_data: Optional[Dict] = Field(
            None, description="Additional parameters as a dictionary"
        ),
        archivebox_url: str = Field(
            default=os.environ.get("ARCHIVEBOX_URL", None),
            description="The URL of the ArchiveBox instance",
        ),
        username: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_USERNAME", None),
            description="Username for authentication",
        ),
        password: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_PASSWORD", None),
            description="Password for authentication",
        ),
        token: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_TOKEN", None),
            description="Bearer token for authentication",
        ),
        api_key: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_API_KEY", None),
            description="API key for authentication",
        ),
        verify: Optional[bool] = Field(
            default=to_boolean(os.environ.get("ARCHIVEBOX_VERIFY", "True")),
            description="Whether to verify SSL certificates",
        ),
    ) -> dict:
        """
        Execute archivebox schedule command.
        """
        client = Api(
            url=archivebox_url,
            username=username,
            password=password,
            token=token,
            api_key=api_key,
            verify=verify,
        )
        response = client.cli_schedule(
            import_path=import_path,
            add=add,
            every=every,
            tag=tag,
            depth=depth,
            overwrite=overwrite,
            update=update,
            clear=clear,
            extra_data=extra_data,
        )
        return response.json()

    @mcp.tool(
        exclude_args=[
            "archivebox_url",
            "username",
            "password",
            "token",
            "api_key",
            "verify",
        ],
        tags={"cli"},
    )
    async def cli_list(
        filter_patterns: Optional[List[str]] = Field(
            None, description="List of filter patterns"
        ),
        filter_type: str = Field("substring", description="Filter type"),
        status: Optional[str] = Field("indexed", description="Filter by status"),
        after: Optional[float] = Field(
            0, description="Filter snapshots after timestamp"
        ),
        before: Optional[float] = Field(
            999999999999999, description="Filter snapshots before timestamp"
        ),
        sort: str = Field("bookmarked_at", description="Sort field"),
        as_json: bool = Field(True, description="Output as JSON"),
        as_html: bool = Field(False, description="Output as HTML"),
        as_csv: Union[str, bool] = Field(
            "timestamp,url", description="Output as CSV or fields to include"
        ),
        with_headers: bool = Field(False, description="Include headers in output"),
        extra_data: Optional[Dict] = Field(
            None, description="Additional parameters as a dictionary"
        ),
        archivebox_url: str = Field(
            default=os.environ.get("ARCHIVEBOX_URL", None),
            description="The URL of the ArchiveBox instance",
        ),
        username: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_USERNAME", None),
            description="Username for authentication",
        ),
        password: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_PASSWORD", None),
            description="Password for authentication",
        ),
        token: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_TOKEN", None),
            description="Bearer token for authentication",
        ),
        api_key: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_API_KEY", None),
            description="API key for authentication",
        ),
        verify: Optional[bool] = Field(
            default=to_boolean(os.environ.get("ARCHIVEBOX_VERIFY", "True")),
            description="Whether to verify SSL certificates",
        ),
    ) -> dict:
        """
        Execute archivebox list command.
        """
        client = Api(
            url=archivebox_url,
            username=username,
            password=password,
            token=token,
            api_key=api_key,
            verify=verify,
        )
        response = client.cli_list(
            filter_patterns=filter_patterns,
            filter_type=filter_type,
            status=status,
            after=after,
            before=before,
            sort=sort,
            as_json=as_json,
            as_html=as_html,
            as_csv=as_csv,
            with_headers=with_headers,
            extra_data=extra_data,
        )
        return response.json()

    @mcp.tool(
        exclude_args=[
            "archivebox_url",
            "username",
            "password",
            "token",
            "api_key",
            "verify",
        ],
        tags={"cli"},
    )
    async def cli_remove(
        delete: bool = Field(True, description="Delete matching snapshots"),
        after: Optional[float] = Field(
            0, description="Filter snapshots after timestamp"
        ),
        before: Optional[float] = Field(
            999999999999999, description="Filter snapshots before timestamp"
        ),
        filter_type: str = Field("exact", description="Filter type"),
        filter_patterns: Optional[List[str]] = Field(
            None, description="List of filter patterns"
        ),
        extra_data: Optional[Dict] = Field(
            None, description="Additional parameters as a dictionary"
        ),
        archivebox_url: str = Field(
            default=os.environ.get("ARCHIVEBOX_URL", None),
            description="The URL of the ArchiveBox instance",
        ),
        username: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_USERNAME", None),
            description="Username for authentication",
        ),
        password: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_PASSWORD", None),
            description="Password for authentication",
        ),
        token: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_TOKEN", None),
            description="Bearer token for authentication",
        ),
        api_key: Optional[str] = Field(
            default=os.environ.get("ARCHIVEBOX_API_KEY", None),
            description="API key for authentication",
        ),
        verify: Optional[bool] = Field(
            default=to_boolean(os.environ.get("ARCHIVEBOX_VERIFY", "True")),
            description="Whether to verify SSL certificates",
        ),
        ctx: Context = None,
    ) -> dict:
        """
        Execute archivebox remove command.
        """
        if ctx:
            # Elicitation not supported by some clients, skipping confirmation
            pass

        client = Api(
            url=archivebox_url,
            username=username,
            password=password,
            token=token,
            api_key=api_key,
            verify=verify,
        )
        response = client.cli_remove(
            delete=delete,
            after=after,
            before=before,
            filter_type=filter_type,
            filter_patterns=filter_patterns,
            extra_data=extra_data,
        )
        return response.json()


def register_resources(mcp: FastMCP):
    @mcp.resource("data://instance_config")
    async def get_instance_config() -> dict:
        """
        Provides the current ArchiveBox instance configuration.
        """
        return {
            "url": os.environ.get("ARCHIVEBOX_URL"),
            "verify": to_boolean(os.environ.get("ARCHIVEBOX_VERIFY", "True")),
        }


def register_prompts(mcp: FastMCP):
    @mcp.prompt
    def add_url_prompt(
        url: str,
        tag: str = "",
        depth: int = 0,
        extractors: str = "",
    ) -> str:
        """
        Generates a prompt for adding a new URL to ArchiveBox.
        """
        return f"Add the URL '{url}' to ArchiveBox. Tags: '{tag}', Depth: {depth}, Extractors: '{extractors}'. Use the `cli_add` tool."

    @mcp.prompt
    def search_snapshots_prompt(
        query: str,
        limit: int = 10,
        tag: str = "",
    ) -> str:
        """
        Generates a prompt for searching snapshots in ArchiveBox.
        """
        return f"Search for snapshots matching '{query}' in ArchiveBox. Limit: {limit}, Tag: '{tag}'. Use the `get_snapshots` tool with the `search` parameter."

    @mcp.prompt
    def get_snapshot_details_prompt(
        id: str,
    ) -> str:
        """
        Generates a prompt for retrieving details of a specific snapshot.
        """
        return f"Get details for the snapshot with ID '{id}'. Use the `get_snapshot` tool (or `get_any` if unsure of the ID type)."

    @mcp.prompt
    def list_recent_snapshots_prompt(
        limit: int = 10,
    ) -> str:
        """
        Generates a prompt for listing the most recent snapshots.
        """
        return f"List the {limit} most recently created snapshots. Use the `get_snapshots` tool sorted by creation date."

    @mcp.prompt
    def update_snapshots_prompt(
        filter_patterns: str = "",
        only_new: bool = True,
    ) -> str:
        """
        Generates a prompt for updating existing snapshots.
        """
        return f"Update existing snapshots. Filter patterns: '{filter_patterns}', Only new: {only_new}. Use the `cli_update` tool."

    @mcp.prompt
    def schedule_archiving_prompt(
        url: str = "",
        tag: str = "",
        every: str = "day",
    ) -> str:
        """
        Generates a prompt for scheduling a recurring archiving job.
        """
        return f"Schedule a recurring archiving job every '{every}'. URL: '{url}', Tag: '{tag}'. Use the `cli_schedule` tool."

    @mcp.prompt
    def remove_snapshots_prompt(
        filter_patterns: str,
        before: float = 0,
    ) -> str:
        """
        Generates a prompt for removing snapshots.
        """
        return f"Remove snapshots matching patterns '{filter_patterns}'. Before timestamp: {before}. Use the `cli_remove` tool."

    @mcp.prompt
    def list_archiveresults_prompt(
        snapshot_id: str = "",
        status: str = "",
        extractor: str = "",
    ) -> str:
        """
        Generates a prompt for listing specific archive results.
        """
        return f"List archive results. Snapshot ID: '{snapshot_id}', Status: '{status}', Extractor: '{extractor}'. Use the `get_archiveresults` tool."

    @mcp.prompt
    def get_tag_details_prompt(
        tag_id: str,
    ) -> str:
        """
        Generates a prompt for getting details about a tag.
        """
        return f"Get details for the tag with ID '{tag_id}'. Use the `get_tag` tool."


def get_archivebox_client() -> Api:
    """
    Creates and returns an ArchiveBox API client using environment variables.
    """
    archivebox_url = os.environ.get("ARCHIVEBOX_URL")
    username = os.environ.get("ARCHIVEBOX_USERNAME")
    password = os.environ.get("ARCHIVEBOX_PASSWORD")
    token = os.environ.get("ARCHIVEBOX_TOKEN")
    api_key = os.environ.get("ARCHIVEBOX_API_KEY")
    verify = to_boolean(os.environ.get("ARCHIVEBOX_VERIFY", "True"))

    if not archivebox_url:
        raise ResourceError("ArchiveBox URL not configured")

    return Api(
        url=archivebox_url,
        username=username,
        password=password,
        token=token,
        api_key=api_key,
        verify=verify,
    )


def mcp_server():
    load_dotenv(find_dotenv())

    args, mcp, middlewares = create_mcp_server(
        name="ArchiveBox",
        version=__version__,
        instructions="ArchiveBox MCP Server - Manage snapshot archival, scheduling, and CLI commands.",
    )

    DEFAULT_MISCTOOL = to_boolean(os.getenv("MISCTOOL", "True"))
    if DEFAULT_MISCTOOL:
        register_misc_tools(mcp)
    DEFAULT_AUTHENTICATIONTOOL = to_boolean(os.getenv("AUTHENTICATIONTOOL", "True"))
    if DEFAULT_AUTHENTICATIONTOOL:
        register_authentication_tools(mcp)
    DEFAULT_CORETOOL = to_boolean(os.getenv("CORETOOL", "True"))
    if DEFAULT_CORETOOL:
        register_core_tools(mcp)
    DEFAULT_CLITOOL = to_boolean(os.getenv("CLITOOL", "True"))
    if DEFAULT_CLITOOL:
        register_cli_tools(mcp)
    register_prompts(mcp)
    register_resources(mcp)

    for mw in middlewares:
        mcp.add_middleware(mw)

    print(f"ArchiveBox MCP v{__version__}")
    print("\nStarting ArchiveBox MCP Server")
    print(f"  Transport: {args.transport.upper()}")
    print(f"  Auth: {args.auth_type}")
    print(f"  Delegation: {'ON' if config['enable_delegation'] else 'OFF'}")
    print(f"  Eunomia: {args.eunomia_type}")

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
