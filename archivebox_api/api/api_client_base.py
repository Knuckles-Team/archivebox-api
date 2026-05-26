import sys
from typing import Any

import requests
import urllib3
from agent_utilities.core.exceptions import (
    AuthError,
    MissingParameterError,
    ParameterError,
    UnauthorizedError,
)


class BaseApiClient:
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
                print(f"Authentication Error: {response.content!r}", file=sys.stderr)
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
            print(f"Unauthorized Error: {response.content!r}", file=sys.stderr)
            raise UnauthorizedError
        elif response.status_code == 401:
            print(f"Authentication Error: {response.content!r}", file=sys.stderr)
            raise AuthError
        elif response.status_code == 404:
            print(f"Parameter Error: {response.content!r}", file=sys.stderr)
            raise ParameterError

    def get_api_token(
        self, username: str | None = None, password: str | None = None
    ) -> requests.Response:
        raise NotImplementedError
