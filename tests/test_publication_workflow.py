"""Keep the connector's canonical Pages and spec dashboard contract explicit."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _actions_on(workflow: dict):
    # PyYAML's YAML 1.1 reader represents the Actions ``on`` key as True.
    return workflow["on"] if "on" in workflow else workflow[True]


def test_pages_publishes_spec_dashboard_from_generated_status():
    assert not (ROOT / ".github/workflows/docs.yml").exists()

    config = json.loads((ROOT / ".github/spec-dashboard.json").read_text())
    assert config == {
        "version": 1,
        "sources": [{"glob": "specs/*/status.json", "kind": "spec"}],
    }
