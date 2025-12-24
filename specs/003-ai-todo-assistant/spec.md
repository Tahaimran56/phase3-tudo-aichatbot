# Feature Specification: Phase 3 - AI Chatbot

**Feature Branch**: `003-ai-todo-assistant`
**Created**: 2025-12-24
**Status**: Draft
**Input**: User description: "Phase 3: AI-powered conversational interface for task management using OpenAI Agents SDK and MCP"

## Overview

Phase 3 introduces an AI-powered conversational interface that allows users to manage tasks through natural language. The system uses the OpenAI Agents SDK with Model Context Protocol (MCP) to expose task operations as standardized tools. The architecture is stateless with conversation history stored in the database.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Natural Language Task Creation (Priority: P1)

As a user, I want to create tasks by chatting naturally with an AI assistant so I can add tasks without clicking through forms.

**Why this priority**: This is the core value proposition of Phase 3 - transforming task management into a conversational experience. Natural language task creation is the most common operation and provides immediate value.

**Independent Test**: Send message "Add a task to buy groceries", verify task is created with correct title, verify AI confirms the creation with task details.

**Acceptance Scenarios**:

1. **Given** a user sends "Add a task to buy groceries", **When** the AI processes the message, **Then** a new task is created with title "Buy groceries" and the AI confirms with the task ID
2. **Given** a user sends "Create a task called 'Call mom tonight' with description 'Remember to ask about her health'", **When** the AI processes the message, **Then** both title and description are correctly set
3. **Given** a user sends "Add tasks to finish report and schedule meeting", **When** the AI processes the message, **Then** two separate tasks are created
4. **Given** a user sends an ambiguous message like "I need to do something", **When** the AI processes it, **Then** the AI asks clarifying questions before creating a task

---

### User Story 2 - Natural Language Task Queries (Priority: P1)

As a user, I want to ask about my tasks in natural language so I can quickly understand what I need to do without scrolling through lists.

**Why this priority**: Querying is equally fundamental as creation. Users need to view and understand their tasks through conversation to make the chat interface useful.

**Independent Test**: Create 5 tasks with different statuses, send message "Show me all my tasks", verify AI lists all tasks with relevant details.

**Acceptance Scenarios**:

1. **Given** a user has tasks in their list, **When** they send "Show me all my tasks", **Then** the AI retrieves and displays all tasks with IDs, titles, and status
2. **Given** a user has both pending and completed tasks, **When** they send "What are my pending tasks?", **Then** the AI filters and shows only pending tasks
3. **Given** a user has completed tasks, **When** they send "Show me completed tasks", **Then** the AI displays only completed tasks
4. **Given** a user has no tasks, **When** they ask "What are my tasks?", **Then** the AI responds gracefully indicating no tasks exist

---

### User Story 3 - Natural Language Task Completion (Priority: P2)

As a user, I want to mark tasks complete by chatting so I can update status without clicking buttons.

**Why this priority**: Completion is a frequent operation but less critical than creation and viewing. Users can still mark complete via UI if chat is unavailable.

**Independent Test**: Create task, send message "Mark task 3 as complete", verify task status changes to completed, verify AI confirms the action.

**Acceptance Scenarios**:

1. **Given** a user has a pending task with ID 3, **When** they send "Mark task 3 as complete", **Then** the task status changes to completed and AI confirms
2. **Given** a user sends "Complete the 'buy groceries' task", **When** the AI processes it, **Then** the AI identifies the task by title and marks it complete
3. **Given** a user tries to complete a non-existent task, **When** they send "Mark task 999 as complete", **Then** the AI responds that the task doesn't exist
4. **Given** a user has multiple tasks with similar titles, **When** they use an ambiguous reference, **Then** the AI asks which specific task to complete

---

### User Story 4 - Natural Language Task Updates (Priority: P3)

As a user, I want to modify task details through chat so I can make quick edits without opening edit forms.

**Why this priority**: Updates are less frequent than creation/viewing/completion. This adds convenience but isn't essential for core functionality.

**Independent Test**: Create task, send message "Change task 1 to 'Call mom tonight'", verify task title is updated, verify AI confirms the change.

**Acceptance Scenarios**:

