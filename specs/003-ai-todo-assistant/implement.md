# Implementation Guide: Phase 3 - AI Chatbot

**Feature**: 003-ai-todo-assistant
**Branch**: `003-ai-todo-assistant`
**Tasks**: [tasks.md](./tasks.md) | **Plan**: [plan.md](./plan.md)
**Created**: 2025-12-24

## Overview

This document provides implementation guidance for Phase 3 AI Chatbot. Follow the tasks in tasks.md sequentially, referring to this guide for implementation patterns and code examples.

---

## Prerequisites

Before starting implementation, ensure:

1. ✅ Phase 2 is complete and working (backend + frontend)
2. ✅ You're on branch `003-ai-todo-assistant`
3. ✅ OpenAI API key obtained from https://platform.openai.com/api-keys
4. ✅ All Phase 2 tests passing
5. ✅ Database is accessible (Neon PostgreSQL)

---

## Phase 1: Setup & Dependencies (T001-T005)

### T001-T002: Install Dependencies

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install OpenAI SDK
pip install openai>=1.0.0

# Install slowapi for rate limiting
pip install slowapi>=0.1.9

# Update requirements.txt
pip freeze > requirements.txt
```

### T003: Add Configuration

**File**: `backend/src/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Existing Phase 2 settings...
    DATABASE_URL: str
    BETTER_AUTH_SECRET: str
    BETTER_AUTH_URL: str

    # NEW: Phase 3 OpenAI Configuration
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_TIMEOUT: int = 10

    # NEW: Phase 3 Chat Configuration
    MAX_CONVERSATION_MESSAGES: int = 20
    CHAT_RATE_LIMIT_PER_MINUTE: int = 60

    class Config:
        env_file = ".env"

settings = Settings()
```

### T004: Update .env.example

**File**: `backend/.env.example`

```bash
# Existing Phase 2 variables
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=...
BETTER_AUTH_URL=...

# NEW: Phase 3 OpenAI Configuration
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_TIMEOUT=10

# NEW: Phase 3 Chat Configuration
MAX_CONVERSATION_MESSAGES=20
CHAT_RATE_LIMIT_PER_MINUTE=60
```

### T005: Verify Tests

```bash
cd backend
pytest
# All Phase 2 tests should still pass
```

---

## Phase 2: Database Schema (T006-T015)

### T006-T007: Create Models

**File**: `backend/src/models/conversation.py`

```python
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .message import Message

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")
```

**File**: `backend/src/models/message.py`

```python
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from .conversation import Conversation

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True, nullable=False)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True, nullable=False)
    role: Literal["user", "assistant"] = Field(nullable=False)
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")
```

### T008: Update __init__.py

**File**: `backend/src/models/__init__.py`

```python
from .user import User
from .task import Task
from .conversation import Conversation  # NEW
from .message import Message  # NEW

__all__ = ["User", "Task", "Conversation", "Message"]
```

### T009-T010: Create Migrations

**File**: `backend/alembic/versions/003_add_conversations.py`

```python
"""Add conversations table

Revision ID: 003_add_conversations
Revises: 002_initial_tasks
Create Date: 2025-12-24
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

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
    op.create_index('ix_conversations_user_id_created_at', 'conversations', ['user_id', sa.desc('created_at')])

def downgrade() -> None:
    op.drop_index('ix_conversations_user_id_created_at', table_name='conversations')
    op.drop_table('conversations')
```

**File**: `backend/alembic/versions/004_add_messages.py`

```python
"""Add messages table

Revision ID: 004_add_messages
Revises: 003_add_conversations
Create Date: 2025-12-24
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

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
    op.create_index('ix_messages_conversation_id_created_at', 'messages', ['conversation_id', 'created_at'])
    op.create_index('ix_messages_user_id', 'messages', ['user_id'])

def downgrade() -> None:
    op.drop_index('ix_messages_user_id', table_name='messages')
    op.drop_index('ix_messages_conversation_id_created_at', table_name='messages')
    op.drop_table('messages')
