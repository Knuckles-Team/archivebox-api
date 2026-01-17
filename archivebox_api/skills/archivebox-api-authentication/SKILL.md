---
name: archivebox-api-authentication
description: Archivebox Api Authentication capabilities for A2A Agent.
---
### Overview
This skill provides access to authentication operations.

### Capabilities
- **get_api_token**: Generate an API token for a given username & password.
- **check_api_token**: Validate an API token to make sure it's valid and non-expired.

### Common Tools
- `get_api_token`: Generate an API token for a given username & password.
- `check_api_token`: Validate an API token to make sure it's valid and non-expired.

### Usage Rules
- Use these tools when the user requests actions related to **authentication**.
- Always interpret the output of these tools to provide a concise summary to the user.

### Example Prompts
- "Please check api token"
- "Please get api token"
