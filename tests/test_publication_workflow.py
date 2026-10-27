"""Keep the connector's canonical Pages and spec dashboard contract explicit."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _actions_on(workflow: dict):
    # PyYAML's YAML 1.1 reader represents the Actions ``on`` key as True.
    return workflow["on"] if "on" in workflow else workflow[True]


def test_pages_publishes_spec_dashboard_from_generated_status():
    assert not (ROOT / ".github/workflows/docs.yml").exists()

    workflow = yaml.safe_load((ROOT / ".github/workflows/pages.yml").read_text())
    publisher = workflow["jobs"]["publish-pages"]
    actions = _actions_on(workflow)

    assert publisher["uses"] == (
        "Knuckles-Team/pipelines/.github/workflows/pages_pipeline.yml@main"
    )
    assert publisher["with"] == {
        "content_source": "docs",
        "spec_dashboard_enabled": True,
        "spec_dashboard_config": ".github/spec-dashboard.json",
    }
    assert "workflow_dispatch" in actions
    assert {
        "docs/**",
        "mkdocs.yml",
        "README.md",
        "specs/**",
        ".github/spec-dashboard.json",
        ".github/workflows/pages.yml",
    } <= set(actions["push"]["paths"])
    assert publisher["permissions"] == {
        "contents": "read",
        "pages": "write",
        "id-token": "write",
    }

    config = json.loads((ROOT / ".github/spec-dashboard.json").read_text())
    assert config == {
        "version": 1,
        "sources": [{"glob": "specs/*/status.json", "kind": "spec"}],
    }
