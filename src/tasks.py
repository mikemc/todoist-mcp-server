#!/usr/bin/env python3

import logging
from typing import Optional, Dict, Any
from mcp.server.fastmcp import Context

logger = logging.getLogger("todoist-mcp-server")

def todoist_add_task(
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

        task_params = {"content": content}

        # Efficiently filter out None values to avoid sending unnecessary API parameters
        optional_params = {
            "description": description,
            "project_id": project_id,
            "section_id": section_id,
            "parent_id": parent_id,
            "order": order,
            "labels": labels,
            "assignee_id": assignee_id,
            "due_string": due_string,
            "due_lang": due_lang,
            "deadline_lang": deadline_lang,
        }

        for key, value in optional_params.items():
            if value is not None:
                task_params[key] = value

        # Transform string dates to objects since v3 API expects proper date/datetime types
        if due_date is not None:
            from datetime import date
            if isinstance(due_date, str):
                task_params["due_date"] = date.fromisoformat(due_date)
            else:
                task_params["due_date"] = due_date

        if due_datetime is not None:
            from datetime import datetime
            if isinstance(due_datetime, str):
                # Normalize RFC3339 format to Python's expected format
                if due_datetime.endswith('Z'):
                    due_datetime = due_datetime[:-1] + '+00:00'
                task_params["due_datetime"] = datetime.fromisoformat(due_datetime)
            else:
                task_params["due_datetime"] = due_datetime

        if deadline_date is not None:
            from datetime import date
            if isinstance(deadline_date, str):
                task_params["deadline_date"] = date.fromisoformat(deadline_date)
            else:
                task_params["deadline_date"] = deadline_date

        # Validate priority bounds to prevent API errors
        if priority is not None and 1 <= priority <= 4:
            task_params["priority"] = priority

        # Duration requires both values to be meaningful - enforce this constraint
        if duration is not None and duration_unit is not None:
            if duration > 0 and duration_unit in ["minute", "day"]:
                task_params["duration"] = duration
                task_params["duration_unit"] = duration_unit
            else:
                logger.warning("Invalid duration parameters: duration must be > 0 and unit must be 'minute' or 'day'")

        task = todoist_client.add_task(**task_params)

        logger.info(f"Task created successfully: {task.id}")
        return task
    except Exception as error:
        logger.error(f"Error creating task: {error}")
        return f"Error creating task: {str(error)}"

def todoist_get_tasks(
    ctx: Context,
    project_id: Optional[str] = None,
    section_id: Optional[str] = None,
    parent_id: Optional[str] = None,
    label: Optional[str] = None,
    ids: Optional[list[str]] = None,
    nmax: Optional[int] = 100,
    limit: int = 200
) -> str:
    """Get a list of tasks from Todoist with basic filters

    This is a wrapper around the Todoist API's get_tasks method that handles pagination
    automatically. By default, it will fetch up to 100 matching tasks. Set nmax=None
    to fetch ALL matching tasks across multiple API calls.

    For natural language filtering (like 'today', 'overdue'), use todoist_filter_tasks instead.

    Examples:
        # Get up to 100 tasks (default)
        todoist_get_tasks(ctx)

        # Get all tasks in a project (up to 100 by default)
        todoist_get_tasks(ctx, project_id="12345")

        # Get first 500 tasks total
        todoist_get_tasks(ctx, nmax=500)

        # Get ALL tasks (unlimited)
        todoist_get_tasks(ctx, nmax=None)

        # Get specific tasks by ID
        todoist_get_tasks(ctx, ids=["task1", "task2", "task3"])

    Args:
        project_id: Filter tasks by project ID (optional)
        section_id: Filter tasks by section ID (optional)
        parent_id: Filter tasks by parent task ID (optional)
        label: Filter tasks by label name (optional)
        ids: A list of the IDs of the tasks to retrieve (optional)
        nmax: Maximum total number of tasks to return. Set to None for ALL matching tasks (default: 100)
        limit: Number of tasks to fetch per API request (default: 200, max: 200)
    """
    todoist_client = ctx.request_context.lifespan_context.todoist_client

    try:
        logger.info(f"Getting tasks with project_id: {project_id}, section_id: {section_id}, parent_id: {parent_id}, label: {label}, limit: {limit}")

        # Enforce API limits to prevent errors and excessive resource usage
        if limit > 200:
            logger.warning(f"Limit {limit} exceeds API maximum of 200, using 200 instead")
            limit = 200
        elif limit <= 0:
            logger.warning(f"Invalid limit {limit}, using default of 200")
            limit = 200

        params = {}
        if project_id:
            params["project_id"] = project_id
        if section_id:
            params["section_id"] = section_id
        if parent_id:
            params["parent_id"] = parent_id
        if label:
            params["label"] = label
        if ids:
            params["ids"] = ids
        if limit:
            params["limit"] = limit

        # Handle paginated results by consuming the iterator until we hit our limit or exhaust results
        tasks_iterator = todoist_client.get_tasks(**params)
        all_tasks = []
        total_fetched = 0

        for task_batch in tasks_iterator:
            all_tasks.extend(task_batch)
            total_fetched += len(task_batch)

            # Respect user-imposed limits to avoid overwhelming responses
            if nmax is not None and total_fetched >= nmax:
                all_tasks = all_tasks[:nmax]
                break

            # Detect end of results when API returns partial batch
            if len(task_batch) < limit:
                break

        if not all_tasks:
            logger.info("No tasks found matching the criteria")
            return "No tasks found matching the criteria"

        logger.info(f"Retrieved {len(all_tasks)} tasks")

        if nmax is not None and len(all_tasks) == nmax:
            logger.info(f"Retrieved the full limit of {nmax} tasks; there may be more available.")

        return all_tasks

    except Exception as error:
        logger.error(f"Error getting tasks: {error}")
        return f"Error getting tasks: {str(error)}"

def todoist_filter_tasks(
    ctx: Context,
    filter: str,
    lang: Optional[str] = None,
    nmax: Optional[int] = 100,
    limit: int = 200
) -> str:
    """Get tasks using Todoist's natural language filter

    This uses the new filter_tasks method for queries like 'today', 'overdue', 'priority 1', etc.

    Args:
        filter: Natural language filter like 'today', 'tomorrow', 'next week', 'priority 1', 'overdue'
        lang: Language for task content (e.g., 'en') (optional)
        nmax: Maximum total number of tasks to return. Set to None for ALL matching tasks (default: 100)
        limit: Number of tasks to fetch per API request (default: 200, max: 200)
    """
    todoist_client = ctx.request_context.lifespan_context.todoist_client

    try:
        logger.info(f"Filtering tasks with filter: {filter}, lang: {lang}, limit: {limit}")

        # Enforce same pagination strategy as get_tasks for consistency
        if limit > 200:
            logger.warning(f"Limit {limit} exceeds API maximum of 200, using 200 instead")
            limit = 200
        elif limit <= 0:
            logger.warning(f"Invalid limit {limit}, using default of 200")
            limit = 200

        params = {"query": filter}
        if lang:
            params["lang"] = lang
        if limit:
            params["limit"] = limit

        tasks_iterator = todoist_client.filter_tasks(**params)
        all_tasks = []
        total_fetched = 0

        for task_batch in tasks_iterator:
            all_tasks.extend(task_batch)
            total_fetched += len(task_batch)

            if nmax is not None and total_fetched >= nmax:
                all_tasks = all_tasks[:nmax]
                break

            if len(task_batch) < limit:
                break

        if not all_tasks:
            logger.info("No tasks found matching the filter")
            return "No tasks found matching the filter"

        logger.info(f"Retrieved {len(all_tasks)} tasks")

        return all_tasks

    except Exception as error:
        logger.error(f"Error filtering tasks: {error}")
        return f"Error filtering tasks: {str(error)}"

def todoist_get_task(ctx: Context, task_id: str) -> str:
    """Get an active task from Todoist

    Args:
        task_id: ID of the task to retrieve
    """
    todoist_client = ctx.request_context.lifespan_context.todoist_client

    try:
        logger.info(f"Getting task with ID: {task_id}")

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

        # Verify task exists before attempting update to provide better error messages
        try:
            task = todoist_client.get_task(task_id=task_id)
            original_content = task.content
        except Exception as error:
            logger.warning(f"Error getting task with ID: {task_id}: {error}")
            return f"Could not verify task with ID: {task_id}. Update aborted."

        update_data = {}

        # Apply same parameter filtering strategy as create
        optional_params = {
            "content": content,
            "description": description,
            "labels": labels,
            "due_string": due_string,
            "due_lang": due_lang,
            "assignee_id": assignee_id,
            "deadline_lang": deadline_lang,
        }

        for key, value in optional_params.items():
            if value is not None:
                update_data[key] = value

        # Apply same date transformation logic as create for consistency
        if due_date is not None:
            from datetime import date
            if isinstance(due_date, str):
                update_data["due_date"] = date.fromisoformat(due_date)
            else:
                update_data["due_date"] = due_date

        if due_datetime is not None:
            from datetime import datetime
            if isinstance(due_datetime, str):
                if due_datetime.endswith('Z'):
                    due_datetime = due_datetime[:-1] + '+00:00'
                update_data["due_datetime"] = datetime.fromisoformat(due_datetime)
            else:
                update_data["due_datetime"] = due_datetime

        if deadline_date is not None:
            from datetime import date
            if isinstance(deadline_date, str):
                update_data["deadline_date"] = date.fromisoformat(deadline_date)
            else:
                update_data["deadline_date"] = deadline_date

        if priority is not None and 1 <= priority <= 4:
            update_data["priority"] = priority

        if duration is not None and duration_unit is not None:
            if duration > 0 and duration_unit in ["minute", "day"]:
                update_data["duration"] = duration
                update_data["duration_unit"] = duration_unit
            else:
                logger.warning("Invalid duration parameters: duration must be > 0 and unit must be 'minute' or 'day'")

        if len(update_data) == 0:
            return f"No update parameters provided for task: {original_content} (ID: {task_id})"

        updated_task = todoist_client.update_task(task_id, **update_data)

        logger.info(f"Task updated successfully: {task_id}")

        response = f"Successfully updated task: {original_content} (ID: {task_id})"
        return response, updated_task
    except Exception as error:
        logger.error(f"Error updating task: {error}")
        return f"Error updating task: {str(error)}"

def todoist_complete_task(ctx: Context, task_id: str) -> str:
    """Close a task in Todoist (i.e., mark the task as complete)

    Args:
        task_id: ID of the task to close
    """
    todoist_client = ctx.request_context.lifespan_context.todoist_client

    try:
        logger.info(f"Closing task with ID: {task_id}")

        # Pre-fetch task content for meaningful success messages
        try:
            task = todoist_client.get_task(task_id=task_id)
            task_content = task.content
        except Exception as error:
            logger.warning(f"Error getting task with ID: {task_id}: {error}")
            return f"Could not verify task with ID: {task_id}. Task closing aborted."

        is_success = todoist_client.complete_task(task_id=task_id)

        logger.info(f"Task closed successfully: {task_id}")
        return f"Successfully closed task: {task_content} (ID: {task_id})"
    except Exception as error:
        logger.error(f"Error closing task: {error}")
        return f"Error closing task: {str(error)}"

def todoist_uncomplete_task(ctx: Context, task_id: str) -> str:
    """Reopen a task in Todoist (i.e., mark the task as incomplete)

    Args:
        task_id: ID of the task to reopen
    """
    todoist_client = ctx.request_context.lifespan_context.todoist_client

    try:
        logger.info(f"Reopening task with ID: {task_id}")

        try:
            task = todoist_client.get_task(task_id=task_id)
            task_content = task.content
        except Exception as error:
            logger.warning(f"Error getting task with ID: {task_id}: {error}")
            return f"Could not verify task with ID: {task_id}. Task reopening aborted."

        is_success = todoist_client.uncomplete_task(task_id=task_id)

        logger.info(f"Task reopened successfully: {task_id}")
        return f"Successfully reopened task: {task_content} (ID: {task_id})"
    except Exception as error:
        logger.error(f"Error reopening task: {error}")
        return f"Error reopening task: {str(error)}"

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

    try:
        logger.info(f"Moving task with ID: {task_id}")

        try:
            task = todoist_client.get_task(task_id=task_id)
            task_content = task.content
        except Exception as error:
            logger.warning(f"Error getting task with ID: {task_id}: {error}")
            return f"Could not verify task with ID: {task_id}. Task move aborted."

        # Validate exclusive destination constraint - API requirement
        destination_count = sum(1 for x in [parent_id, section_id, project_id] if x is not None)

        if destination_count != 1:
            return "Error: Exactly one of parent_id, section_id, or project_id must be specified"

        is_success = todoist_client.move_task(
            task_id=task_id,
            parent_id=parent_id,
            section_id=section_id,
            project_id=project_id
        )

        if is_success:
            logger.info(f"Task moved successfully: {task_id}")
            return f"Successfully moved task: {task_content} (ID: {task_id})"
        else:
            error_msg = "Failed to move task"
            logger.error(error_msg)
            return error_msg

    except Exception as error:
        logger.error(f"Error moving task: {error}")
        return f"Error moving task: {str(error)}"

def todoist_delete_task(ctx: Context, task_id: str) -> str:
    """Delete a task from Todoist

    Args:
        task_id: ID of the task to delete
    """
    todoist_client = ctx.request_context.lifespan_context.todoist_client

    try:
        logger.info(f"Deleting task with ID: {task_id}")

        try:
            task = todoist_client.get_task(task_id=task_id)
            task_content = task.content
        except Exception as error:
            logger.warning(f"Error getting task with ID: {task_id}: {error}")
            return f"Could not verify task with ID: {task_id}. Deletion aborted."

        is_success = todoist_client.delete_task(task_id=task_id)

        logger.info(f"Task deleted successfully: {task_id}")
        return f"Successfully deleted task: {task_content} (ID: {task_id})"
    except Exception as error:
        logger.error(f"Error deleting task: {error}")
        return f"Error deleting task: {str(error)}"
