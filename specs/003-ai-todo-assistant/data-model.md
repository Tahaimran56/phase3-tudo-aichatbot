# Data Model: Phase 3 - AI Chatbot

**Feature**: Phase 3 - AI Chatbot
**Date**: 2025-12-24
**Related**: [spec.md](./spec.md) | [plan.md](./plan.md)

## Overview

This document defines the database schema for Phase 3, which adds conversational AI capabilities to the todo application. Two new tables (Conversation and Message) are added to support persistent chat history while maintaining strict multi-user isolation.

## Design Principles

1. **Multi-User Isolation**: All queries MUST filter by user_id to prevent cross-user data access
2. **Stateless Architecture**: Conversation history stored in database enables horizontal scalability
3. **Type Safety**: All fields use SQLModel for ORM-level type validation
4. **Performance**: Strategic indexes on foreign keys and timestamp fields for efficient queries
5. **Data Integrity**: Foreign key constraints enforce referential integrity

## Existing Entities (No Changes)

### User

Existing user model from Phase 2 - no modifications required.

**Table**: `users`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique user identifier |
| email | String | UNIQUE, NOT NULL | User email address |
| password_hash | String | NOT NULL | Hashed password (Better Auth) |
| created_at | DateTime | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| updated_at | DateTime | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**:
- Primary key index on `id`
- Unique index on `email`

**Relationships**:
- One-to-many with Task
- One-to-many with Conversation (new)
- One-to-many with Message (new)

---

### Task

Existing task model from Phase 2 - no modifications required.

**Table**: `tasks`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PRIMARY KEY, AUTO_INCREMENT | Unique task identifier |
| user_id | UUID | FOREIGN KEY (users.id), NOT NULL, INDEXED | Owner of the task |
| title | String(255) | NOT NULL | Task title |
| description | Text | NULLABLE | Optional detailed description |
| completed | Boolean | NOT NULL, DEFAULT FALSE | Completion status |
| created_at | DateTime | NOT NULL, DEFAULT NOW() | Task creation timestamp |
| updated_at | DateTime | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**:
- Primary key index on `id`
- Foreign key index on `user_id`
- Composite index on `(user_id, completed, created_at)` for efficient filtering

**Relationships**:
- Many-to-one with User

---

## New Entities (Phase 3)

### Conversation

Represents a chat conversation thread between a user and the AI assistant.

**Table**: `conversations`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique conversation identifier |
| user_id | UUID | FOREIGN KEY (users.id), NOT NULL, INDEXED | Owner of the conversation |
| created_at | DateTime | NOT NULL, DEFAULT NOW() | Conversation start timestamp |
| updated_at | DateTime | NOT NULL, DEFAULT NOW() | Last message timestamp |

**Indexes**:
- Primary key index on `id`
- Composite index on `(user_id, created_at DESC)` for listing user's conversations by recency

**Relationships**:
- Many-to-one with User (one user has many conversations)
- One-to-many with Message (one conversation contains many messages)

**Business Rules**:
1. A conversation belongs to exactly one user
2. Conversations cannot be shared between users
3. Conversations are never deleted (soft delete could be added later if needed)
4. `updated_at` is updated whenever a new message is added

**SQLModel Definition**:
```python
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")
```

**Usage Examples**:
```python
# Create new conversation
conversation = Conversation(user_id=current_user.id)
session.add(conversation)
session.commit()

# List user's conversations (most recent first)
conversations = session.exec(
    select(Conversation)
    .where(Conversation.user_id == current_user.id)
    .order_by(Conversation.updated_at.desc())
).all()
```

---

### Message

Represents a single message in a conversation (either from user or assistant).

**Table**: `messages`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique message identifier |
| user_id | UUID | FOREIGN KEY (users.id), NOT NULL, INDEXED | Owner of the conversation |
| conversation_id | UUID | FOREIGN KEY (conversations.id), NOT NULL, INDEXED | Parent conversation |
| role | String(20) | NOT NULL, CHECK(role IN ('user', 'assistant')) | Message sender role |
| content | Text | NOT NULL | Message content (unlimited length) |
| created_at | DateTime | NOT NULL, DEFAULT NOW() | Message timestamp |

**Indexes**:
- Primary key index on `id`
- Composite index on `(conversation_id, created_at ASC)` for efficient chronological message retrieval
- Index on `user_id` for isolation enforcement

**Relationships**:
- Many-to-one with Conversation (many messages belong to one conversation)
- Many-to-one with User (implicit through conversation, but stored for isolation enforcement)

