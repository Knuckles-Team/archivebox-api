"""Authentication module for archivebox-api."""

import os

from agent_utilities.base_utilities import get_logger, to_boolean

from archivebox_api.api_client import Api

logger = get_logger(__name__)


def get_client():
    """Get authenticated client for archivebox-api."""
    base_url = os.getenv("ARCHIVEBOX_BASE_URL")
    token = os.getenv("ARCHIVEBOX_TOKEN")
    username = os.getenv("ARCHIVEBOX_USERNAME")
    password = os.getenv("ARCHIVEBOX_PASSWORD")
    api_key = os.getenv("ARCHIVEBOX_API_KEY")
    verify = to_boolean(os.getenv("ARCHIVEBOX_SSL_VERIFY", "False"))
    if not base_url:
        raise RuntimeError("ARCHIVEBOX_BASE_URL not set")
    return Api(
        url=base_url,
        token=token,
        username=username,
        password=password,
        api_key=api_key,
        verify=verify,
    )
