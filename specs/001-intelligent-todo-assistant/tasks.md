---

description: "Task list for Intelligent Todo Assistant - Phase 3 AI Integration"
---

# Tasks: Intelligent Todo Assistant

**Input**: Design documents from `/specs/001-intelligent-todo-assistant/`
**Prerequisites**: plan.md, spec.md, research.md

**Tests**: Not explicitly requested - focusing on implementation

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Backend: FastAPI 0.115, Python 3.12+, SQLAlchemy 2.0
- Frontend: Next.js 15.1, React 19, TypeScript 5.7

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependency installation, and environment configuration

- [ ] T001 Add OpenAI SDK to backend dependencies in backend/requirements.txt
- [ ] T002 [P] Add qdrant-client to backend dependencies in backend/requirements.txt
- [ ] T003 [P] Add openai agents SDK to backend dependencies in backend/requirements.txt
- [ ] T004 [P] Update .env.example with QDRANT_URL placeholder
- [ ] T005 [P] Update .env.example with QDRANT_API_KEY placeholder
- [ ] T006 [P] Update .env.example with OPENAI_API_KEY placeholder
- [ ] T007 Update backend/src/config.py to load QDRANT_URL from environment
- [ ] T008 [P] Update backend/src/config.py to load QDRANT_API_KEY from environment
- [ ] T009 [P] Update backend/src/config.py to load OPENAI_API_KEY from environment
- [ ] T010 Install all backend dependencies with pip install -r backend/requirements.txt

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T011 Create Alembic migration to add professional_background column to users table in backend/alembic/versions/
- [ ] T012 [P] Create chat_sessions table schema in Alembic migration in backend/alembic/versions/
- [ ] T013 [P] Create chat_messages table schema in Alembic migration in backend/alembic/versions/
- [ ] T014 [P] Create translation_cache table schema in Alembic migration in backend/alembic/versions/
- [ ] T015 Run Alembic migration to apply database schema changes
- [ ] T016 Create User model extension for professional_background field in backend/src/models/user.py
- [ ] T017 [P] Create ChatSession model in backend/src/models/chat_session.py
- [ ] T018 [P] Create ChatMessage model in backend/src/models/chat_message.py
- [ ] T019 [P] Create TranslationCache model in backend/src/models/translation_cache.py
- [ ] T020 Create Qdrant client dependency injection in backend/src/api/deps.py
- [ ] T021 [P] Create OpenAI client dependency injection in backend/src/api/deps.py
- [ ] T022 Create Qdrant collection initialization function in backend/src/api/deps.py
- [ ] T023 Add Qdrant collection initialization to app startup in backend/src/main.py
- [ ] T024 Create PII redaction patterns in backend/src/services/pii_redactor.py
- [ ] T025 [P] Implement PII detection logic in backend/src/services/pii_redactor.py
- [ ] T026 [P] Implement PII redaction logic in backend/src/services/pii_redactor.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - AI-Powered Task Insights via RAG Chat (Priority: P1) 🎯 MVP

**Goal**: Enable users to chat with an AI assistant that understands their task context through RAG-based semantic search

**Independent Test**: Create tasks, open chat interface, ask "What are my priorities?", verify AI provides contextually relevant answers based on task data

### Vector Infrastructure for User Story 1

- [ ] T027 [P] [US1] Create VectorSyncService class in backend/src/services/vector_sync.py
- [ ] T028 [US1] Implement sync_task_embedding method with PII redaction in backend/src/services/vector_sync.py
- [ ] T029 [US1] Implement delete_task_embedding method in backend/src/services/vector_sync.py
- [ ] T030 [US1] Implement batch_sync_embeddings method for bulk operations in backend/src/services/vector_sync.py
- [ ] T031 [US1] Add exponential backoff retry logic to vector sync in backend/src/services/vector_sync.py
- [ ] T032 [US1] Update task create endpoint to trigger background vector sync in backend/src/api/routes/tasks.py
- [ ] T033 [US1] Update task update endpoint to trigger background vector sync in backend/src/api/routes/tasks.py
- [ ] T034 [US1] Update task delete endpoint to trigger background vector cleanup in backend/src/api/routes/tasks.py

