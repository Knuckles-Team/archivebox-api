"""Archivebox ontology contribution (CONCEPT:AU-KG.ontology.federation-provider-leg).

Data-only subpackage: it carries ``archivebox.ttl`` (the ``owl:Ontology``
``https://knuckles-team.github.io/ontology/connector/archivebox`` module) which the Arbora hub federates in via
the ``scion_sdk.ontology_providers`` entry-point. It holds no business logic
and no heavy imports so the hub can resolve it cheaply.
"""
