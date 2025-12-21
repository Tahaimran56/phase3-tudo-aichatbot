# Tasks: Phase 2 Full-Stack Web Application

**Input**: Design documents from `/specs/002-todo-web-app/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/openapi.yaml, research.md, quickstart.md

**Tests**: Not explicitly requested in specification - tests are OPTIONAL and not included in this task list.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Backend: FastAPI (Python 3.12+)
- Frontend: Next.js with React and Tailwind CSS

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for both backend and frontend

- [x] T001 Create backend project structure per plan.md in backend/
- [x] T002 [P] Create frontend project structure per plan.md in frontend/
- [x] T003 Initialize FastAPI project with dependencies in backend/requirements.txt
- [x] T004 [P] Initialize Next.js project with Tailwind CSS in frontend/package.json
- [x] T005 [P] Configure Python linting (ruff) and formatting in backend/pyproject.toml
- [x] T006 [P] Configure TypeScript ESLint in frontend/eslint.config.mjs
- [x] T007 Create .env.example files for both backend/.env.example and frontend/.env.local.example

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

### Database Setup

- [x] T008 Configure Neon PostgreSQL connection in backend/src/config.py
- [x] T009 Setup SQLAlchemy database engine and session in backend/src/database.py
- [x] T010 Initialize Alembic migration framework in backend/alembic/
- [x] T011 Create initial migration for users table in backend/alembic/versions/001_initial_users.py
- [x] T012 Create initial migration for tasks table in backend/alembic/versions/002_initial_tasks.py

### Authentication Framework

- [x] T013 Create User SQLAlchemy model in backend/src/models/user.py
- [x] T014 [P] Create user Pydantic schemas in backend/src/schemas/user.py
- [x] T015 Implement Better Auth integration in backend/src/services/auth_service.py
- [x] T016 Create authentication dependency (get_current_user) in backend/src/api/deps.py
- [x] T017 Implement auth endpoints (signup, signin, signout, me) in backend/src/api/auth.py

### API Infrastructure

- [x] T018 Setup FastAPI application with CORS in backend/src/main.py
- [x] T019 [P] Configure CORS middleware in backend/src/middleware/cors.py
- [x] T020 [P] Setup error handling and HTTP exceptions in backend/src/api/errors.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Authentication (Priority: P1)

**Goal**: Users can create accounts, sign in securely, and have sessions persist across requests

**Independent Test**: Navigate to signup page, create account with email/password, sign in, verify redirect to dashboard with empty task list

### Frontend Authentication Implementation

- [x] T021 [US1] Create API client wrapper with credentials handling in frontend/src/lib/api.ts
- [x] T022 [P] [US1] Create auth utility functions in frontend/src/lib/auth.ts
- [x] T023 [P] [US1] Create TypeScript types for user and auth in frontend/src/types/index.ts
- [x] T024 [US1] Create AuthForm component with email/password fields in frontend/src/components/AuthForm.tsx
- [x] T025 [US1] Create root layout with auth context in frontend/src/app/layout.tsx
- [x] T026 [US1] Create landing page with auth navigation in frontend/src/app/page.tsx
- [x] T027 [US1] Implement signup page in frontend/src/app/auth/signup/page.tsx
- [x] T028 [P] [US1] Implement signin page in frontend/src/app/auth/signin/page.tsx
- [x] T029 [US1] Add form validation and error display for auth forms
- [x] T030 [US1] Implement signout functionality and session handling

**Checkpoint**: User Story 1 complete - users can signup, signin, signout. Verify independently.

---

## Phase 4: User Story 2 - Task Persistence (Priority: P2)

**Goal**: Tasks are saved to Neon PostgreSQL and persist across sessions/devices, isolated per user

**Independent Test**: Sign in, create a task, sign out, sign back in, verify task still exists with all attributes

### Backend Task Implementation

- [x] T031 [US2] Create Task SQLAlchemy model in backend/src/models/task.py
- [x] T032 [P] [US2] Create task Pydantic schemas in backend/src/schemas/task.py
- [x] T033 [US2] Implement task service with CRUD operations in backend/src/services/task_service.py
- [x] T034 [US2] Implement POST /api/tasks endpoint in backend/src/api/tasks.py
- [x] T035 [US2] Implement GET /api/tasks endpoint (user-filtered) in backend/src/api/tasks.py
- [x] T036 [US2] Implement GET /api/tasks/{id} endpoint in backend/src/api/tasks.py
- [x] T037 [US2] Add user_id filtering to all task queries (FR-006 multi-user isolation)
- [x] T038 [US2] Register task router in backend/src/main.py

**Checkpoint**: User Story 2 complete - tasks persist in database, isolated per user. Verify via API.

---

## Phase 5: User Story 3 - Web-Based Task Management (Priority: P3)

**Goal**: Full CRUD functionality for tasks through responsive web UI

**Independent Test**: Sign in, add a task with title/description, view it in list, mark complete, edit title, delete it, verify each operation reflects immediately in UI

### Backend Task Operations

- [x] T039 [US3] Implement PUT /api/tasks/{id} endpoint in backend/src/api/tasks.py
- [x] T040 [P] [US3] Implement DELETE /api/tasks/{id} endpoint in backend/src/api/tasks.py
- [x] T041 [P] [US3] Implement PATCH /api/tasks/{id}/complete endpoint in backend/src/api/tasks.py
- [x] T042 [US3] Add validation for empty title (FR-007) in task endpoints

### Frontend Dashboard and Task UI

- [x] T043 [US3] Create TaskItem component in frontend/src/components/TaskItem.tsx
- [x] T044 [P] [US3] Create TaskForm component for add/edit in frontend/src/components/TaskForm.tsx
- [x] T045 [US3] Create TaskList component in frontend/src/components/TaskList.tsx
- [x] T046 [US3] Create protected dashboard page in frontend/src/app/dashboard/page.tsx
- [x] T047 [US3] Integrate TanStack Query for task state management
- [x] T048 [US3] Implement add task flow with optimistic updates
- [x] T049 [US3] Implement edit task flow with inline editing
- [x] T050 [US3] Implement complete task toggle
- [x] T051 [US3] Implement delete task with confirmation

**Checkpoint**: User Story 3 complete - full CRUD via web UI. Run quickstart scenarios 2-6.

---

## Phase 6: User Story 4 - Responsive Mobile Experience (Priority: P4)

**Goal**: Mobile-first responsive design with touch-friendly UI

**Independent Test**: Access dashboard on mobile device/emulator, verify buttons are tappable (44px min), layout adapts, all CRUD operations work

### Mobile Styling Implementation

- [x] T052 [US4] Configure Tailwind CSS for mobile-first breakpoints in frontend/tailwind.config.ts
- [x] T053 [US4] Apply mobile-first styles to AuthForm component
- [x] T054 [P] [US4] Apply mobile-first styles to TaskList component
- [x] T055 [P] [US4] Apply mobile-first styles to TaskItem component
- [x] T056 [P] [US4] Apply mobile-first styles to TaskForm component
- [x] T057 [US4] Ensure 44px minimum touch targets on all interactive elements
- [x] T058 [US4] Add responsive navigation for mobile (hamburger menu or similar)
- [x] T059 [US4] Test and adjust layout for 320px-1920px viewport range (NFR-004)

**Checkpoint**: User Story 4 complete - app works on mobile devices. Run quickstart scenario 8.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, loading states, validation, and final cleanup

### Error Handling & Loading States

- [x] T060 [P] Add loading skeleton components in frontend/src/components/ui/
- [x] T061 [P] Add error boundary component in frontend/src/components/ErrorBoundary.tsx
- [x] T062 Implement API error handling with user-friendly messages
- [x] T063 Add loading states during Neon DB cold starts
- [x] T064 Implement session expiry handling with redirect to signin

### Validation & Hardening

- [x] T065 [P] Add inline form validation errors (NFR-005)
- [x] T066 [P] Verify all HTTP status codes per OpenAPI spec (FR-009)
- [x] T067 Verify HTTP-only cookie configuration (FR-008)

### Final Validation

- [x] T068 Run Zero-to-One validation: Signup -> Login -> Add Task -> Logout -> Re-login
- [x] T069 [P] Run quickstart.md all scenarios (1-8)
- [x] T070 [P] Verify multi-user isolation (FR-006) per quickstart scenario 7
- [x] T071 Verify API documentation at /docs (FR-010)

### Documentation

- [x] T072 Create implement.md documenting Phase 1 to Phase 2 transition

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4)**: Depends on Foundational phase completion, integrates with US1 auth
- **User Story 3 (Phase 5)**: Depends on US2 (needs task persistence)
- **User Story 4 (Phase 6)**: Depends on US3 (needs UI to style)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational - Uses auth from US1 but independently testable
- **User Story 3 (P3)**: Requires US2 for task data - Builds UI for persistence layer
- **User Story 4 (P4)**: Requires US3 for UI components - Adds responsive styling

### Within Each Phase

- Database setup before authentication
- Models before services
- Services before endpoints
- Backend APIs before frontend integration
- Core implementation before polish
- Commit after each task or logical group

### Parallel Opportunities

**Phase 1 (Setup)**:
- T001 and T002 can run in parallel (backend/frontend structure)
- T003 and T004 can run in parallel (backend/frontend dependencies)
- T005 and T006 can run in parallel (linting configs)

**Phase 2 (Foundational)**:
- T014 can run with T013 (schemas and models)
- T019 and T020 can run in parallel (middleware components)

**Phase 3 (US1)**:
- T022 and T023 can run in parallel (auth utilities)
- T027 and T028 can run in parallel (signup/signin pages)

**Phase 4 (US2)**:
- T031 and T032 can run in parallel (model and schemas)

**Phase 5 (US3)**:
- T039, T040, T041 can run in parallel (different endpoints)
- T043 and T044 can run in parallel (different components)

**Phase 6 (US4)**:
- T053, T054, T055, T056 can run in parallel (different components)

---

## Parallel Example: Phase 5 (User Story 3)

```bash
# Launch backend endpoints in parallel (different functions, same file):
Task: "Implement PUT /api/tasks/{id} endpoint in backend/src/api/tasks.py"
Task: "Implement DELETE /api/tasks/{id} endpoint in backend/src/api/tasks.py"
Task: "Implement PATCH /api/tasks/{id}/complete endpoint in backend/src/api/tasks.py"