### MCP Server and Tool Definitions for User Story 1

- [ ] T035 [P] [US1] Create get_task_tools function with tool schemas in backend/src/services/mcp_server.py
- [ ] T036 [P] [US1] Create ToolExecutor class in backend/src/services/mcp_server.py
- [ ] T037 [US1] Implement get_user_tasks tool method in backend/src/services/mcp_server.py
- [ ] T038 [US1] Implement create_task tool method in backend/src/services/mcp_server.py
- [ ] T039 [US1] Implement update_task tool method in backend/src/services/mcp_server.py
- [ ] T040 [US1] Implement search_tasks tool method with vector search in backend/src/services/mcp_server.py

### RAG Service for User Story 1

- [ ] T041 [P] [US1] Create RAGService class in backend/src/services/rag_service.py
- [ ] T042 [US1] Implement build_user_filter for Qdrant isolation in backend/src/services/rag_service.py
- [ ] T043 [US1] Implement search_task_vectors with relevance threshold in backend/src/services/rag_service.py
- [ ] T044 [US1] Implement build_system_prompt with context injection in backend/src/services/rag_service.py
- [ ] T045 [US1] Implement get_conversation_history from database in backend/src/services/rag_service.py
- [ ] T046 [US1] Implement save_messages to persist chat history in backend/src/services/rag_service.py
- [ ] T047 [US1] Implement chat method with full RAG pipeline in backend/src/services/rag_service.py
- [ ] T048 [US1] Implement chat_stream method for real-time streaming in backend/src/services/rag_service.py

### Chat API Endpoints for User Story 1

- [ ] T049 [P] [US1] Create chat request/response schemas in backend/src/schemas/chat.py
- [ ] T050 [P] [US1] Create chat routes file in backend/src/api/routes/chat.py
- [ ] T051 [US1] Implement POST /chat/sessions endpoint to create session in backend/src/api/routes/chat.py
- [ ] T052 [US1] Implement GET /chat/sessions endpoint to list user sessions in backend/src/api/routes/chat.py
- [ ] T053 [US1] Implement POST /chat/messages endpoint with streaming support in backend/src/api/routes/chat.py
- [ ] T054 [US1] Implement GET /chat/sessions/{session_id}/messages endpoint in backend/src/api/routes/chat.py
- [ ] T055 [US1] Register chat routes in backend/src/main.py

### Frontend Chat UI for User Story 1

- [ ] T056 [P] [US1] Create chat TypeScript types in frontend/src/types/chat.ts
- [ ] T057 [P] [US1] Create chat API client functions in frontend/src/lib/api/chat.ts
- [ ] T058 [P] [US1] Create useChat hook for state management in frontend/src/lib/hooks/useChat.ts
- [ ] T059 [US1] Create ChatMessage component in frontend/src/components/chat/ChatMessage.tsx
- [ ] T060 [US1] Create ChatInput component with send button in frontend/src/components/chat/ChatInput.tsx
- [ ] T061 [US1] Create FloatingChatWidget component with open/close state in frontend/src/components/chat/FloatingChatWidget.tsx
- [ ] T062 [US1] Add streaming message handling to FloatingChatWidget in frontend/src/components/chat/FloatingChatWidget.tsx
- [ ] T063 [US1] Add mobile-responsive styles with Tailwind to FloatingChatWidget in frontend/src/components/chat/FloatingChatWidget.tsx
- [ ] T064 [US1] Integrate FloatingChatWidget in frontend/src/app/layout.tsx

**Checkpoint**: At this point, User Story 1 should be fully functional - users can chat with AI and get task insights

---

