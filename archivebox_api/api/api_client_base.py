import sys
from abc import ABC, abstractmethod
from typing import Any

import httpx
from scion_sdk.exceptions import (
    AuthError,
    MissingParameterError,
)
from scion_sdk.http.client import build_http_client
from scion_sdk.http.options import HttpClientOptions
from scion_sdk.tls.profile import ResolvedTLSProfile
from scion_sdk.tls.resolve import resolve_tls_profile


class BaseApiClient(ABC):
    def __init__(
        self,
        url: str | None = None,
        token: str | None = None,
        username: str | None = None,
        password: str | None = None,
        api_key: str | None = None,
        tls_profile: ResolvedTLSProfile | None = None,
    ):
        if url is None:
            raise MissingParameterError("URL is required")

        self.tls_profile = tls_profile or resolve_tls_profile("archivebox")
        self.url = url.rstrip("/")
        self._session = build_http_client(
            HttpClientOptions(
                base_url=self.url,
                tls=self.tls_profile,
                allow_plaintext=self.url.startswith("http://"),
            )
        )
        self.headers = {"Content-Type": "application/json"}

        self._configure_auth_headers(
            token=token, username=username, password=password, api_key=api_key
        )

        # NOTE: no eager connectivity probe at construction time. A client is
        # built per-call via ``Depends(get_client)``; doing network I/O here made
        # construction raise (e.g. a 404 -> ParameterError) before any tool ran,
        # which FastMCP surfaces as "Failed to resolve dependency 'client'". Each
        # tool method issues its own request and surfaces transport/auth errors
        # per-call, so the constructor only configures auth headers.

    def _configure_auth_headers(
        self,
        *,
        token: str | None,
        username: str | None,
        password: str | None,
        api_key: str | None,
    ) -> None:
        """Set the auth header for whichever credential kind was supplied.

        No credentials supplied at all is a valid state (a client may be built
        just to probe, or authenticated later) and is a deliberate no-op.
        """
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
        elif api_key:
            self.headers["X-ArchiveBox-API-Key"] = api_key
        elif username and password:
            self._authenticate_with_credentials(username, password)

    def _authenticate_with_credentials(self, username: str, password: str) -> None:
        """Exchange a username/password for a bearer token via get_api_token."""
        response = self.get_api_token(username=username, password=password)
        if response.status_code != 200:
            print("Authentication was rejected", file=sys.stderr)
            raise AuthError
        fetched_token = response.json().get("token")
        if not fetched_token:
            raise AuthError("Failed to retrieve API token")
        self.headers["Authorization"] = f"Bearer {fetched_token}"

    def _send(
        self,
        verb: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        api_key: str | None = None,
        follow_redirects: bool = False,
    ) -> httpx.Response:
        """Send one ArchiveBox REST call; ``None`` values are dropped from both
        the query string and the JSON body so upstream defaults apply."""
        query = {k: v for k, v in (params or {}).items() if v is not None}
        if api_key:
            query["api_key"] = api_key
        body = None
        if json is not None:
            body = {k: v for k, v in json.items() if v is not None}
        return self._session.request(
            verb,
            f"{self.url}{path}",
            params=query or None,
            json=body,
            headers=self.headers,
            follow_redirects=follow_redirects,
        )

    def _send_form(
        self,
        verb: str,
        path: str,
        *,
        fields: dict[str, Any],
        files: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Send a multipart form (ArchiveBox's archive-result upload shape).

        ``files`` maps each output path (relative to the plugin directory) to
        its base64-encoded content; each becomes one ``files`` part with its
        path in ``output_paths``.
        """
        import base64
        import json as _json

        data = {k: str(v) for k, v in fields.items() if v is not None}
        parts: list[tuple[str, tuple[str, bytes]]] = []
        if files:
            data["output_paths"] = _json.dumps(list(files))
            for out_path, b64 in files.items():
                name = out_path.rsplit("/", 1)[-1]
                parts.append(("files", (name, base64.b64decode(b64))))
        headers = {k: v for k, v in self.headers.items() if k != "Content-Type"}
        return self._session.request(
            verb,
            f"{self.url}{path}",
            data=data,
            files=parts or None,
            headers=headers,
        )

    def close(self) -> None:
        """Release transport resources and runtime-only TLS material."""
        self._session.close()
        self.tls_profile.cleanup()

    @abstractmethod
    def get_api_token(
        self, username: str | None = None, password: str | None = None
    ) -> httpx.Response:
        raise NotImplementedError()
