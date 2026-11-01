# CONN-ARCHIVEBOX-API-WEB-SOURCE — Archive pages as the secondary web-source backend

Owner: archivebox-api. Cross-repo IDs: `SCION-SOURCE-INGEST-R005.40`, `ARBORA-OPS-R067`, `MEDULLA-UNIFIED-DATA-PLANE-R651.7`.

Extends: [SCION-SOURCE-INGEST](https://github.com/Knuckles-Team/scion-sdk/blob/main/specs/SCION-SOURCE-INGEST/spec.md)
References: [ARBORA-OPS](https://github.com/Knuckles-Team/arbora/blob/main/specs/hosted-api-operations/spec.md)

## Purpose and user stories

The archivebox-api connector serves archived pages as the secondary web-source backend. The web research operation selects it explicitly or falls back to it on a primary failure.

A person asks the platform to research a topic on the web. The platform stores each chosen page as one Document with its source URL.

## Why a new spec

The search covered `specs/` of this repository and the SDK and arbora specs. This repository had no spec for page fetch. The SDK owns only the contract (`SCION-SOURCE-INGEST-R005.40`). The behavior of this one external system belongs here.

## Scope and interfaces

In scope: the web-source tools and their mapping onto the SDK contract.

Out of scope: search, page selection, enrichment and citations. The engine owns them. Served operations belong to arbora.

## User Scenarios & Testing

### User Story 1 - Archive pages as the secondary web-source backend (Priority: P1)

The archivebox-api connector serves archived pages as the secondary web-source backend. The web research operation selects it explicitly or falls back to it on a primary failure.

**Acceptance Scenarios**:

1. **Given** the connector is configured, **When** the behaviour of row `CONN-ARCHIVEBOX-API-WEB-SOURCE-R001` (archived pages answer through the web-source contract (rollup)) is exercised, **Then** see each child.

### Edge Cases

- If `CONN-ARCHIVEBOX-API-WEB-SOURCE-R001` is not met, its proving test fails: archived pages answer through the web-source contract (rollup).

## Requirements

- **FR-001**: Archived pages answer through the web-source contract (rollup). Rows: `CONN-ARCHIVEBOX-API-WEB-SOURCE-R001`.

## Success Criteria

- **SC-001**: See each child. Rows: `CONN-ARCHIVEBOX-API-WEB-SOURCE-R001`.

## Assumptions

- The external system is reachable with operator-supplied credentials.
- The SDK and engine contracts the rows cite are at the floors declared in `pyproject.toml`.

## Traceability

| Label | Rows | Design section | Test ID | Evidence |
|---|---|---|---|---|
| FR-001 | `CONN-ARCHIVEBOX-API-WEB-SOURCE-R001` | [plan.md](plan.md) | T-001 | [test-spec.md](test-spec.md) |
