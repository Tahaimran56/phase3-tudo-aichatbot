---
id: 002
title: Phase 2 Web Migration Technical Plan
stage: plan
date: 2025-12-21
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-todo-web-app
branch: 002-todo-web-app
user: Dell
command: /sp.plan
labels: ["plan", "phase2", "web", "fastapi", "nextjs", "neon", "better-auth", "architecture"]
links:
  spec: specs/002-todo-web-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-todo-web-app/plan.md
  - specs/002-todo-web-app/research.md
  - specs/002-todo-web-app/data-model.md
  - specs/002-todo-web-app/quickstart.md
  - specs/002-todo-web-app/contracts/openapi.yaml
tests:
  - null
---

## Prompt

Technical Plan: Phase 2 Web Migration
1. Tech Stack
Frontend: Next.js or React with Tailwind CSS.

Backend: FastAPI (Python) or Next.js API Routes.

Database: Neon Serverless PostgreSQL.

Auth: Better Auth (v1.0+).

2. Data Schema
Users Table: id, email, password_hash, created_at.

Tasks Table: id, user_id (Foreign Key), title, description, is_completed, updated_at.

3. Component Architecture
Auth Service: Manages user sessions and registration.

Task Controller: Handles CRUD logic and ensures user_id validation on every request.

Database Layer: Connection pooling and schema migrations for Neon.

4. Risks
Cold Starts: Neon serverless may have a slight delay; implement loading states in UI.

Auth Complexity: Ensure correct environment variables for Better Auth secrets.

## Response snapshot

Generated comprehensive Phase 2 technical plan with 5 artifacts:

**Technology Decisions (research.md)**:
- Frontend: Next.js with React
- Backend: FastAPI (Python 3.12+)
- ORM: SQLAlchemy 2.0
- Auth: Better Auth v1.0+
- Database: Neon PostgreSQL (serverless)
- Deployment: Vercel (frontend) + Railway (backend)

**Data Model (data-model.md)**:
- Users table: UUID id, email, password_hash, timestamps
- Tasks table: Serial id, user_id FK, title, description, is_completed, timestamps
- Sessions table: Managed by Better Auth
- Multi-user isolation via user_id filtering

**API Contract (contracts/openapi.yaml)**:
- Auth endpoints: /auth/signup, /auth/signin, /auth/signout, /auth/me
- Task endpoints: CRUD at /api/tasks with ownership validation
- HTTP-only cookie session authentication

**Project Structure (plan.md)**:
- backend/: FastAPI with services, models, schemas, api layers
- frontend/: Next.js with app router, components, lib
- Alembic for database migrations

**Quickstart (quickstart.md)**:
- Setup instructions for backend and frontend
- Environment variable configuration
- 8 verification scenarios mapping to user stories

**Constitution Compliance**: All 12 gates passed

## Outcome

- ✅ Impact: High - comprehensive technical foundation for Phase 2
- 🧪 Tests: N/A - design artifacts, test strategy defined
- 📁 Files: 5 files created (plan.md, research.md, data-model.md, quickstart.md, openapi.yaml)
- 🔁 Next prompts: /sp.tasks to generate implementation tasks
- 🧠 Reflection: FastAPI chosen over Next.js API routes to maintain Python ecosystem and constitution compliance

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution gate check - ALL PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
