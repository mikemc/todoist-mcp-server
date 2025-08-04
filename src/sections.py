#!/usr/bin/env python3

import logging
import json
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

        # Use same pagination pattern as projects for consistency
        sections_iterator = todoist_client.get_sections(project_id=project_id)
        all_sections = []

        for section_batch in sections_iterator:
            all_sections.extend(section_batch)
            if len(section_batch) < 200:
                break

        if not all_sections:
            logger.info("No sections found")
            return "No sections found" + (f" in project ID: {project_id}" if project_id else "")

        logger.info(f"Retrieved {len(all_sections)} sections")
        return json.dumps([section.to_dict() for section in all_sections], indent=2, default=str)
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

        section = todoist_client.get_section(section_id=section_id)

        if not section:
            logger.info(f"No section found with ID: {section_id}")
            return f"No section found with ID: {section_id}"

        logger.info(f"Retrieved section: {section.id}")
        return json.dumps(section.to_dict(), indent=2, default=str)
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

        section_params = {
            "name": name,
            "project_id": project_id
        }

        if order is not None:
            section_params["order"] = order

        section = todoist_client.add_section(**section_params)

        logger.info(f"Section created successfully: {section.id}")
        return json.dumps(section.to_dict(), indent=2, default=str)
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

        # Capture original name for informative response messages
        try:
            section = todoist_client.get_section(section_id=section_id)
            original_name = section.name
        except Exception as error:
            logger.warning(f"Error getting section with ID: {section_id}: {error}")
            return f"Could not verify section with ID: {section_id}. Update aborted."

        updated_section = todoist_client.update_section(section_id=section_id, name=name)

        logger.info(f"Section updated successfully: {section_id}")
        return json.dumps(updated_section.to_dict(), indent=2, default=str)

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

        try:
            section = todoist_client.get_section(section_id=section_id)
            section_name = section.name
        except Exception as error:
            logger.warning(f"Error getting section with ID: {section_id}: {error}")
            return f"Could not verify section with ID: {section_id}. Deletion aborted."

        is_success = todoist_client.delete_section(section_id=section_id)

        logger.info(f"Section deleted successfully: {section_id}")
        return f"Successfully deleted section: {section_name} (ID: {section_id})"

    except Exception as error:
        logger.error(f"Error deleting section: {error}")
        return f"Error deleting section: {str(error)}"