1. **Given** a user has task with ID 1, **When** they send "Change task 1 to 'Call mom tonight'", **Then** the task title updates and AI confirms
2. **Given** a user sends "Update the description of task 2 to 'Include meeting notes'", **When** the AI processes it, **Then** only the description is updated
3. **Given** a user tries to update a non-existent task, **When** they send the command, **Then** the AI responds that the task doesn't exist
4. **Given** a user sends an update request without specifying what to change, **When** the AI processes it, **Then** the AI asks what should be updated

---

### User Story 5 - Natural Language Task Deletion (Priority: P3)

As a user, I want to delete tasks through chat so I can clean up my list conversationally.

**Why this priority**: Deletion is less frequent and potentially destructive. Users may prefer explicit UI buttons for deletion to avoid accidental data loss.

**Independent Test**: Create task, send message "Delete the meeting task", verify task is removed, verify AI confirms deletion.

**Acceptance Scenarios**:

1. **Given** a user has a task titled "Meeting", **When** they send "Delete the meeting task", **Then** the task is removed and AI confirms
2. **Given** a user sends "Delete task 5", **When** the AI processes it, **Then** the task with ID 5 is removed
3. **Given** a user tries to delete a non-existent task, **When** they send the command, **Then** the AI responds that the task doesn't exist
4. **Given** a user sends an ambiguous deletion request, **When** the AI processes it, **Then** the AI asks for confirmation before deleting

---

### User Story 6 - Conversation History Persistence (Priority: P2)

As a user, I want my chat conversations to be saved so I can refer back to previous interactions and maintain context across sessions.

**Why this priority**: Persistent history improves user experience by maintaining context, but the system can function without it (stateless model with conversation_id provides basic continuity).

**Independent Test**: Send multiple messages in a conversation, sign out, sign back in, verify previous conversation is still accessible with full message history.

**Acceptance Scenarios**:

1. **Given** a user has an ongoing conversation, **When** they send multiple messages, **Then** each message and response is stored in the database with timestamps
2. **Given** a user has previous conversations, **When** they view the chat interface, **Then** they can see a list of past conversations
3. **Given** a user resumes a previous conversation, **When** they continue chatting, **Then** the AI has context from previous messages in that conversation
4. **Given** a user starts a new conversation, **When** they send the first message, **Then** a new conversation_id is created and associated with all subsequent messages

---

### Edge Cases

- What happens when a user sends a message that isn't task-related? (AI should respond conversationally but clarify it can only manage tasks)
- What happens when multiple tool calls are needed for one user request? (AI should chain tool calls appropriately, e.g., "Delete all completed tasks")
- What happens when the OpenAI API is temporarily unavailable? (Display user-friendly error, suggest trying again later)
- What happens when a user refers to "the meeting task" but has three tasks with "meeting" in the title? (AI should list options and ask for clarification)
- What happens when two users have the same conversation_id? (System enforces user_id + conversation_id uniqueness)
- What happens when user sends very long messages? (System should handle gracefully, potentially summarizing or asking to break down the request)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST integrate OpenAI Agents SDK to power conversational AI interface
- **FR-002**: System MUST implement MCP (Model Context Protocol) server to expose task operations as standardized tools
- **FR-003**: System MUST provide five core MCP tools: add_task, list_tasks, complete_task, delete_task, update_task
- **FR-004**: System MUST implement stateless chat endpoint at POST /api/{user_id}/chat
- **FR-005**: Chat endpoint MUST accept conversation_id (optional) and message (required) parameters
- **FR-006**: Chat endpoint MUST return conversation_id, assistant response, and tool_calls array
- **FR-007**: System MUST store conversation history in database using Conversation and Message models
- **FR-008**: System MUST fetch conversation history from database before processing each request to maintain context
- **FR-009**: System MUST enforce strict multi-user isolation - users can only access their own conversations and tasks
- **FR-010**: System MUST interpret various natural language phrasings for each tool (e.g., "Add task", "Create a task", "I need to")
- **FR-011**: System MUST provide friendly confirmations after each action citing specific task details
- **FR-012**: System MUST handle missing/invalid task IDs gracefully with helpful error messages
- **FR-013**: System MUST support chaining multiple tool calls when user intent requires multiple operations
- **FR-014**: System MUST integrate OpenAI ChatKit UI component for conversational interface in frontend
- **FR-015**: System MUST authenticate all chat requests using JWT tokens from Better Auth
- **FR-016**: System MUST log all AI interactions with user_id, conversation_id, and timestamps for debugging
- **FR-017**: System MUST provide visual loading states during AI processing
- **FR-018**: System MUST handle ambiguous queries by asking clarifying questions before executing actions

