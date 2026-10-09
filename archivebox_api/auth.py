"""Authentication module for archivebox-api."""

import logging

from agent_connector_sdk.config import setting
from agent_connector_sdk.tls.resolve import resolve_tls_profile

from archivebox_api.api_client import Api

logger = logging.getLogger(__name__)


def get_client():
    """Get authenticated client for archivebox-api."""
    base_url = setting("ARCHIVEBOX_URL") or setting("ARCHIVEBOX_BASE_URL")
    token = setting("ARCHIVEBOX_TOKEN")
    username = setting("ARCHIVEBOX_USERNAME")
    password = setting("ARCHIVEBOX_PASSWORD")
    api_key = setting("ARCHIVEBOX_TOKEN") or setting("ARCHIVEBOX_API_KEY")
    if not base_url:
        raise RuntimeError("ARCHIVEBOX_BASE_URL not set")
    return Api(
        url=base_url,
        token=token,
        username=username,
        password=password,
        api_key=api_key,
        tls_profile=resolve_tls_profile(
            "archivebox",
            profile_name=setting("ARCHIVEBOX_TLS_PROFILE", "") or None,
            profile_ref=setting("ARCHIVEBOX_TLS_PROFILE_REF", "") or None,
        ),
    )
