"""Add conversations table.

Revision ID: 003_add_conversations
Revises: 002_initial_tasks
Create Date: 2025-12-24

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003_add_conversations"
down_revision: Union[str, None] = "002_initial_tasks"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "conversations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
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
    op.create_index("conversations_user_id_idx", "conversations", ["user_id"])
    op.create_index(
        "conversations_user_id_created_at_idx",
        "conversations",
        ["user_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("conversations_user_id_created_at_idx", table_name="conversations")
    op.drop_index("conversations_user_id_idx", table_name="conversations")
    op.drop_table("conversations")