### Non-Functional Requirements

- **NFR-001**: Chat responses MUST complete within 5 seconds for p95 latency including AI processing and tool execution
- **NFR-002**: System MUST scale horizontally - any server instance can handle any conversation by fetching history from database
- **NFR-003**: System MUST gracefully degrade when OpenAI API is unavailable with user-friendly error messages
- **NFR-004**: Conversation history queries MUST be optimized with database indexes on user_id and conversation_id
- **NFR-005**: System MUST rate-limit chat requests to prevent abuse (e.g., max 60 requests per minute per user)

### Key Entities

- **Task**: Existing model from Phase 2 (user_id, id, title, description, completed, created_at, updated_at)

- **Conversation**: Represents a chat conversation thread
  - user_id (UUID, foreign key to User)
  - id (UUID, primary key)
  - created_at (timestamp)
  - updated_at (timestamp)

- **Message**: Represents a single message in a conversation
  - user_id (UUID, foreign key to User)
  - id (UUID, primary key)
  - conversation_id (UUID, foreign key to Conversation)
  - role (enum: "user" or "assistant")
  - content (text)
  - created_at (timestamp)

## MCP Tools Specification

### Tool 1: add_task

**Purpose**: Creates a new task for the user

**Parameters**:
- title (string, required): The task title
- description (string, optional): Detailed task description

**Returns**:
```json
{
  "task_id": "integer",
  "status": "success",
  "title": "string"
}
```

**Natural Language Examples**:
- "Add a task to buy groceries"
- "Create a task called 'Finish report'"
- "I need to call mom tonight"

---

### Tool 2: list_tasks

**Purpose**: Retrieves user's tasks filtered by status

**Parameters**:
- status (string, optional): Filter by "all", "pending", or "completed" (default: "all")

**Returns**:
```json
{
  "tasks": [
    {
      "id": "integer",
      "title": "string",
      "description": "string",
      "completed": "boolean",
      "created_at": "timestamp",
      "updated_at": "timestamp"
    }
  ]
}
```

**Natural Language Examples**:
- "Show me all my tasks"
- "What are my pending tasks?"
- "List completed tasks"

---

### Tool 3: complete_task

**Purpose**: Marks a task as completed

**Parameters**:
- user_id (UUID, automatically provided)
- task_id (integer, required): The task to mark complete

**Returns**:
```json
{
  "status": "success",
  "task_id": "integer",
  "title": "string"
}
```

**Natural Language Examples**:
- "Mark task 3 as complete"
- "Complete the 'buy groceries' task"
- "I finished task 5"

---

### Tool 4: delete_task

**Purpose**: Removes a task from the database

**Parameters**:
- user_id (UUID, automatically provided)
- task_id (integer, required): The task to delete

**Returns**:
```json
{
  "status": "success",
  "task_id": "integer",
  "message": "Task deleted"
}
```

**Natural Language Examples**:
- "Delete the meeting task"
- "Remove task 7"
- "Get rid of the shopping task"

---

### Tool 5: update_task

**Purpose**: Modifies task title or description

**Parameters**:
- user_id (UUID, automatically provided)
- task_id (integer, required): The task to update
- title (string, optional): New title
- description (string, optional): New description

**Returns**:
```json
{
  "status": "success",
  "task_id": "integer",
  "updated_fields": ["title", "description"]
}
```

**Natural Language Examples**:
- "Change task 1 to 'Call mom tonight'"
- "Update the description of task 2 to 'Include meeting notes'"
- "Rename the meeting task to 'Team sync'"

---

## Chat API Endpoint Specification

### POST /api/{user_id}/chat

**Request Body**:
```json
{
  "conversation_id": "uuid (optional)",
  "message": "string (required)"
}
```

**Response**:
```json
{
  "conversation_id": "uuid",
  "response": "string",
  "tool_calls": [
    {
      "tool": "add_task",
      "parameters": {"title": "Buy groceries"},
      "result": {"task_id": 5, "status": "success"}
    }
  ]
}
```

