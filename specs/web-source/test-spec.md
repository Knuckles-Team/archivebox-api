# CONN-ARCHIVEBOX-API-WEB-SOURCE — Test specification

Governing spec: [spec.md](spec.md).

| Test ID | Requirement | Level | Setup and input | Expected observation | Evidence |
|---|---|---|---|---|---|
| T-001 | `CONN-ARCHIVEBOX-API-WEB-SOURCE-R001` | Unit | Every child row. | See each child. |  |
| T-002 | `CONN-ARCHIVEBOX-API-WEB-SOURCE-R001.1` | Unit | `tests/test_web_source.py::test_tool_schemas_match_contract` | Each tool schema equals the contract schema. |  |
| T-003 | `CONN-ARCHIVEBOX-API-WEB-SOURCE-R001.2` | Unit | `tests/test_web_source.py::test_add_reuses_existing_snapshot` | Two calls for one URL leave one snapshot. |  |
| T-004 | `CONN-ARCHIVEBOX-API-WEB-SOURCE-R001.3` | Unit | `tests/test_web_source.py::test_status_poll_and_timeout` | A complete snapshot returns, and a stalled snapshot refuses with `upstream_failed`. |  |
| T-005 | `CONN-ARCHIVEBOX-API-WEB-SOURCE-R001.4` | Unit | `tests/test_web_source.py::test_extract_reads_archive_results` | The result carries the text, the metadata and the digest of the fixture snapshot. |  |
| T-006 | `CONN-ARCHIVEBOX-API-WEB-SOURCE-R001.5` | Unit | `tests/test_web_source.py::test_refusals_and_provenance` | Each case returns its reason, and each result names its snapshot. |  |
| T-007 | `CONN-ARCHIVEBOX-API-WEB-SOURCE-R001.6` | Served | `tests/test_web_source_served.py::test_archivebox_run_and_forced_fallback` | Both runs store a Document equal to the primary run, except for `backend=archivebox`. |  |
| T-008 | `CONN-ARCHIVEBOX-API-WEB-SOURCE-R001.7` | Unit | `tests/test_web_source.py::test_served_manifest_maps_document_and_chunk` | The served manifest maps Document and Chunk to the core classes. |  |
| T-009 | `CONN-ARCHIVEBOX-API-WEB-SOURCE-R001.8` | Unit | `tests/test_conformance.py::test_archivebox_conforms_to_the_web_source_contract` | The kit reports no broken obligation. |  |
