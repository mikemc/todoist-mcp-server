#!/usr/bin/env python3
"""
Functions for working with tasks that use the Todoist Sync endpoint.
"""

import logging
import uuid
import json
import requests
from typing import Optional, Dict, Any
from mcp.server.fastmcp import Context

logger = logging.getLogger("todoist-mcp-server")

def todoist_move_task(
    ctx: Context,
    task_id: str,
    parent_id: Optional[str] = None,
    section_id: Optional[str] = None,
    project_id: Optional[str] = None
) -> str:
    """Move a task to a different location

    Args:
        task_id: ID of the task to move
        parent_id: ID of the destination parent task (optional)
        section_id: ID of the destination section (optional)
        project_id: ID of the destination project (optional)

    Note: Only one of parent_id, section_id or project_id must be set.
    """
    todoist_client = ctx.request_context.lifespan_context.todoist_client
    api_token = todoist_client._token  # Get the API token from the client

    try:
        logger.info(f"Moving task with ID: {task_id}")

        # Verify the task exists first
        try:
            task = todoist_client.get_task(task_id=task_id)
            task_content = task.content
        except Exception as error:
            logger.warning(f"Error getting task with ID: {task_id}: {error}")
            return f"Could not verify task with ID: {task_id}. Task move aborted."

        # Count how many destination parameters are set
        destination_count = sum(1 for x in [parent_id, section_id, project_id] if x is not None)

        if destination_count != 1:
            return "Error: Exactly one of parent_id, section_id, or project_id must be specified"

        # Create move command
        command = {
            "type": "item_move",
            "uuid": str(uuid.uuid4()),
            "args": {
                "id": task_id
            }
        }

        # Add the destination parameter
        if parent_id:
            command["args"]["parent_id"] = parent_id
        elif section_id:
            command["args"]["section_id"] = section_id
        elif project_id:
            command["args"]["project_id"] = project_id

        # Create the payload for the sync API
        payload = {
            "commands": json.dumps([command])
        }

        # Make the request to the sync API
        response = requests.post(
            "https://api.todoist.com/sync/v9/sync",
            headers={"Authorization": f"Bearer {api_token}"},
            data=payload
        )

        response.raise_for_status()
        response_data = response.json()

        sync_status = response_data.get("sync_status", {}).get(command["uuid"])
        if sync_status == "ok":
            logger.info(f"Task moved successfully: {task_id}")
            return f"Successfully moved task: {task_content} (ID: {task_id})"
        else:
            error_msg = f"Error moving task: {sync_status}"
            logger.error(error_msg)
            return error_msg

    except Exception as error:
        logger.error(f"Error moving task: {error}")
        return f"Error moving task: {str(error)}"
