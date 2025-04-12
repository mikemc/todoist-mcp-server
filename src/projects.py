#!/usr/bin/env python3

import logging
from typing import Optional
from mcp.server.fastmcp import Context

logger = logging.getLogger("todoist-mcp-server")

def todoist_get_projects(ctx: Context) -> str:
    """Get all projects from the user's Todoist account

    Returns:
        A formatted list of all projects with their IDs, names, and other details
    """
    todoist_client = ctx.request_context.lifespan_context.todoist_client

    try:
        logger.info("Getting all projects")

        # Get all projects
        projects = todoist_client.get_projects()

        if not projects:
            logger.info("No projects found")
            return "No projects found in your Todoist account"

        # Format response
        project_list = []
        for project in projects:
            project_text = f"- {project.name} (ID: {project.id})"
            if hasattr(project, 'is_favorite') and project.is_favorite:
                project_text += "\n  Favorite: Yes"
            if hasattr(project, 'is_shared') and project.is_shared:
                project_text += "\n  Shared: Yes"
            if hasattr(project, 'parent_id') and project.parent_id:
                project_text += f"\n  Parent ID: {project.parent_id}"

            project_list.append(project_text)

        logger.info(f"Retrieved {len(projects)} projects")
        return "\n\n".join(project_list)
    except Exception as error:
        logger.error(f"Error getting projects: {error}")
        return f"Error getting projects: {str(error)}"

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

        # Create project parameters
        project_params = {
            "name": name
        }

        # Add optional parameters if provided
        if color:
            project_params["color"] = color
        if parent_id:
            project_params["parent_id"] = parent_id
        if is_favorite is not None:
            project_params["is_favorite"] = is_favorite
        if view_style and view_style in ["list", "board"]:
            project_params["view_style"] = view_style

        # Create the project
        project = todoist_client.add_project(**project_params)

        # Format response
        response = f"Project created:\nName: {project.name} (ID: {project.id})"
        if hasattr(project, 'color') and project.color:
            response += f"\nColor: {project.color}"
        if hasattr(project, 'parent_id') and project.parent_id:
            response += f"\nParent Project ID: {project.parent_id}"
        if hasattr(project, 'is_favorite') and project.is_favorite:
            response += "\nFavorite: Yes"
        if hasattr(project, 'view_style') and project.view_style:
            response += f"\nView Style: {project.view_style}"

        logger.info(f"Project created successfully: {project.id}")
        return response
    except Exception as error:
        logger.error(f"Error creating project: {error}")
        return f"Error creating project: {str(error)}"

def todoist_delete_project(ctx: Context, project_id: str) -> str:
    """Deletes a project from the user's Todoist account

    Args:
        project_id: ID of the project to delete
    """
    todoist_client = ctx.request_context.lifespan_context.todoist_client

    try:
        logger.info(f"Deleting project with ID: {project_id}")

        # Verify the project exists and get name
        try:
            projects = todoist_client.get_projects()
            project_to_delete = None

            for project in projects:
                if project.id == project_id:
                    project_to_delete = project
                    break

            if not project_to_delete:
                logger.warning(f"No project found with ID: {project_id}")
                return f"Could not find a project with ID: {project_id}"

            project_name = project_to_delete.name

        except Exception:
            # If we can't verify, we'll still attempt to delete
            project_name = "Unknown"

        # Delete the project
        is_success = todoist_client.delete_project(project_id=project_id)

        if is_success:
            logger.info(f"Project deleted successfully: {project_id}")
            return f"Successfully deleted project: {project_name} (ID: {project_id})"
        else:
            logger.warning(f"Project deletion failed for project ID: {project_id}")
            return "Project deletion failed"

    except Exception as error:
        logger.error(f"Error deleting project: {error}")
        return f"Error deleting project: {str(error)}"
