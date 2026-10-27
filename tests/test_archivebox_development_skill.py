"""PIPE-CONNSPEC-R103.4: ArchiveBox rapid-delivery skill contract."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "archivebox_api/skills/archivebox-api-development/SKILL.md"

pytestmark = pytest.mark.spec("PIPE-CONNSPEC-R103.4")


def test_development_skill_binds_archivebox_contract_and_package_data() -> None:
    text = SKILL.read_text()
    assert text.startswith("---\nname: archivebox-api-development\n")
    assert "## Rapid delivery: the 5-minute contract" in text
    assert "PIPE-CONNSPEC-R103.4" in text
    for reference in (
        "archivebox_api/mcp_server.py",
        "archivebox_api/connector_sources.py",
        "archivebox_api/web_source.py",
        "ARCHIVEBOX_BASE_URL",
        "ARCHIVEBOX_TLS_PROFILE",
        "ARCHIVEBOX_KG_AUTO_INGEST",
        "render_connector: true",
    ):
        assert reference in text

    project_data = tomllib.loads((ROOT / "pyproject.toml").read_text())
    project = project_data["project"]
    package_data = project_data["tool"]["setuptools"]["package-data"][
        "archivebox_api"
    ]
    assert "skills/**" in package_data
    assert SKILL.is_file()
    assert not re.search(r"(?:sk-|ghp_|Bearer\s+)[A-Za-z0-9_./-]{12,}", text)
    assert project["name"] == "archivebox-api"
