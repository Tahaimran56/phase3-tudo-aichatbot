"""Initial tasks table.

Revision ID: 002_initial_tasks
Revises: 001_initial_users
Create Date: 2025-12-21

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_initial_tasks"
down_revision: Union[str, None] = "001_initial_users"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_completed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("tasks_user_id_idx", "tasks", ["user_id"])
    op.create_index("tasks_user_id_created_at_idx", "tasks", ["user_id", "created_at"])


def downgrade() -> None:
    op.drop_index("tasks_user_id_created_at_idx", table_name="tasks")
    op.drop_index("tasks_user_id_idx", table_name="tasks")
    op.drop_table("tasks")
