# CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT — Test specification

Governing spec: [spec.md](spec.md).

| Test ID | Requirement | Proving test | Expected observation |
|---|---|---|---|
| T-001 | `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R001` | `tests/test_default_content_surfaces.py` | The listings include the packaged skills, ontology and prompts. |
| T-002 | `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R002` | `tests/test_surface_contracts.py::test_access_contracts_route_each_class_to_a_served_read_tool` | The row's acceptance holds. |
| T-003 | `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R003` | `tests/test_surface_contracts.py::test_one_typed_tool_per_upstream_operation` | The row's acceptance holds. |
| T-004 | `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R004` | `tests/test_surface_contracts.py::test_results_carry_the_upstream_body` | The row's acceptance holds. |
| T-005 | `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R005` | `tests/test_surface_contracts.py::test_cli_remove_refuses_an_empty_selection` | The row's acceptance holds. |
| T-006 | `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R006` | `tests/test_surface_contracts.py::test_pack_contracts_cover_tools_skills_and_prompts` | The row's acceptance holds. |
| T-007 | `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R007` | `tests/test_surface_contracts.py::test_classes_roll_up_by_subclass_and_never_import_core` | The row's acceptance holds. |
| T-008 | `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R008` | `tests/test_surface_contracts.py::test_research_archive_skill_is_served` | The row's acceptance holds. |
