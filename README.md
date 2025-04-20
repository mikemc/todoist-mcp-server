# Todoist MCP Server (Python)

A Todoist MCP server written in Python, using the [Todoist Python API](https://developer.todoist.com/rest/v2/?python). I first created the server by using Claude to translate this [TypeScript Todoist MCP server](https://github.com/abhiz123/todoist-mcp-server) to Python. I'm gradually changing and adding functionality to suit my workflow as I experiment with using Claude to help with task management.

## Installation

### Prerequisites

* Python 3.10+
* UV package manager ([installation guide](https://docs.astral.sh/uv/getting-started/installation/))
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

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