**Business Rules**:
1. A message belongs to exactly one conversation
2. A message role is either "user" or "assistant"
3. Messages are immutable once created (no updates)
4. Messages are never deleted (ensures conversation history integrity)
5. `user_id` MUST match the conversation's `user_id` (enforced at application level)
6. Messages are always retrieved in chronological order (ASC by created_at)

**SQLModel Definition**:
```python
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from typing import Literal

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True, nullable=False)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True, nullable=False)
    role: Literal["user", "assistant"] = Field(nullable=False)
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")
```

**Usage Examples**:
```python
# Create user message
user_message = Message(
    user_id=current_user.id,
    conversation_id=conversation.id,
    role="user",
    content="Add a task to buy groceries"
)
session.add(user_message)

# Create assistant message
assistant_message = Message(
    user_id=current_user.id,
    conversation_id=conversation.id,
    role="assistant",
    content="I've created a task 'Buy groceries' with ID 42."
)
session.add(assistant_message)
session.commit()

# Retrieve conversation history (chronological order)
messages = session.exec(
    select(Message)
    .where(
        Message.conversation_id == conversation.id,
        Message.user_id == current_user.id  # Isolation enforcement
    )
    .order_by(Message.created_at.asc())
).all()

# Get last N messages for context window
recent_messages = session.exec(
    select(Message)
    .where(
        Message.conversation_id == conversation.id,
        Message.user_id == current_user.id
    )
    .order_by(Message.created_at.desc())
    .limit(20)
).all()[::-1]  # Reverse to get chronological order
```

---

## Database Migrations

### Migration 1: Add Conversations Table

**File**: `alembic/versions/003_add_conversations.py`

```python
"""Add conversations table

Revision ID: 003_add_conversations
Revises: 002_initial_tasks
Create Date: 2025-12-24

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '003_add_conversations'
down_revision = '002_initial_tasks'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_conversations_user_id'),
    )

    # Create composite index for efficient conversation listing
    op.create_index(
        'ix_conversations_user_id_created_at',
        'conversations',
        ['user_id', sa.desc('created_at')]
    )

def downgrade() -> None:
    op.drop_index('ix_conversations_user_id_created_at', table_name='conversations')
    op.drop_table('conversations')
```

### Migration 2: Add Messages Table

**File**: `alembic/versions/004_add_messages.py`

```python
"""Add messages table

Revision ID: 004_add_messages
Revises: 003_add_conversations
Create Date: 2025-12-24

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '004_add_messages'
down_revision = '003_add_conversations'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_messages_user_id'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], name='fk_messages_conversation_id'),
        sa.CheckConstraint("role IN ('user', 'assistant')", name='ck_messages_role'),
    )

    # Create composite index for efficient message retrieval
    op.create_index(
        'ix_messages_conversation_id_created_at',
        'messages',
        ['conversation_id', 'created_at']
    )

    # Create index on user_id for isolation queries
    op.create_index('ix_messages_user_id', 'messages', ['user_id'])

def downgrade() -> None:
    op.drop_index('ix_messages_user_id', table_name='messages')
    op.drop_index('ix_messages_conversation_id_created_at', table_name='messages')
    op.drop_table('messages')
```

---

## Entity Relationship Diagram

```
┌─────────────┐
│    User     │
│  (Phase 2)  │
├─────────────┤
│ id (PK)     │
│ email       │
│ password    │
│ created_at  │
│ updated_at  │
└─────┬───────┘
      │
      │ 1:N
      │
      ├─────────────────┬─────────────────┐
      │                 │                 │
      │                 │                 │
┌─────▼───────┐   ┌────▼──────────┐  ┌──▼───────┐
│    Task     │   │ Conversation  │  │ Message  │
│  (Phase 2)  │   │   (Phase 3)   │  │(Phase 3) │
├─────────────┤   ├───────────────┤  ├──────────┤
│ id (PK)     │   │ id (PK)       │  │ id (PK)  │
│ user_id(FK) │   │ user_id (FK)  │  │ user_id  │
│ title       │   │ created_at    │  │ conv_id  │
│ description │   │ updated_at    │  │ role     │
│ completed   │   └───────┬───────┘  │ content  │
│ created_at  │           │          │created_at│
│ updated_at  │           │ 1:N      └──────────┘
└─────────────┘           │
                          │
                     ┌────▼───────┐
                     │  Message   │
                     └────────────┘
```

---

## Query Patterns

### 1. Create New Conversation

```python
async def create_conversation(user_id: UUID, session: AsyncSession) -> Conversation:
    """Create a new conversation for a user."""
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    return conversation
```

### 2. Get User's Conversations

```python
async def get_user_conversations(
    user_id: UUID,
    session: AsyncSession,
    limit: int = 10
) -> List[Conversation]:
    """Retrieve user's most recent conversations."""
    result = await session.exec(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
    )
    return result.all()
```

