# Implementation Tasks: Phase 3 - AI Chatbot

**Feature**: 003-ai-todo-assistant
**Branch**: `003-ai-todo-assistant`
**Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md)
**Created**: 2025-12-24

## Overview

Phase 3 transforms the todo application into an AI-powered conversational interface. Users manage tasks through natural language chat, with the system interpreting intent and executing operations via five MCP tools. The architecture is stateless with conversation history stored in PostgreSQL.

**Key Components**:
- Backend: OpenAI SDK with function calling, 5 MCP tools, chat endpoint
- Frontend: Custom chat UI with Tailwind CSS
- Database: 2 new tables (Conversation, Message)

## Implementation Strategy

**MVP Scope**: User Stories 1-2 (Task Creation + Queries via chat)
**Incremental Delivery**: Complete one user story at a time for testable increments
**Parallel Opportunities**: Backend and frontend tasks can run in parallel after Phase 2

---

## Phase 1: Setup & Dependencies

**Goal**: Install dependencies and configure environment for Phase 3

- [X] T001 Install OpenAI SDK in backend: `pip install openai>=1.0.0` and add to requirements.txt
- [X] T002 Install slowapi for rate limiting: `pip install slowapi>=0.1.9` and add to requirements.txt
- [X] T003 Add OpenAI configuration to backend/src/config.py (OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TIMEOUT, MAX_CONVERSATION_MESSAGES, CHAT_RATE_LIMIT_PER_MINUTE)
- [X] T004 Update backend/.env.example with new Phase 3 environment variables
- [X] T005 Verify all Phase 2 tests still pass after dependency updates

---

## Phase 2: Database Schema & Migrations

**Goal**: Add Conversation and Message tables to support chat history

- [X] T006 Create Conversation model in backend/src/models/conversation.py with SQLModel (id: UUID, user_id: UUID FK, created_at, updated_at)
- [X] T007 Create Message model in backend/src/models/message.py with SQLModel (id: UUID, user_id: UUID FK, conversation_id: UUID FK, role: Literal["user", "assistant"], content: str, created_at)
- [X] T008 Update backend/src/models/__init__.py to export Conversation and Message
- [X] T009 Create Alembic migration 003_add_conversations.py to create conversations table with indexes
- [X] T010 Create Alembic migration 004_add_messages.py to create messages table with indexes
- [X] T011 Run migrations locally and verify tables created: `alembic upgrade head`
- [X] T012 Create Pydantic schemas in backend/src/schemas/conversation.py (ConversationRead, ConversationCreate)
- [X] T013 Create Pydantic schemas in backend/src/schemas/message.py (MessageRead, MessageCreate)
- [X] T014 Create Pydantic schemas in backend/src/schemas/chat.py (ChatRequest, ChatResponse, ToolCall)
- [X] T015 Update backend/src/schemas/__init__.py to export new schemas

---

## Phase 3: MCP Tools Implementation (User Stories 1-5)

**Goal**: Implement 5 MCP tools for task operations
**Independent Test**: Test each tool independently via Python REPL

### MCP Tools Module

- [X] T016 [P] Create backend/src/services/mcp_tools.py with get_tool_definitions() function returning OpenAI function schemas for all 5 tools
- [X] T017 [P] [US1] Implement add_task tool in mcp_tools.py (parameters: title, description?, returns: {task_id, status, title})
- [X] T018 [P] [US2] Implement list_tasks tool in mcp_tools.py (parameters: status?, returns: {tasks: [...]})
- [X] T019 [P] [US3] Implement complete_task tool in mcp_tools.py (parameters: task_id, returns: {status, task_id, title})
- [X] T020 [P] [US4] Implement update_task tool in mcp_tools.py (parameters: task_id, title?, description?, returns: {status, task_id, updated_fields})
- [X] T021 [P] [US5] Implement delete_task tool in mcp_tools.py (parameters: task_id, returns: {status, task_id, message})
- [X] T022 Implement execute_tool() router function in mcp_tools.py to dispatch tool calls to appropriate handlers
- [X] T023 Add type hints and docstrings to all MCP tool functions
- [X] T024 Add user_id filtering and security checks to all MCP tools

---

## Phase 4: Chat Service (User Stories 1-2, 6)

**Goal**: Implement OpenAI integration and conversation management
**Independent Test**: Test chat service with mock OpenAI responses

### Chat Service Implementation

- [X] T025 Create backend/src/services/chat_service.py with AsyncOpenAI client initialization
- [X] T026 [US6] Implement get_conversation_history() in chat_service.py to load last N messages from database
- [X] T027 [US6] Implement save_message() in chat_service.py to persist user/assistant messages
- [X] T028 [US6] Implement create_or_get_conversation() in chat_service.py
- [X] T029 [US1] [US2] Implement process_chat_message() in chat_service.py: fetch history, call OpenAI with tools, handle tool calls, return response
- [X] T030 Add error handling for OpenAI API failures in chat_service.py (timeout, rate limits, API errors)
- [X] T031 Add logging for all AI interactions (user_id, conversation_id, tool_calls, timestamps) in chat_service.py
- [X] T032 Implement tool_call_handler() to execute MCP tools and format results for OpenAI
- [X] T033 Add type hints and docstrings to all chat service functions

