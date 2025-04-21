#!/usr/bin/env python3

import logging
from typing import Optional, Dict, Any
from mcp.server.fastmcp import Context

logger = logging.getLogger("todoist-mcp-server")

def todoist_create_task(
    ctx: Context,
    content: str,
    description: Optional[str] = None,
    project_id: Optional[str] = None,
    section_id: Optional[str] = None,
    parent_id: Optional[str] = None,
    order: Optional[int] = None,
    labels: Optional[list[str]] = None,
    priority: Optional[int] = None,
    due_string: Optional[str] = None,
    due_date: Optional[str] = None,
    due_datetime: Optional[str] = None,
    due_lang: Optional[str] = None,
    assignee_id: Optional[str] = None,
    duration: Optional[int] = None,
    duration_unit: Optional[str] = None,
    deadline_date: Optional[str] = None,
    deadline_lang: Optional[str] = None
) -> str:
    """Create a new task in Todoist with optional description, due date, and priority

    Args:
        content: The content/title of the task
        description: Detailed description of the task (optional)
        project_id: Task project ID. If not set, task is put to user's Inbox (optional)
        section_id: ID of section to put task into (optional)
        parent_id: Parent task ID (optional)
        order: Non-zero integer value used to sort tasks under the same parent (optional)
        labels: The task's labels (a list of names that may represent either personal or shared labels) (optional)
        priority: Task priority from 1 (normal) to 4 (urgent) (optional)
        due_string: Natural language due date like 'tomorrow', 'next Monday', 'Jan 23' (optional)
        due_date: Specific date in YYYY-MM-DD format relative to user's timezone (optional)
        due_datetime: Specific date and time in RFC3339 format in UTC (optional)
        due_lang: 2-letter code specifying language in case due_string is not written in English (optional)
        assignee_id: The responsible user ID (only applies to shared tasks) (optional)
        duration: A positive integer for the amount of duration_unit the task will take (optional)
        duration_unit: The unit of time that the duration field represents (minute or day) (optional)
        deadline_date: Specific date in YYYY-MM-DD format relative to user's timezone (optional)
        deadline_lang: 2-letter code specifying language of deadline (optional)
    """
    todoist_client = ctx.request_context.lifespan_context.todoist_client

    try:
        logger.info(f"Creating task: {content}")

        # Start with required parameters
        task_params = {"content": content}

        # Add all optional parameters in a cleaner way
        optional_params = {
            "description": description,
            "project_id": project_id,
            "section_id": section_id,
            "parent_id": parent_id,
            "order": order,
            "labels": labels,
            "assignee_id": assignee_id,
            "due_string": due_string,
            "due_date": due_date,
            "due_datetime": due_datetime,
            "due_lang": due_lang,
            "deadline_date": deadline_date,
            "deadline_lang": deadline_lang,
        }

        # Add non-null parameters to task_params
        for key, value in optional_params.items():
            if value is not None:
                task_params[key] = value

        # Special handling for priority (must be 1-4)
        if priority is not None and 1 <= priority <= 4:
            task_params["priority"] = priority

        # Special handling for duration (must have both duration and unit)
        if duration is not None and duration_unit is not None:
            if duration > 0 and duration_unit in ["minute", "day"]:
                task_params["duration"] = duration
                task_params["duration_unit"] = duration_unit
            else:
                logger.warning("Invalid duration parameters: duration must be > 0 and unit must be 'minute' or 'day'")

        # Create the task
        task = todoist_client.add_task(**task_params)

        logger.info(f"Task created successfully: {task.id}")
        return task
    except Exception as error:
        logger.error(f"Error creating task: {error}")
        return f"Error creating task: {str(error)}"

def todoist_get_tasks(
    ctx: Context,
    project_id: Optional[str] = None,
    filter: Optional[str] = None,
    priority: Optional[int] = None,
    limit: int = 10
) -> str:
    """Get a list of tasks from Todoist with various filters

    Args:
        project_id: Filter tasks by project ID (optional)
        filter: Natural language filter like 'today', 'tomorrow', 'next week', 'priority 1', 'overdue' (optional)
        priority: Filter by priority level (1-4) (optional)
        limit: Maximum number of tasks to return (optional)
    """
    todoist_client = ctx.request_context.lifespan_context.todoist_client

    try:
        logger.info(f"Getting tasks with filter: {filter}, project_id: {project_id}, priority: {priority}, limit: {limit}")

        # Create API request parameters
        params: Dict[str, Any] = {}
        if project_id:
            params["project_id"] = project_id
        if filter:
            params["filter"] = filter

        # Get tasks
        tasks = todoist_client.get_tasks(**params)

        # Apply additional filters that aren't supported directly by the API
        if priority and 1 <= priority <= 4:
            tasks = [task for task in tasks if task.priority == priority]

        # Apply limit
        if limit and limit > 0:
            tasks = tasks[:limit]

        # Format response
        if not tasks:
            logger.info("No tasks found matching the criteria")
            return "No tasks found matching the criteria"

        logger.info(f"Retrieved {len(tasks)} tasks")
        return tasks
    except Exception as error:
        logger.error(f"Error getting tasks: {error}")
        return f"Error getting tasks: {str(error)}"

def todoist_get_task(ctx: Context, task_id: str) -> str:
    """Get an active task from Todoist

    Args:
        task_id: ID of the task to retrieve
    """
    todoist_client = ctx.request_context.lifespan_context.todoist_client

    try:
        logger.info(f"Getting task with ID: {task_id}")

        # Get the task
        task = todoist_client.get_task(task_id=task_id)

        if not task:
            logger.info(f"No task found with ID: {task_id}")
            return f"No task found with ID: {task_id}"

        logger.info(f"Retrieved task: {task.id}")
        return task
    except Exception as error:
        logger.error(f"Error getting task: {error}")
        return f"Error getting task: {str(error)}"

