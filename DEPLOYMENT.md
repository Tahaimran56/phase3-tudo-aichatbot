# Deployment Guide - Vercel Full Stack

## Architecture

This application is a **full-stack monorepo** that deploys both frontend and backend to Vercel:
1. **Frontend**: Next.js app
2. **Backend**: FastAPI Python app
3. **Database**: Neon PostgreSQL (serverless)

## 🚀 Quick Deploy to Vercel (Recommended)

Vercel now supports FastAPI with **zero configuration**! You can deploy both frontend and backend in a single deployment.

### Prerequisites

1. A [Vercel account](https://vercel.com)
2. A [Neon PostgreSQL database](https://neon.tech) (free tier available)
3. Your code pushed to GitHub

### Step 1: Prepare Your Database

1. Go to [Neon Console](https://console.neon.tech)
2. Copy your connection string (it looks like):
   ```
   postgresql://username:password@host/database?sslmode=require
   ```
3. Keep this handy - you'll need it for environment variables

### Step 2: Deploy to Vercel

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click **"Add New Project"**
3. Import your GitHub repository
4. Vercel will automatically detect the configuration from `vercel.json`
5. **Add Environment Variables** (click "Environment Variables"):

   ```
   DATABASE_URL=postgresql://your-neon-connection-string
   SECRET_KEY=your-secret-key-at-least-32-characters-long
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   FRONTEND_URL=https://your-app.vercel.app
   ENVIRONMENT=production
   ```

   **Important Notes:**
   - Replace `DATABASE_URL` with your actual Neon connection string
   - Generate a secure `SECRET_KEY` (at least 32 characters)
   - Update `FRONTEND_URL` after deployment (you can edit it later)

6. Click **"Deploy"**

### Step 3: Update Frontend URL

After your first deployment:

1. Copy your Vercel deployment URL (e.g., `https://your-app.vercel.app`)
2. Go to your Vercel project settings → Environment Variables
3. Update `FRONTEND_URL` to your actual Vercel URL
4. Redeploy to apply changes

## 📁 Project Structure

```
todo/
├── api/
│   └── index.py              # Vercel FastAPI entry point
├── backend/
│   └── src/
│       ├── main.py           # FastAPI application
│       ├── api/              # API endpoints
│       ├── models/           # Database models
│       ├── services/         # Business logic
│       └── ...
├── frontend/
│   ├── src/                  # Next.js application
│   └── ...
├── requirements.txt          # Python dependencies
├── vercel.json              # Vercel configuration
├── .vercelignore            # Files to ignore in deployment
└── .env.example             # Environment variables template

```

## 🔧 How It Works

### Vercel Configuration (`vercel.json`)

The project is configured to:
- Install Python dependencies from `requirements.txt`
- Install Node.js dependencies for the frontend
- Build the Next.js frontend
- Route `/api/*` requests to the FastAPI backend
- Route all other requests to the Next.js frontend

### API Routing

- **Frontend**: `https://your-app.vercel.app/` → Next.js app
- **Backend API**: `https://your-app.vercel.app/api/*` → FastAPI endpoints

Example endpoints:
- `GET /api/` → Backend health check
- `POST /api/auth/signup` → User registration
- `POST /api/auth/signin` → User login
- `GET /api/tasks` → Get user's tasks

## 🔐 Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Neon PostgreSQL connection string | `postgresql://user:pass@host/db?sslmode=require` |
| `SECRET_KEY` | JWT secret key (32+ chars) | `your-super-secret-key-here` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `30` |
| `FRONTEND_URL` | Your Vercel app URL | `https://your-app.vercel.app` |
| `ENVIRONMENT` | Environment name | `production` |

### Setting Environment Variables

#### Via Vercel Dashboard:
1. Go to your project → Settings → Environment Variables
2. Add each variable with its value
3. Select "Production", "Preview", and "Development"
4. Click "Save"

#### Via Vercel CLI:
```bash
vercel env add DATABASE_URL
vercel env add SECRET_KEY
# ... add other variables
```

## 🧪 Testing Your Deployment

1. Visit your Vercel URL: `https://your-app.vercel.app`
2. Try to create an account (sign up)
3. Sign in with your credentials
4. Create, update, and delete tasks
5. Check the browser console for errors

### Testing the API Directly

```bash
# Health check
curl https://your-app.vercel.app/api/

# Create account
curl -X POST https://your-app.vercel.app/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

## 🔄 Continuous Deployment

Once connected to GitHub, Vercel will automatically:
- Deploy when you push to `main` branch
- Create preview deployments for pull requests
- Run builds and tests before deployment

## 🐛 Troubleshooting

### "500 Internal Server Error" on API Calls

1. Check Vercel logs:
   - Go to your project dashboard
   - Click "Deployments" → Select latest deployment
   - Click "Runtime Logs"

2. Common issues:
   - Missing environment variables
   - Invalid `DATABASE_URL`
   - Database connection issues

### "Module not found" Errors

1. Verify `requirements.txt` includes all dependencies
2. Check that `api/index.py` correctly imports from `backend/src`
3. Redeploy to rebuild dependencies

### Database Connection Issues

1. Verify your Neon database is active
2. Check that `DATABASE_URL` includes `?sslmode=require`
3. Ensure Neon allows connections from anywhere (it does by default)

### CORS Errors

1. Verify `FRONTEND_URL` environment variable matches your Vercel URL
2. Check that you're using the correct protocol (`https://`)
3. Redeploy after updating environment variables

## 📊 Vercel Limits (Free Tier)

- **Function Duration**: 10 seconds
- **Function Size**: 250MB
- **Bandwidth**: 100GB/month
- **Invocations**: Unlimited

For production apps with higher traffic, consider upgrading to Vercel Pro.

## 🆘 Getting Help

- **Vercel FastAPI Docs**: https://vercel.com/docs/frameworks/backend/fastapi
- **Vercel Community**: https://vercel.com/community
- **Project Issues**: Check your Vercel deployment logs

## 📝 Local Development

```bash
# Backend (FastAPI)
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r ../requirements.txt
uvicorn src.main:app --reload

# Frontend (Next.js)
cd frontend
npm install
npm run dev
```

## 🎉 Success!

Once deployed, you'll have:
- ✅ Full-stack app running on Vercel
- ✅ FastAPI backend with automatic scaling
- ✅ Next.js frontend with SSR
- ✅ PostgreSQL database with Neon
- ✅ Automatic deployments from GitHub
- ✅ HTTPS and custom domain support

Your todo app is now live! 🚀
