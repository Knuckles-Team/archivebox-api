#!/usr/bin/python


from typing import Any

import requests
import urllib3
from agent_utilities.decorators import require_auth
from agent_utilities.exceptions import (
    AuthError,
    MissingParameterError,
    ParameterError,
    UnauthorizedError,
)
from pydantic import ValidationError


class Api:
    def __init__(
        self,
        url: str | None = None,
        token: str | None = None,
        username: str | None = None,
        password: str | None = None,
        api_key: str | None = None,
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

        if token:
            self.headers["Authorization"] = f"Bearer {token}"
        elif api_key:
            self.headers["X-ArchiveBox-API-Key"] = api_key
        elif username and password:
            response = self.get_api_token(username=username, password=password)
            if response.status_code == 200:
                data = response.json()
                fetched_token = data.get("token")
                if not fetched_token:
                    raise AuthError("Failed to retrieve API token")
                self.headers["Authorization"] = f"Bearer {fetched_token}"
            else:
                print(f"Authentication Error: {response.content!r}")
                raise AuthError
        elif not api_key and not token:
            # Check if we have enough info for auth later or if we are just probing
            pass

        test_params: dict[str, Any] = {"limit": 1}
        if api_key and "X-ArchiveBox-API-Key" not in self.headers:
            test_params["api_key"] = api_key

        response = self._session.get(
            f"{self.url}/api/v1/core/snapshots",
            params=test_params,
            headers=self.headers,
            verify=self.verify,
        )

        if response.status_code == 403:
            print(f"Unauthorized Error: {response.content!r}")
            raise UnauthorizedError
        elif response.status_code == 401:
            print(f"Authentication Error: {response.content!r}")
            raise AuthError
        elif response.status_code == 404:
            print(f"Parameter Error: {response.content!r}")
            raise ParameterError

    def get_api_token(
        self, username: str | None = None, password: str | None = None
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
            data: dict[str, Any] = {}
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
            raise ParameterError(f"Invalid parameters: {e.errors()}") from e
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
            raise ParameterError(f"Invalid parameters: {e.errors()}") from e
        return response

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

    @require_auth
    def cli_add(
        self,
        urls: list[str],
        tag: str = "",
        depth: int = 0,
        update: bool = False,
        update_all: bool = False,
        index_only: bool = False,
        overwrite: bool = False,
        init: bool = False,
        extractors: str = "",
        parser: str = "auto",
        extra_data: dict | None = None,
    ) -> requests.Response:
        """
        Execute archivebox add command

        Args:
            urls: List of URLs to archive.
            tag: Comma-separated tags.
            depth: Crawl depth.
            update: Update existing snapshots.
            update_all: Update all snapshots.
            index_only: Index without archiving.
            overwrite: Overwrite existing files.
            init: Initialize collection if needed.
            extractors: Comma-separated list of extractors to use.
            parser: Parser type.
            extra_data: Additional parameters as a dictionary.

        Returns:
            Response: The response object from the POST request.

        Raises:
            ParameterError: If the provided parameters are invalid.
        """
        data: dict[str, Any] = {
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
            raise ParameterError(f"Invalid parameters: {e.errors()}") from e
        return response

    @require_auth
    def cli_update(
        self,
        resume: float | None = 0,
        only_new: bool = True,
        index_only: bool = False,
        overwrite: bool = False,
        after: float | None = 0,
        before: float | None = 999999999999999,
        status: str | None = "unarchived",
        filter_type: str | None = "substring",
        filter_patterns: list[str] | None = None,
        extractors: str | None = "",
        extra_data: dict | None = None,
    ) -> requests.Response:
        """
        Execute archivebox update command

        Args:
            resume: Resume from timestamp.
            only_new: Update only new snapshots.
            index_only: Index without archiving.
            overwrite: Overwrite existing files.
            after: Filter snapshots after timestamp.
            before: Filter snapshots before timestamp.
            status: Filter by status.
            filter_type: Filter type.
            filter_patterns: List of filter patterns.
            extractors: Comma-separated list of extractors.
            extra_data: Additional parameters as a dictionary.

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
            raise ParameterError(f"Invalid parameters: {e.errors()}") from e
        return response

    @require_auth
    def cli_schedule(
        self,
        import_path: str | None = None,
        add: bool = False,
        every: str | None = None,
        tag: str = "",
        depth: int = 0,
        overwrite: bool = False,
        update: bool = False,
        clear: bool = False,
        extra_data: dict | None = None,
    ) -> requests.Response:
        """
        Execute archivebox schedule command

        Args:
            import_path: Path to import file.
            add: Enable adding new URLs.
            every: Schedule frequency.
            tag: Comma-separated tags.
            depth: Crawl depth.
            overwrite: Overwrite existing files.
            update: Update existing snapshots.
            clear: Clear existing schedules.
            extra_data: Additional parameters as a dictionary.

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
            raise ParameterError(f"Invalid parameters: {e.errors()}") from e
        return response

    @require_auth
    def cli_list(
        self,
        filter_patterns: list[str] | None = None,
        filter_type: str = "substring",
        status: str | None = "indexed",
        after: float | None = 0,
        before: float | None = 999999999999999,
        sort: str = "bookmarked_at",
        as_json: bool = True,
        as_html: bool = False,
        as_csv: str | bool = "timestamp,url",
        with_headers: bool = False,
        extra_data: dict | None = None,
    ) -> requests.Response:
        """
        Execute archivebox list command

        Args:
            filter_patterns: List of filter patterns.
            filter_type: Filter type.
            status: Filter by status.
            after: Filter snapshots after timestamp.
            before: Filter snapshots before timestamp.
            sort: Sort field.
            as_json: Output as JSON.
            as_html: Output as HTML.
            as_csv: Output as CSV or fields to include.
            with_headers: Include headers in output.
            extra_data: Additional parameters as a dictionary.

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
            raise ParameterError(f"Invalid parameters: {e.errors()}") from e
        return response

    @require_auth
    def cli_remove(
        self,
        delete: bool = True,
        after: float | None = 0,
        before: float | None = 999999999999999,
        filter_type: str = "exact",
        filter_patterns: list[str] | None = None,
        extra_data: dict | None = None,
    ) -> requests.Response:
        """
        Execute archivebox remove command

        Args:
            delete: Delete matching snapshots.
            after: Filter snapshots after timestamp.
            before: Filter snapshots before timestamp.
            filter_type: Filter type.
            filter_patterns: List of filter patterns.
            extra_data: Additional parameters as a dictionary.

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
            raise ParameterError(f"Invalid parameters: {e.errors()}") from e
        return response
