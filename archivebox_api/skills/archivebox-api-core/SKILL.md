---
name: archivebox-api-core
description: Archivebox Api Core capabilities for A2A Agent.
---
### Overview
This skill provides access to core operations.

### Capabilities
- **get_snapshots**: Retrieve list of snapshots.
- **get_snapshot**: Get a specific Snapshot by abid or id.
- **get_archiveresults**: List all ArchiveResult entries matching these filters.
- **get_tag**: Get a specific Tag by id or abid.
- **get_any**: Get a specific Snapshot, ArchiveResult, or Tag by abid.

### Common Tools
- `get_snapshots`: Retrieve list of snapshots.
- `get_snapshot`: Get a specific Snapshot by abid or id.
- `get_archiveresults`: List all ArchiveResult entries matching these filters.
- `get_tag`: Get a specific Tag by id or abid.
- `get_any`: Get a specific Snapshot, ArchiveResult, or Tag by abid.

### Usage Rules
- Use these tools when the user requests actions related to **core**.
- Always interpret the output of these tools to provide a concise summary to the user.

### Example Prompts
- "Please get snapshots"
- "Please get snapshot"
- "Please get archiveresults"
- "Please get any"
- "Please get tag"
