#!/usr/bin/env python3

import logging
import json
from typing import Optional
from mcp.server.fastmcp import Context

logger = logging.getLogger("todoist-mcp-server")

def todoist_get_comment(ctx: Context, comment_id: str) -> str:
    """Get a single comment from Todoist

    Args:
        comment_id: ID of the comment to retrieve
    """
    todoist_client = ctx.request_context.lifespan_context.todoist_client

    try:
        logger.info(f"Getting comment with ID: {comment_id}")

        comment = todoist_client.get_comment(comment_id=comment_id)

        if not comment:
            logger.info(f"No comment found with ID: {comment_id}")
            return f"No comment found with ID: {comment_id}"

        logger.info(f"Retrieved comment: {comment.id}")
        return json.dumps(comment.to_dict(), indent=2, default=str)
    except Exception as error:
        logger.error(f"Error getting comment: {error}")
        return f"Error getting comment: {str(error)}"

def todoist_get_comments(
    ctx: Context,
    project_id: Optional[str] = None,
    task_id: Optional[str] = None,
    nmax: Optional[int] = 100,
    limit: int = 200
) -> str:
    """Get comments for a task or project from Todoist

    Args:
        project_id: ID of the project to retrieve comments for (optional)
        task_id: ID of the task to retrieve comments for (optional)
        nmax: Maximum total number of comments to return. Set to None for ALL matching comments (default: 100)
        limit: Maximum number of comments per page (default: 200, max: 200)

    Note: Either project_id or task_id must be provided.
    """
    todoist_client = ctx.request_context.lifespan_context.todoist_client

    try:
        if project_id is None and task_id is None:
            return "Error: Either project_id or task_id must be provided"

        logger.info(f"Getting comments for project_id: {project_id}, task_id: {task_id}, nmax: {nmax}, limit: {limit}")

        # Early exit for zero requests to avoid unnecessary API calls
        if nmax is not None:
            if nmax == 0:
                logger.info("nmax=0 specified, returning empty result")
                return []
            elif nmax < 0:
                logger.warning(f"Invalid nmax {nmax}, using default of 100")
                nmax = 100

        if limit > 200:
            logger.warning(f"Limit {limit} exceeds API maximum of 200, using 200 instead")
            limit = 200
        elif limit <= 0:
            logger.warning(f"Invalid limit {limit}, using default of 200")
            limit = 200

        # Key optimization: match page size to actual need to reduce API payload
        effective_limit = limit
        if nmax is not None and nmax < limit:
            effective_limit = nmax
            logger.info(f"Optimized limit from {limit} to {effective_limit} to match nmax")

        params = {"limit": effective_limit}
        if project_id:
            params["project_id"] = project_id
        if task_id:
            params["task_id"] = task_id

        comments_iterator = todoist_client.get_comments(**params)
        all_comments = []
        pages_fetched = 0

        for comment_batch in comments_iterator:
            pages_fetched += 1
            all_comments.extend(comment_batch)

            logger.info(f"Fetched page {pages_fetched} with {len(comment_batch)} comments (total: {len(all_comments)})")

            if nmax is not None and len(all_comments) >= nmax:
                # Trim excess - rare due to effective_limit optimization, but handles edge cases
                all_comments = all_comments[:nmax]
                logger.info(f"Reached nmax of {nmax} comments, stopping pagination")
                break

            # Todoist API signals end of results by returning fewer items than requested
            if len(comment_batch) < effective_limit:
                logger.info(f"Received {len(comment_batch)} comments (less than limit {effective_limit}), reached end of results")
                break

        if not all_comments:
            logger.info("No comments found matching the criteria")
            return "No comments found matching the criteria"

        logger.info(f"Retrieved {len(all_comments)} comments total across {pages_fetched} pages")

        if nmax is None:
            logger.info("Fetched ALL matching comments (nmax=None specified)")
        elif len(all_comments) == nmax:
            logger.info(f"Retrieved exactly the requested {nmax} comments")

        return json.dumps([comment.to_dict() for comment in all_comments], indent=2, default=str)

    except Exception as error:
        logger.error(f"Error getting comments: {error}")
        return f"Error getting comments: {str(error)}"

def todoist_add_comment(
    ctx: Context,
    content: str,
    project_id: Optional[str] = None,
    task_id: Optional[str] = None,
    uids_to_notify: Optional[list[str]] = None
) -> str:
    """Create a new comment on a task or project in Todoist

    Args:
        content: The text content of the comment (supports Markdown)
        project_id: ID of the project to add the comment to (optional)
        task_id: ID of the task to add the comment to (optional)
        uids_to_notify: List of user IDs to notify (optional)

    Note: Either project_id or task_id must be provided.
    """
    todoist_client = ctx.request_context.lifespan_context.todoist_client

    try:
        if project_id is None and task_id is None:
            return "Error: Either project_id or task_id must be provided"

        logger.info(f"Creating comment on project_id: {project_id}, task_id: {task_id}")

        comment_params = {"content": content}

        if project_id:
            comment_params["project_id"] = project_id
        if task_id:
            comment_params["task_id"] = task_id
        if uids_to_notify:
            comment_params["uids_to_notify"] = uids_to_notify

        comment = todoist_client.add_comment(**comment_params)

        logger.info(f"Comment created successfully: {comment.id}")
        return json.dumps(comment.to_dict(), indent=2, default=str)
    except Exception as error:
        logger.error(f"Error creating comment: {error}")
        return f"Error creating comment: {str(error)}"

def todoist_update_comment(ctx: Context, comment_id: str, content: str) -> str:
    """Update an existing comment in Todoist

    Args:
        comment_id: ID of the comment to update
        content: New text content for the comment
    """
    todoist_client = ctx.request_context.lifespan_context.todoist_client

    try:
        logger.info(f"Updating comment with ID: {comment_id}")

        updated_comment = todoist_client.update_comment(comment_id=comment_id, content=content)

        logger.info(f"Comment updated successfully: {comment_id}")
        return json.dumps(updated_comment.to_dict(), indent=2, default=str)

    except Exception as error:
        logger.error(f"Error updating comment: {error}")
        return f"Error updating comment: {str(error)}"

def todoist_delete_comment(ctx: Context, comment_id: str) -> str:
    """Delete a comment from Todoist

    Args:
        comment_id: ID of the comment to delete
    """
    todoist_client = ctx.request_context.lifespan_context.todoist_client

    try:
        logger.info(f"Deleting comment with ID: {comment_id}")

        try:
            comment = todoist_client.get_comment(comment_id=comment_id)
            comment_preview = comment.content[:50] + "..." if len(comment.content) > 50 else comment.content
        except Exception as error:
            logger.warning(f"Error getting comment with ID: {comment_id}: {error}")
            return f"Could not verify comment with ID: {comment_id}. Deletion aborted."

        is_success = todoist_client.delete_comment(comment_id=comment_id)

        logger.info(f"Comment deleted successfully: {comment_id}")
        return f"Successfully deleted comment: '{comment_preview}' (ID: {comment_id})"

    except Exception as error:
        logger.error(f"Error deleting comment: {error}")
        return f"Error deleting comment: {str(error)}"