## Phase 4: User Story 2 - Personalized AI Recommendations Based on User Background (Priority: P2)

**Goal**: Capture user professional background during signup to tailor AI recommendations with domain-specific knowledge

**Independent Test**: Complete signup with background selection, create tasks, verify AI responses use domain-specific terminology (software vs hardware contexts)

### Backend Schema Updates for User Story 2

- [ ] T065 [P] [US2] Create signup request schema with professional_background field in backend/src/schemas/user.py
- [ ] T066 [US2] Update user create endpoint to accept professional_background in backend/src/api/routes/users.py

### Frontend Signup Enhancement for User Story 2

- [ ] T067 [P] [US2] Add professional_background field to signup TypeScript types in frontend/src/types/user.ts
- [ ] T068 [US2] Add background selection dropdown to SignupForm in frontend/src/app/signup/page.tsx
- [ ] T069 [US2] Add background field validation to signup form in frontend/src/app/signup/page.tsx
- [ ] T070 [US2] Update signup API call to include professional_background in frontend/src/app/signup/page.tsx

### Personalization Logic for User Story 2

- [ ] T071 [US2] Update build_system_prompt to inject user background context in backend/src/services/rag_service.py
- [ ] T072 [US2] Create get_domain_glossary function in backend/src/services/rag_service.py
- [ ] T073 [US2] Add software domain terminology to glossary in backend/src/services/rag_service.py
- [ ] T074 [US2] Add hardware domain terminology to glossary in backend/src/services/rag_service.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - AI provides personalized domain-aware responses

---

## Phase 5: User Story 3 - One-Click Urdu Translation for Tasks (Priority: P3)

**Goal**: Enable instant Urdu translation of task titles and descriptions with technical term preservation

**Independent Test**: Create task in English, click translate button, verify accurate Urdu translation with preserved technical terms and formatting

### Translation Service for User Story 3

- [ ] T075 [P] [US3] Create translation request/response schemas in backend/src/schemas/translation.py
- [ ] T076 [P] [US3] Create TranslationService class in backend/src/services/translation_service.py
- [ ] T077 [US3] Implement build_translation_prompt with glossary injection in backend/src/services/translation_service.py
- [ ] T078 [US3] Implement get_domain_glossary with software/hardware terms in backend/src/services/translation_service.py
- [ ] T079 [US3] Implement translate_to_urdu method with OpenAI chat in backend/src/services/translation_service.py
- [ ] T080 [US3] Implement get_cached_translation method in backend/src/services/translation_service.py
- [ ] T081 [US3] Implement cache_translation method with 30-day TTL in backend/src/services/translation_service.py

### Translation API Endpoint for User Story 3

- [ ] T082 [P] [US3] Create translation routes file in backend/src/api/routes/translation.py
- [ ] T083 [US3] Implement POST /tasks/{task_id}/translate endpoint in backend/src/api/routes/translation.py
- [ ] T084 [US3] Add translation response to task model in backend/src/api/routes/translation.py
- [ ] T085 [US3] Register translation routes in backend/src/main.py

### Frontend Translation UI for User Story 3

- [ ] T086 [P] [US3] Create translation TypeScript types in frontend/src/types/translation.ts
- [ ] T087 [P] [US3] Create translation API client in frontend/src/lib/api/translation.ts
- [ ] T088 [P] [US3] Create useTranslation hook in frontend/src/lib/hooks/useTranslation.ts
- [ ] T089 [US3] Create TranslateButton component in frontend/src/components/tasks/TranslateButton.tsx
- [ ] T090 [US3] Add TranslateButton to TaskList items in frontend/src/components/tasks/TaskList.tsx
- [ ] T091 [US3] Add RTL text direction support for Urdu display in frontend/src/components/tasks/TaskList.tsx
- [ ] T092 [US3] Add toggle between English and Urdu versions in frontend/src/components/tasks/TaskList.tsx

