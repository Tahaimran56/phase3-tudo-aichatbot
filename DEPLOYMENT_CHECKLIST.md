# Deployment Checklist: Separate Vercel Projects

This guide walks you through deploying your Todo app with **frontend and backend as separate Vercel projects**.

## 🎯 Overview

- **Frontend**: Next.js app → Separate Vercel project
- **Backend**: FastAPI app → Separate Vercel project
- **Database**: PostgreSQL (Neon, Supabase, etc.)

---

## 📋 Pre-Deployment Checklist

### ✅ 1. Database Setup

- [ ] PostgreSQL database created (recommend [Neon](https://neon.tech) - free tier available)
- [ ] Database connection string obtained
- [ ] Connection string includes `?sslmode=require` for production

**Example connection string:**
```
postgresql://user:password@ep-cool-name.us-east-2.aws.neon.tech/neondb?sslmode=require
```

### ✅ 2. Repository Preparation

- [ ] All changes committed to git
- [ ] Repository pushed to GitHub/GitLab/Bitbucket
- [ ] Sensitive files (.env) are in .gitignore

---

## 🚀 Step-by-Step Deployment

### STEP 1: Deploy Backend First (API)

#### 1.1 Create Vercel Project for Backend

**Via Vercel Dashboard:**
1. Go to https://vercel.com/new
2. Import your repository
3. **IMPORTANT**: Set "Root Directory" to `api`
4. Project Name: `todo-api` (or your choice)
5. **Don't click Deploy yet!**

#### 1.2 Configure Backend Environment Variables

In Project Settings → Environment Variables, add ALL of these:

| Variable Name | Example Value | Where to Get |
|---------------|---------------|--------------|
| `DATABASE_URL` | `postgresql://user:pass@host/db?sslmode=require` | Your Neon/PostgreSQL dashboard |
| `SECRET_KEY` | Generate using command below | Run: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `ALGORITHM` | `HS256` | Use this value |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Use this value (30 minutes) |
| `FRONTEND_URL` | `https://your-frontend.vercel.app` | Leave blank for now, will update after frontend deployment |
| `ENVIRONMENT` | `production` | Use this value |

**Apply to**: Select "Production", "Preview", and "Development" for each variable

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### 1.3 Deploy Backend

- Click "Deploy" button
- Wait for deployment to complete (2-3 minutes)
- Copy your backend URL (e.g., `https://todo-api-xyz.vercel.app`)

#### 1.4 Test Backend

Open in browser:
```
https://your-backend-url.vercel.app/health
```

Should return: `{"status": "healthy"}`

Also test API docs:
```
https://your-backend-url.vercel.app/docs
```

---

### STEP 2: Deploy Frontend

#### 2.1 Create Vercel Project for Frontend

**Via Vercel Dashboard:**
1. Go to https://vercel.com/new (again)
2. Import the SAME repository
3. **IMPORTANT**: Set "Root Directory" to `frontend`
4. Project Name: `todo-frontend` (or your choice)
5. Framework Preset: Next.js (should auto-detect)
6. **Don't click Deploy yet!**

#### 2.2 Configure Frontend Environment Variables

In Project Settings → Environment Variables, add:

| Variable Name | Value |
|---------------|-------|
| `NEXT_PUBLIC_API_URL` | `https://your-backend-url.vercel.app` (from Step 1.3) |

**Apply to**: Select "Production", "Preview", and "Development"

#### 2.3 Deploy Frontend

- Click "Deploy" button
- Wait for deployment to complete (2-3 minutes)
- Copy your frontend URL (e.g., `https://todo-frontend-xyz.vercel.app`)

---

### STEP 3: Update Backend with Frontend URL

#### 3.1 Add Frontend URL to Backend

Go back to **Backend Project** in Vercel:
1. Settings → Environment Variables
2. Find `FRONTEND_URL` variable
3. Update value to your actual frontend URL: `https://your-frontend-url.vercel.app`
4. Save

#### 3.2 Redeploy Backend

1. Go to Deployments tab
2. Click on the latest deployment
3. Click "⋯" menu → "Redeploy"
4. Select "Redeploy" (not "Redeploy with existing build cache")

---

### STEP 4: Verify Everything Works

#### 4.1 Test Backend
```bash
# Health check
curl https://your-backend-url.vercel.app/health

# Should return: {"status":"healthy"}
```

#### 4.2 Test Frontend

1. Open your frontend URL: `https://your-frontend-url.vercel.app`
2. Try to create an account:
   - Click "Sign Up"
   - Enter email and password
   - Click "Create Account"
3. Should successfully create account and log you in

#### 4.3 Check Browser Console

- Open browser DevTools (F12)
- Go to Console tab
- Should see NO errors
- API requests should go to your backend URL

#### 4.4 Check Network Tab

- Open DevTools → Network tab
- Click "Sign Up" or "Sign In"
- Look for requests to `/api/auth/signup` or `/api/auth/signin`
- Should show 200 or 201 status code
- Should NOT show CORS errors

---

## 🐛 Troubleshooting

### Issue: "Failed to load resource: 500"

**Solution**: Check backend logs
```bash
# Install Vercel CLI if not already
npm install -g vercel

# View logs
cd api
vercel logs

# Look for error messages
```

**Common causes:**
- Database tables not created → Should auto-create on startup
- Invalid DATABASE_URL → Check connection string
- Missing SECRET_KEY → Verify environment variable set

### Issue: "CORS error" or "Access-Control-Allow-Origin"

**Solution**: Verify CORS configuration

1. Backend `FRONTEND_URL` must match exact frontend URL
2. Check api/src/middleware/cors.py is updated (done in this setup)
3. Redeploy backend after changing `FRONTEND_URL`

### Issue: "relation 'users' does not exist"

**Solution**: Database tables not initialized

The `main.py` startup event should create tables automatically. If it doesn't:

1. Check backend logs for initialization errors
2. Verify DATABASE_URL is correct
3. Try manual initialization:
   ```bash
   # Local only - if you have direct database access
   cd api/src
   python init_db.py
   ```

### Issue: Frontend shows "Network Error" or "Failed to fetch"

**Solution**: API URL configuration

1. Verify `NEXT_PUBLIC_API_URL` is set in frontend
2. Check the URL is accessible: `curl https://your-backend-url.vercel.app/health`
3. Redeploy frontend after changing environment variables

### Issue: "Module not found" errors in deployment

**Solution**: Check file paths

1. Verify `vercel.json` root directory settings
2. Frontend root should be `frontend/`
3. Backend root should be `api/`

---

## 📊 Deployment URLs Reference

After deployment, you'll have:

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | `https://todo-frontend-[random].vercel.app` | User interface |
| Backend | `https://todo-api-[random].vercel.app` | REST API |
| API Docs | `https://todo-api-[random].vercel.app/docs` | Interactive API documentation |
| Health Check | `https://todo-api-[random].vercel.app/health` | Backend health status |

---

## 🔄 Making Updates After Deployment

### Update Frontend Code

```bash
cd frontend

# Make your changes to components, pages, etc.

git add .
git commit -m "Update: description of changes"
git push

# Vercel automatically deploys on push to main branch
```

### Update Backend Code

```bash
cd api

# Make your changes to routes, models, etc.

git add .
git commit -m "Update: description of changes"
git push

# Vercel automatically deploys on push to main branch
```

### Update Environment Variables

1. Go to Vercel Dashboard → Project → Settings → Environment Variables
2. Edit the variable
3. Select which environments (Production/Preview/Development)
4. Save
5. **IMPORTANT**: Redeploy for changes to take effect

---

## 🎉 Success Criteria

Your deployment is successful when:

- [ ] Backend health check returns `{"status":"healthy"}`
- [ ] Frontend loads without errors
- [ ] Can sign up a new user
- [ ] Can sign in with created user
- [ ] Can create, view, update, and delete tasks
- [ ] No CORS errors in browser console
- [ ] No 500 errors on any endpoint

---

## 📞 Need Help?

If you're still having issues:

1. **Check Vercel logs**:
   ```bash
   vercel logs --app=todo-api
   vercel logs --app=todo-frontend
   ```

2. **Check deployment function logs** in Vercel Dashboard:
   - Project → Deployments → Click deployment → Functions tab

3. **Verify environment variables** are set correctly in both projects

4. **Test locally first**:
   ```bash
   # Backend
   cd api/src
   uvicorn main:app --reload

   # Frontend (in another terminal)
   cd frontend
   npm run dev
   ```

---

## 🚀 Next Steps

After successful deployment:

1. **Set up custom domains** (optional):
   - Vercel Dashboard → Project → Settings → Domains

2. **Enable HTTPS** (automatic on Vercel)

3. **Set up monitoring**:
   - Enable Vercel Analytics
   - Add error tracking (Sentry, etc.)

4. **Database backups**:
   - Configure automatic backups on Neon/Supabase

5. **CI/CD**:
   - Already set up! Vercel auto-deploys on git push

---

## ✅ Configuration Files Created

This setup created the following files:

```
todo/
├── frontend/
│   ├── vercel.json              # Frontend Vercel config
│   ├── .vercelignore            # Files to ignore in deployment
│   ├── .env.example             # Environment template
│   ├── next.config.ts           # Updated with API proxy
│   └── DEPLOYMENT.md            # Detailed frontend guide
│
├── api/
│   ├── vercel.json              # Backend Vercel config
│   ├── .vercelignore            # Files to ignore in deployment
│   ├── .env.example             # Environment template
│   ├── src/
│   │   ├── main.py              # Updated with startup event
│   │   └── middleware/cors.py   # Updated CORS config
│   └── DEPLOYMENT.md            # Detailed backend guide
│
└── DEPLOYMENT_CHECKLIST.md      # This file
```

---

## 🔐 Security Reminders

- [ ] Never commit `.env` files
- [ ] Use strong `SECRET_KEY` (32+ characters)
- [ ] Always use `?sslmode=require` in production DATABASE_URL
- [ ] Keep dependencies updated
- [ ] Review Vercel logs regularly

---

**Happy Deploying! 🎉**

Need more help? Check the detailed guides:
- Frontend: `frontend/DEPLOYMENT.md`
- Backend: `api/DEPLOYMENT.md`
