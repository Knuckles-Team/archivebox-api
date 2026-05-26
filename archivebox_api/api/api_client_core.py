from typing import Any

import requests
from agent_utilities.core.decorators import require_auth
from agent_utilities.core.exceptions import (
    ParameterError,
)
from pydantic import ValidationError

from archivebox_api.api.api_client_base import BaseApiClient


class Api(BaseApiClient):
    @require_auth
    def get_snapshots(
        self,
        id: str | None = None,
        abid: str | None = None,
        created_by_id: str | None = None,
        created_by_username: str | None = None,
        created_at__gte: str | None = None,
        created_at__lt: str | None = None,
        created_at: str | None = None,
        modified_at: str | None = None,
        modified_at__gte: str | None = None,
        modified_at__lt: str | None = None,
        search: str | None = None,
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
    ) -> requests.Response:
        """
        Retrieve list of snapshots

        Args:
            id: Filter by snapshot ID.
            abid: Filter by snapshot abid.
            created_by_id: Filter by creator ID.
            created_by_username: Filter by creator username.
            created_at__gte: Filter by creation date >= (ISO 8601 format).
            created_at__lt: Filter by creation date < (ISO 8601 format).
            created_at: Filter by exact creation date (ISO 8601 format).
            modified_at: Filter by exact modification date (ISO 8601 format).
            modified_at__gte: Filter by modification date >= (ISO 8601 format).
            modified_at__lt: Filter by modification date < (ISO 8601 format).
            search: Search across url, title, tags, id, abid, timestamp.
            url: Filter by URL (exact).
            tag: Filter by tag name (exact).
            title: Filter by title (icontains).
            timestamp: Filter by timestamp (startswith).
            bookmarked_at__gte: Filter by bookmark date >= (ISO 8601 format).
            bookmarked_at__lt: Filter by bookmark date < (ISO 8601 format).
            with_archiveresults: Include archiveresults in response.
            limit: Number of results to return.
            offset: Offset for pagination.
            page: Page number for pagination.
            api_key: API key for QueryParamTokenAuth (optional).

        Returns:
            Response: The response object from the GET request.

        Raises:
            ParameterError: If the provided parameters are invalid.
        """
        params = {
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
        }
        params = {k: v for k, v in params.items() if v is not None}
        if api_key:
            params["api_key"] = api_key
        try:
            response = self._session.get(
                url=f"{self.url}/api/v1/core/snapshots",
                params=params,
                headers=self.headers,
                verify=self.verify,
            )
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}") from e
        return response

    @require_auth
    def get_snapshot(
        self, snapshot_id: str, with_archiveresults: bool = True
    ) -> requests.Response:
        """
        Get a specific Snapshot by abid or id

        Args:
            snapshot_id: The ID or abid of the snapshot.
            with_archiveresults: Whether to include archiveresults.

        Returns:
            Response: The response object from the GET request.

        Raises:
            ParameterError: If the provided parameters are invalid.
        """
        try:
            response = self._session.get(
                url=f"{self.url}/api/v1/core/snapshot/{snapshot_id}",
                params={"with_archiveresults": with_archiveresults},
                headers=self.headers,
                verify=self.verify,
            )
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}") from e
        return response

    @require_auth
    def get_archiveresults(
        self,
        id: str | None = None,
        search: str | None = None,
        snapshot_id: str | None = None,
        snapshot_url: str | None = None,
        snapshot_tag: str | None = None,
        status: str | None = None,
        output: str | None = None,
        extractor: str | None = None,
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
    ) -> requests.Response:
        """
        List all ArchiveResult entries matching these filters

        Args:
            id: Filter by ID.
            search: Search across snapshot url, title, tags, extractor, output, id.
            snapshot_id: Filter by snapshot ID.
            snapshot_url: Filter by snapshot URL.
            snapshot_tag: Filter by snapshot tag.
            status: Filter by status.
            output: Filter by output.
            extractor: Filter by extractor.
            cmd: Filter by command.
            pwd: Filter by working directory.
            cmd_version: Filter by command version.
            created_at: Filter by exact creation date (ISO 8601 format).
            created_at__gte: Filter by creation date >= (ISO 8601 format).
            created_at__lt: Filter by creation date < (ISO 8601 format).
            limit: Number of results to return.
            offset: Offset for pagination.
            page: Page number for pagination.
            api_key: API key for QueryParamTokenAuth (optional).

        Returns:
            Response: The response object from the GET request.

        Raises:
            ParameterError: If the provided parameters are invalid.
        """
        params = {
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
        }
        params = {k: v for k, v in params.items() if v is not None}
        if api_key:
            params["api_key"] = api_key
        try:
            response = self._session.get(
                url=f"{self.url}/api/v1/core/archiveresults",
                params=params,
                headers=self.headers,
                verify=self.verify,
            )
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}") from e
        return response

    @require_auth
    def get_archiveresult(self, archiveresult_id: str) -> requests.Response:
        """
        Get a specific ArchiveResult by id or abid

        Args:
            archiveresult_id: The ID or abid of the ArchiveResult.

        Returns:
            Response: The response object from the GET request.

        Raises:
            ParameterError: If the provided parameters are invalid.
        """
        try:
            response = self._session.get(
                url=f"{self.url}/api/v1/core/archiveresult/{archiveresult_id}",
                headers=self.headers,
                verify=self.verify,
            )
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}") from e
        return response

    @require_auth
    def get_tags(
        self,
        limit: int = 200,
        offset: int = 0,
        page: int = 0,
        api_key: str | None = None,
    ) -> requests.Response:
        """
        Retrieve list of tags

        Args:
            limit: Number of results to return.
            offset: Offset for pagination.
            page: Page number for pagination.
            api_key: API key for QueryParamTokenAuth (optional).

        Returns:
            Response: The response object from the GET request.

        Raises:
            ParameterError: If the provided parameters are invalid.
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset, "page": page}
        params = {k: v for k, v in params.items() if v is not None}
        if api_key:
            params["api_key"] = api_key
        try:
            response = self._session.get(
                url=f"{self.url}/api/v1/core/tags",
                params=params,
                headers=self.headers,
                verify=self.verify,
            )
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}") from e
        return response

    @require_auth
    def get_tag(self, tag_id: str, with_snapshots: bool = True) -> requests.Response:
        """
        Get a specific Tag by id or abid

        Args:
            tag_id: The ID or abid of the tag.
            with_snapshots: Whether to include snapshots.

        Returns:
            Response: The response object from the GET request.

        Raises:
            ParameterError: If the provided parameters are invalid.
        """
        try:
            response = self._session.get(
                url=f"{self.url}/api/v1/core/tag/{tag_id}",
                params={"with_snapshots": with_snapshots},
                headers=self.headers,
                verify=self.verify,
            )
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}") from e
        return response

    @require_auth
    def get_any(self, abid: str) -> requests.Response:
        """
        Get a specific Snapshot, ArchiveResult, or Tag by abid

        Args:
            abid: The abid of the Snapshot, ArchiveResult, or Tag.

        Returns:
            Response: The response object from the GET request.

        Raises:
            ParameterError: If the provided parameters are invalid.
        """
        try:
            response = self._session.get(
                url=f"{self.url}/api/v1/core/any/{abid}",
                headers=self.headers,
                verify=self.verify,
            )
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}") from e
        return response
