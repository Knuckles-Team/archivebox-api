"""The served surface matches the ArchiveBox API, the pack contracts and the content.

CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R003..R006.
"""

from __future__ import annotations

import asyncio
import json
import re
from pathlib import Path

import httpx
import pytest
import pyoxigraph as ox
from scion_sdk.connector import build_server
from scion_sdk.exceptions import ParameterError

from archivebox_api.api_client import Api
from archivebox_api.mcp_server import coerce_result

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "archivebox_api"
CP = "http://knuckles.team/kg/connector-pack#"
KG = "http://knuckles.team/kg#"
RDFS_SUB = ox.NamedNode("http://www.w3.org/2000/01/rdf-schema#subClassOf")
RDF_TYPE = ox.NamedNode("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
OWL_CLASS = ox.NamedNode("http://www.w3.org/2002/07/owl#Class")

# Every operation of the ArchiveBox 0.9 REST API (/api/v1/openapi.json).
UPSTREAM = {
    ("POST", "/api/v1/auth/get_api_token"),
    ("POST", "/api/v1/auth/check_api_token"),
    ("POST", "/api/v1/auth/browser_session"),
    ("GET", "/api/v1/core/archiveresults"),
    ("POST", "/api/v1/core/archiveresults"),
    ("GET", "/api/v1/core/archiveresult/{archiveresult_id}"),
    ("PATCH", "/api/v1/core/archiveresult/{archiveresult_id}"),
    ("GET", "/api/v1/core/snapshots"),
    ("POST", "/api/v1/core/snapshots"),
    ("GET", "/api/v1/core/snapshots.rss"),
    ("GET", "/api/v1/core/snapshot/{snapshot_id}"),
    ("PATCH", "/api/v1/core/snapshot/{snapshot_id}"),
    ("DELETE", "/api/v1/core/snapshot/{snapshot_id}"),
    ("GET", "/api/v1/core/tags"),
    ("GET", "/api/v1/core/tag/{tag_id}"),
    ("DELETE", "/api/v1/core/tag/{tag_id}"),
    ("GET", "/api/v1/core/any/{id}"),
    ("GET", "/api/v1/core/tags/search/"),
    ("GET", "/api/v1/core/tags/autocomplete/"),
    ("POST", "/api/v1/core/tags/create/"),
    ("POST", "/api/v1/core/tag/{tag_id}/rename"),
    ("GET", "/api/v1/core/tag/{tag_id}/urls.txt"),
    ("GET", "/api/v1/core/tag/{tag_id}/snapshots.jsonl"),
    ("POST", "/api/v1/core/tags/add-to-snapshot/"),
    ("POST", "/api/v1/core/tags/remove-from-snapshot/"),
    ("GET", "/api/v1/crawls/crawls"),
    ("POST", "/api/v1/crawls/crawls"),
    ("GET", "/api/v1/crawls/crawl/{crawl_id}"),
    ("PATCH", "/api/v1/crawls/crawl/{crawl_id}"),
    ("DELETE", "/api/v1/crawls/crawl/{crawl_id}"),
    ("GET", "/api/v1/crawls/crawl/{crawl_id}/files/{filename}"),
    ("GET", "/api/v1/crawls/crawl/{crawl_id}/files/{folder}/{filename}"),
    ("GET", "/api/v1/crawls/crawl/{crawl_id}/files/{folder}/{subfolder}/{filename}"),
    ("POST", "/api/v1/cli/add"),
    ("POST", "/api/v1/cli/update"),
    ("POST", "/api/v1/cli/schedule"),
    ("POST", "/api/v1/cli/search"),
    ("POST", "/api/v1/cli/remove"),
    ("GET", "/api/v1/machine/machines"),
    ("GET", "/api/v1/machine/machine/current"),
    ("GET", "/api/v1/machine/machine/{machine_id}"),
    ("GET", "/api/v1/machine/binaries"),
    ("GET", "/api/v1/machine/binary/{binary_id}"),
    ("GET", "/api/v1/machine/binary/by-name/{name}"),
    ("GET", "/api/v1/personas/personas"),
    ("POST", "/api/v1/personas/sync"),
}
_DOC = re.compile(r"^\s*(GET|POST|PATCH|DELETE)\s+(/\S+)", re.MULTILINE)
_SKIP = {"close"}


def _client_operations() -> dict[str, tuple[str, str]]:
    ops = {}
    for name in dir(Api):
        if name.startswith("_") or name in _SKIP:
            continue
        fn = getattr(Api, name)
        if not callable(fn):
            continue
        doc = fn.__doc__ or ""
        match = _DOC.search(doc)
        if match:
            ops[name] = (match.group(1), match.group(2))
        elif name in ("get_api_token", "check_api_token"):
            ops[name] = ("POST", f"/api/v1/auth/{name}")
    return ops


def _served():
    import os

    os.environ.setdefault("ARCHIVEBOX_BASE_URL", "http://archivebox.invalid")
    _, mcp = build_server("archivebox_api", command_args=[])

    async def lists():
        return (
            await mcp.list_tools(),
            await mcp.list_prompts(),
            await mcp.list_resources(),
        )

    return asyncio.run(lists())


def _graph(*names: str) -> ox.Store:
    store = ox.Store()
    for name in names:
        store.load(path=str(PKG / "ontology" / name), format=ox.RdfFormat.TURTLE)
    return store


def _ids(store: ox.Store, kind: str) -> set[str]:
    comp = ox.NamedNode(CP + "componentId")
    out = set()
    for quad in store.quads_for_pattern(None, RDF_TYPE, ox.NamedNode(CP + kind)):
        for q in store.quads_for_pattern(quad.subject, comp, None):
            out.add(q.object.value)
    return out


@pytest.mark.spec("CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R003")
def test_one_typed_tool_per_upstream_operation():
    ops = _client_operations()
    assert set(ops.values()) == UPSTREAM
    assert len(ops) == len(UPSTREAM)
    tools, _, _ = _served()
    names = {t.name for t in tools}
    assert {f"archivebox_{op}" for op in ops} <= names
    for tool in tools:
        props = tool.parameters.get("properties", {})
        assert "action" not in props, tool.name
        assert "params_json" not in props, tool.name


@pytest.mark.spec("CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R004")
def test_results_carry_the_upstream_body():
    req = httpx.Request("GET", "http://x/api")
    ok = httpx.Response(200, json={"items": [1]}, request=req)
    assert coerce_result(ok) == {"items": [1]}
    text = httpx.Response(
        200, text="https://a\nhttps://b", headers={"content-type": "text/plain"},
        request=req,
    )
    assert coerce_result(text)["text"] == "https://a\nhttps://b"
    jsonl = httpx.Response(
        200, text='{"a":1}\n{"b":2}', headers={"content-type": "application/x-ndjson"},
        request=req,
    )
    assert coerce_result(jsonl)["text"].count("\n") == 1
    err = httpx.Response(403, text="control plane disabled", request=req)
    assert coerce_result(err) == {"status_code": 403, "error": "control plane disabled"}


@pytest.mark.spec("CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R005")
def test_cli_remove_refuses_an_empty_selection():
    api = Api(url="http://archivebox.invalid", token="t")
    with pytest.raises(ParameterError):
        api.cli_remove()


@pytest.mark.spec("CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R006")
def test_pack_contracts_cover_tools_skills_and_prompts():
    tools, prompts, _ = _served()
    store = _graph("pack.ttl", "archivebox.ttl")
    assert _ids(store, "Tool") == {t.name for t in tools}
    skills = {p.name for p in (PKG / "skills").iterdir() if (p / "SKILL.md").is_file()}
    assert _ids(store, "Skill") == skills
    packaged = {p.stem for p in (PKG / "prompts").glob("*.json")}
    assert _ids(store, "Prompt") == packaged
    assert packaged <= {p.name for p in prompts}
    served = {t.name for t in tools}
    for path in (PKG / "prompts").glob("*.json"):
        data = json.loads(path.read_text())
        own_tools = {t for t in data["tools"] if t.startswith("archivebox_")}
        assert own_tools <= served, path.name
        own_skills = {s for s in data["skills"] if s.startswith("archivebox-")}
        assert own_skills <= skills, path.name
        for tool in own_tools:
            assert tool in data["instructions"]["core_directive"], (path.name, tool)


@pytest.mark.spec("CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R007")
def test_classes_roll_up_by_subclass_and_never_import_core():
    for name in ("archivebox.ttl", "pack.ttl", "access_contracts.ttl"):
        assert "owl:imports" not in (PKG / "ontology" / name).read_text()
    store = _graph("archivebox.ttl")
    classes = [q.subject for q in store.quads_for_pattern(None, RDF_TYPE, OWL_CLASS)]
    assert classes
    for cls in classes:
        assert list(store.quads_for_pattern(cls, RDFS_SUB, None)), cls
    for core in ("WebSnapshot", "ArchiveResult", "hasArchiveResult", "sourceRef"):
        assert not list(store.quads_for_pattern(ox.NamedNode(KG + core), RDF_TYPE, None))


@pytest.mark.spec("CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R002")
def test_access_contracts_route_each_class_to_a_served_read_tool():
    from scion_sdk.access_contract import parse_access_contracts

    tools, _, _ = _served()
    served = {t.name: t for t in tools}
    contracts = parse_access_contracts(
        (PKG / "ontology" / "access_contracts.ttl").read_text()
    )
    assert {c.class_iri.rsplit("#", 1)[-1] for c in contracts} == {
        "WebSnapshot",
        "ArchiveResult",
        "ArchiveCrawl",
    }
    for contract in contracts:
        tool = served[contract.operation]
        assert tool.annotations.read_only_hint, contract.operation
        assert contract.key_field == "id"


@pytest.mark.spec("CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R008")
def test_research_archive_skill_is_served():
    _, _, resources = _served()
    uris = {str(r.uri) for r in resources}
    assert "skill://archivebox-research-archive/SKILL.md" in uris
    text = (PKG / "skills/archivebox-research-archive/SKILL.md").read_text()
    for needle in (
        "webarchiver-mcp",
        "archivebox_cli_add",
        "market-research,<subject>,<YYYY-MM-DD>",
        "archivebox_get_archiveresults",
        "archivebox_create_archiveresult",
    ):
        assert needle in text
