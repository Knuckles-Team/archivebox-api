# CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT — Test specification

Governing spec: [spec.md](spec.md).

| Test ID | Requirement | Proving test | Expected observation |
|---|---|---|---|
| T-001 | `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R001` | `tests/test_default_content_surfaces.py` | The listings include the packaged skills, ontology and prompts. |

## Rows awaiting bound tests
- `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R002`: planned proof `tests/test_access_contracts.py::test_competency_contracts_certified`. Expected: each recording validates against its contract and column names equal the ontology property local names. Refusal: a contract naming a column that is not an ontology property, or lacking ac:keyField, fails certification.
