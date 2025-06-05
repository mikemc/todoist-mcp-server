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

### Configuration with Goose (and a local LLM)

You can use [Goose](https://block.github.io/goose/) and a local LLM provider: [LM Studio](https://lmstudio.ai/) or [Ollama](https://ollama.com/).

Configure the LLM you want Goose to use: 

`$ goose configure`

This command will ask you whether you want to use a local model or a cloud hosted model. Ensure your model provider is running your model first. Specify the address of the model API, and the model name. Many locally deployed LLMs use a format compatible with `Ollama`, so for both `LM Studio` or `Ollama` LLMs, select `Ollama`.

```bash
◇  Which model provider should we use?
│  Ollama 
│
◇  Provider Ollama requires OLLAMA_HOST, please enter a value
│  localhost:1234
│
◇  Model fetch complete
│
◇  Enter a model from that provider:
│  phi-4
```

Then run the same command again to configure the Todoist MCP: 

`$ goose configure`

This time it will ask about extensions:

```bash
◇  What would you like to configure?
│  Add Extension 
│
◇  What type of extension would you like to add?
│  Command-line Extension 
│
◇  What would you like to call this extension?
│  todoist
│
◇  What command should be run?
│  uvx git+https://github.com/mikemc/todoist-mcp-server
│
◇  Please set the timeout for this tool (in secs):
│  60
│
◇  Would you like to add a description?
│  No 
│
◇  Would you like to add environment variables?
│  Yes 
│
◇  Environment variable name:
│  TODOIST_API_TOKEN
│
◇  Environment variable value:
│  ▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪▪
│
◇  Add another environment variable?
│  No 
│
└  Added todoist extension
```

Now you can run `goose` and ask it questions about your todo list, or make changes.
```bash
$ goose          
starting session | provider: ollama model: phi-4
    logging to ******
    working directory: ******

Goose is running! Enter your instructions, or try asking what goose can do.

( O)> how many todo list tasks have I completed in the last 7 days

─── todoist_get_tasks | todoist ──────────────────────────
filter: last 7 days completed

...
*Ideally* You have been very busy this week. You have completed 15 tasks! Listed below are the tasks.
...
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
