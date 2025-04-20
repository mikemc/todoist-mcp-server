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

def todoist_update_task(
    ctx: Context,
    task_name: str,
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
    """Update an existing task in Todoist by searching for it by name and then updating it

    Args:
        task_name: Name/content of the task to search for and update
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
        logger.info(f"Updating task matching: {task_name}")

        # First, search for the task
        tasks = todoist_client.get_tasks()
        matching_task = None

        for task in tasks:
            if task_name.lower() in task.content.lower():
                matching_task = task
                break

        if not matching_task:
            logger.warning(f"No task found matching: {task_name}")
            return f"Could not find a task matching \"{task_name}\""

        # Build update data
        update_data = {}

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

        # Update the task
        is_success = todoist_client.update_task(task_id=matching_task.id, **update_data)

        if is_success:
            logger.info(f"Task updated successfully: {matching_task.id}")

            # Create a descriptive response about what was updated
            response_lines = [f"Task \"{matching_task.content}\" updated:"]

            # Map parameters to human-readable descriptions
            update_descriptions = {
                "content": "New Title",
                "description": "New Description",
                "labels": "New Labels",
                "priority": "New Priority",
                "assignee_id": "New Assignee",
            }

            # Add basic parameter updates to response
            for param, description in update_descriptions.items():
                if param in update_data:
                    value = update_data[param]
                    if param == "labels" and isinstance(value, list):
                        response_lines.append(f"{description}: {', '.join(value)}")
                    else:
                        response_lines.append(f"{description}: {value}")

            # Handle special cases for due dates
            if any(key in update_data for key in ["due_string", "due_date", "due_datetime"]):
                if "due_string" in update_data:
                    response_lines.append(f"New Due Date: derived from '{update_data['due_string']}'")
                elif "due_date" in update_data:
                    response_lines.append(f"New Due Date: {update_data['due_date']}")
                elif "due_datetime" in update_data:
                    response_lines.append(f"New Due Date: {update_data['due_datetime']}")

            # Handle duration
            if "duration" in update_data and "duration_unit" in update_data:
                response_lines.append(f"New Duration: {update_data['duration']} {update_data['duration_unit']}(s)")

            # Handle deadline
            if "deadline_date" in update_data:
                response_lines.append(f"New Deadline: {update_data['deadline_date']}")

            return "\n".join(response_lines)
        else:
            logger.warning(f"Task update failed for task ID: {matching_task.id}")
            return "Task update failed"
    except Exception as error:
        logger.error(f"Error updating task: {error}")
        return f"Error updating task: {str(error)}"

def todoist_delete_task(ctx: Context, task_name: str) -> str:
    """Delete a task from Todoist by searching for it by name

    Args:
        task_name: Name/content of the task to search for and delete
    """
    todoist_client = ctx.request_context.lifespan_context.todoist_client

    try:
        logger.info(f"Deleting task matching: {task_name}")

        # First, search for the task
        tasks = todoist_client.get_tasks()
        matching_task = None

        for task in tasks:
            if task_name.lower() in task.content.lower():
                matching_task = task
                break

        if not matching_task:
            logger.warning(f"No task found matching: {task_name}")
            return f"Could not find a task matching \"{task_name}\""

        # Delete the task
        is_success = todoist_client.delete_task(task_id=matching_task.id)

        if is_success:
            logger.info(f"Task deleted successfully: {matching_task.id}")
            return f"Successfully deleted task: \"{matching_task.content}\""
        else:
            logger.warning(f"Task deletion failed for task ID: {matching_task.id}")
            return "Task deletion failed"
    except Exception as error:
        logger.error(f"Error deleting task: {error}")
        return f"Error deleting task: {str(error)}"

def todoist_complete_task(ctx: Context, task_name: str) -> str:
    """Mark a task as complete by searching for it by name

    Args:
        task_name: Name/content of the task to search for and complete
    """
    todoist_client = ctx.request_context.lifespan_context.todoist_client

    try:
        logger.info(f"Completing task matching: {task_name}")

        # First, search for the task
        tasks = todoist_client.get_tasks()
        matching_task = None

        for task in tasks:
            if task_name.lower() in task.content.lower():
                matching_task = task
                break

        if not matching_task:
            logger.warning(f"No task found matching: {task_name}")
            return f"Could not find a task matching \"{task_name}\""

        # Complete the task
        is_success = todoist_client.close_task(task_id=matching_task.id)

        if is_success:
            logger.info(f"Task completed successfully: {matching_task.id}")
            return f"Successfully completed task: \"{matching_task.content}\""
        else:
            logger.warning(f"Task completion failed for task ID: {matching_task.id}")
            return "Task completion failed"
    except Exception as error:
        logger.error(f"Error completing task: {error}")
        return f"Error completing task: {str(error)}"