**Request Flow**:
1. Receive user message and optional conversation_id
2. Fetch conversation history from database (if conversation_id provided)
3. Send history + new message to OpenAI Agents SDK
4. Agent invokes MCP tools as needed
5. Store user message and assistant response in database
6. Return response with conversation_id

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create tasks through natural language with 95%+ intent recognition accuracy
- **SC-002**: Chat responses complete within 5 seconds for p95 latency including AI processing and tool execution
- **SC-003**: Zero cross-user information leakage verified through isolation testing with concurrent users
- **SC-004**: AI correctly handles ambiguous queries by asking clarifying questions in 90%+ of cases
- **SC-005**: Conversation history persists correctly across sessions with full message fidelity
- **SC-006**: System remains functional when horizontally scaled - any server can handle any conversation
- **SC-007**: Chat interface provides clear loading states for all async operations
- **SC-008**: AI confirms all destructive actions (delete) with specific task details before execution
- **SC-009**: System gracefully handles OpenAI API failures with user-friendly error messages
- **SC-010**: MCP tool execution success rate is 98%+ for valid user intents

## Architecture Benefits

### Stateless Server Design

The Phase 3 architecture emphasizes statelessness with the following benefits:

1. **Horizontal Scalability**: Any server instance can handle any request because conversation history is fetched from the database on demand. No sticky sessions or in-memory state required.

2. **Resilience**: Server restarts don't lose conversation data. Database serves as single source of truth.

3. **Load Balancing**: Requests can be distributed across multiple backend instances without concern for session affinity.

4. **Development Simplicity**: No need to manage distributed caching or session replication.

### Agent Behavior Requirements

The AI agent must:

1. **Interpret Intent**: Map natural language variations to the appropriate MCP tool
2. **Confirm Actions**: Always respond with friendly confirmations citing specific task details
3. **Handle Errors Gracefully**: Provide helpful messages when tasks don't exist or requests are ambiguous
4. **Ask for Clarification**: When intent is unclear, ask targeted questions before acting
5. **Chain Tools**: Execute multiple tool calls when a single request requires multiple operations

### Security & Authentication

- All chat endpoints require JWT tokens from Better Auth
- Backend verifies tokens and extracts user_id
- All database queries filter by authenticated user_id
- Conversation and task isolation is strictly enforced
- No user can access another user's conversations or tasks through any API path

## Technology Stack

### Backend
- **Runtime**: Python 3.12+
- **Framework**: FastAPI
- **ORM**: SQLModel
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: Better Auth with JWT
- **AI SDK**: OpenAI Agents SDK
- **Protocol**: Official MCP (Model Context Protocol) SDK

### Frontend
- **Framework**: Next.js 16+
- **UI Component**: OpenAI ChatKit
- **Styling**: Tailwind CSS
- **Design**: Responsive, mobile-first

### Infrastructure
- **Database**: Neon Postgres (cloud-hosted)
- **Deployment**: [To be determined in Phase 4]

## Assumptions

1. **OpenAI API Access**: Project has valid OpenAI API key with sufficient quota for chat completions
2. **MCP SDK Compatibility**: Official MCP SDK integrates smoothly with FastAPI backend
3. **ChatKit Integration**: OpenAI ChatKit React components are compatible with Next.js 16+
4. **Database Schema**: Conversation and Message tables can be added without breaking existing Phase 2 functionality
5. **Cost**: Estimated AI API costs are acceptable (~$0.002 per chat message for GPT-4o-mini)
6. **User Consent**: Terms of Service covers AI processing of user task data
7. **Conversation Scope**: Chat conversations are scoped to task management only - general AI chat is out of scope

## Out of Scope (Phase 3)

- **RAG/Vector Search**: Phase 3 does NOT use embeddings or vector databases. Tasks are accessed via direct database queries through MCP tools.
- **Semantic Search**: Finding tasks by semantic similarity is out of scope. Only exact/fuzzy matching via MCP tools.
- **AI Task Suggestions**: AI cannot autonomously generate task recommendations based on patterns
- **Voice Input**: Voice-to-text for chat is deferred to bonus features
- **Multi-language Support**: Only English is supported in Phase 3
- **Persistent UI Chat History**: Chat bubbles may be session-based; full history persistence is optional
- **Advanced Analytics**: AI-powered insights and productivity metrics are deferred to Phase 4
- **Collaborative Features**: Sharing conversations or tasks with other users is out of scope
- **Offline Mode**: AI chat requires internet connectivity
- **Custom AI Models**: Phase 3 uses OpenAI APIs exclusively; no fine-tuning or custom models
- **Agent Memory Beyond Conversation**: AI doesn't remember user preferences across different conversations
