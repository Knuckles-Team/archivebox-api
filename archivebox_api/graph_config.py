"""ArchiveBox graph configuration — tag prompts and env var mappings.

This is the only file needed to enable graph mode for this agent.
Provides TAG_PROMPTS and TAG_ENV_VARS for create_graph_agent_server().
"""

TAG_PROMPTS: dict[str, str] = {
    "authentication": (
        "You are a ArchiveBox Authentication specialist. Help users manage and interact with Authentication functionality using the available tools."
    ),
    "cli": (
        "You are a ArchiveBox Cli specialist. Help users manage and interact with Cli functionality using the available tools."
    ),
    "core": (
        "You are a ArchiveBox Core specialist. Help users manage and interact with Core functionality using the available tools."
    ),
}


TAG_ENV_VARS: dict[str, str] = {
    "authentication": "AUTHENTICATIONTOOL",
    "cli": "CLITOOL",
    "core": "CORETOOL",
}
