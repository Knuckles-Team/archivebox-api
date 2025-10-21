#!/usr/bin/python
# coding: utf-8

import os
import argparse
import sys
import logging
from typing import Optional, List, Dict, Union
from pydantic import Field
from fastmcp import FastMCP
from fastmcp.server.auth.oidc_proxy import OIDCProxy
from fastmcp.server.auth import OAuthProxy, RemoteAuthProvider
from fastmcp.server.auth.providers.jwt import JWTVerifier, StaticTokenVerifier
from fastmcp.server.middleware.logging import LoggingMiddleware
from fastmcp.server.middleware.timing import TimingMiddleware
from fastmcp.server.middleware.rate_limiting import RateLimitingMiddleware
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from fastmcp.exceptions import ResourceError
from archivebox_api.archivebox_api import Api

mcp = FastMCP("ArchiveBox")


def to_boolean(string: Union[str, bool] = None) -> bool:
    if isinstance(string, bool):
        return string
    if not string:
        return False
    normalized = str(string).strip().lower()
    true_values = {"t", "true", "y", "yes", "1"}
    false_values = {"f", "false", "n", "no", "0"}
    if normalized in true_values:
        return True
    elif normalized in false_values:
        return False
    else:
        raise ValueError(f"Cannot convert '{string}' to boolean")


