# Deployment Guide

## Architecture

This application consists of two parts:
1. **Frontend**: Next.js app (deployed to Vercel)
2. **Backend**: FastAPI app (needs separate deployment)

## Backend Deployment

The backend needs to be deployed separately. Recommended options:

### Option 1: Render.com (Recommended - Free Tier Available)

1. Go to [render.com](https://render.com)
2. Create a new Web Service
3. Connect your GitHub repository
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn src.main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**:
     ```
     DATABASE_URL=postgresql://neondb_owner:npg_j8lLfYvn7rqk@ep-misty-bird-a4pp85kw-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require
     SECRET_KEY=tahatahatahatahatahatahatahatahataha
     ALGORITHM=HS256
     ACCESS_TOKEN_EXPIRE_MINUTES=30
     FRONTEND_URL=https://your-frontend-url.vercel.app
     ENVIRONMENT=production
     ```

5. Copy the deployed backend URL (e.g., `https://your-app.onrender.com`)

### Option 2: Railway.app

1. Go to [railway.app](https://railway.app)
2. Create new project from GitHub repo
3. Add environment variables (same as above)
4. Deploy

### Option 3: Fly.io

1. Install Fly CLI
2. Run `fly launch` in the backend directory
3. Configure environment variables
4. Deploy with `fly deploy`

## Frontend Deployment to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Import your GitHub repository
3. Configure build settings:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

4. Add Environment Variables in Vercel:
   ```
   NEXT_PUBLIC_API_URL=/api
   BACKEND_API_URL=https://your-backend-url.onrender.com
   ```

   **IMPORTANT**: Replace `https://your-backend-url.onrender.com` with your actual deployed backend URL from step 1.

5. Deploy

## Testing Production Deployment

1. Visit your Vercel URL
2. Try to create an account
3. Check browser console for any errors
4. Verify the API requests are going through the Next.js proxy (`/api/auth/signup`)

## Environment Variables Summary

### Frontend (.env.production)
- `NEXT_PUBLIC_API_URL=/api` - Frontend uses Next.js API routes as proxy
- `BACKEND_API_URL=https://your-backend.com` - Backend API URL for server-side proxying

### Backend (.env or Render environment variables)
- `DATABASE_URL` - Neon PostgreSQL connection string
- `SECRET_KEY` - JWT secret key
- `ALGORITHM=HS256` - JWT algorithm
- `ACCESS_TOKEN_EXPIRE_MINUTES=30` - Token expiration
- `FRONTEND_URL` - Your Vercel frontend URL (for CORS)
- `ENVIRONMENT=production` - Environment name

## Troubleshooting

### "Not Found" Error on Signup/Signin

1. Check Vercel logs: `vercel logs`
2. Verify `BACKEND_API_URL` environment variable in Vercel
3. Ensure backend is deployed and running
4. Check CORS settings in backend

### Database Connection Issues

1. Verify `DATABASE_URL` in backend environment
2. Ensure Neon database is accessible
3. Check database connection pooling settings

### Cookie/Session Issues

1. Verify `FRONTEND_URL` in backend matches your Vercel domain
2. Check CORS credentials settings
3. Ensure cookies are being set with correct domain

## Architecture Flow

```
User Browser
     ↓
Next.js Frontend (Vercel)
     ↓
Next.js API Routes (/api/*)
     ↓
FastAPI Backend (Render/Railway/Fly)
     ↓
Neon PostgreSQL Database
```

This setup ensures:
- No CORS issues (API routes proxy requests)
- Cookies work properly (same domain)
- Backend can be deployed anywhere
- Easy to scale and maintain
