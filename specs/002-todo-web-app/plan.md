# Implementation Plan: Phase 2 Web Migration

**Branch**: `002-todo-web-app` | **Date**: 2025-12-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-todo-web-app/spec.md`

## Summary

Transition the Phase 1 in-memory CLI todo application to a multi-user web application with:
- **Backend**: FastAPI (Python 3.12+) with SQLAlchemy ORM
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: Better Auth with email/password
- **Frontend**: Next.js with React and Tailwind CSS (mobile-first)

## Technical Context

**Language/Version**: Python 3.12+ (backend), TypeScript/Node.js 18+ (frontend)
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0, Better Auth, Next.js, Tailwind CSS
**Storage**: Neon PostgreSQL (serverless)
**Testing**: pytest (backend), Jest/Testing Library (frontend)
**Target Platform**: Web (all modern browsers, mobile responsive)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: <500ms p95 API latency, 100 concurrent users
**Constraints**: Mobile-first responsive (320px-1920px), HTTP-only session cookies
**Scale/Scope**: Multi-user SaaS, MVP feature set

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Architectural Integrity | ✅ PASS | Spec and plan before implementation |
| II. SDD Strictness | ✅ PASS | Tasks will be defined before implementation |
| III. Language Standard | ✅ PASS | Python 3.12+ PEP 8, TypeScript ESLint |
| IV. Modularity | ✅ PASS | Service/controller separation |
| V. Type Safety | ✅ PASS | Type hints, Pydantic schemas |
| VI. Documentation | ✅ PASS | FastAPI Swagger auto-generation |
| VII. Multi-User Isolation | ✅ PASS | All queries filtered by user_id |
| VIII. Responsive Design | ✅ PASS | Tailwind CSS mobile-first |
| IX. RESTful Integrity | ✅ PASS | Standard HTTP methods/status codes |
| Database Safety | ✅ PASS | SQLAlchemy ORM, no raw SQL |
| Authentication | ✅ PASS | Better Auth exclusive |
| API Documentation | ✅ PASS | FastAPI Swagger enabled |

**Gate Status**: ✅ ALL PASS - Proceed to implementation

## Project Structure

### Documentation (this feature)

```text
specs/002-todo-web-app/
├── plan.md              # This file
├── research.md          # Technology decisions
├── data-model.md        # Database schema
├── quickstart.md        # Setup and verification
├── contracts/           # API specifications
│   └── openapi.yaml     # OpenAPI 3.1 spec
├── checklists/          # Validation checklists
│   └── requirements.md
└── tasks.md             # Implementation tasks (via /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Environment configuration
│   ├── database.py          # SQLAlchemy setup
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          # User SQLAlchemy model
│   │   └── task.py          # Task SQLAlchemy model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py          # Pydantic user schemas
│   │   └── task.py          # Pydantic task schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py  # Better Auth integration
│   │   └── task_service.py  # Task CRUD logic
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py          # Auth endpoints
│   │   ├── tasks.py         # Task endpoints
│   │   └── deps.py          # Dependencies (get_current_user)
│   └── middleware/
│       └── cors.py          # CORS configuration
├── alembic/
│   ├── versions/            # Migration scripts
│   └── env.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Test fixtures
│   ├── unit/
│   │   └── test_task_service.py
│   └── integration/
│       └── test_api_tasks.py
├── requirements.txt
├── alembic.ini
└── .env.example

frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Landing page
│   │   ├── dashboard/
│   │   │   └── page.tsx     # Task dashboard
│   │   ├── auth/
│   │   │   ├── signin/
│   │   │   │   └── page.tsx
│   │   │   └── signup/
│   │   │       └── page.tsx
│   │   └── api/             # API route handlers (if needed)
│   ├── components/
│   │   ├── TaskList.tsx
│   │   ├── TaskItem.tsx
│   │   ├── TaskForm.tsx
│   │   ├── AuthForm.tsx
│   │   └── ui/              # Reusable UI components
│   ├── lib/
│   │   ├── api.ts           # API client
│   │   └── auth.ts          # Auth utilities
│   └── types/
│       └── index.ts         # TypeScript types
├── public/
├── tailwind.config.js
├── next.config.js
├── package.json
└── .env.local.example
```

**Structure Decision**: Web application with separate frontend (Next.js) and backend (FastAPI) directories. This enables independent deployment and clear separation of concerns between Python API and React UI.

## Component Architecture

### Backend Components

```
┌─────────────────────────────────────────────────────────────┐
│                        FastAPI App                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ Auth Router │  │ Task Router │  │   Middleware        │ │
│  │ /auth/*     │  │ /api/tasks/*│  │ (CORS, Session)     │ │
│  └──────┬──────┘  └──────┬──────┘  └─────────────────────┘ │
│         │                │                                  │
│  ┌──────▼──────┐  ┌──────▼──────┐                          │
│  │ Auth Service│  │ Task Service│  ← Business Logic        │
│  │ (Better Auth│  │ (CRUD)      │                          │
│  └──────┬──────┘  └──────┬──────┘                          │
│         │                │                                  │
│  ┌──────▼────────────────▼──────┐                          │
│  │       SQLAlchemy ORM          │  ← Data Access          │
│  │  (User, Task, Session models) │                          │
│  └──────────────┬────────────────┘                          │
└─────────────────┼───────────────────────────────────────────┘
                  │
         ┌────────▼────────┐
         │ Neon PostgreSQL │
         │   (Serverless)  │
         └─────────────────┘
```

### Frontend Components

```
┌─────────────────────────────────────────────────────────────┐
│                      Next.js App                            │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    Pages (Routes)                    │   │
│  │  /           → Landing                              │   │
│  │  /auth/signin → Sign In Form                        │   │
│  │  /auth/signup → Sign Up Form                        │   │
│  │  /dashboard   → Task List (Protected)               │   │
│  └──────────────────────┬──────────────────────────────┘   │
│                         │                                   │
│  ┌──────────────────────▼──────────────────────────────┐   │
│  │                   Components                         │   │
│  │  AuthForm, TaskList, TaskItem, TaskForm             │   │
│  └──────────────────────┬──────────────────────────────┘   │
│                         │                                   │
│  ┌──────────────────────▼──────────────────────────────┐   │
│  │                  API Client (lib/api.ts)            │   │
│  │  Fetch wrapper with credentials: 'include'          │   │
│  └──────────────────────┬──────────────────────────────┘   │
└─────────────────────────┼───────────────────────────────────┘
                          │
                 ┌────────▼────────┐
                 │ FastAPI Backend │
                 │  (Port 8000)    │
                 └─────────────────┘
```

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Neon cold starts | Medium | Low | UI loading states, connection keep-alive |
| Better Auth complexity | Medium | Medium | Follow official docs, validate env vars on startup |
| CORS issues | High | Low | Explicit CORS config, test cross-origin early |
| Session expiry mid-operation | Medium | Medium | Auth check on each request, graceful redirect |

## Generated Artifacts

| Artifact | Path | Purpose |
|----------|------|---------|
| research.md | `specs/002-todo-web-app/research.md` | Technology decisions |
| data-model.md | `specs/002-todo-web-app/data-model.md` | Database schema |
| openapi.yaml | `specs/002-todo-web-app/contracts/openapi.yaml` | API specification |
| quickstart.md | `specs/002-todo-web-app/quickstart.md` | Setup and verification |

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks from this plan
2. Execute tasks in dependency order
3. Verify each user story independently
4. Run quickstart.md scenarios for validation

## Complexity Tracking

> No constitution violations requiring justification.

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Two-project structure | frontend + backend | Clear separation, independent deployment |
| SQLAlchemy over raw SQL | ORM | Constitution requirement, safety |
| Better Auth over custom | External lib | Constitution requirement, security |
