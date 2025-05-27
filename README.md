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

Add the MCP server to your claude_desktop_config.json,

```json
{
  "mcpServers": {
    "todoist": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/mikemc/todoist-mcp-server",
        "todoist-mcp"
      ],
      "env": {
        "TODOIST_API_TOKEN": "your_todoist_api_token"
      }
    }
  }
}
```

Or, to run from a local copy,

```json
{
  "mcpServers": {
    "todoist": {
      "command": "uvx",
      "args": [
        "--from",
        "/absolute/path/to/todoist-mcp-server",
        "todoist-mcp"
      ],
      "env": {
        "TODOIST_API_TOKEN": "your_todoist_api_token"
      }
    }
  }
}
```

## Available Tools

To see currently available tools, run

```sh
# With GNU grep installed as ggrep (as with `brew install grep` on Mac)
ggrep -Po '(?<=^mcp.tool\(\)\()([^)]+)' src/main.py
```

As of 2025-05-26,

- Projects
  - `todoist_get_projects`
  - `todoist_get_project`
  - `todoist_add_project`
  - `todoist_update_project`
  - `todoist_delete_project`
- Sections
  - `todoist_get_sections`
  - `todoist_get_section`
  - `todoist_add_section`
  - `todoist_update_section`
  - `todoist_delete_section`
- Tasks
  - `todoist_get_task`
  - `todoist_get_tasks`
  - `todoist_filter_tasks`
  - `todoist_add_task`
  - `todoist_update_task`
  - `todoist_complete_task`
  - `todoist_uncomplete_task`
  - `todoist_move_task`
  - `todoist_delete_task`
- Comments
  - `todoist_get_comment`
  - `todoist_get_comments`
  - `todoist_add_comment`
  - `todoist_update_comment`
  - `todoist_delete_comment`

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
