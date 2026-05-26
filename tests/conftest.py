import os
from unittest.mock import MagicMock
import pytest
from fastmcp import Context

# CONCEPT:OS-5.4 — Telemetry & Observability
# CONCEPT:ECO-4.0 — Tool Interface & MCP Factory


@pytest.fixture
def temp_env():
    """Fixture to backup and restore environment variables after the test."""
    old_env = dict(os.environ)
    yield os.environ
    os.environ.clear()
    os.environ.update(old_env)


@pytest.fixture
def mock_client():
    """Fixture to provide a standard mocked Api client for tests."""
    client = MagicMock()
    # Pre-populate common methods with MagicMocks returning default mock dicts
    client.get_api_token.return_value = {"token": "mock-token-123"}
    client.check_api_token.return_value = {"ok": True}
    client.get_snapshots.return_value = {"snapshots": []}
    client.get_snapshot.return_value = {"snapshot": {}}
    client.get_archiveresults.return_value = {"archiveresults": []}
    client.get_archiveresult.return_value = {"archiveresult": {}}
    client.get_tags.return_value = {"tags": []}
    client.get_tag.return_value = {"tag": {}}
    client.get_any.return_value = {"data": {}}
    client.cli_add.return_value = {"status": "added"}
    client.cli_update.return_value = {"status": "updated"}
    client.cli_schedule.return_value = {"status": "scheduled"}
    client.cli_list.return_value = {"status": "listed"}
    client.cli_remove.return_value = {"status": "removed"}
    return client


@pytest.fixture
def mock_context():
    """Fixture to provide a mock FastMCP Context for progression logging tests."""
    ctx = MagicMock(spec=Context)
    return ctx
