#!/usr/bin/env python3

import logging
from typing import Optional
from mcp.server.fastmcp import Context

logger = logging.getLogger("todoist-mcp-server")

def todoist_get_sections(ctx: Context, project_id: Optional[str] = None) -> str:
    """Get all sections from the user's Todoist account

    Args:
        project_id: Filter sections by project ID (optional)
    """
    todoist_client = ctx.request_context.lifespan_context.todoist_client

    try:
        logger.info(f"Getting sections{' for project ID: ' + project_id if project_id else ''}")

        # Create parameters dictionary
        params = {}
        if project_id:
            params["project_id"] = project_id

        # Get sections
        sections = todoist_client.get_sections(**params)

        if not sections:
            logger.info("No sections found")
            return "No sections found" + (f" in project ID: {project_id}" if project_id else "")

        logger.info(f"Retrieved {len(sections)} sections")
        return sections
    except Exception as error:
        logger.error(f"Error getting sections: {error}")
        return f"Error getting sections: {str(error)}"

def todoist_get_section(ctx: Context, section_id: str) -> str:
    """Get a single section from Todoist

    Args:
        section_id: ID of the section to retrieve
    """
    todoist_client = ctx.request_context.lifespan_context.todoist_client

    try:
        logger.info(f"Getting section with ID: {section_id}")

        # Get the section
        section = todoist_client.get_section(section_id=section_id)

        if not section:
            logger.info(f"No section found with ID: {section_id}")
            return f"No section found with ID: {section_id}"

        logger.info(f"Retrieved section: {section.id}")
        return section
    except Exception as error:
        logger.error(f"Error getting section: {error}")
        return f"Error getting section: {str(error)}"

def todoist_add_section(
    ctx: Context,
    name: str,
    project_id: str,
    order: Optional[int] = None
) -> str:
    """Create a new section in Todoist

    Args:
        name: Section name
        project_id: Project ID this section should belong to
        order: Order among other sections in a project (optional)
    """
    todoist_client = ctx.request_context.lifespan_context.todoist_client

    try:
        logger.info(f"Creating section '{name}' in project ID: {project_id}")

        # Create section parameters
        section_params = {
            "name": name,
            "project_id": project_id
        }

        # Add optional parameters if provided
        if order is not None:
            section_params["order"] = order

        # Create the section
        section = todoist_client.add_section(**section_params)

        logger.info(f"Section created successfully: {section.id}")
        return section
    except Exception as error:
        logger.error(f"Error creating section: {error}")
        return f"Error creating section: {str(error)}"

def todoist_update_section(ctx: Context, section_id: str, name: str) -> str:
    """Updates a section in Todoist

    Args:
        section_id: ID of the section to update
        name: New name for the section
    """
    todoist_client = ctx.request_context.lifespan_context.todoist_client

    try:
        logger.info(f"Updating section with ID: {section_id}")

        # Verify the section exists
        try:
            sections = todoist_client.get_sections()
            section_to_update = None

            for section in sections:
                if section.id == section_id:
                    section_to_update = section
                    break

            if not section_to_update:
                logger.warning(f"No section found with ID: {section_id}")
                return f"Could not find a section with ID: {section_id}"

            old_name = section_to_update.name

        except Exception:
            # If we can't verify, we'll still attempt to update
            old_name = "Unknown"

        # Update the section
        updated_section = todoist_client.update_section(section_id=section_id, name=name)

        logger.info(f"Section updated successfully: {section_id}")
        return f"Successfully updated section from '{old_name}' to '{name}' (ID: {section_id})"

    except Exception as error:
        logger.error(f"Error updating section: {error}")
        return f"Error updating section: {str(error)}"

def todoist_delete_section(ctx: Context, section_id: str) -> str:
    """Deletes a section from Todoist

    Args:
        section_id: ID of the section to delete
    """
    todoist_client = ctx.request_context.lifespan_context.todoist_client

    try:
        logger.info(f"Deleting section with ID: {section_id}")

        # Verify the section exists and get name
        try:
            sections = todoist_client.get_sections()
            section_to_delete = None

            for section in sections:
                if section.id == section_id:
                    section_to_delete = section
                    break

            if not section_to_delete:
                logger.warning(f"No section found with ID: {section_id}")
                return f"Could not find a section with ID: {section_id}"

            section_name = section_to_delete.name
            project_id = section_to_delete.project_id

        except Exception:
            # If we can't verify, we'll still attempt to delete
            section_name = "Unknown"
            project_id = "Unknown"

        # Delete the section
        is_success = todoist_client.delete_section(section_id=section_id)

        if is_success:
            logger.info(f"Section deleted successfully: {section_id}")
            return f"Successfully deleted section: {section_name} (ID: {section_id}) from project ID: {project_id}"
        else:
            logger.warning(f"Section deletion failed for section ID: {section_id}")
            return "Section deletion failed"

    except Exception as error:
        logger.error(f"Error deleting section: {error}")
        return f"Error deleting section: {str(error)}"
