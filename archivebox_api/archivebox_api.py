#!/usr/bin/python
# coding: utf-8

import requests
import urllib3
from pydantic import ValidationError
from typing import Optional, Dict, List, Union

from archivebox_api.decorators import require_auth
from archivebox_api.exceptions import (
    AuthError,
    UnauthorizedError,
    ParameterError,
    MissingParameterError,
)


class Api(object):
    def __init__(
        self,
        url: str = None,
        token: str = None,
        username: str = None,
        password: str = None,
        api_key: str = None,
        verify: bool = True,
    ):
        if url is None:
            raise MissingParameterError("URL is required")

        self._session = requests.Session()
        self.url = url.rstrip("/")
        self.headers = {"Content-Type": "application/json"}
        self.verify = verify

        if self.verify is False:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # Handle authentication methods
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
        elif api_key:
            self.headers["X-ArchiveBox-API-Key"] = api_key
        elif username and password:
            # Fetch API token using username and password
            response = self.get_api_token(username=username, password=password)
            if response.status_code == 200:
                data = response.json()
                fetched_token = data.get("token")
                if not fetched_token:
                    raise AuthError("Failed to retrieve API token")
                self.headers["Authorization"] = f"Bearer {fetched_token}"
            else:
                print(f"Authentication Error: {response.content}")
                raise AuthError
        # else: no authentication

        # Test connection and authentication
        test_params = {"limit": 1}
        if api_key and "X-ArchiveBox-API-Key" not in self.headers:
            test_params["api_key"] = api_key

        response = self._session.get(
            f"{self.url}/api/v1/core/snapshots",
            params=test_params,
            headers=self.headers,
            verify=self.verify,
        )

        if response.status_code == 403:
            print(f"Unauthorized Error: {response.content}")
            raise UnauthorizedError
        elif response.status_code == 401:
            print(f"Authentication Error: {response.content}")
            raise AuthError
        elif response.status_code == 404:
            print(f"Parameter Error: {response.content}")
            raise ParameterError

    ####################################################################################################################
    #                                              Authentication Endpoints                                           #
    ####################################################################################################################
    def get_api_token(
        self, username: Optional[str] = None, password: Optional[str] = None
    ) -> requests.Response:
        """
        Generate an API token for a given username & password

        Args:
            username: The username for authentication.
            password: The password for authentication.

        Returns:
            Response: The response object from the POST request.

        Raises:
            ParameterError: If the provided parameters are invalid.
        """
        try:
            data = {}
            if username is not None:
                data["username"] = username
            if password is not None:
                data["password"] = password
            response = self._session.post(
                url=f"{self.url}/api/v1/auth/get_api_token",
                json=data,
                headers={"Content-Type": "application/json"},
                verify=self.verify,
            )
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    def check_api_token(self, token: str) -> requests.Response:
        """
        Validate an API token to make sure it's valid and non-expired

        Args:
            token: The API token to validate.

        Returns:
            Response: The response object from the POST request.

        Raises:
            ParameterError: If the provided parameters are invalid.
        """
        try:
            response = self._session.post(
                url=f"{self.url}/api/v1/auth/check_api_token",
                json={"token": token},
                headers={"Content-Type": "application/json"},
                verify=self.verify,
            )
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    ####################################################################################################################
    #                                              Core Model Endpoints                                               #
    ####################################################################################################################
    @require_auth
    def get_snapshots(
        self,
        id: Optional[str] = None,
        abid: Optional[str] = None,
        created_by_id: Optional[str] = None,
        created_by_username: Optional[str] = None,
        created_at__gte: Optional[str] = None,
        created_at__lt: Optional[str] = None,
        created_at: Optional[str] = None,
        modified_at: Optional[str] = None,
        modified_at__gte: Optional[str] = None,
        modified_at__lt: Optional[str] = None,
        search: Optional[str] = None,
        url: Optional[str] = None,
        tag: Optional[str] = None,
        title: Optional[str] = None,
        timestamp: Optional[str] = None,
        bookmarked_at__gte: Optional[str] = None,
        bookmarked_at__lt: Optional[str] = None,
        with_archiveresults: bool = False,
        limit: int = 200,
        offset: int = 0,
        page: int = 0,
        api_key: Optional[str] = None,
    ) -> requests.Response:
        """
        Retrieve list of snapshots

        Args:
            id: Filter by snapshot ID (startswith, icontains, timestamp__startswith).
            abid: Filter by snapshot abid (icontains).
            created_by_id: Filter by creator ID.
            created_by_username: Filter by creator username (icontains).
            created_at__gte: Filter by creation date >= (ISO 8601 format).
            created_at__lt: Filter by creation date < (ISO 8601 format).
            created_at: Filter by exact creation date (ISO 8601 format).
            modified_at: Filter by exact modification date (ISO 8601 format).
            modified_at__gte: Filter by modification date >= (ISO 8601 format).
            modified_at__lt: Filter by modification date < (ISO 8601 format).
            search: Search across url, title, tags, id, abid, timestamp (icontains).
            url: Filter by URL (exact).
            tag: Filter by tag name (exact).
            title: Filter by title (icontains).
            timestamp: Filter by timestamp (startswith).
            bookmarked_at__gte: Filter by bookmark date >= (ISO 8601 format).
            bookmarked_at__lt: Filter by bookmark date < (ISO 8601 format).
            with_archiveresults: Include archiveresults in response (default: False).
            limit: Number of results to return (default: 200).
            offset: Offset for pagination (default: 0).
            page: Page number for pagination (default: 0).
            api_key: API key for QueryParamTokenAuth (optional).

        Returns:
            Response: The response object from the GET request.

        Raises:
            ParameterError: If the provided parameters are invalid.
        """
        params = {
            k: v
            for k, v in locals().items()
            if k != "self" and v is not None and k != "api_key"
        }
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
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def get_snapshot(
        self, snapshot_id: str, with_archiveresults: bool = True
    ) -> requests.Response:
        """
        Get a specific Snapshot by abid or id

        Args:
            snapshot_id: The ID or abid of the snapshot.
            with_archiveresults: Whether to include archiveresults (default: True).

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
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def get_archiveresults(
        self,
        id: Optional[str] = None,
        search: Optional[str] = None,
        snapshot_id: Optional[str] = None,
        snapshot_url: Optional[str] = None,
        snapshot_tag: Optional[str] = None,
        status: Optional[str] = None,
        output: Optional[str] = None,
        extractor: Optional[str] = None,
        cmd: Optional[str] = None,
        pwd: Optional[str] = None,
        cmd_version: Optional[str] = None,
        created_at: Optional[str] = None,
        created_at__gte: Optional[str] = None,
        created_at__lt: Optional[str] = None,
        limit: int = 200,
        offset: int = 0,
        page: int = 0,
        api_key: Optional[str] = None,
    ) -> requests.Response:
        """
        List all ArchiveResult entries matching these filters

        Args:
            id: Filter by ID (startswith, icontains, snapshot-related fields).
            search: Search across snapshot url, title, tags, extractor, output, id.
            snapshot_id: Filter by snapshot ID (startswith, icontains).
            snapshot_url: Filter by snapshot URL (icontains).
            snapshot_tag: Filter by snapshot tag (icontains).
            status: Filter by status (exact).
            output: Filter by output (icontains).
            extractor: Filter by extractor (icontains).
            cmd: Filter by command (icontains).
            pwd: Filter by working directory (icontains).
            cmd_version: Filter by command version (exact).
            created_at: Filter by exact creation date (ISO 8601 format).
            created_at__gte: Filter by creation date >= (ISO 8601 format).
            created_at__lt: Filter by creation date < (ISO 8601 format).
            limit: Number of results to return (default: 200).
            offset: Offset for pagination (default: 0).
            page: Page number for pagination (default: 0).
            api_key: API key for QueryParamTokenAuth (optional).

        Returns:
            Response: The response object from the GET request.

        Raises:
            ParameterError: If the provided parameters are invalid.
        """
        params = {
            k: v
            for k, v in locals().items()
            if k != "self" and v is not None and k != "api_key"
        }
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
            raise ParameterError(f"Invalid parameters: {e.errors()}")
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
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def get_tags(
        self,
        limit: int = 200,
        offset: int = 0,
        page: int = 0,
        api_key: Optional[str] = None,
    ) -> requests.Response:
        """
        Retrieve list of tags

        Args:
            limit: Number of results to return (default: 200).
            offset: Offset for pagination (default: 0).
            page: Page number for pagination (default: 0).
            api_key: API key for QueryParamTokenAuth (optional).

        Returns:
            Response: The response object from the GET request.

        Raises:
            ParameterError: If the provided parameters are invalid.
        """
        params = {
            k: v
            for k, v in locals().items()
            if k != "self" and v is not None and k != "api_key"
        }
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
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def get_tag(self, tag_id: str, with_snapshots: bool = True) -> requests.Response:
        """
        Get a specific Tag by id or abid

        Args:
            tag_id: The ID or abid of the tag.
            with_snapshots: Whether to include snapshots (default: True).

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
            raise ParameterError(f"Invalid parameters: {e.errors()}")
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
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    ####################################################################################################################
    #                                              CLI Sub-Command Endpoints                                          #
    ####################################################################################################################
    @require_auth
    def cli_add(
        self,
        urls: List[str],
        tag: str = "",
        depth: int = 0,
        update: bool = False,
        update_all: bool = False,
        index_only: bool = False,
        overwrite: bool = False,
        init: bool = False,
        extractors: str = "",
        parser: str = "auto",
        extra_data: Optional[Dict] = None,
    ) -> requests.Response:
        """
        Execute archivebox add command

        Args:
            urls: List of URLs to archive.
            tag: Comma-separated tags (default: "").
            depth: Crawl depth (default: 0).
            update: Update existing snapshots (default: False).
            update_all: Update all snapshots (default: False).
            index_only: Index without archiving (default: False).
            overwrite: Overwrite existing files (default: False).
            init: Initialize collection if needed (default: False).
            extractors: Comma-separated list of extractors to use (default: "").
            parser: Parser type (default: "auto").
            extra_data: Additional parameters as a dictionary (optional).

        Returns:
            Response: The response object from the POST request.

        Raises:
            ParameterError: If the provided parameters are invalid.
        """
        data = {
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
        }
        if extra_data:
            data.update(extra_data)
        try:
            response = self._session.post(
                url=f"{self.url}/api/v1/cli/add",
                json=data,
                headers=self.headers,
                verify=self.verify,
            )
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def cli_update(
        self,
        resume: Optional[float] = 0,
        only_new: bool = True,
        index_only: bool = False,
        overwrite: bool = False,
        after: Optional[float] = 0,
        before: Optional[float] = 999999999999999,
        status: Optional[str] = "unarchived",
        filter_type: Optional[str] = "substring",
        filter_patterns: Optional[List[str]] = None,
        extractors: Optional[str] = "",
        extra_data: Optional[Dict] = None,
    ) -> requests.Response:
        """
        Execute archivebox update command

        Args:
            resume: Resume from timestamp (default: 0).
            only_new: Update only new snapshots (default: True).
            index_only: Index without archiving (default: False).
            overwrite: Overwrite existing files (default: False).
            after: Filter snapshots after timestamp (default: 0).
            before: Filter snapshots before timestamp (default: 999999999999999).
            status: Filter by status (default: "unarchived").
            filter_type: Filter type (default: "substring").
            filter_patterns: List of filter patterns (default: ["https://example.com"]).
            extractors: Comma-separated list of extractors (default: "").
            extra_data: Additional parameters as a dictionary (optional).

        Returns:
            Response: The response object from the POST request.

        Raises:
            ParameterError: If the provided parameters are invalid.
        """
        data = {
            k: v
            for k, v in locals().items()
            if k != "self" and v is not None and k != "extra_data"
        }
        if filter_patterns is None:
            data["filter_patterns"] = ["https://example.com"]
        if extra_data:
            data.update(extra_data)
        try:
            response = self._session.post(
                url=f"{self.url}/api/v1/cli/update",
                json=data,
                headers=self.headers,
                verify=self.verify,
            )
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def cli_schedule(
        self,
        import_path: Optional[str] = None,
        add: bool = False,
        every: Optional[str] = None,
        tag: str = "",
        depth: int = 0,
        overwrite: bool = False,
        update: bool = False,
        clear: bool = False,
        extra_data: Optional[Dict] = None,
    ) -> requests.Response:
        """
        Execute archivebox schedule command

        Args:
            import_path: Path to import file (optional).
            add: Enable adding new URLs (default: False).
            every: Schedule frequency (e.g., "daily").
            tag: Comma-separated tags (default: "").
            depth: Crawl depth (default: 0).
            overwrite: Overwrite existing files (default: False).
            update: Update existing snapshots (default: False).
            clear: Clear existing schedules (default: False).
            extra_data: Additional parameters as a dictionary (optional).

        Returns:
            Response: The response object from the POST request.

        Raises:
            ParameterError: If the provided parameters are invalid.
        """
        data = {
            k: v
            for k, v in locals().items()
            if k != "self" and v is not None and k != "extra_data"
        }
        if extra_data:
            data.update(extra_data)
        try:
            response = self._session.post(
                url=f"{self.url}/api/v1/cli/schedule",
                json=data,
                headers=self.headers,
                verify=self.verify,
            )
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def cli_list(
        self,
        filter_patterns: Optional[List[str]] = None,
        filter_type: str = "substring",
        status: Optional[str] = "indexed",
        after: Optional[float] = 0,
        before: Optional[float] = 999999999999999,
        sort: str = "bookmarked_at",
        as_json: bool = True,
        as_html: bool = False,
        as_csv: Union[str, bool] = "timestamp,url",
        with_headers: bool = False,
        extra_data: Optional[Dict] = None,
    ) -> requests.Response:
        """
        Execute archivebox list command

        Args:
            filter_patterns: List of filter patterns (default: ["https://example.com"]).
            filter_type: Filter type (default: "substring").
            status: Filter by status (default: "indexed").
            after: Filter snapshots after timestamp (default: 0).
            before: Filter snapshots before timestamp (default: 999999999999999).
            sort: Sort field (default: "bookmarked_at").
            as_json: Output as JSON (default: True).
            as_html: Output as HTML (default: False).
            as_csv: Output as CSV or fields to include (default: "timestamp,url").
            with_headers: Include headers in output (default: False).
            extra_data: Additional parameters as a dictionary (optional).

        Returns:
            Response: The response object from the POST request.

        Raises:
            ParameterError: If the provided parameters are invalid.
        """
        data = {
            k: v
            for k, v in locals().items()
            if k != "self" and v is not None and k != "extra_data"
        }
        if filter_patterns is None:
            data["filter_patterns"] = ["https://example.com"]
        if extra_data:
            data.update(extra_data)
        try:
            response = self._session.post(
                url=f"{self.url}/api/v1/cli/list",
                json=data,
                headers=self.headers,
                verify=self.verify,
            )
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response

    @require_auth
    def cli_remove(
        self,
        delete: bool = True,
        after: Optional[float] = 0,
        before: Optional[float] = 999999999999999,
        filter_type: str = "exact",
        filter_patterns: Optional[List[str]] = None,
        extra_data: Optional[Dict] = None,
    ) -> requests.Response:
        """
        Execute archivebox remove command

        Args:
            delete: Delete matching snapshots (default: True).
            after: Filter snapshots after timestamp (default: 0).
            before: Filter snapshots before timestamp (default: 999999999999999).
            filter_type: Filter type (default: "exact").
            filter_patterns: List of filter patterns (default: ["https://example.com"]).
            extra_data: Additional parameters as a dictionary (optional).

        Returns:
            Response: The response object from the POST request.

        Raises:
            ParameterError: If the provided parameters are invalid.
        """
        data = {
            k: v
            for k, v in locals().items()
            if k != "self" and v is not None and k != "extra_data"
        }
        if filter_patterns is None:
            data["filter_patterns"] = ["https://example.com"]
        if extra_data:
            data.update(extra_data)
        try:
            response = self._session.post(
                url=f"{self.url}/api/v1/cli/remove",
                json=data,
                headers=self.headers,
                verify=self.verify,
            )
        except ValidationError as e:
            raise ParameterError(f"Invalid parameters: {e.errors()}")
        return response