**Checkpoint**: All user stories should now be independently functional - complete AI-powered todo assistant with translation

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Error Handling and Logging

- [ ] T093 [P] Add error logging for vector sync failures in backend/src/services/vector_sync.py
- [ ] T094 [P] Add error logging for RAG service failures in backend/src/services/rag_service.py
- [ ] T095 [P] Add error logging for translation failures in backend/src/services/translation_service.py
- [ ] T096 [P] Add user-friendly error messages to chat API in backend/src/api/routes/chat.py
- [ ] T097 [P] Add user-friendly error messages to translation API in backend/src/api/routes/translation.py

### Rate Limiting and Security

- [ ] T098 [P] Implement rate limiting middleware for chat endpoints in backend/src/middleware/rate_limiter.py
- [ ] T099 [P] Implement rate limiting middleware for translation endpoints in backend/src/middleware/rate_limiter.py
- [ ] T100 Add API key validation on startup in backend/src/main.py
- [ ] T101 [P] Verify user isolation in vector search queries in backend/src/services/rag_service.py
- [ ] T102 [P] Add input validation for chat messages in backend/src/schemas/chat.py

### Performance Optimization

- [ ] T103 [P] Add Qdrant payload indexing for user_id field via initialization script
- [ ] T104 [P] Implement query result caching for repeated searches in backend/src/services/rag_service.py
- [ ] T105 Add batch embedding generation for bulk sync in backend/src/services/vector_sync.py

### Documentation

- [ ] T106 [P] Update API documentation with chat endpoints in FastAPI OpenAPI
- [ ] T107 [P] Update API documentation with translation endpoints in FastAPI OpenAPI
- [ ] T108 [P] Create quickstart guide for Qdrant setup in specs/001-intelligent-todo-assistant/quickstart.md
- [ ] T109 [P] Document environment variables in .env.example

### Final Validation

- [ ] T110 Test complete user flow: signup with background, create tasks, chat with AI, translate to Urdu
- [ ] T111 Verify all API keys are not exposed in client-side code
- [ ] T112 Run security audit for PII redaction effectiveness
- [ ] T113 Validate mobile responsiveness of chat UI across devices

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion - Core RAG chat functionality
- **User Story 2 (Phase 4)**: Depends on Foundational phase and US1 completion - Enhances chat with personalization
- **User Story 3 (Phase 5)**: Depends on Foundational phase and US2 completion - Adds translation capability
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories - MVP DELIVERABLE
- **User Story 2 (P2)**: Depends on US1 for chat system but can be developed in parallel after foundational phase - Enhances existing chat
- **User Story 3 (P3)**: Independent of US1/US2 technically but benefits from user background context - Can be developed in parallel

### Within Each User Story

**User Story 1 (RAG Chat)**:
- Vector Infrastructure → MCP Server → RAG Service → Chat API → Frontend UI
- Models (T027-T034) before services (T041-T048)
- Services before API endpoints (T049-T055)
- API before frontend (T056-T064)

**User Story 2 (Personalization)**:
- Backend schema → Frontend signup → Personalization logic
- Independent tasks can run in parallel (T065-T066, T067-T070)

**User Story 3 (Translation)**:
- Translation service → API endpoint → Frontend UI
- Service components (T075-T081) before API (T082-T085) before UI (T086-T092)

### Parallel Opportunities

**Within Setup (Phase 1)**:
- All T002-T009 can run in parallel (different files)

**Within Foundational (Phase 2)**:
- T012-T014 (table schemas) can run in parallel
- T017-T019 (model files) can run in parallel
- T020-T021 (client injections) can run in parallel
- T024-T026 (PII redactor) can run in parallel

**Within User Story 1**:
- T027 (vector sync), T035-T036 (MCP server), T041 (RAG service), T049-T050 (schemas), T056-T058 (frontend types/hooks) can start in parallel
- T059-T060 (chat components) can run in parallel

