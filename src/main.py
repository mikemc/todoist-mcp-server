#!/usr/bin/env python3

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass

from mcp.server.fastmcp import FastMCP
from todoist_api_python.api import TodoistAPI

from .api import get_api_client
from .projects import (
    todoist_get_projects,
    todoist_get_project,
    todoist_add_project,
    todoist_update_project,
    todoist_delete_project,
)
from .sections import (
    todoist_get_sections,
    todoist_get_section,
    todoist_add_section,
    todoist_update_section,
    todoist_delete_section,
)
from .tasks import (
    todoist_get_task,
    todoist_get_tasks,
    todoist_filter_tasks,
    todoist_add_task,
    todoist_update_task,
    todoist_complete_task,
    todoist_uncomplete_task,
    todoist_move_task,
    todoist_delete_task,
)

from .comments import (
    todoist_get_comment,
    todoist_get_comments,
    todoist_add_comment,
    todoist_update_comment,
    todoist_delete_comment,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("todoist-mcp-server")

@dataclass
class TodoistContext:
    """Type-safe container for shared application context across MCP tool calls"""
    todoist_client: TodoistAPI

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[TodoistContext]:
    """Manage application lifecycle with proper resource initialization and cleanup"""
    try:
        # Initialize API client once and share across all tool invocations for efficiency
        todoist_client = get_api_client()
        yield TodoistContext(todoist_client=todoist_client)
    finally:
        # Placeholder for any needed cleanup - current client doesn't require explicit cleanup
        logger.info("Shutting down Todoist MCP Server")

# Initialize MCP server with lifecycle management
mcp = FastMCP("Todoist MCP Server", lifespan=app_lifespan)

# Register all tools using decorator pattern for automatic tool discovery
mcp.tool()(todoist_get_projects)
mcp.tool()(todoist_get_project)
mcp.tool()(todoist_add_project)
mcp.tool()(todoist_update_project)
mcp.tool()(todoist_delete_project)

mcp.tool()(todoist_get_sections)
mcp.tool()(todoist_get_section)
mcp.tool()(todoist_add_section)
mcp.tool()(todoist_update_section)
mcp.tool()(todoist_delete_section)

mcp.tool()(todoist_get_task)
mcp.tool()(todoist_get_tasks)
mcp.tool()(todoist_filter_tasks)
mcp.tool()(todoist_add_task)
mcp.tool()(todoist_update_task)
mcp.tool()(todoist_complete_task)
mcp.tool()(todoist_uncomplete_task)
mcp.tool()(todoist_move_task)
mcp.tool()(todoist_delete_task)

mcp.tool()(todoist_get_comment)
mcp.tool()(todoist_get_comments)
mcp.tool()(todoist_add_comment)
mcp.tool()(todoist_update_comment)
mcp.tool()(todoist_delete_comment)

def main():
    logger.info("Starting Todoist MCP Server")
    # Use stdio transport for Claude Desktop integration
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
