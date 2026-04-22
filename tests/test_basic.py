from unittest.mock import patch, MagicMock
from archivebox_api.api_wrapper import Api

@patch("requests.Session.get")
def test_api_init(mock_get):
    # Mock the probe response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    api = Api(url="http://localhost", token="test")
    assert api.url == "http://localhost"
    assert api.headers["Authorization"] == "Bearer test"
    assert mock_get.called
