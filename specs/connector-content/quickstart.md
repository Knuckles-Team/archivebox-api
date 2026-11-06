# CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT — Quickstart

Governing spec: [spec.md](spec.md).

## Scenario 1: the served surface matches the ArchiveBox API and the pack

Rows: `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R002` to `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R008`.

```bash
uv run --locked --extra test pytest tests/test_surface_contracts.py
```

Expected: every test passes. The server lists one typed tool per ArchiveBox
operation, the pack names every served tool, skill and prompt, the access
contracts route each class to a served read tool, and the research archive
skill is served.

## Scenario 2: live check against a deployed instance

1. `archivebox_cli_add(urls=["https://example.com"], tag="zz-validation-<date>")`.
2. `archivebox_get_snapshots(tag="zz-validation-<date>")` returns the snapshot
   body (not just a status code); wait for `status` `sealed`.
3. `archivebox_get_archiveresults(snapshot_url="https://example.com", status="succeeded")`.
4. Remove the test capture: `archivebox_cli_remove(filter_patterns=["https://example.com"], filter_type="exact", tag="zz-validation-<date>")`.
