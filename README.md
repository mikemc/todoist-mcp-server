# Todoist MCP Server (Python)

This is a Python port of this [TypeScript Todoist MCP server](https://github.com/abhiz123/todoist-mcp-server). The port was created with Claude to provide the same functionality while leveraging the Python MCP SDK and Todoist Python API.

## Installation

### Prerequisites

* Python 3.10+
* UV package manager ([installation guide](https://docs.astral.sh/uv/installation/))
* Todoist API token

### Getting a Todoist API Token

1. Log in to your Todoist account
2. Go to Settings → Integrations
3. Find your API token under "Developer"

### Configuration with Claude Desktop

Add to your claude_desktop_config.json:

```json
{
  "mcpServers": {
    "todoist": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/todoist-mcp-server",
        "run",
        "main.py"
      ],
      "env": {
        "TODOIST_API_TOKEN": "your_todoist_api_token"
      }
    }
  }
}
```

## Available Tools

To see currently available tools,

```sh
# (For Mac) With GNU grep installed as ggrep
ggrep -Po '(?<=^mcp.tool\(\)\()([^)]+)' main.py
```
