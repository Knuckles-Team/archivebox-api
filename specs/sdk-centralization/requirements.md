# CONN-ARCHIVEBOX-API-SDK-CENTRALIZATION — Requirements

Governing spec: [spec.md](spec.md).

Each row is one requirement. A child row `.n` is one five-minute unit of work. A row names the file it touches and the test that proves it. The generator sets each row's state in `status.json`.

| ID | Requirement | Acceptance |
|---|---|---|
| `CONN-ARCHIVEBOX-API-SDK-CENTRALIZATION-R001` | **Capabilities come from the SDK (rollup).** The connector must use the SDK for HTTP, retry, TLS and optional dependencies. Children `.1` to `.4` deliver it. | See each child. |
| `CONN-ARCHIVEBOX-API-SDK-CENTRALIZATION-R001.1` | **Governed client.** The API client and the archive session must send HTTP through the SDK governed client and must not import `requests` (`SDK-CENTRALIZED-CAPABILITIES-R001`, `SDK-CENTRALIZED-CAPABILITIES-R003`). The robots.txt read must use the same client. Proving test: `tests/test_sdk_transport.py::test_package_uses_the_governed_client`. | The package imports no `requests` and builds its clients with `create_http_client`. |
| `CONN-ARCHIVEBOX-API-SDK-CENTRALIZATION-R001.2` | **TLS profile only.** Transport trust must come from `resolve_tls_profile` for the `archivebox` prefix (`SDK-CENTRALIZED-CAPABILITIES-R008`). The archive session must not accept a `verify` option. Proving test: `tests/test_sdk_transport.py::test_archive_session_takes_trust_from_the_profile`. | The session has no verify field and builds its client with the TLS profile. |
| `CONN-ARCHIVEBOX-API-SDK-CENTRALIZATION-R001.3` | **One session refresh.** A read redirected to the login page must log in again and read once more. It must refuse with `upstream_failed` when the second read is still redirected. Transport retries belong to the SDK client, not to a connector loop. Proving test: `tests/test_sdk_transport.py::test_expired_session_refreshes_once`. | An expired session logs in once more, and a persistent redirect refuses. |
| `CONN-ARCHIVEBOX-API-SDK-CENTRALIZATION-R001.4` | **SDK floor.** The package must depend on `agent-connector-sdk[mcp]` at the latest release floor and must not pin `requests` (`SDK-CENTRALIZED-CAPABILITIES-R040`). Proving test: `tests/test_sdk_transport.py::test_dependencies_come_from_the_sdk`. | `pyproject.toml` has no `requests` pin and the SDK floor is `0.3.11` or later. |
