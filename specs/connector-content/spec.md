# CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT — The connector serves its packaged content

Owner: archivebox-api. Cross-repo IDs: `SCION-CONNECTOR-CONTROL-R071`, `SCION-CONNECTOR-CONTROL-R073`.

## Purpose and user stories

The `archivebox-mcp` server serves its packaged skills, prompts and ontology to any client, with no wiring of its own.

## Why a new spec

The specs of this repository were read; none owns this capability. This spec states it for this connector only.

## Scope and interfaces

In scope: the rows of [requirements.md](requirements.md). Out of scope: the SDK modules and the engine, which own the shared capabilities.

## User Scenarios & Testing

### User Story 1 - The connector serves its packaged content (Priority: P1)

The `archivebox-mcp` server serves its packaged skills, prompts and ontology to any client, with no wiring of its own.

**Acceptance Scenarios**:

1. **Given** the connector is configured, **When** the behaviour of row `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R001` (default content) is exercised, **Then** `resources/list` includes `skill://` and `ontology://`; `prompts/list` includes each packaged prompt.
2. **Given** the connector is configured, **When** the behaviour of row `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R002` (declare access contracts for the competency reads of archivebox-api) is exercised, **Then** each access contract names a served read-only tool keyed on `id`.
3. **Given** the connector is configured, **When** the behaviour of row `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R003` (one typed tool per archivebox api operation) is exercised, **Then** the set of `(verb, path)` of the client methods equals the upstream operation set, every one is served, and no served tool has an `action` or `params_json` input.
4. **Given** the connector is configured, **When** the behaviour of row `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R004` (tool results carry the upstream body) is exercised, **Then** jSON, text, JSON Lines and error responses coerce as stated.
5. **Given** the connector is configured, **When** the behaviour of row `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R005` (selection removal never removes everything) is exercised, **Then** `cli_remove()` with no selection raises.
6. **Given** the connector is configured, **When** the behaviour of row `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R006` (tool-use contracts and prompt/skill/tool links) is exercised, **Then** the pack's tool, skill and prompt ids equal the served tools, packaged skills and packaged prompts; every archivebox tool and skill a prompt names is served and its tools appear in its directive.
7. **Given** the connector is configured, **When** the behaviour of row `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R007` (classes roll up to medulla core by subclassing) is exercised, **Then** every declared class has a superclass, no core term is redeclared and no file imports.
8. **Given** the connector is configured, **When** the behaviour of row `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R008` (research archive skill) is exercised, **Then** the skill is served as `skill://archivebox-research-archive/SKILL.md` and names both connectors' tools and the tag scheme.

### Edge Cases

- If `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R001` is not met, its proving test fails: default content.
- If `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R002` is not met, its proving test fails: declare access contracts for the reads of archivebox-api.
- If `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R003` is not met, its proving test fails: one typed tool per archivebox api operation.
- If `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R004` is not met, its proving test fails: tool results carry the upstream body.
- If `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R005` is not met, its proving test fails: selection removal never removes everything.
- If `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R006` is not met, its proving test fails: tool-use contracts and prompt/skill/tool links.
- If `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R007` is not met, its proving test fails: classes roll up to medulla core by subclassing.
- If `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R008` is not met, its proving test fails: research archive skill.

## Requirements

- **FR-001**: Default content. Rows: `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R001`.
- **FR-002**: Declare access contracts for the reads of archivebox-api. Rows: `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R002`.
- **FR-003**: One typed tool per ArchiveBox API operation. Rows: `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R003`.
- **FR-004**: Tool results carry the upstream body. Rows: `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R004`.
- **FR-005**: Selection removal never removes everything. Rows: `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R005`.
- **FR-006**: Tool-use contracts and prompt/skill/tool links. Rows: `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R006`.
- **FR-007**: Classes roll up to medulla core by subclassing. Rows: `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R007`.
- **FR-008**: Research archive skill. Rows: `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R008`.

## Success Criteria

- **SC-001**: `resources/list` includes `skill://` and `ontology://`; `prompts/list` includes each packaged prompt. Rows: `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R001`.
- **SC-002**: Each access contract names a served read-only tool keyed on `id`. Rows: `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R002`.
- **SC-003**: One typed tool per ArchiveBox API operation holds; its proving test passes. Rows: `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R003`.
- **SC-004**: Tool results carry the upstream body holds; its proving test passes. Rows: `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R004`.
- **SC-005**: Selection removal never removes everything holds; its proving test passes. Rows: `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R005`.
- **SC-006**: Tool-use contracts and prompt/skill/tool links holds; its proving test passes. Rows: `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R006`.
- **SC-007**: Classes roll up to medulla core by subclassing holds; its proving test passes. Rows: `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R007`.
- **SC-008**: Research archive skill holds; its proving test passes. Rows: `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R008`.

## Assumptions

- The external system is reachable with operator-supplied credentials.
- The SDK and engine contracts the rows cite are at the floors declared in `pyproject.toml`.

## Traceability

| Label | Rows | Design section | Test ID | Evidence |
|---|---|---|---|---|
| FR-001 | `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R001` | [plan.md](plan.md) | T-001 | [test-spec.md](test-spec.md) |
| FR-002 | `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R002` | [plan.md](plan.md) | T-002 | [test-spec.md](test-spec.md) |
| FR-003 | `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R003` | [plan.md](plan.md) | T-003 | [test-spec.md](test-spec.md) |
| FR-004 | `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R004` | [plan.md](plan.md) | T-004 | [test-spec.md](test-spec.md) |
| FR-005 | `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R005` | [plan.md](plan.md) | T-005 | [test-spec.md](test-spec.md) |
| FR-006 | `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R006` | [plan.md](plan.md) | T-006 | [test-spec.md](test-spec.md) |
| FR-007 | `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R007` | [plan.md](plan.md) | T-007 | [test-spec.md](test-spec.md) |
| FR-008 | `CONN-ARCHIVEBOX-API-CONNECTOR-CONTENT-R008` | [plan.md](plan.md) | T-008 | [test-spec.md](test-spec.md) |
