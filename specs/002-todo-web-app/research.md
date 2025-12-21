# Research: Phase 2 Web Migration

**Feature**: `002-todo-web-app`
**Date**: 2025-12-21
**Status**: Complete

## Research Summary

This document resolves all technical unknowns from the specification and user-provided technical plan.

---

## Decision 1: Frontend Framework

**Decision**: Next.js with React

**Rationale**:
- User input specified "Next.js or React with Tailwind CSS"
- Next.js provides both frontend and optional API routes in one framework
- Built-in routing, SSR capabilities, and excellent Tailwind integration
- Strong ecosystem for authentication and database integration
- TypeScript support out-of-the-box

**Alternatives Considered**:
- Plain React + Vite: Simpler but requires separate routing setup
- Vue.js: Good option but React ecosystem is larger for this stack

---

## Decision 2: Backend Framework

**Decision**: FastAPI (Python)

**Rationale**:
- User input specified "FastAPI (Python) or Next.js API Routes"
- Constitution mandates Python 3.12+ with PEP 8 compliance
- FastAPI provides automatic OpenAPI/Swagger documentation (FR-010)
- Pydantic integration for request/response validation
- Async support for performance (NFR-001: <500ms p95)
- Maintains consistency with Phase 1 Python codebase

**Alternatives Considered**:
- Next.js API Routes: Would simplify deployment but loses Python ecosystem and constitution compliance

---

## Decision 3: Database ORM

**Decision**: SQLAlchemy 2.0

**Rationale**:
- Industry-standard Python ORM for PostgreSQL
- Constitution requires ORM usage (no raw SQL)
- Strong async support with asyncpg
- Alembic for migrations (version-controlled as required)
- Type hints support for Python 3.12+

**Alternatives Considered**:
- Prisma (Python client): Less mature than SQLAlchemy
- SQLModel: Built on SQLAlchemy but less flexible

---

## Decision 4: Better Auth Integration

**Decision**: Better Auth v1.0+ with FastAPI adapter

**Rationale**:
- Constitution mandates Better Auth for authentication
- Provides email/password authentication (FR-001)
- Session management with HTTP-only cookies (FR-008)
- Python/FastAPI integration available
- Handles password hashing with industry-standard algorithms

**Implementation Notes**:
- Environment variables required: `BETTER_AUTH_SECRET`, `BETTER_AUTH_URL`
- Session storage in PostgreSQL (same Neon instance)
- Cookie configuration for secure session handling

---

## Decision 5: Neon PostgreSQL Configuration

**Decision**: Neon Serverless PostgreSQL with connection pooling

**Rationale**:
- User specified "Neon Serverless PostgreSQL"
- Serverless model suitable for variable load
- Built-in connection pooling for efficiency
- Cold start mitigation via UI loading states (per user risk assessment)

**Configuration**:
- Connection pooling: Enabled (required by constitution)
- SSL: Required for all connections
- Branching: Available for development/staging environments

**Risk Mitigation**:
- Cold starts: Implement loading states in UI (user-identified risk)
- Connection limits: Use pooling to stay within Neon free tier limits

---

## Decision 6: Project Structure

**Decision**: Monorepo with separate frontend/backend directories

**Rationale**:
- Clear separation between Python backend and Next.js frontend
- Independent deployment capability
- Shared types/contracts in spec directory
- Matches "Option 2: Web application" from plan template

**Structure**:
```
backend/          # FastAPI Python application
frontend/         # Next.js React application
specs/            # Specifications and contracts
```

---

## Decision 7: Testing Strategy

**Decision**: pytest for backend, Jest/Testing Library for frontend

**Rationale**:
- pytest: Standard Python testing (constitution compliant)
- Jest: Standard React/Next.js testing
- Integration tests for API endpoints
- E2E tests deferred to Phase 3

**Coverage Targets**:
- Backend services: 80%+ unit test coverage
- API endpoints: 100% integration test coverage
- Frontend: Component tests for critical flows

---

## Decision 8: Deployment Strategy

**Decision**: Vercel (frontend) + Railway/Render (backend)

**Rationale**:
- Vercel: Optimized for Next.js deployment
- Railway/Render: Simple Python/FastAPI deployment
- Both support environment variables for secrets
- Automatic deployments from Git

**Alternatives Considered**:
- Single deployment (Next.js API routes): Loses Python/constitution compliance
- Docker + AWS: More complex than needed for Phase 2

---

## Resolved Unknowns Summary

| Unknown | Resolution |
|---------|------------|
| Frontend Framework | Next.js with React |
| Backend Framework | FastAPI (Python 3.12+) |
| ORM | SQLAlchemy 2.0 |
| Auth | Better Auth v1.0+ |
| Database | Neon PostgreSQL (serverless) |
| Project Structure | Monorepo (frontend + backend) |
| Testing | pytest + Jest |
| Deployment | Vercel + Railway |

---

## Environment Variables Required

```env
# Database
DATABASE_URL=postgres://...@neon.tech/todoapp

# Better Auth
BETTER_AUTH_SECRET=<random-secret>
BETTER_AUTH_URL=http://localhost:8000

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Neon cold starts | Medium | Low | UI loading states |
| Better Auth complexity | Medium | Medium | Follow official docs, env var validation |
| CORS issues | High | Low | Proper FastAPI CORS configuration |
| Session expiry handling | Medium | Medium | Graceful redirect to login |
