# MCP_AGENTS.md - Dynamic Agent Registry

This file tracks the generated agents from MCP servers. You can manually modify the 'Tools' list to customize agent expertise.

## Agent Mapping Table

| Name | Description | System Prompt | Tools | Tag | Source MCP |
|------|-------------|---------------|-------|-----|------------|
| Archivebox Authentication Specialist | Expert specialist for authentication domain tasks. | You are a Archivebox Authentication specialist. Help users manage and interact with Authentication functionality using the available tools. | archivebox-mcp_authentication_toolset | authentication | archivebox-mcp |
| Archivebox Cli Specialist | Expert specialist for cli domain tasks. | You are a Archivebox Cli specialist. Help users manage and interact with Cli functionality using the available tools. | archivebox-mcp_cli_toolset | cli | archivebox-mcp |
| Archivebox Misc Specialist | Expert specialist for misc domain tasks. | You are a Archivebox Misc specialist. Help users manage and interact with Misc functionality using the available tools. | archivebox-mcp_misc_toolset | misc | archivebox-mcp |
| Archivebox Core Specialist | Expert specialist for core domain tasks. | You are a Archivebox Core specialist. Help users manage and interact with Core functionality using the available tools. | archivebox-mcp_core_toolset | core | archivebox-mcp |

## Tool Inventory Table

| Tool Name | Description | Tag | Source |
|-----------|-------------|-----|--------|
| archivebox-mcp_authentication_toolset | Static hint toolset for authentication based on config env. | authentication | archivebox-mcp |
| archivebox-mcp_cli_toolset | Static hint toolset for cli based on config env. | cli | archivebox-mcp |
| archivebox-mcp_misc_toolset | Static hint toolset for misc based on config env. | misc | archivebox-mcp |
| archivebox-mcp_core_toolset | Static hint toolset for core based on config env. | core | archivebox-mcp |
