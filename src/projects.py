#!/usr/bin/env python3

import logging
import json
from typing import Optional
from mcp.server.fastmcp import Context

logger = logging.getLogger("todoist-mcp-server")

def todoist_get_projects(ctx: Context) -> str:
    """Get all projects from the user's Todoist account
    """
    todoist_client = ctx.request_context.lifespan_context.todoist_client

    try:
        logger.info("Getting all projects")

        # Consume iterator to flatten paginated results into single list
        projects_iterator = todoist_client.get_projects()
        all_projects = []

        for project_batch in projects_iterator:
            all_projects.extend(project_batch)
            # Break early when partial batch indicates end of results
            if len(project_batch) < 200:
                break

        if not all_projects:
            logger.info("No projects found")
            return "No projects found in your Todoist account"

        logger.info(f"Retrieved {len(all_projects)} projects")
        return json.dumps([project.to_dict() for project in all_projects], indent=2, default=str)
    except Exception as error:
        logger.error(f"Error getting projects: {error}")
        return f"Error getting projects: {str(error)}"

def todoist_get_project(ctx: Context, project_id: str) -> str:
    """Get a single project from Todoist

    Args:
        project_id: ID of the project to retrieve
    """
    todoist_client = ctx.request_context.lifespan_context.todoist_client

    try:
        logger.info(f"Getting project with ID: {project_id}")

        project = todoist_client.get_project(project_id=project_id)

        if not project:
            logger.info(f"No project found with ID: {project_id}")
            return f"No project found with ID: {project_id}"

        logger.info(f"Retrieved project: {project.id}")
        return json.dumps(project.to_dict(), indent=2, default=str)
    except Exception as error:
        logger.error(f"Error getting project: {error}")
        return f"Error getting project: {str(error)}"

def todoist_add_project(
    ctx: Context,
    name: str,
    color: Optional[str] = None,
    parent_id: Optional[str] = None,
    is_favorite: Optional[bool] = None,
    view_style: Optional[str] = None
) -> str:
    """Create a new project in Todoist

    Args:
        name: Name of the project
        color: Color of the project (optional)
        parent_id: ID of the parent project for creating sub-projects (optional)
        is_favorite: Whether the project should be marked as favorite (optional)
        view_style: View style of the project, either 'list' or 'board' (optional)
    """
    todoist_client = ctx.request_context.lifespan_context.todoist_client

    try:
        logger.info(f"Creating project: {name}")

        project_params = {
            "name": name
        }

        # Add optional parameters efficiently
        if color:
            project_params["color"] = color
        if parent_id:
            project_params["parent_id"] = parent_id
        if is_favorite is not None:
            project_params["is_favorite"] = is_favorite
        # Validate view_style against API-supported values to prevent errors
        if view_style and view_style in ["list", "board", "calendar"]:
            project_params["view_style"] = view_style

        project = todoist_client.add_project(**project_params)

        logger.info(f"Project created successfully: {project.id}")
        return json.dumps(project.to_dict(), indent=2, default=str)
    except Exception as error:
        logger.error(f"Error creating project: {error}")
        return f"Error creating project: {str(error)}"

def todoist_update_project(
    ctx: Context,
    project_id: str,
    name: Optional[str] = None,
    color: Optional[str] = None,
    is_favorite: Optional[bool] = None,
    view_style: Optional[str] = None
) -> str:
    """Update an existing project in Todoist

    Args:
        project_id: ID of the project to update
        name: New name for the project (optional)
        color: New color for the project (optional)
        is_favorite: Whether the project should be marked as favorite (optional)
        view_style: View style of the project, either 'list', 'board', or 'calendar' (optional)
    """
    todoist_client = ctx.request_context.lifespan_context.todoist_client

    try:
        logger.info(f"Updating project with ID: {project_id}")

        # Pre-fetch for validation and meaningful error messages
        try:
            project = todoist_client.get_project(project_id=project_id)
            original_name = project.name
        except Exception as error:
            logger.warning(f"Error getting project with ID: {project_id}: {error}")
            return f"Could not verify project with ID: {project_id}. Update aborted."

        update_params = {}
        if name:
            update_params["name"] = name
        if color:
            update_params["color"] = color
        if is_favorite is not None:
            update_params["is_favorite"] = is_favorite
        # Same validation as create to maintain consistency
        if view_style and view_style in ["list", "board", "calendar"]:
            update_params["view_style"] = view_style

        if len(update_params) == 0:
            return f"No update parameters provided for project: {original_name} (ID: {project_id})"

        updated_project = todoist_client.update_project(project_id, **update_params)

        logger.info(f"Project updated successfully: {project_id}")
        return json.dumps(updated_project.to_dict(), indent=2, default=str)

    except Exception as error:
        logger.error(f"Error updating project: {error}")
        return f"Error updating project: {str(error)}"

def todoist_delete_project(ctx: Context, project_id: str) -> str:
    """Deletes a project from the user's Todoist account

    Args:
        project_id: ID of the project to delete
    """
    todoist_client = ctx.request_context.lifespan_context.todoist_client

    try:
        logger.info(f"Deleting project with ID: {project_id}")

        # Capture project name for meaningful success/failure messages
        try:
            project = todoist_client.get_project(project_id=project_id)
            project_name = project.name
        except Exception as error:
            logger.warning(f"Error getting project with ID: {project_id}: {error}")
            return f"Could not verify project with ID: {project_id}. Deletion aborted."

        is_success = todoist_client.delete_project(project_id=project_id)

        logger.info(f"Project deleted successfully: {project_id} ({project_name})")
        return f"Successfully deleted project: {project_name} (ID: {project_id})"

    except Exception as error:
        logger.error(f"Error deleting project: {error}")
        return f"Error deleting project: {str(error)}"
