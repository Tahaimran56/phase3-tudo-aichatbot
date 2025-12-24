# Quickstart Guide: Phase 3 - AI Chatbot

**Feature**: Phase 3 - AI Chatbot
**Date**: 2025-12-24
**Prerequisites**: Phase 2 completed (backend + frontend running successfully)

## Overview

This guide walks through setting up the Phase 3 AI chatbot locally for development and testing. Phase 3 adds conversational AI capabilities to the existing todo application, allowing users to manage tasks through natural language chat.

---

## Prerequisites

Before starting Phase 3 setup, ensure:

1. ✅ Phase 2 is complete and running successfully
2. ✅ Backend running on `http://localhost:8000`
3. ✅ Frontend running on `http://localhost:3000`
4. ✅ Neon PostgreSQL database is accessible
5. ✅ Better Auth authentication is working
6. ✅ Python 3.12+ installed
7. ✅ Node.js 18+ installed
8. ✅ OpenAI API key obtained (sign up at https://platform.openai.com)

---

## Step 1: Environment Configuration

### 1.1 Backend Environment Variables

Add the following to `backend/.env`:

```bash
# Existing Phase 2 variables (keep these)
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=...
BETTER_AUTH_URL=...

# NEW: Phase 3 OpenAI Configuration
OPENAI_API_KEY=sk-proj-...              # Required: Your OpenAI API key
OPENAI_MODEL=gpt-4o-mini                 # Cost-effective model
OPENAI_TIMEOUT=10                        # Request timeout (seconds)

# NEW: Phase 3 Chat Configuration
MAX_CONVERSATION_MESSAGES=20             # Load last 20 messages for context
CHAT_RATE_LIMIT_PER_MINUTE=60           # Rate limit: 60 requests/min per user

# NEW: Phase 3 PII Detection (Optional)
PII_DETECTION_ENABLED=true              # Enable basic PII pattern matching
PII_LOG_DETECTIONS=true                 # Log when PII is detected
```

**Get Your OpenAI API Key**:
1. Go to https://platform.openai.com/api-keys
2. Sign in or create account
3. Click "Create new secret key"
4. Copy the key and add to `.env` as `OPENAI_API_KEY`

**Important**: Add `.env` to `.gitignore` to avoid committing API keys!

### 1.2 Frontend Environment Variables

No new environment variables needed for Phase 3 frontend. Existing Phase 2 configuration is sufficient.

---

## Step 2: Install Dependencies

### 2.1 Backend Dependencies

```bash
cd backend

# Activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Phase 3 dependencies
pip install openai>=1.0.0
pip install slowapi>=0.1.9

# Or update from requirements.txt (if updated)
pip install -r requirements.txt
```

### 2.2 Frontend Dependencies

No new dependencies needed for Phase 3 (custom chat UI built with existing stack).

```bash
cd frontend

# Verify existing dependencies are installed
npm install  # Should be already done from Phase 2
```

---

## Step 3: Database Migrations

Apply database migrations to create Conversation and Message tables.

```bash
cd backend

# Ensure virtual environment is activated
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run migrations
alembic upgrade head

# Expected output:
# INFO  [alembic.runtime.migration] Running upgrade 002_initial_tasks -> 003_add_conversations
# INFO  [alembic.runtime.migration] Running upgrade 003_add_conversations -> 004_add_messages
```

**Verify Migration Success**:

```bash
# Connect to database and verify tables exist
psql $DATABASE_URL -c "\dt"

# Should show:
#  conversations
#  messages
#  tasks
#  users
```

**Troubleshooting**:
- If migrations fail, check `DATABASE_URL` is correct in `.env`
- Ensure Neon database is accessible and user has CREATE TABLE permissions
- Check alembic/versions/ for 003 and 004 migration files

---

## Step 4: Start Backend Server

```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start FastAPI server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process [PID]
# INFO:     Started server process [PID]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
```

**Verify Backend**:
- Open http://localhost:8000/docs
- Should see Swagger UI with `/api/{user_id}/chat` endpoint listed
- Existing Phase 2 endpoints (auth, tasks) should still be present

---

## Step 5: Start Frontend Server

```bash
cd frontend

# Start Next.js development server
npm run dev

# Expected output:
# ▲ Next.js 16.x.x
# - Local:        http://localhost:3000
# - Ready in X.Xs
```

**Verify Frontend**:
- Open http://localhost:3000
- Sign in with existing Phase 2 account
- Navigation should now include "Chat" link

---

## Step 6: Test Chat Interface

### 6.1 Access Chat Page

1. Navigate to http://localhost:3000
2. Sign in with your Phase 2 account
3. Click "Chat" in navigation
4. Should see chat interface with input box

### 6.2 Test Basic Chat Commands

Try these natural language commands:

**Create Task**:
```
You: Add a task to buy groceries
AI: I've created a task 'Buy groceries' with ID 42.
```

**List Tasks**:
```
You: Show me all my tasks
AI: Here are your tasks:
1. Task 42: Buy groceries (pending)
2. Task 43: Finish report (pending)
```

**Complete Task**:
```
You: Mark task 42 as complete
AI: Great! I've marked task 42 'Buy groceries' as complete.
```

**Update Task**:
```
You: Change task 43 to 'Finish Q4 report'
AI: I've updated task 43 to 'Finish Q4 report'.
```

**Delete Task**:
```
You: Delete task 42
AI: I've deleted task 42 'Buy groceries'.
```

### 6.3 Test Conversation Persistence

1. Send several messages in chat
2. Refresh the page
3. Previous conversation should still be visible
4. Continue conversation - AI should remember context

---

## Step 7: Verify API Endpoints

### 7.1 Using Swagger UI

1. Go to http://localhost:8000/docs
2. Click on `POST /api/{user_id}/chat`
3. Click "Try it out"
4. Enter your `user_id` (get from auth token or database)
5. Enter request body:
   ```json
   {
     "message": "Add a task to test the API"
   }
   ```
6. Click "Execute"
7. Should see 200 response with `conversation_id` and AI response

### 7.2 Using curl

```bash
# Get auth token first
TOKEN="your-jwt-token-here"
USER_ID="your-user-id-here"

# Send chat message
curl -X POST "http://localhost:8000/api/$USER_ID/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me all my tasks"
  }'

# Expected response:
# {
#   "conversation_id": "660e8400-e29b-41d4-a716-446655440001",
#   "response": "Here are your tasks: ...",
#   "tool_calls": [
#     {
#       "tool": "list_tasks",
#       "parameters": {"status": "all"},
#       "result": {"tasks": [...]}
#     }
#   ]
# }
```

---

## Step 8: Verify Rate Limiting

Test rate limiting is working:

```bash
# Send 61 requests rapidly (exceeds 60/minute limit)
for i in {1..61}; do
  curl -X POST "http://localhost:8000/api/$USER_ID/chat" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"message": "Test"}' \
    -s -w "\n%{http_code}\n" | tail -1
done

# First 60 should return 200
# 61st should return 429 (Too Many Requests)
```

---

## Step 9: Monitor Logs

### 9.1 Backend Logs

```bash
# Backend terminal should show:
INFO:     POST /api/{user_id}/chat 200 OK
INFO:     OpenAI API call completed in 1.2s
INFO:     Tool executed: add_task (task_id: 42)
```

### 9.2 Check for PII Detections (if enabled)

```bash
# If PII_LOG_DETECTIONS=true, logs will show:
WARNING:  PII detected in message: ['email']
```

---

## Troubleshooting

### Issue: "OpenAI API key not configured"

**Solution**:
- Verify `OPENAI_API_KEY` is set in `backend/.env`
- Restart backend server after adding environment variable
- Check API key is valid at https://platform.openai.com/api-keys

### Issue: "Module 'openai' not found"

**Solution**:
```bash
cd backend
source venv/bin/activate
pip install openai>=1.0.0
```

### Issue: "Conversation table does not exist"

**Solution**:
```bash
cd backend
alembic upgrade head
```

### Issue: "Rate limit exceeded immediately"

**Solution**:
- Check `CHAT_RATE_LIMIT_PER_MINUTE` in `.env`
- Restart backend server
- Clear browser cache and cookies

### Issue: "AI responses are very slow (>5s)"

**Possible Causes**:
- OpenAI API experiencing high load
- Network latency
- Large conversation history (>20 messages)

**Solution**:
- Check OpenAI API status: https://status.openai.com
- Reduce `MAX_CONVERSATION_MESSAGES` in `.env`
- Consider using `gpt-3.5-turbo` instead of `gpt-4o-mini` (faster but less accurate)

### Issue: "Chat UI not showing in navigation"

**Solution**:
- Verify frontend code includes chat route
- Clear browser cache
- Check browser console for errors
- Restart frontend dev server

---

## Next Steps

### For Development

1. **Write Tests**: Add unit tests for MCP tools and integration tests for chat endpoint
2. **Add Logging**: Enhance logging for debugging AI interactions
3. **Error Handling**: Improve error messages for edge cases
4. **UI Polish**: Add loading states, error states, empty states to chat UI

### For Production

1. **Environment Secrets**: Use secrets manager (AWS Secrets Manager, HashiCorp Vault) for `OPENAI_API_KEY`
2. **Rate Limiting**: Upgrade to Redis-backed rate limiting with `slowapi`
3. **Monitoring**: Add metrics for OpenAI API latency, tool execution success rates
4. **Cost Tracking**: Monitor OpenAI API usage and costs via OpenAI dashboard
5. **Conversation Pruning**: Implement cleanup job for old conversations (optional)

---

## Useful Commands

### Backend

```bash
# Run backend tests
pytest

# Run specific test file
pytest tests/services/test_chat_service.py

# Check linting
ruff check src/

# Format code
ruff format src/
```

### Frontend

```bash
# Run frontend tests
npm test

# Run specific test
npm test ChatInterface

# Check TypeScript types
npm run type-check

# Build for production
npm run build
```

### Database

```bash
# View conversations
psql $DATABASE_URL -c "SELECT id, user_id, created_at FROM conversations ORDER BY created_at DESC LIMIT 10;"

# View messages
psql $DATABASE_URL -c "SELECT conversation_id, role, content FROM messages ORDER BY created_at DESC LIMIT 20;"

# Count messages per conversation
psql $DATABASE_URL -c "SELECT conversation_id, COUNT(*) as message_count FROM messages GROUP BY conversation_id;"
```

---

## Example Conversation Flow

```
User:  Hi, can you help me manage my tasks?
AI:    Of course! I can help you add, view, complete, update, and delete tasks.
       What would you like to do?

User:  Add a task to buy groceries
AI:    I've created a task 'Buy groceries' with ID 42. Anything else?

User:  Also add a task to call mom tonight
AI:    I've created a task 'Call mom tonight' with ID 43.

User:  Show me all my tasks
AI:    Here are your tasks:
       1. Task 42: Buy groceries (pending)
       2. Task 43: Call mom tonight (pending)

User:  Mark the groceries task as complete
AI:    Great! I've marked task 42 'Buy groceries' as complete.

User:  Thanks!
AI:    You're welcome! Let me know if you need anything else.
```

---

## Resources

- **OpenAI Documentation**: https://platform.openai.com/docs
- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **Next.js Documentation**: https://nextjs.org/docs
- **Neon PostgreSQL**: https://neon.tech/docs

---

**Generated**: 2025-12-24
**Author**: AI Agent (Claude Sonnet 4.5)
**Status**: Complete
**Next**: Run `/sp.tasks` to generate implementation tasks
