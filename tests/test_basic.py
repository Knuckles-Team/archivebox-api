from unittest.mock import patch

from archivebox_api.api_client import Api


@patch("requests.Session.get")
def test_api_init(mock_get):
    # The constructor configures auth headers only and performs NO network I/O,
    # so Depends(get_client) can resolve a client without a reachable server.
    api = Api(url="http://localhost", token="test")
    assert api.url == "http://localhost"
    assert api.headers["Authorization"] == "Bearer test"
    assert not mock_get.called