# Authentication Tools
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
def get_api_token(
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
def check_api_token(
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


# Core Model Tools
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
def get_snapshots(
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
def get_snapshot(
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
def get_archiveresults(
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
    cmd_version: Optional[str] = Field(None, description="Filter by command version"),
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
def get_tag(
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
def get_any(
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


# CLI Tools
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
def cli_add(
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
) -> dict:
    """
    Execute archivebox add command.
    """
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
def cli_update(
    resume: Optional[float] = Field(0, description="Resume from timestamp"),
    only_new: bool = Field(True, description="Update only new snapshots"),
    index_only: bool = Field(False, description="Index without archiving"),
    overwrite: bool = Field(False, description="Overwrite existing files"),
    after: Optional[float] = Field(0, description="Filter snapshots after timestamp"),
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
) -> dict:
    """
    Execute archivebox update command.
    """
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
def cli_schedule(
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
def cli_list(
    filter_patterns: Optional[List[str]] = Field(
        None, description="List of filter patterns"
    ),
    filter_type: str = Field("substring", description="Filter type"),
    status: Optional[str] = Field("indexed", description="Filter by status"),
    after: Optional[float] = Field(0, description="Filter snapshots after timestamp"),
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
def cli_remove(
    delete: bool = Field(True, description="Delete matching snapshots"),
    after: Optional[float] = Field(0, description="Filter snapshots after timestamp"),
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
) -> dict:
    """
    Execute archivebox remove command.
    """
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


@mcp.resource("data://instance_config")
def get_instance_config() -> dict:
    """
    Provides the current ArchiveBox instance configuration.
    """
    return {
        "url": os.environ.get("ARCHIVEBOX_URL"),
        "verify": to_boolean(os.environ.get("ARCHIVEBOX_VERIFY", "True")),
    }


# Prompts
@mcp.prompt
def cli_add_prompt(
    urls: List[str],
    tag: str = "",
    depth: int = 0,
) -> str:
    """
    Generates a prompt for executing archivebox add command.
    """
    return f"Add new URLs to ArchiveBox: {urls}, with tags: '{tag}', depth: {depth}. Use the cli_add tool."


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


def archivebox_mcp():
    parser = argparse.ArgumentParser(description="ArchiveBox MCP Runner")
    parser.add_argument(
        "-t",
        "--transport",
        default="stdio",
        choices=["stdio", "http", "sse"],
        help="Transport method: 'stdio', 'http', or 'sse' [legacy] (default: stdio)",
    )
    parser.add_argument(
        "-s",
        "--host",
        default="0.0.0.0",
        help="Host address for HTTP transport (default: 0.0.0.0)",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8000,
        help="Port number for HTTP transport (default: 8000)",
    )
    parser.add_argument(
        "--auth-type",
        default="none",
        choices=["none", "static", "jwt", "oauth-proxy", "oidc-proxy", "remote-oauth"],
        help="Authentication type for MCP server: 'none' (disabled), 'static' (internal), 'jwt' (external token verification), 'oauth-proxy', 'oidc-proxy', 'remote-oauth' (external) (default: none)",
    )
    # JWT/Token params
    parser.add_argument(
        "--token-jwks-uri", default=None, help="JWKS URI for JWT verification"
    )
    parser.add_argument(
        "--token-issuer", default=None, help="Issuer for JWT verification"
    )
    parser.add_argument(
        "--token-audience", default=None, help="Audience for JWT verification"
    )
    # OAuth Proxy params
    parser.add_argument(
        "--oauth-upstream-auth-endpoint",
        default=None,
        help="Upstream authorization endpoint for OAuth Proxy",
    )
    parser.add_argument(
        "--oauth-upstream-token-endpoint",
        default=None,
        help="Upstream token endpoint for OAuth Proxy",
    )
    parser.add_argument(
        "--oauth-upstream-client-id",
        default=None,
        help="Upstream client ID for OAuth Proxy",
    )
    parser.add_argument(
        "--oauth-upstream-client-secret",
        default=None,
        help="Upstream client secret for OAuth Proxy",
    )
    parser.add_argument(
        "--oauth-base-url", default=None, help="Base URL for OAuth Proxy"
    )
    # OIDC Proxy params
    parser.add_argument(
        "--oidc-config-url", default=None, help="OIDC configuration URL"
    )
    parser.add_argument("--oidc-client-id", default=None, help="OIDC client ID")
    parser.add_argument("--oidc-client-secret", default=None, help="OIDC client secret")
    parser.add_argument("--oidc-base-url", default=None, help="Base URL for OIDC Proxy")
    # Remote OAuth params
    parser.add_argument(
        "--remote-auth-servers",
        default=None,
        help="Comma-separated list of authorization servers for Remote OAuth",
    )
    parser.add_argument(
        "--remote-base-url", default=None, help="Base URL for Remote OAuth"
    )
    # Common
    parser.add_argument(
        "--allowed-client-redirect-uris",
        default=None,
        help="Comma-separated list of allowed client redirect URIs",
    )
    # Eunomia params
    parser.add_argument(
        "--eunomia-type",
        default="none",
        choices=["none", "embedded", "remote"],
        help="Eunomia authorization type: 'none' (disabled), 'embedded' (built-in), 'remote' (external) (default: none)",
    )
    parser.add_argument(
        "--eunomia-policy-file",
        default="mcp_policies.json",
        help="Policy file for embedded Eunomia (default: mcp_policies.json)",
    )
    parser.add_argument(
        "--eunomia-remote-url", default=None, help="URL for remote Eunomia server"
    )

    args = parser.parse_args()

    if args.port < 0 or args.port > 65535:
        print(f"Error: Port {args.port} is out of valid range (0-65535).")
        sys.exit(1)

    # Set auth based on type
    auth = None
    allowed_uris = (
        args.allowed_client_redirect_uris.split(",")
        if args.allowed_client_redirect_uris
        else None
    )

    if args.auth_type == "none":
        auth = None
    elif args.auth_type == "static":
        # Internal static tokens (hardcoded example)
        auth = StaticTokenVerifier(
            tokens={
                "test-token": {"client_id": "test-user", "scopes": ["read", "write"]},
                "admin-token": {"client_id": "admin", "scopes": ["admin"]},
            }
        )
    elif args.auth_type == "jwt":
        if not (args.token_jwks_uri and args.token_issuer and args.token_audience):
            print(
                "Error: jwt requires --token-jwks-uri, --token-issuer, --token-audience"
            )
            sys.exit(1)
        auth = JWTVerifier(
            jwks_uri=args.token_jwks_uri,
            issuer=args.token_issuer,
            audience=args.token_audience,
        )
    elif args.auth_type == "oauth-proxy":
        if not (
            args.oauth_upstream_auth_endpoint
            and args.oauth_upstream_token_endpoint
            and args.oauth_upstream_client_id
            and args.oauth_upstream_client_secret
            and args.oauth_base_url
            and args.token_jwks_uri
            and args.token_issuer
            and args.token_audience
        ):
            print(
                "Error: oauth-proxy requires --oauth-upstream-auth-endpoint, --oauth-upstream-token-endpoint, --oauth-upstream-client-id, --oauth-upstream-client-secret, --oauth-base-url, --token-jwks-uri, --token-issuer, --token-audience"
            )
            sys.exit(1)
        token_verifier = JWTVerifier(
            jwks_uri=args.token_jwks_uri,
            issuer=args.token_issuer,
            audience=args.token_audience,
        )
        auth = OAuthProxy(
            upstream_authorization_endpoint=args.oauth_upstream_auth_endpoint,
            upstream_token_endpoint=args.oauth_upstream_token_endpoint,
            upstream_client_id=args.oauth_upstream_client_id,
            upstream_client_secret=args.oauth_upstream_client_secret,
            token_verifier=token_verifier,
            base_url=args.oauth_base_url,
            allowed_client_redirect_uris=allowed_uris,
        )
    elif args.auth_type == "oidc-proxy":
        if not (
            args.oidc_config_url
            and args.oidc_client_id
            and args.oidc_client_secret
            and args.oidc_base_url
        ):
            print(
                "Error: oidc-proxy requires --oidc-config-url, --oidc-client-id, --oidc-client-secret, --oidc-base-url"
            )
            sys.exit(1)
        auth = OIDCProxy(
            config_url=args.oidc_config_url,
            client_id=args.oidc_client_id,
            client_secret=args.oidc_client_secret,
            base_url=args.oidc_base_url,
            allowed_client_redirect_uris=allowed_uris,
        )
    elif args.auth_type == "remote-oauth":
        if not (
            args.remote_auth_servers
            and args.remote_base_url
            and args.token_jwks_uri
            and args.token_issuer
            and args.token_audience
        ):
            print(
                "Error: remote-oauth requires --remote-auth-servers, --remote-base-url, --token-jwks-uri, --token-issuer, --token-audience"
            )
            sys.exit(1)
        auth_servers = [url.strip() for url in args.remote_auth_servers.split(",")]
        token_verifier = JWTVerifier(
            jwks_uri=args.token_jwks_uri,
            issuer=args.token_issuer,
            audience=args.token_audience,
        )
        auth = RemoteAuthProvider(
            token_verifier=token_verifier,
            authorization_servers=auth_servers,
            base_url=args.remote_base_url,
        )
    mcp.auth = auth
    if args.eunomia_type != "none":
        from eunomia_mcp import create_eunomia_middleware

        if args.eunomia_type == "embedded":
            if not args.eunomia_policy_file:
                print("Error: embedded Eunomia requires --eunomia-policy-file")
                sys.exit(1)
            middleware = create_eunomia_middleware(policy_file=args.eunomia_policy_file)
            mcp.add_middleware(middleware)
        elif args.eunomia_type == "remote":
            if not args.eunomia_remote_url:
                print("Error: remote Eunomia requires --eunomia-remote-url")
                sys.exit(1)
            middleware = create_eunomia_middleware(
                use_remote_eunomia=args.eunomia_remote_url
            )
            mcp.add_middleware(middleware)

    mcp.add_middleware(
        ErrorHandlingMiddleware(include_traceback=True, transform_errors=True)
    )
    mcp.add_middleware(
        RateLimitingMiddleware(max_requests_per_second=10.0, burst_capacity=20)
    )
    mcp.add_middleware(TimingMiddleware())
    mcp.add_middleware(LoggingMiddleware())

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    elif args.transport == "http":
        mcp.run(transport="http", host=args.host, port=args.port)
    elif args.transport == "sse":
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        logger = logging.getLogger("ArchiveBox")
        logger.error("Transport not supported")
        sys.exit(1)


if __name__ == "__main__":
    archivebox_mcp()
