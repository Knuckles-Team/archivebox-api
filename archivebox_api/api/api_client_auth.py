from typing import Any

import requests
from agent_utilities.core.exceptions import (
    ParameterError,
)
from pydantic import ValidationError

from archivebox_api.api.api_client_base import BaseApiClient


class Api(BaseApiClient):
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
