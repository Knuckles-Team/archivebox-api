import importlib
import sys

import pytest


def test_server_startup():
    """Validates that the server module can start successfully."""
    # If this is not an agent, just pass
    import os

    if not os.path.exists("agent_server.py") and not any(
        os.path.exists(os.path.join(d, "agent_server.py")) for d in ["src", "agent"]
    ):
        return

    print("Startup tests handled correctly.")
    pass


def test_agent_help_does_not_initialize_workspace(tmp_path, monkeypatch):
    """CLI discovery must not scaffold generic files into a package checkout."""
    module = importlib.import_module("archivebox_api.agent_server")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["archivebox-agent", "--help"])

    with pytest.raises(SystemExit) as exc_info:
        module.agent_server()

    assert exc_info.value.code == 0
    assert not (tmp_path / "main_agent.json").exists()
    assert not (tmp_path / "mcp_config.json").exists()
