# CONN-ARCHIVEBOX-API-WEB-SOURCE — Archive pages as the secondary web-source backend

Owner: archivebox-api. Cross-repo IDs: `SCION-SOURCE-INGEST-R005.40`, `ARBORA-OPS-R067`, `MEDULLA-UNIFIED-DATA-PLANE-R651.7`.

Extends: [SCION-SOURCE-INGEST](https://github.com/Knuckles-Team/agent-connector-sdk/blob/main/specs/SCION-SOURCE-INGEST/spec.md)
References: [ARBORA-OPS](https://github.com/Knuckles-Team/arbora/blob/main/specs/hosted-api-operations/spec.md)

## Purpose and user stories

The archivebox-api connector serves archived pages as the secondary web-source backend. The web research operation selects it explicitly or falls back to it on a primary failure.

A person asks the platform to research a topic on the web. The platform stores each chosen page as one Document with its source URL.

## Requirements and acceptance

The rows are in [requirements.md](requirements.md). The proving tests are in [test-spec.md](test-spec.md).

## Why a new spec

The search covered `specs/` of this repository and the SDK and arbora specs. This repository had no spec for page fetch. The SDK owns only the contract (`SCION-SOURCE-INGEST-R005.40`). The behavior of this one external system belongs here.

## Scope and interfaces

In scope: the web-source tools and their mapping onto the SDK contract.

Out of scope: search, page selection, enrichment and citations. The engine owns them. Served operations belong to arbora.
