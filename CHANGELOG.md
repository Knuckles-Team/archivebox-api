# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.5.7] - 2026-10-27

### Added
- Add the ArchiveBox rapid-delivery development skill and its package-content contract test.

## [2.5.6] - 2026-10-24

### Changed
- Central connector migration: requires `agent-connector-sdk>=0.5.3`; server bootstrap, version, containers, ontology artifacts, security scaffold and pre-commit config are provided centrally.

## [2.5.5] - 2026-10-23

### Changed
- Requires `agent-connector-sdk>=0.4.1`; data sources are declared in code (`connector_sources`).

## [Unreleased]

### Added
- None

## [0.14.0] - 2026-05-22

### Added
- Explicit ecosystem **Concept Traceability** decoration across all code, tests, and documentation, covering:
  - `ECO-4.0` (Tool Interface & MCP Factory)
  - `ECO-4.1` (A2A Network & Consensus)
  - `OS-5.1` (Security & Auth)
  - `OS-5.4` (Telemetry & Observability)
- Brand new `conftest.py` containing reusable fixtures (`mock_client`, `mock_context`, and `temp_env`) to simplify the test suite.
- Parameterized HTTP response exception mappings using `@pytest.mark.parametrize` for clean data-driven test coverage.
- Fully documented environment variables and fallbacks (like `ARCHIVEBOX_URL`) in `.env.example` and `README.md`.
- Interactive Table of Contents and concrete usage examples with markdown code blocks in `README.md`.

### Fixed
- Outdated internal documentation page links in `README.md`.
- Unregistered concept pytest warnings by explicitly registering the custom marker in `pytest.ini`.

### Changed
- Refactored `tests/test_archivebox_coverage_extra.py` to achieve full compliance with standard repository structures, reaching a Grade Point Average (GPA) of **3.8/4.0+**.

## [0.1.54] - 2026-04-29

### Added
- Initial release of the `archivebox-api` package.