def todoist_update_task(
    ctx: Context,
    task_id: str,
    content: Optional[str] = None,
    description: Optional[str] = None,
    labels: Optional[list[str]] = None,
    priority: Optional[int] = None,
    due_string: Optional[str] = None,
    due_date: Optional[str] = None,
    due_datetime: Optional[str] = None,
    due_lang: Optional[str] = None,
    assignee_id: Optional[str] = None,
    duration: Optional[int] = None,
    duration_unit: Optional[str] = None,
    deadline_date: Optional[str] = None,
    deadline_lang: Optional[str] = None
) -> str:
    """Update an existing task in Todoist

    Args:
        task_id: ID of the task to update
        content: New content/title for the task (optional)
        description: New description for the task (optional)
        labels: New labels for the task (optional)
        priority: New priority level from 1 (normal) to 4 (urgent) (optional)
        due_string: New due date in natural language like 'tomorrow', 'next Monday' (optional)
        due_date: New specific date in YYYY-MM-DD format (optional)
        due_datetime: New specific date and time in RFC3339 format in UTC (optional)
        due_lang: 2-letter code specifying language in case due_string is not written in English (optional)
        assignee_id: The responsible user ID or null to unset (for shared tasks) (optional)
        duration: A positive integer for the amount of duration_unit the task will take (optional)
        duration_unit: The unit of time that the duration field represents (minute or day) (optional)
        deadline_date: Specific date in YYYY-MM-DD format relative to user's timezone (optional)
        deadline_lang: 2-letter code specifying language of deadline (optional)
    """
    todoist_client = ctx.request_context.lifespan_context.todoist_client

    try:
        logger.info(f"Updating task with ID: {task_id}")

        # First, get the task to verify it exists
        try:
            task = todoist_client.get_task(task_id=task_id)
            original_content = task.content
        except Exception as error:
            logger.warning(f"Error getting task with ID: {task_id}: {error}")
            return f"Could not verify task with ID: {task_id}. Update aborted."

        # Build update data
        update_data = {"task_id": task_id}

        # Define all updateable parameters
        optional_params = {
            "content": content,
            "description": description,
            "labels": labels,
            "due_string": due_string,
            "due_date": due_date,
            "due_datetime": due_datetime,
            "due_lang": due_lang,
            "assignee_id": assignee_id,
            "deadline_date": deadline_date,
            "deadline_lang": deadline_lang,
        }

        # Add non-null parameters to update_data
        for key, value in optional_params.items():
            if value is not None:
                update_data[key] = value

        # Special handling for priority (must be 1-4)
        if priority is not None and 1 <= priority <= 4:
            update_data["priority"] = priority

        # Special handling for duration (must have both duration and unit)
        if duration is not None and duration_unit is not None:
            if duration > 0 and duration_unit in ["minute", "day"]:
                update_data["duration"] = duration
                update_data["duration_unit"] = duration_unit
            else:
                logger.warning("Invalid duration parameters: duration must be > 0 and unit must be 'minute' or 'day'")

        if len(update_data) <= 1:  # Only task_id
            return f"No update parameters provided for task: {original_content} (ID: {task_id})"

        # Update the task
        updated_task = todoist_client.update_task(**update_data)

        logger.info(f"Task updated successfully: {task_id}")

        response = f"Successfully updated task: {original_content} (ID: {task_id})"
        return response, updated_task
    except Exception as error:
        logger.error(f"Error updating task: {error}")
        return f"Error updating task: {str(error)}"

def todoist_close_task(ctx: Context, task_id: str) -> str:
    """Close a task in Todoist (i.e., mark the task as complete)

    Args:
        task_id: ID of the task to close
    """
    todoist_client = ctx.request_context.lifespan_context.todoist_client

    try:
        logger.info(f"Closing task with ID: {task_id}")

        # First, verify the task exists
        try:
            task = todoist_client.get_task(task_id=task_id)
            task_content = task.content
        except Exception as error:
            logger.warning(f"Error getting task with ID: {task_id}: {error}")
            return f"Could not verify task with ID: {task_id}. Task closing aborted."

        is_success = todoist_client.close_task(task_id=task_id)

        if is_success:
            logger.info(f"Task closed successfully: {task_id}")
            return f"Successfully closed task: {task_content} (ID: {task_id})"
        else:
            logger.warning(f"Task closing failed for task ID: {task_id}")
            return "Task closing failed"
    except Exception as error:
        logger.error(f"Error closing task: {error}")
        return f"Error closing task: {str(error)}"

def todoist_delete_task(ctx: Context, task_id: str) -> str:
    """Delete a task from Todoist

    Args:
        task_id: ID of the task to delete
    """
    todoist_client = ctx.request_context.lifespan_context.todoist_client

    try:
        logger.info(f"Deleting task with ID: {task_id}")

        # First, verify the task exists
        try:
            task = todoist_client.get_task(task_id=task_id)
            task_content = task.content
        except Exception as error:
            logger.warning(f"Error getting task with ID: {task_id}: {error}")
            return f"Could not verify task with ID: {task_id}. Deletion aborted."

        # Delete the task
        is_success = todoist_client.delete_task(task_id=task_id)

        if is_success:
            logger.info(f"Task deleted successfully: {task_id}")
            return f"Successfully deleted task: {task_content} (ID: {task_id})"
        else:
            logger.warning(f"Task deletion failed for task ID: {task_id}")
            return "Task deletion failed"
    except Exception as error:
        logger.error(f"Error deleting task: {error}")
        return f"Error deleting task: {str(error)}"
