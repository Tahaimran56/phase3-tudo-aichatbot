# Data Model: Phase 2 Web Migration

**Feature**: `002-todo-web-app`
**Date**: 2025-12-21
**Database**: Neon PostgreSQL (Serverless)
**ORM**: SQLAlchemy 2.0

## Entity Relationship Diagram

```
┌──────────────────┐       ┌──────────────────────┐
│      users       │       │        tasks         │
├──────────────────┤       ├──────────────────────┤
│ id (UUID) PK     │───┐   │ id (SERIAL) PK       │
│ email (VARCHAR)  │   │   │ user_id (UUID) FK    │──┐
│ password_hash    │   └──►│ title (VARCHAR)      │  │
│ created_at       │       │ description (TEXT)   │  │
│ updated_at       │       │ is_completed (BOOL)  │  │
└──────────────────┘       │ created_at           │  │
                           │ updated_at           │  │
                           └──────────────────────┘  │
                                                     │
┌──────────────────┐                                 │
│    sessions      │ (Managed by Better Auth)        │
├──────────────────┤                                 │
│ id (UUID) PK     │                                 │
│ user_id (UUID) FK│─────────────────────────────────┘
│ token (VARCHAR)  │
│ expires_at       │
│ created_at       │
└──────────────────┘
```

## Entities

### 1. User

**Purpose**: Represents an authenticated user of the application.

**Table Name**: `users`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique user identifier |
| email | VARCHAR(255) | NOT NULL, UNIQUE | User's email address |
| password_hash | VARCHAR(255) | NOT NULL | Bcrypt-hashed password |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Account creation time |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Last update time |

**Indexes**:
- `users_pkey` on `id` (primary key)
- `users_email_idx` on `email` (unique)

**Validation Rules**:
- Email must be valid email format
- Email must be unique (case-insensitive)
- Password must be hashed before storage

**SQLAlchemy Model**:
```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
```

---

### 2. Task

**Purpose**: Represents a todo item owned by a specific user.

**Table Name**: `tasks`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-incrementing task ID |
| user_id | UUID | NOT NULL, FOREIGN KEY (users.id) | Owner user reference |
| title | VARCHAR(255) | NOT NULL | Task title (required) |
| description | TEXT | NULL | Optional task description |
| is_completed | BOOLEAN | NOT NULL, DEFAULT FALSE | Completion status |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Task creation time |
| updated_at | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Last modification time |

**Indexes**:
- `tasks_pkey` on `id` (primary key)
- `tasks_user_id_idx` on `user_id` (for user-filtered queries)
- `tasks_user_id_created_at_idx` on `(user_id, created_at DESC)` (for sorted listing)

**Foreign Keys**:
- `tasks_user_id_fkey`: `user_id` REFERENCES `users(id)` ON DELETE CASCADE

**Validation Rules**:
- Title must be non-empty after trimming whitespace (FR-007)
- Title maximum length: 255 characters
- Description maximum length: 10,000 characters
- user_id must reference an existing user

**SQLAlchemy Model**:
```python
class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="tasks")
```

---

### 3. Session (Better Auth Managed)

**Purpose**: Represents an active user authentication session. Managed by Better Auth library.

**Table Name**: `sessions` (created by Better Auth)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Session identifier |
| user_id | UUID | NOT NULL, FOREIGN KEY | User reference |
| token | VARCHAR(255) | NOT NULL, UNIQUE | Session token (HTTP-only cookie) |
| expires_at | TIMESTAMP WITH TIME ZONE | NOT NULL | Session expiration time |
| created_at | TIMESTAMP WITH TIME ZONE | NOT NULL | Session start time |

**Note**: This table is managed by Better Auth. Do not modify directly.

---

## State Transitions

### Task Status

```
┌─────────────┐     complete_task()     ┌─────────────┐
│   PENDING   │ ─────────────────────► │  COMPLETED  │
│ is_completed│                        │ is_completed│
│   = false   │                        │   = true    │
└─────────────┘                        └─────────────┘
```

**Rules**:
- New tasks are always created with `is_completed = false`
- Tasks can be marked complete via `PATCH /api/tasks/{id}/complete`
- No transition back to pending (Phase 2 scope)

---

## Database Migrations

### Migration 001: Initial Schema

```sql
-- Create users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX users_email_idx ON users(email);

-- Create tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX tasks_user_id_idx ON tasks(user_id);
CREATE INDEX tasks_user_id_created_at_idx ON tasks(user_id, created_at DESC);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

## Query Patterns

### Multi-User Isolation (FR-006)

**All task queries MUST filter by user_id**:

```python
# Correct: Always filter by authenticated user
def get_user_tasks(db: Session, user_id: UUID) -> list[Task]:
    return db.query(Task).filter(Task.user_id == user_id).all()

# WRONG: Never query tasks without user filter
def get_all_tasks(db: Session) -> list[Task]:  # PROHIBITED
    return db.query(Task).all()
```

### Common Queries

```python
# List user's tasks (sorted by creation date, newest first)
db.query(Task).filter(Task.user_id == user_id).order_by(Task.created_at.desc()).all()

# Get specific task (with ownership check)
db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()

# Count user's tasks
db.query(func.count(Task.id)).filter(Task.user_id == user_id).scalar()

# Get pending tasks only
db.query(Task).filter(Task.user_id == user_id, Task.is_completed == False).all()
```

---

## Pydantic Schemas (API Layer)

```python
# Request schemas
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=10000)

class TaskUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)

# Response schemas
class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    is_completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserResponse(BaseModel):
    id: UUID
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```
