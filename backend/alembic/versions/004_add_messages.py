"""Add messages table.

Revision ID: 004_add_messages
Revises: 003_add_conversations
Create Date: 2025-12-24

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "004_add_messages"
down_revision: Union[str, None] = "003_add_conversations"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "messages",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("conversation_id", sa.UUID(), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["conversation_id"], ["conversations.id"], ondelete="CASCADE"
        ),
    )
    op.create_index("messages_user_id_idx", "messages", ["user_id"])
    op.create_index("messages_conversation_id_idx", "messages", ["conversation_id"])
    op.create_index(
        "messages_conversation_id_created_at_idx",
        "messages",
        ["conversation_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "messages_conversation_id_created_at_idx", table_name="messages"
    )
    op.drop_index("messages_conversation_id_idx", table_name="messages")
    op.drop_index("messages_user_id_idx", table_name="messages")
    op.drop_table("messages")