---

## Phase 5: Chat API Endpoint (User Stories 1-6)

**Goal**: Expose chat functionality via REST API
**Independent Test**: POST to /api/{user_id}/chat with Postman/curl and verify response

### API Route Implementation

- [X] T034 Create backend/src/api/chat.py with chat router
- [X] T035 Implement POST /api/{user_id}/chat endpoint with JWT authentication
- [X] T036 Add request validation using ChatRequest schema in chat endpoint
- [X] T037 Add response formatting using ChatResponse schema in chat endpoint
- [X] T038 Integrate chat_service.process_chat_message() in chat endpoint
- [X] T039 Add rate limiting to chat endpoint using slowapi (60 req/min per user)
- [X] T040 Add error handling and appropriate HTTP status codes (400, 401, 404, 429, 500) in chat endpoint
- [X] T041 Register chat router in backend/src/main.py
- [X] T042 Update FastAPI Swagger docs with chat endpoint documentation
- [ ] T043 Test chat endpoint manually via Swagger UI

---

## Phase 6: Frontend - Chat UI (User Stories 1-6)

**Goal**: Build custom chat interface with Tailwind CSS
**Independent Test**: Navigate to /chat page and verify UI renders correctly

### Chat Components

- [X] T044 [P] Create frontend/src/types/chat.ts with TypeScript interfaces (Message, Conversation, ChatRequest, ChatResponse)
- [X] T045 [P] Create frontend/src/lib/api/chat.ts with sendMessage() API client function
- [X] T046 [P] Create frontend/src/lib/hooks/useChat.ts custom hook for chat state management
- [X] T047 [P] [US6] Create frontend/src/components/chat/ChatMessage.tsx component with role-based styling (user: right/blue, assistant: left/gray)
- [X] T048 [P] Create frontend/src/components/chat/ChatInput.tsx component with input field and send button
- [X] T049 [P] Create frontend/src/components/chat/ChatInterface.tsx main container component with message list and input
- [X] T050 [US6] Implement conversation history loading in ChatInterface.tsx
- [X] T051 Implement message sending and response handling in ChatInterface.tsx
- [X] T052 Add loading states (spinner/typing indicator) to ChatInterface.tsx
- [X] T053 Add error states and error messages to ChatInterface.tsx
- [X] T054 Add empty state (no messages yet) to ChatInterface.tsx
- [X] T055 Implement responsive design for mobile screens in chat components (Tailwind breakpoints)
- [X] T056 Create frontend/src/app/chat/page.tsx with ChatInterface component
- [X] T057 Add "Chat" link to frontend/src/components/layout/Navigation.tsx
- [ ] T058 Test chat UI manually in browser (create conversation, send messages, verify responses)

---

## Phase 7: Integration & End-to-End Testing

**Goal**: Verify complete chat flow works end-to-end

### Integration Testing

- [ ] T059 [US1] Manual test: Send "Add a task to buy groceries" → verify task created → verify AI confirms with task ID
- [ ] T060 [US2] Manual test: Send "Show me all my tasks" → verify AI lists all tasks with IDs and status
- [ ] T061 [US3] Manual test: Send "Mark task X as complete" → verify task status changes → verify AI confirms
- [ ] T062 [US4] Manual test: Send "Change task X to 'New Title'" → verify task updated → verify AI confirms
- [ ] T063 [US5] Manual test: Send "Delete task X" → verify task removed → verify AI confirms
- [ ] T064 [US6] Manual test: Send multiple messages → refresh page → verify conversation persists
- [ ] T065 Test multi-user isolation: Two users chat simultaneously → verify conversations are separate
- [ ] T066 Test rate limiting: Send 61 requests in 1 minute → verify 61st returns 429 error
- [ ] T067 Test error handling: Disconnect from OpenAI → send message → verify graceful error message
- [ ] T068 Test ambiguous queries: Send "Delete the task" when multiple tasks exist → verify AI asks for clarification
- [ ] T069 Performance test: Send message → verify response within 5s (p95 latency requirement)

---

## Phase 8: Polish & Production Readiness

**Goal**: Finalize UI/UX and prepare for deployment

### UI Polish

- [ ] T070 Add conversation list sidebar to ChatInterface (show past conversations, allow switching)
- [ ] T071 Add "New Conversation" button to start fresh conversation
- [ ] T072 Add markdown rendering support for AI responses in ChatMessage.tsx
- [ ] T073 Add auto-scroll to bottom when new messages arrive
- [ ] T074 Add message timestamps to ChatMessage.tsx
- [ ] T075 Implement keyboard shortcuts (Enter to send, Shift+Enter for newline)

### Documentation & Deployment

- [ ] T076 Update quickstart.md with tested setup instructions
- [ ] T077 Update README.md with Phase 3 features and chat usage examples
- [ ] T078 Create .env.example with all Phase 3 variables documented
- [ ] T079 Verify all migrations run cleanly on fresh database
- [ ] T080 Final smoke test: Complete end-to-end task management via chat only (no dashboard clicks)