### 3. Add Message to Conversation

```python
async def add_message(
    user_id: UUID,
    conversation_id: UUID,
    role: Literal["user", "assistant"],
    content: str,
    session: AsyncSession
) -> Message:
    """Add a message to a conversation and update conversation.updated_at."""
    # Verify conversation belongs to user (security check)
    conversation = await session.get(Conversation, conversation_id)
    if not conversation or conversation.user_id != user_id:
        raise ValueError("Conversation not found or access denied")

    # Create message
    message = Message(
        user_id=user_id,
        conversation_id=conversation_id,
        role=role,
        content=content
    )
    session.add(message)

    # Update conversation timestamp
    conversation.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(message)
    return message
```

### 4. Get Conversation History

```python
async def get_conversation_history(
    user_id: UUID,
    conversation_id: UUID,
    session: AsyncSession,
    limit: Optional[int] = None
) -> List[Message]:
    """Retrieve messages for a conversation with optional windowing."""
    query = (
        select(Message)
        .where(
            Message.conversation_id == conversation_id,
            Message.user_id == user_id  # Isolation enforcement
        )
        .order_by(Message.created_at.asc())
    )

    if limit:
        # Get last N messages
        query = query.order_by(Message.created_at.desc()).limit(limit)
        result = await session.exec(query)
        return list(reversed(result.all()))  # Reverse to chronological order

    result = await session.exec(query)
    return result.all()
```

---

## Performance Considerations

### Index Strategy

**Conversations Table**:
- `(user_id, created_at DESC)`: Optimizes listing user's conversations by recency
- Covers common query: "Show me my recent conversations"

**Messages Table**:
- `(conversation_id, created_at ASC)`: Optimizes retrieving conversation history chronologically
- `(user_id)`: Enables efficient isolation filtering
- Covers common queries: "Load messages for conversation X" and "Filter by user"

### Query Optimization

1. **Conversation Listing**: Composite index `(user_id, created_at)` allows index-only scan
2. **Message Retrieval**: Composite index `(conversation_id, created_at)` enables efficient range scans
3. **Windowing**: Using `LIMIT` with reversed order is more efficient than offset pagination
4. **Isolation**: Always including `user_id` in WHERE clause leverages indexes for security checks

### Estimated Storage

**Per Conversation**:
- Overhead: ~100 bytes (UUID, timestamps)

**Per Message**:
- Overhead: ~120 bytes (UUID, foreign keys, timestamps)
- Content: Variable (typically 50-500 characters = 50-500 bytes)
- Average: ~300 bytes per message

**Example**: User with 10 conversations, 50 messages each = 10 * 100 + 500 * 300 = 151 KB

**Scalability**: PostgreSQL handles millions of rows efficiently with proper indexes. No immediate concerns for Phase 3 scale.

---

## Security & Isolation

### Multi-User Isolation Rules

1. **Always filter by user_id**: All conversation and message queries MUST include `WHERE user_id = current_user.id`
2. **Verify ownership**: Before accessing a conversation by ID, verify it belongs to the authenticated user
3. **No cross-user references**: Conversations and messages cannot reference data from other users
4. **Enforce at multiple layers**:
   - Database: Foreign key constraints ensure referential integrity
   - ORM: SQLModel relationships enforce type safety
   - API: Route handlers verify JWT token and extract user_id
   - Service: All service functions require user_id parameter

### Example: Secure Conversation Access

```python
async def get_conversation_securely(
    user_id: UUID,
    conversation_id: UUID,
    session: AsyncSession
) -> Conversation:
    """Securely retrieve a conversation with ownership verification."""
    result = await session.exec(
        select(Conversation)
        .where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id  # CRITICAL: Isolation check
        )
    )
    conversation = result.one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return conversation
```

---

## Future Considerations

### Potential Enhancements (Out of Scope for Phase 3)

1. **Soft Delete**: Add `deleted_at` column to Conversation for archival
2. **Message Metadata**: Add `tool_calls` JSON column to Message for debugging
3. **Conversation Titles**: Add `title` column to Conversation (auto-generated from first message)
4. **Message Attachments**: Add `attachments` JSON column for future file support
5. **Conversation Sharing**: Add `shared_with` array column for collaborative features
6. **Read Receipts**: Add `read_at` timestamp to Message for unread count
7. **Message Reactions**: Add separate `MessageReaction` table for emoji reactions
8. **Search**: Add full-text search index on Message.content for conversation search

---

**Generated**: 2025-12-24
**Author**: AI Agent (Claude Sonnet 4.5)
**Status**: Complete
**Next**: Generate contracts/ and quickstart.md