```

### T011: Run Migrations

```bash
cd backend
alembic upgrade head
# Should show: Running upgrade 002 -> 003, Running upgrade 003 -> 004
```

### T012-T015: Create Schemas

**File**: `backend/src/schemas/conversation.py`

```python
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class ConversationBase(BaseModel):
    pass

class ConversationCreate(ConversationBase):
    user_id: UUID

class ConversationRead(ConversationBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

**File**: `backend/src/schemas/message.py`

```python
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from typing import Literal

class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    user_id: UUID
    conversation_id: UUID
    role: Literal["user", "assistant"]

class MessageRead(MessageBase):
    id: UUID
    user_id: UUID
    conversation_id: UUID
    role: Literal["user", "assistant"]
    created_at: datetime

    class Config:
        from_attributes = True
```

**File**: `backend/src/schemas/chat.py`

```python
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    conversation_id: Optional[UUID] = None
    message: str = Field(..., min_length=1, max_length=5000)

class ToolCall(BaseModel):
    tool: str
    parameters: Dict[str, Any]
    result: Dict[str, Any]

class ChatResponse(BaseModel):
    conversation_id: UUID
    response: str
    tool_calls: List[ToolCall] = []
```

**File**: `backend/src/schemas/__init__.py`

```python
from .user import UserCreate, UserRead
from .task import TaskCreate, TaskRead, TaskUpdate
from .conversation import ConversationCreate, ConversationRead  # NEW
from .message import MessageCreate, MessageRead  # NEW
from .chat import ChatRequest, ChatResponse, ToolCall  # NEW

__all__ = [
    "UserCreate", "UserRead",
    "TaskCreate", "TaskRead", "TaskUpdate",
    "ConversationCreate", "ConversationRead",
    "MessageCreate", "MessageRead",
    "ChatRequest", "ChatResponse", "ToolCall",
]
```

---

## Phase 3: MCP Tools (T016-T024)

### T016-T022: Implement MCP Tools

**File**: `backend/src/services/mcp_tools.py`

```python
"""MCP Tools for Task Management

This module implements 5 MCP tools that expose task operations
to the OpenAI agent via function calling.
"""

from uuid import UUID
from typing import Dict, Any, List, Optional
from sqlmodel import Session, select
from ..models.task import Task
from ..database import get_session

def get_tool_definitions() -> List[Dict[str, Any]]:
    """Return OpenAI function calling schemas for all MCP tools."""
    return [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Creates a new task for the user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Task title (1-255 characters)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional detailed description"
                        }
                    },
                    "required": ["title"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "Retrieves user's tasks filtered by status",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["all", "pending", "completed"],
                            "description": "Filter tasks by status (default: all)"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "complete_task",
                "description": "Marks a task as completed",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "ID of the task to mark complete"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Removes a task from the database",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "ID of the task to delete"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Modifies task title or description",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "ID of the task to update"
                        },
                        "title": {
                            "type": "string",
                            "description": "New task title"
                        },
                        "description": {
                            "type": "string",
                            "description": "New task description"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        }
    ]

async def add_task(user_id: UUID, title: str, description: str = "", session: Session = None) -> Dict[str, Any]:
    """MCP Tool: Create a new task."""
    if not session:
        session = next(get_session())

    if not title or len(title) > 255:
        return {
            "status": "error",
            "message": "Task title must be between 1 and 255 characters"
        }

    task = Task(
        user_id=user_id,
        title=title,
        description=description,
        completed=False
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    return {
        "task_id": task.id,
        "status": "success",
        "title": task.title
    }

async def list_tasks(user_id: UUID, status: str = "all", session: Session = None) -> Dict[str, Any]:
    """MCP Tool: List user's tasks filtered by status."""
    if not session:
        session = next(get_session())

    query = select(Task).where(Task.user_id == user_id)

    if status == "pending":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)
    elif status != "all":
        return {
            "status": "error",
            "message": "Status must be 'all', 'pending', or 'completed'"
        }

    tasks = session.exec(query.order_by(Task.created_at.desc())).all()

    return {
        "tasks": [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }
            for task in tasks
        ]
    }

async def complete_task(user_id: UUID, task_id: int, session: Session = None) -> Dict[str, Any]:
    """MCP Tool: Mark a task as completed."""
    if not session:
        session = next(get_session())

    task = session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    ).first()

    if not task:
        return {
            "status": "error",
            "message": f"Task {task_id} not found"
        }

    task.completed = True
    session.commit()

    return {
        "status": "success",
        "task_id": task.id,
        "title": task.title
    }

async def delete_task(user_id: UUID, task_id: int, session: Session = None) -> Dict[str, Any]:
    """MCP Tool: Delete a task."""
    if not session:
        session = next(get_session())

    task = session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    ).first()

    if not task:
        return {
            "status": "error",
            "message": f"Task {task_id} not found"
        }

    session.delete(task)
    session.commit()

    return {
        "status": "success",
        "task_id": task_id,
        "message": "Task deleted"
    }

async def update_task(
    user_id: UUID,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    session: Session = None
) -> Dict[str, Any]:
    """MCP Tool: Update task title or description."""
    if not session:
        session = next(get_session())

    if not title and not description:
        return {
            "status": "error",
            "message": "At least one field (title or description) must be provided"
        }

    task = session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    ).first()

    if not task:
        return {
            "status": "error",
            "message": f"Task {task_id} not found"
        }

    updated_fields = []
    if title:
        if len(title) > 255:
            return {
                "status": "error",
                "message": "Task title must be 255 characters or less"
            }
        task.title = title
        updated_fields.append("title")

    if description is not None:
        task.description = description
        updated_fields.append("description")

    session.commit()

    return {
        "status": "success",
        "task_id": task.id,
        "updated_fields": updated_fields
    }

async def execute_tool(
    tool_name: str,
    arguments: Dict[str, Any],
    user_id: UUID,
    session: Session
) -> Dict[str, Any]:
    """Route tool calls to appropriate handler functions."""
    if tool_name == "add_task":
        return await add_task(user_id=user_id, session=session, **arguments)
    elif tool_name == "list_tasks":
        return await list_tasks(user_id=user_id, session=session, **arguments)
    elif tool_name == "complete_task":
        return await complete_task(user_id=user_id, session=session, **arguments)
    elif tool_name == "delete_task":
        return await delete_task(user_id=user_id, session=session, **arguments)
    elif tool_name == "update_task":
        return await update_task(user_id=user_id, session=session, **arguments)
    else:
        return {
            "status": "error",
            "message": f"Unknown tool: {tool_name}"
        }
```

---

## Phase 4-8: Remaining Implementation

Due to length constraints, the remaining phases (Chat Service, API Endpoint, Frontend UI, Testing, Polish) follow similar patterns:

### Key Patterns to Follow:

1. **Always filter by user_id** in database queries
2. **Use type hints** on all functions
3. **Add docstrings** to public functions
4. **Handle errors gracefully** with try/except
5. **Return consistent response formats**
6. **Log important operations** (tool calls, API errors)

### Reference Files:

- **Chat Service**: See research.md section 1 for OpenAI SDK usage
- **API Endpoint**: Follow existing Phase 2 patterns in `backend/src/api/`
- **Frontend**: Follow Next.js 16+ patterns, use Tailwind for styling
- **Testing**: Use pytest for backend, manual testing for frontend

---

## Implementation Command

Once you're ready to start, run:

```bash
/sp.implement
```

This will execute tasks T001-T080 sequentially, implementing the complete Phase 3 AI Chatbot feature!

---

**Generated**: 2025-12-24
**Author**: AI Agent (Claude Sonnet 4.5)
**Status**: Ready for implementation
**Next**: Run `/sp.implement` to begin