---

## Task Summary

**Total Tasks**: 80
**Parallelizable Tasks**: 15 (marked with [P])

### Tasks by User Story

| User Story | Task IDs | Description |
|------------|----------|-------------|
| **US1** (P1) | T017, T029, T059 | Natural Language Task Creation |
| **US2** (P1) | T018, T029, T060 | Natural Language Task Queries |
| **US3** (P2) | T019, T061 | Natural Language Task Completion |
| **US4** (P3) | T020, T062 | Natural Language Task Updates |
| **US5** (P3) | T021, T063 | Natural Language Task Deletion |
| **US6** (P2) | T026-T028, T047, T050, T064 | Conversation History Persistence |

### Dependencies & Execution Order

```
Phase 1 (Setup) → Phase 2 (Database)
                ↓
                Phase 3 (MCP Tools) ← Can start after Phase 2
                ↓
                Phase 4 (Chat Service) ← Depends on Phase 3
                ↓
                Phase 5 (API Endpoint) ← Depends on Phase 4
                ↓
                Phase 6 (Frontend UI) ← Can start in parallel with Phase 3-5
                ↓
                Phase 7 (Integration Testing) ← Depends on Phase 5 & 6
                ↓
                Phase 8 (Polish)
```

### Parallel Execution Opportunities

**Backend Track** (T001-T043):
- Phase 1-5 can run sequentially
- Individual MCP tools (T017-T021) can be implemented in parallel

**Frontend Track** (T044-T058):
- Can start after Phase 2 is complete
- Chat components (T047-T049) can be built in parallel
- TypeScript types, API client, hooks can all be developed in parallel

**Optimal Parallelization**:
1. Start backend track (one developer)
2. After Phase 2 complete, start frontend track (second developer)
3. Both tracks meet at Phase 7 for integration testing

### MVP Scope (Minimum Viable Product)

For fastest time-to-value, implement **User Stories 1-2 only**:

**MVP Tasks**: T001-T043, T044-T058, T059-T060, T069
**Estimated Effort**: ~40 tasks (50% of total)
**Deliverable**: Users can create tasks and query tasks via chat

**Post-MVP Increments**:
- Increment 1: Add US3 (Complete tasks) - T061
- Increment 2: Add US4-US5 (Update/Delete) - T062-T063
- Increment 3: Add US6 (Conversation persistence) - Already in MVP
- Increment 4: Polish & deploy - T070-T080

---

## Independent Test Criteria

Each user story can be independently tested without dependencies:

### US1 (Natural Language Task Creation) - P1
**Test**: Send "Add a task to buy groceries"
**Verify**: Task created in database, AI confirms with task ID
**Pass Criteria**: Task exists with correct title, API returns 200, AI response contains "created" and task ID

### US2 (Natural Language Task Queries) - P1
**Test**: Create 5 tasks, send "Show me all my tasks"
**Verify**: AI lists all 5 tasks with IDs and status
**Pass Criteria**: Response contains all task titles, IDs match database, no tasks from other users

### US3 (Natural Language Task Completion) - P2
**Test**: Create task, send "Mark task X as complete"
**Verify**: Task.completed = true in database, AI confirms
**Pass Criteria**: Database shows completed=true, AI response contains "complete" and task title

### US4 (Natural Language Task Updates) - P3
**Test**: Create task, send "Change task X to 'New Title'"
**Verify**: Task.title updated in database, AI confirms
**Pass Criteria**: Database shows new title, AI response contains "updated" and new title

### US5 (Natural Language Task Deletion) - P3
**Test**: Create task, send "Delete task X"
**Verify**: Task removed from database, AI confirms
**Pass Criteria**: Task no longer exists in database, AI response contains "deleted"

### US6 (Conversation History Persistence) - P2
**Test**: Send 3 messages, refresh page, send another message
**Verify**: All messages persist, AI has context
**Pass Criteria**: All messages in database, AI references previous messages in response

---

## Risk Mitigation

| Risk | Mitigation Tasks |
|------|------------------|
| OpenAI API latency > 5s | T030 (timeout handling), T069 (performance test) |
| Rate limit abuse | T039 (slowapi rate limiting) |
| Multi-user data leakage | T024 (user_id filtering), T065 (isolation test) |
| Chat UI mobile issues | T055 (responsive design), T058 (manual mobile test) |
| Conversation history performance | T026 (load last 20 messages only, not all) |

---

## Checklist Format Validation

✅ All tasks follow required format: `- [ ] [TaskID] [P?] [Story?] Description with file path`
✅ Task IDs sequential (T001-T080)
✅ User Story labels applied (US1-US6) where appropriate
✅ Parallelizable tasks marked with [P]
✅ File paths specified for implementation tasks

---

**Generated**: 2025-12-24
**Author**: AI Agent (Claude Sonnet 4.5)
**Status**: Ready for implementation via `/sp.implement`
**Next Command**: `/sp.implement` to begin task execution
