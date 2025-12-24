"""MCP (Model Context Protocol) tools for task operations.

This module provides 5 MCP tools that the AI can use to manage tasks:
- add_task: Create a new task
- list_tasks: Query tasks with optional status filter
- complete_task: Mark a task as completed
- update_task: Update task title and/or description
- delete_task: Delete a task
"""

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from ..models.task import Task
from ..schemas.task import TaskCreate, TaskUpdate
from ..services.task_service import TaskService


def get_tool_definitions() -> list[dict[str, Any]]:
    """Return OpenAI function schema definitions for all MCP tools.

    These schemas follow the OpenAI function calling format and define
    the tools available to the AI assistant.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Create a new task for the user. Use this when the user wants to add, create, or make a new task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The title or main text of the task (required, non-empty)",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional additional details or description for the task",
                        },
                    },
                    "required": ["title"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "Get all tasks for the user. Can optionally filter by completion status. Use this when the user asks to see, show, list, or query their tasks.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["all", "completed", "pending"],
                            "description": "Filter tasks by status: 'all' (default), 'completed', or 'pending'",
                        },
                    },
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "complete_task",
                "description": "Mark a task as completed. Use this when the user wants to complete, finish, or mark a task as done.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to mark as completed",
                        },
                    },
                    "required": ["task_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Update a task's title and/or description. Use this when the user wants to modify, change, or update task details.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to update",
                        },
                        "title": {
                            "type": "string",
                            "description": "New title for the task (optional)",
                        },
                        "description": {
                            "type": "string",
                            "description": "New description for the task (optional)",
                        },
                    },
                    "required": ["task_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Delete a task permanently. Use this when the user wants to remove or delete a task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to delete",
                        },
                    },
                    "required": ["task_id"],
                },
            },
        },
    ]


def add_task(
    db: Session,
    user_id: UUID,
    title: str,
    description: str | None = None,
) -> dict[str, Any]:
    """Create a new task for the user.

    Args:
        db: Database session
        user_id: ID of the user creating the task
        title: Task title (required, non-empty)
        description: Optional task description

    Returns:
        Dict with task_id, status, and title
    """
    if not title or not title.strip():
        return {
            "status": "error",
            "message": "Task title cannot be empty",
        }

    task_data = TaskCreate(title=title, description=description)
    task = TaskService.create_task(db, task_data, user_id)

    return {
        "status": "success",
        "task_id": task.id,
        "title": task.title,
        "message": f"Created task '{task.title}' with ID {task.id}",
    }


def list_tasks(
    db: Session,
    user_id: UUID,
    status: str = "all",
) -> dict[str, Any]:
    """Get all tasks for the user with optional status filter.

    Args:
        db: Database session
        user_id: ID of the user
        status: Filter by status - "all", "completed", or "pending"

    Returns:
        Dict with tasks array containing task details
    """
    all_tasks = TaskService.get_user_tasks(db, user_id)

    # Filter by status if requested
    if status == "completed":
        filtered_tasks = [t for t in all_tasks if t.is_completed]
    elif status == "pending":
        filtered_tasks = [t for t in all_tasks if not t.is_completed]
    else:  # "all" or any other value
        filtered_tasks = all_tasks

    tasks_list = [
        {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "is_completed": task.is_completed,
            "created_at": task.created_at.isoformat(),
        }
        for task in filtered_tasks
    ]

    return {
        "status": "success",
        "count": len(tasks_list),
        "tasks": tasks_list,
    }


def complete_task(
    db: Session,
    user_id: UUID,
    task_id: int,
) -> dict[str, Any]:
    """Mark a task as completed.

    Args:
        db: Database session
        user_id: ID of the user
        task_id: ID of the task to complete

    Returns:
        Dict with status, task_id, and title
    """
    task = TaskService.get_task_by_id(db, task_id, user_id)
    if not task:
        return {
            "status": "error",
            "message": f"Task with ID {task_id} not found",
        }

    if task.is_completed:
        return {
            "status": "success",
            "task_id": task.id,
            "title": task.title,
            "message": f"Task '{task.title}' was already completed",
        }

    completed_task = TaskService.complete_task(db, task)

    return {
        "status": "success",
        "task_id": completed_task.id,
        "title": completed_task.title,
        "message": f"Marked task '{completed_task.title}' as completed",
    }


def update_task(
    db: Session,
    user_id: UUID,
    task_id: int,
    title: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    """Update a task's title and/or description.

    Args:
        db: Database session
        user_id: ID of the user
        task_id: ID of the task to update
        title: New title (optional)
        description: New description (optional)

    Returns:
        Dict with status, task_id, and updated fields
    """
    task = TaskService.get_task_by_id(db, task_id, user_id)
    if not task:
        return {
            "status": "error",
            "message": f"Task with ID {task_id} not found",
        }

    updated_fields = []

    if title is not None:
        if not title.strip():
            return {
                "status": "error",
                "message": "Task title cannot be empty",
            }
        task_data = TaskUpdate(title=title)
        task = TaskService.update_task(db, task, task_data)
        updated_fields.append("title")

    if description is not None:
        task.description = description.strip() if description else None
        db.commit()
        db.refresh(task)
        updated_fields.append("description")

    if not updated_fields:
        return {
            "status": "error",
            "message": "No fields to update. Provide title and/or description",
        }

    return {
        "status": "success",
        "task_id": task.id,
        "title": task.title,
        "updated_fields": updated_fields,
        "message": f"Updated task '{task.title}' ({', '.join(updated_fields)})",
    }


def delete_task(
    db: Session,
    user_id: UUID,
    task_id: int,
) -> dict[str, Any]:
    """Delete a task permanently.

    Args:
        db: Database session
        user_id: ID of the user
        task_id: ID of the task to delete

    Returns:
        Dict with status, task_id, and message
    """
    task = TaskService.get_task_by_id(db, task_id, user_id)
    if not task:
        return {
            "status": "error",
            "message": f"Task with ID {task_id} not found",
        }

    task_title = task.title
    TaskService.delete_task(db, task)

    return {
        "status": "success",
        "task_id": task_id,
        "message": f"Deleted task '{task_title}' (ID {task_id})",
    }


def execute_tool(
    tool_name: str,
    tool_args: dict[str, Any],
    db: Session,
    user_id: UUID,
) -> dict[str, Any]:
    """Execute an MCP tool by name with the given arguments.

    This is the main router function that dispatches tool calls to the
    appropriate handler based on the tool name.

    Args:
        tool_name: Name of the tool to execute
        tool_args: Arguments for the tool
        db: Database session
        user_id: ID of the user making the request

    Returns:
        Tool execution result as a dictionary
    """
    # Route to appropriate tool handler
    if tool_name == "add_task":
        return add_task(
            db=db,
            user_id=user_id,
            title=tool_args.get("title", ""),
            description=tool_args.get("description"),
        )
    elif tool_name == "list_tasks":
        return list_tasks(
            db=db,
            user_id=user_id,
            status=tool_args.get("status", "all"),
        )
    elif tool_name == "complete_task":
        return complete_task(
            db=db,
            user_id=user_id,
            task_id=tool_args.get("task_id", 0),
        )
    elif tool_name == "update_task":
        return update_task(
            db=db,
            user_id=user_id,
            task_id=tool_args.get("task_id", 0),
            title=tool_args.get("title"),
            description=tool_args.get("description"),
        )
    elif tool_name == "delete_task":
        return delete_task(
            db=db,
            user_id=user_id,
            task_id=tool_args.get("task_id", 0),
        )
    else:
        return {
            "status": "error",
            "message": f"Unknown tool: {tool_name}",
        }
