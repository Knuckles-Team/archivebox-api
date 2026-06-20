"""Authentication module for archivebox-api."""

from agent_utilities.base_utilities import get_logger, to_boolean
from agent_utilities.core.config import setting

from archivebox_api.api_client import Api

logger = get_logger(__name__)


def get_client():
    """Get authenticated client for archivebox-api."""
    base_url = setting("ARCHIVEBOX_URL") or setting("ARCHIVEBOX_BASE_URL")
    token = setting("ARCHIVEBOX_TOKEN")
    username = setting("ARCHIVEBOX_USERNAME")
    password = setting("ARCHIVEBOX_PASSWORD")
    api_key = setting("ARCHIVEBOX_TOKEN") or setting("ARCHIVEBOX_API_KEY")
    verify = to_boolean(setting("ARCHIVEBOX_SSL_VERIFY", False))
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
