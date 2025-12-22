"""Task API endpoints with full CRUD operations."""

from fastapi import APIRouter, status

from ..api.errors import bad_request_exception, not_found_exception
from ..schemas.task import TaskCreate, TaskResponse, TaskUpdate
from ..services.task_service import TaskService
from .deps import CurrentUser, DbSession

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


@router.get("", response_model=list[TaskResponse])
def list_tasks(db: DbSession, current_user: CurrentUser) -> list[TaskResponse]:
    """Get all tasks for the authenticated user.

    FR-006: Tasks filtered by user_id for multi-user isolation.
    """
    tasks = TaskService.get_user_tasks(db, current_user.id)
    return [TaskResponse.model_validate(task) for task in tasks]


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> TaskResponse:
    """Create a new task for the authenticated user.

    FR-007: Title must be non-empty.
    """
    # Validate title is not just whitespace
    if not task_data.title.strip():
        raise bad_request_exception("Title cannot be empty")

    task = TaskService.create_task(db, task_data, current_user.id)
    return TaskResponse.model_validate(task)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> TaskResponse:
    """Get a specific task by ID.

    Returns 404 if task not found or not owned by user.
    """
    task = TaskService.get_task_by_id(db, task_id, current_user.id)
    if not task:
        raise not_found_exception("Task")
    return TaskResponse.model_validate(task)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> TaskResponse:
    """Update a task's title.

    FR-007: Title must be non-empty.
    Returns 404 if task not found or not owned by user.
    """
    # Validate title is not just whitespace
    if not task_data.title.strip():
        raise bad_request_exception("Title cannot be empty")

    task = TaskService.get_task_by_id(db, task_id, current_user.id)
    if not task:
        raise not_found_exception("Task")

    updated_task = TaskService.update_task(db, task, task_data)
    return TaskResponse.model_validate(updated_task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    """Delete a task.

    Returns 404 if task not found or not owned by user.
    """
    task = TaskService.get_task_by_id(db, task_id, current_user.id)
    if not task:
        raise not_found_exception("Task")

    TaskService.delete_task(db, task)


@router.patch("/{task_id}/complete", response_model=TaskResponse)
def complete_task(
    task_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> TaskResponse:
    """Mark a task as completed.

    Returns 404 if task not found or not owned by user.
    """
    task = TaskService.get_task_by_id(db, task_id, current_user.id)
    if not task:
        raise not_found_exception("Task")

    completed_task = TaskService.complete_task(db, task)
    return TaskResponse.model_validate(completed_task)
