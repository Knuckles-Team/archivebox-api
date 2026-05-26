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
        }
        data = {k: v for k, v in data.items() if v is not None}
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
            "import_path": import_path,
            "add": add,
            "every": every,
            "tag": tag,
            "depth": depth,
            "overwrite": overwrite,
            "update": update,
            "clear": clear,
        }
        data = {k: v for k, v in data.items() if v is not None}
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
        }
        data = {k: v for k, v in data.items() if v is not None}
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
            "delete": delete,
            "after": after,
            "before": before,
            "filter_type": filter_type,
            "filter_patterns": filter_patterns,
        }
        data = {k: v for k, v in data.items() if v is not None}
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
