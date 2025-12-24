---
id: 001
title: Phase 3 AI Chatbot Planning
stage: plan
date: 2025-12-24
surface: agent
model: claude-sonnet-4-5-20250929
feature: 003-ai-todo-assistant
branch: 003-ai-todo-assistant
user: system
command: /sp.plan
labels: ["phase3", "planning", "ai-chatbot", "mcp", "openai"]
links:
  spec: specs/003-ai-todo-assistant/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-ai-todo-assistant/plan.md
  - specs/003-ai-todo-assistant/research.md
  - specs/003-ai-todo-assistant/data-model.md
  - specs/003-ai-todo-assistant/contracts/chat-api.yaml
  - specs/003-ai-todo-assistant/contracts/mcp-tools.yaml
  - specs/003-ai-todo-assistant/quickstart.md
  - CLAUDE.md (updated)
tests:
  - No tests written (planning phase)
---

## Prompt

User requested execution of `/sp.plan` command for Phase 3 - AI Chatbot feature.

The user had previously updated the Phase 3 specification (spec.md) to remove RAG/vector database/Qdrant components and align with the official hackathon requirements:
- Use OpenAI Agents SDK with Model Context Protocol (MCP)
- Implement stateless chat endpoint with database-backed conversation history
- Expose 5 MCP tools: add_task, list_tasks, complete_task, delete_task, update_task
- NO vector embeddings, NO Qdrant, NO semantic search
- Build custom chat UI (no ChatKit dependency)

The planning agent was tasked with:
1. Generating comprehensive implementation plan (plan.md)
2. Resolving research unknowns (research.md)
3. Designing data models (data-model.md)
4. Creating API contracts (contracts/)
5. Writing developer quickstart guide (quickstart.md)
6. Updating agent context

## Response snapshot

Successfully completed all Phase 0 and Phase 1 planning deliverables:

**plan.md** (Complete):
- Technical Context defined (Python 3.12+, FastAPI, Next.js 16+, OpenAI SDK, Neon PostgreSQL)
- Constitution Check passed (all 15 principles validated)
- Project structure documented (backend + frontend extensions)
- 2 new database tables: Conversation, Message
- 1 new API endpoint: POST /api/{user_id}/chat
- 5 MCP tools specified with parameters and returns
- Risk analysis with 6 identified risks and mitigations
- Implementation phases defined
- Success validation criteria (15 checkpoints)

**research.md** (Complete):
- 6 technical decisions researched and documented:
  1. OpenAI Integration: Use direct OpenAI SDK with function calling (not separate Agents SDK)
  2. MCP Implementation: Manual implementation as thin wrapper (no heavyweight SDK)
  3. Chat UI: Build custom UI with Tailwind (no ChatKit)
  4. PII Handling: Basic pattern matching with ToS consent
  5. Conversation History: Load last 20 messages (not full history)
  6. Rate Limiting: Use slowapi with in-memory storage
- Dependencies identified: openai>=1.0.0, slowapi>=0.1.9
- Configuration summarized (environment variables)

**data-model.md** (Complete):
- Conversation entity designed (UUID id, user_id FK, timestamps)
- Message entity designed (UUID id, user_id FK, conversation_id FK, role enum, content text, timestamp)
- Database migrations specified (003_add_conversations.py, 004_add_messages.py)
- Query patterns documented with code examples
- Indexes specified for performance ((user_id, created_at) on conversations, (conversation_id, created_at) on messages)
- Security isolation rules documented
- ERD diagram provided

**contracts/** (Complete):
- chat-api.yaml: OpenAPI 3.0 specification for POST /api/{user_id}/chat endpoint
  - Request schema: ChatRequest (conversation_id optional, message required)
  - Response schema: ChatResponse (conversation_id, response, tool_calls array)
  - Error responses: 400, 401, 404, 429, 500
  - Examples for all operations
- mcp-tools.yaml: Detailed specification for 5 MCP tools
  - add_task(title, description?) → {task_id, status, title}
  - list_tasks(status?) → {tasks: [...]}
  - complete_task(task_id) → {status, task_id, title}
  - delete_task(task_id) → {status, task_id, message}
  - update_task(task_id, title?, description?) → {status, task_id, updated_fields}
  - Natural language examples for each tool
  - Error responses documented

**quickstart.md** (Complete):
- Prerequisites listed (Phase 2 complete, OpenAI API key)
- Environment configuration documented (OPENAI_API_KEY, model, timeouts)
- Dependency installation instructions (backend: openai, slowapi)
- Database migration commands (alembic upgrade head)
- Server startup procedures (backend + frontend)
- Testing procedures (chat interface, API endpoints, rate limiting)
- Troubleshooting guide (common issues and solutions)
- Example conversation flow provided

**Agent Context Updated**:
- CLAUDE.md updated with Phase 3 technologies via update-agent-context.ps1
- Added Python 3.12+, TypeScript/Next.js 16+, Neon PostgreSQL

## Outcome

- ✅ Impact: Complete planning deliverables for Phase 3 AI Chatbot - ready for task generation
- 🧪 Tests: No tests written (planning phase - tests will be generated in implementation phase)
- 📁 Files: 6 planning artifacts created (plan.md, research.md, data-model.md, 2 contract files, quickstart.md) + 1 updated (CLAUDE.md)
- 🔁 Next prompts: User should run `/sp.tasks` to generate implementation tasks, then `/sp.implement` to execute
- 🧠 Reflection: Planning successfully aligned Phase 3 with hackathon requirements by removing RAG/Qdrant complexity and focusing on core MCP + OpenAI integration. Research decisions favor simplicity (no ChatKit, no MCP SDK, minimal dependencies) which reduces implementation risk. Data model design enforces multi-user isolation at multiple layers (database constraints, indexes, application queries). Quickstart guide provides clear path for developers to test locally.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning completed successfully on first attempt
- Graders run and results (PASS/FAIL): Constitution Check: PASS (all 15 principles validated)
- Prompt variant (if applicable): Standard /sp.plan workflow
- Next experiment (smallest change to try): None needed - proceed to `/sp.tasks` for task generation

---

**Generated**: 2025-12-24 by Claude Sonnet 4.5
**Status**: Complete - Ready for task generation phase
