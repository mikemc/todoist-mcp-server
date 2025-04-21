#!/usr/bin/env python3

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass

from mcp.server.fastmcp import FastMCP
from todoist_api_python.api import TodoistAPI

from src.api import get_api_client
# Import functions directly
from src.projects import (
    todoist_get_projects,
    todoist_get_project,
    todoist_add_project,
    todoist_update_project,
    todoist_delete_project,
)
from src.sections import (
    todoist_get_sections,
    todoist_get_section,
    todoist_add_section,
    todoist_update_section,
    todoist_delete_section,
)
from src.tasks import (
    todoist_create_task,
    todoist_get_tasks,
    todoist_get_task,
    todoist_update_task,
    todoist_close_task,
    todoist_reopen_task,
    todoist_delete_task,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("todoist-mcp-server")

# Create lifespan context type for type hints
@dataclass
class TodoistContext:
    todoist_client: TodoistAPI

# Set up lifespan context manager
@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[TodoistContext]:
    """Manage application lifecycle with type-safe context"""
    # Initialize Todoist client on startup
    try:
        todoist_client = get_api_client()
        yield TodoistContext(todoist_client=todoist_client)
    finally:
        # Any cleanup needed
        logger.info("Shutting down Todoist MCP Server")

# Create an MCP server
mcp = FastMCP("Todoist MCP Server", lifespan=app_lifespan)

# Register project tools
mcp.tool()(todoist_get_projects)
mcp.tool()(todoist_get_project)
mcp.tool()(todoist_add_project)
mcp.tool()(todoist_update_project)
mcp.tool()(todoist_delete_project)

# Register section tools
mcp.tool()(todoist_get_sections)
mcp.tool()(todoist_get_section)
mcp.tool()(todoist_add_section)
mcp.tool()(todoist_update_section)
mcp.tool()(todoist_delete_section)

# Register task tools
mcp.tool()(todoist_get_tasks)
mcp.tool()(todoist_get_task)
mcp.tool()(todoist_create_task)
mcp.tool()(todoist_update_task)
mcp.tool()(todoist_close_task)
mcp.tool()(todoist_reopen_task)
mcp.tool()(todoist_delete_task)

# Run the server
if __name__ == "__main__":
    logger.info("Starting Todoist MCP Server")
    # Run with stdio transport
    mcp.run(transport='stdio')
