"""Task service with CRUD operations and user isolation."""

from uuid import UUID

from sqlalchemy import desc
from sqlalchemy.orm import Session

from ..models.task import Task
from ..schemas.task import TaskCreate, TaskUpdate


class TaskService:
    """Service class for task operations with user isolation."""

    @staticmethod
    def get_user_tasks(db: Session, user_id: UUID) -> list[Task]:
        """Get all tasks for a specific user, ordered by creation date (newest first).

        FR-006: All queries filtered by user_id for multi-user isolation.
        """
        return (
            db.query(Task)
            .filter(Task.user_id == user_id)
            .order_by(desc(Task.created_at))
            .all()
        )

    @staticmethod
    def get_task_by_id(db: Session, task_id: int, user_id: UUID) -> Task | None:
        """Get a specific task by ID, ensuring it belongs to the user.

        FR-006: Returns None if task doesn't exist or doesn't belong to user.
        """
        return (
            db.query(Task)
            .filter(Task.id == task_id, Task.user_id == user_id)
            .first()
        )

    @staticmethod
    def create_task(db: Session, task_data: TaskCreate, user_id: UUID) -> Task:
        """Create a new task for a user."""
        task = Task(
            user_id=user_id,
            title=task_data.title.strip(),
            description=task_data.description.strip() if task_data.description else None,
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def update_task(db: Session, task: Task, task_data: TaskUpdate) -> Task:
        """Update an existing task."""
        task.title = task_data.title.strip()
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def complete_task(db: Session, task: Task) -> Task:
        """Mark a task as completed."""
        task.is_completed = True
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def delete_task(db: Session, task: Task) -> None:
        """Delete a task."""
        db.delete(task)
        db.commit()
