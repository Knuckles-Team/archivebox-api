# CONN-ARCHIVEBOX-API-WEB-SOURCE — Data model

Entities, classes and tables this spec adds, one section per row.

## CONN-ARCHIVEBOX-API-WEB-SOURCE-R001.7

Row title: Ingest mappings.

Definition from the row: Ingest mappings. The server must serve `manifest://connector` from `archivebox_api/connector_manifest.yml` through the SDK content registration, and the manifest must declare `schema_mappings` for the `Document` and `Chunk` record types mapped to the core classes, so `SourceIngest` resolves `manifes.