**Within User Story 2**:
- T065-T066 (backend), T067-T068 (frontend) can run in parallel
- T073-T074 (glossaries) can run in parallel

**Within User Story 3**:
- T075-T076 (schemas), T082 (routes), T086-T088 (frontend types/hooks) can start in parallel

**Within Polish (Phase 6)**:
- T093-T097 (logging) can run in parallel
- T098-T099 (rate limiting) can run in parallel
- T103-T105 (optimization) can run in parallel
- T106-T109 (documentation) can run in parallel

---

## Parallel Example: User Story 1 (RAG Chat)

```bash
# Launch foundational services in parallel:
Task: "Create VectorSyncService class in backend/src/services/vector_sync.py"
Task: "Create get_task_tools function in backend/src/services/mcp_server.py"
Task: "Create RAGService class in backend/src/services/rag_service.py"
Task: "Create chat schemas in backend/src/schemas/chat.py"

# Launch frontend components in parallel after API is ready:
Task: "Create chat TypeScript types in frontend/src/types/chat.ts"
Task: "Create chat API client in frontend/src/lib/api/chat.ts"
Task: "Create useChat hook in frontend/src/lib/hooks/useChat.ts"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T010)
2. Complete Phase 2: Foundational (T011-T026) - CRITICAL
3. Complete Phase 3: User Story 1 (T027-T064)
4. **STOP and VALIDATE**: Test RAG chat independently
5. Deploy/demo MVP with AI-powered task insights

**MVP Delivers**: Core value proposition - users can chat with AI about their tasks using natural language

### Incremental Delivery

1. **Foundation** (Phases 1-2): Setup + database + base services → Ready for development
2. **MVP Release** (Phase 3): User Story 1 → AI Chat fully functional → DEPLOY
3. **Enhancement Release** (Phase 4): User Story 2 → Personalized responses → DEPLOY
4. **Feature Complete** (Phase 5): User Story 3 → Translation capability → DEPLOY
5. **Production Ready** (Phase 6): Polish and optimization → FINAL RELEASE

### Parallel Team Strategy

With multiple developers after foundational phase:

**Team Distribution**:
- **Developer A**: User Story 1 - Backend (T027-T055)
- **Developer B**: User Story 1 - Frontend (T056-T064)
- **Developer C**: User Story 2 (T065-T074) - can start in parallel
- **Developer D**: User Story 3 (T075-T092) - can start after basic framework

**Coordination Points**:
- All must complete Phase 2 together first
- Frontend developers need backend APIs before integration
- Polish phase requires all stories complete

---

## Notes

- [P] tasks = different files, no dependencies - can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- All tasks include exact file paths for clarity
- Qdrant Cloud account and OpenAI API key must be provisioned before Phase 2
- Vector embeddings use text-embedding-3-small model (1536 dimensions)
- Chat uses gpt-4o-mini model for cost efficiency
- All vector queries include user_id filter for multi-tenant isolation
- PII redaction is mandatory before sending to OpenAI embedding API
- Translation caching reduces API costs with 30-day TTL
- Rate limiting prevents API cost overruns
- Background tasks use FastAPI BackgroundTasks (not Celery) for MVP simplicity

---

## Task Count Summary

- **Phase 1 (Setup)**: 10 tasks
- **Phase 2 (Foundational)**: 16 tasks
- **Phase 3 (User Story 1 - RAG Chat)**: 38 tasks
- **Phase 4 (User Story 2 - Personalization)**: 10 tasks
- **Phase 5 (User Story 3 - Translation)**: 18 tasks
- **Phase 6 (Polish)**: 21 tasks

**Total**: 113 tasks

**Parallel Opportunities**: 45+ tasks marked with [P] can run concurrently

**Critical Path**: Phase 1 → Phase 2 (blocking) → Phase 3 (MVP) → Phase 4 → Phase 5 → Phase 6

**MVP Scope**: Phases 1-3 (64 tasks) deliver core AI chat functionality
