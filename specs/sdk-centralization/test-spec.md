# CONN-ARCHIVEBOX-API-SDK-CENTRALIZATION — Test specification

Governing spec: [spec.md](spec.md).

| Test ID | Requirement | Level | Setup and input | Expected observation | Evidence |
|---|---|---|---|---|---|
| T-001 | `CONN-ARCHIVEBOX-API-SDK-CENTRALIZATION-R001` | Unit | Every child row. | See each child. |  |
| T-002 | `CONN-ARCHIVEBOX-API-SDK-CENTRALIZATION-R001.1` | Unit | `tests/test_sdk_transport.py::test_package_uses_the_governed_client` | The package imports no `requests` and builds its clients with `create_http_client`. |  |
| T-003 | `CONN-ARCHIVEBOX-API-SDK-CENTRALIZATION-R001.2` | Unit | `tests/test_sdk_transport.py::test_archive_session_takes_trust_from_the_profile` | The session has no verify field and builds its client with the TLS profile. |  |
| T-004 | `CONN-ARCHIVEBOX-API-SDK-CENTRALIZATION-R001.3` | Unit | `tests/test_sdk_transport.py::test_expired_session_refreshes_once` | An expired session logs in once more, and a persistent redirect refuses. |  |
| T-005 | `CONN-ARCHIVEBOX-API-SDK-CENTRALIZATION-R001.4` | Unit | `tests/test_sdk_transport.py::test_dependencies_come_from_the_sdk` | `pyproject.toml` has no `requests` pin and the SDK floor is `0.3.11` or later. |  |
