import sys
from abc import ABC, abstractmethod

import requests
import urllib3
from agent_utilities.core.exceptions import (
    AuthError,
    MissingParameterError,
)


class BaseApiClient(ABC):
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

        # NOTE: no eager connectivity probe at construction time. A client is
        # built per-call via ``Depends(get_client)``; doing network I/O here made
        # construction raise (e.g. a 404 -> ParameterError) before any tool ran,
        # which FastMCP surfaces as "Failed to resolve dependency 'client'". Each
        # tool method issues its own request and surfaces transport/auth errors
        # per-call, so the constructor only configures auth headers.

    @abstractmethod
    def get_api_token(
        self, username: str | None = None, password: str | None = None
    ) -> requests.Response:
        raise NotImplementedError()