# Launch frontend components in parallel (different files):
Task: "Create TaskItem component in frontend/src/components/TaskItem.tsx"
Task: "Create TaskForm component in frontend/src/components/TaskForm.tsx"
```

---

## Implementation Strategy

### MVP First (User Stories 1-2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Authentication)
4. **CHECKPOINT**: Users can signup/signin - deploy auth-only version
5. Complete Phase 4: User Story 2 (Task Persistence)
6. **CHECKPOINT**: Users can create/view tasks via API - test persistence
7. Deploy MVP with auth + persistence

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test auth independently → Deploy (Auth MVP!)
3. Add User Story 2 → Test persistence independently → Deploy
4. Add User Story 3 → Test full CRUD via UI → Deploy (Full MVP!)
5. Add User Story 4 → Test mobile → Deploy (Complete!)
6. Polish phase → Final hardening and validation

### Task Count Summary

| Phase | Tasks | Parallel Opportunities |
|-------|-------|------------------------|
| Phase 1: Setup | 7 | 4 |
| Phase 2: Foundational | 13 | 3 |
| Phase 3: US1 Authentication | 10 | 4 |
| Phase 4: US2 Task Persistence | 8 | 1 |
| Phase 5: US3 Web Task Management | 13 | 4 |
| Phase 6: US4 Mobile Responsive | 8 | 3 |
| Phase 7: Polish | 13 | 5 |
| **Total** | **72** | **24** |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All task file paths are absolute relative to repository root
