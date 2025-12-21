# Quickstart: Phase 2 Todo Web App

**Feature**: `002-todo-web-app`
**Date**: 2025-12-21

## Prerequisites

- Python 3.12+
- Node.js 18+ (for frontend)
- Neon PostgreSQL account
- Git

## Environment Setup

### 1. Clone and Navigate

```bash
cd todo
```

### 2. Backend Setup

```bash
# Create Python virtual environment
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Unix/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

### 4. Environment Variables

Create `.env` files:

**backend/.env**:
```env
# Database (from Neon dashboard)
DATABASE_URL=postgres://user:password@ep-xxx.region.neon.tech/todoapp?sslmode=require

# Better Auth
BETTER_AUTH_SECRET=your-32-character-random-secret
BETTER_AUTH_URL=http://localhost:8000

# CORS
FRONTEND_URL=http://localhost:3000
```

**frontend/.env.local**:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 5. Database Migration

```bash
cd backend

# Run Alembic migrations
alembic upgrade head
```

## Running the Application

### Start Backend (Terminal 1)

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn src.main:app --reload --port 8000
```

Backend available at: http://localhost:8000
API docs available at: http://localhost:8000/docs

### Start Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

Frontend available at: http://localhost:3000

## Verification Scenarios

### Scenario 1: User Signup (US1)

1. Open http://localhost:3000
2. Click "Sign Up"
3. Enter email: `test@example.com`
4. Enter password: `testpass123`
5. Click "Create Account"
6. **Expected**: Redirected to empty dashboard

### Scenario 2: Task Creation (US2, US3)

1. Sign in as `test@example.com`
2. Click "Add Task"
3. Enter title: "Buy groceries"
4. Enter description: "Milk, bread, eggs"
5. Click "Save"
6. **Expected**: Task appears in list with "Pending" status

### Scenario 3: Task Persistence (US2)

1. Create a task (as above)
2. Click "Sign Out"
3. Sign back in
4. **Expected**: Previously created task is still visible

### Scenario 4: Mark Complete (US3)

1. Sign in with existing tasks
2. Click "Complete" on a pending task
3. **Expected**: Task status changes to "Complete"

### Scenario 5: Update Task (US3)

1. Sign in with existing tasks
2. Click "Edit" on a task
3. Change title to "Buy groceries (updated)"
4. Click "Save"
5. **Expected**: Task title is updated

### Scenario 6: Delete Task (US3)

1. Sign in with existing tasks
2. Click "Delete" on a task
3. Confirm deletion
4. **Expected**: Task is removed from list

### Scenario 7: Multi-User Isolation (FR-006)

1. Create user A (`usera@example.com`), add a task
2. Sign out
3. Create user B (`userb@example.com`)
4. **Expected**: User B sees empty task list (not User A's tasks)

### Scenario 8: Mobile Responsiveness (US4)

1. Open browser DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Select iPhone SE or similar mobile viewport
4. Navigate through app
5. **Expected**: Layout adapts, buttons are tappable

## API Testing with curl

### Signup

```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}' \
  -c cookies.txt
```

### Signin

```bash
curl -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}' \
  -c cookies.txt
```

### List Tasks

```bash
curl http://localhost:8000/api/tasks \
  -b cookies.txt
```

### Create Task

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task", "description": "From curl"}' \
  -b cookies.txt
```

### Complete Task

```bash
curl -X PATCH http://localhost:8000/api/tasks/1/complete \
  -b cookies.txt
```

### Delete Task

```bash
curl -X DELETE http://localhost:8000/api/tasks/1 \
  -b cookies.txt
```

## Troubleshooting

### Database Connection Failed

- Verify `DATABASE_URL` is correct in `.env`
- Check Neon dashboard for connection string
- Ensure SSL mode is `require`

### CORS Errors

- Verify `FRONTEND_URL` in backend `.env`
- Check browser console for specific CORS error
- Restart backend after `.env` changes

### Better Auth Session Issues

- Verify `BETTER_AUTH_SECRET` is set (32+ characters)
- Clear browser cookies and try again
- Check backend logs for auth errors

### Neon Cold Start

- First request may be slow (1-2 seconds)
- Subsequent requests should be <500ms
- Loading states should display during cold start

## Success Criteria Checklist

- [ ] SC-001: Signup to first task < 3 minutes
- [ ] SC-002: CRUD operations < 10 seconds
- [ ] SC-003: Correct status codes (check API docs)
- [ ] SC-004: Mobile (375px) and desktop (1440px) work
- [ ] SC-005: User data isolation verified
