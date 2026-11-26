---
name: archivebox-api-operations
skill_type: skill
description: >-
  Operate archivebox-api through its governed MCP and Arbora capabilities, including web archiving, snapshot search, the research archive, archive administration and KG ingestion. Use when a request requires this provider's read, change, automation, ingestion, troubleshooting, or evidence workflows.
---

# Archivebox Api Operations

Use the provider's governed MCP tools through Arbora delegation.

## Steps

1. Establish the verified GraphSession and tenant with `manage(intent="session")`. Verify the response names the expected tenant.
2. Discover the typed tools with `find(intent="archivebox")`. Verify the tool name and schema you plan to use appear in the result.
3. Inspect read-only first, for example `archivebox_get_snapshots`(tag). Verify the result lists the records you will act on.
4. Run a change through `act(op="fleet.call")` after previewing its plan. Verify the plan names the exact records and that destructive ones were approved.
5. Read the result back with `archivebox_get_snapshot`(snapshot_id). Verify the durable record shows the new state before reporting completion.

## Failure recovery

| Failure | Cause | Recovery |
|---|---|---|
| Tool not found | The tool name is stale | Rediscover with `find(intent="archivebox")` and use the returned op id. |
| 403 from ArchiveBox | The write went to a host other than the configured one | Check the configured base URL setting and send writes only to that instance. |
| Destructive call refused | Approval or confirmation was not given | Ask the user to approve the named target and resubmit the previewed plan with `execute=true`. |

## Workflow

1. Establish the verified GraphSession and tenant before discovery or retrieval.
2. Discover the current typed tool surface (one tool per ArchiveBox operation); never assume a stale tool name or schema.
3. Prefer read-only inspection first. For changes, present impact and use the provider's
   dry-run or preview mode when available.
4. Execute mutations as fenced WorkItems so retries remain idempotent and auditable.
5. Ingest source data only through the signed connector preset and ChangeEnvelope path.
6. Verify the durable result and its trace/evidence before reporting completion.

## Safety contract

- Never persist credentials, endpoints, raw personal identifiers, hostnames, or local paths.
- Resolve TLS trust and verification from environment/configuration; never hardcode bypasses.
- Treat unknown ACL, tenant, schema, or tool-contract state as a hard failure.
- Require explicit approval for destructive, externally visible, or irreversible actions.
- Keep runtime traces policy-scoped and privacy-sanitized.

## Specialized workflows

Read [the workflow catalog](references/catalog.md) only when the request needs a
provider-specific procedure, parameter map, script, or reference asset.
