# Backend API Deployment Guide (Vercel)

## Prerequisites
- Vercel account
- PostgreSQL database (Neon, Supabase, or similar)
- Database connection string

## Deployment Steps

### 1. Prepare Database

Make sure your PostgreSQL database is ready:
- Database created
- Connection string available (with `?sslmode=require` for production)

### 2. Deploy to Vercel

#### Option A: Via Vercel CLI
```bash
# Install Vercel CLI globally
npm install -g vercel

# Navigate to API directory
cd api

# Login to Vercel
vercel login

# Deploy
vercel

# For production deployment
vercel --prod
```

#### Option B: Via Vercel Dashboard
1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your repository
3. Set Root Directory to `api`
4. Click Deploy

### 3. Configure Environment Variables

In Vercel Dashboard → Your Project → Settings → Environment Variables:

Add the following **CRITICAL** variables:

| Name | Value | Environment |
|------|-------|-------------|
| `DATABASE_URL` | `postgresql://user:pass@host/db?sslmode=require` | Production, Preview, Development |
| `SECRET_KEY` | Generate a secure random string (32+ chars) | Production, Preview, Development |
| `ALGORITHM` | `HS256` | Production, Preview, Development |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Production, Preview, Development |
| `FRONTEND_URL` | `https://your-frontend.vercel.app` | Production, Preview, Development |
| `ENVIRONMENT` | `production` | Production, Preview, Development |

**Generate SECRET_KEY:**
```bash
# Python method
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or use OpenSSL
openssl rand -base64 32
```

### 4. Redeploy

After setting environment variables:
- Go to Deployments tab
- Click on the latest deployment
- Click "Redeploy"

### 5. Initialize Database

The app will automatically create tables on first startup (via the startup event in main.py).

To manually initialize:
```bash
# Local only - if you have database access
cd api/src
python init_db.py
```

### 6. Verify Deployment

Test your API:

```bash
# Health check
curl https://your-backend.vercel.app/health

# API docs
# Visit: https://your-backend.vercel.app/docs
```

## Local Development

```bash
# Create .env file
cp .env.example .env

# Edit .env with your local database credentials

# Install dependencies
pip install -r requirements.txt

# Run development server (from api/src directory)
cd src
uvicorn main:app --reload --port 8000
```

Visit: http://localhost:8000/docs

## Troubleshooting

### Database Connection Errors
- Verify `DATABASE_URL` is correct
- Ensure `?sslmode=require` is in the connection string
- Check database allows external connections
- Verify IP whitelist (some providers require this)

### Import Errors
- Check `index.py` path resolution
- Verify all dependencies in `requirements.txt`
- Check function names match between files

### 500 Errors on Signup/Signin
- Check database tables are created (visit `/health` endpoint)
- Verify `SECRET_KEY` is set
- Review Vercel function logs

### Timeout Errors
- Optimize slow database queries
- Consider upgrading Vercel plan (10s → 60s timeout)
- Or migrate to Railway/Render for no timeout

## View Logs

```bash
# Via CLI
vercel logs

# Or in Vercel Dashboard → Functions → View Logs
```

## Project Structure
```
api/
├── src/
│   ├── api/          # API routes
│   ├── models/       # Database models
│   ├── schemas/      # Pydantic schemas
│   ├── services/     # Business logic
│   ├── middleware/   # CORS, etc.
│   ├── main.py       # FastAPI app
│   ├── database.py   # DB connection
│   ├── config.py     # Settings
│   └── requirements.txt
├── index.py          # Vercel entry point
├── vercel.json       # Vercel configuration
└── .env.example      # Environment template
```

## Vercel Limitations

Be aware of these limits:

1. **Function Size**: 250MB max
2. **Timeout**: 10s (Hobby), 60s (Pro), 900s (Enterprise)
3. **Cold Starts**: 1-3 seconds for first request
4. **No Persistent Storage**: Use external database
5. **Stateless**: Each request is independent

## Alternative Deployment (Railway)

If you hit Vercel limitations, consider Railway:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize
cd api
railway init

# Add environment variables via dashboard

# Deploy
railway up
```

Railway advantages:
- No timeout limits
- Better Python support
- Built-in PostgreSQL
- Persistent connections
- WebSocket support

## Security Checklist

Before going live:

- [ ] Strong `SECRET_KEY` set (32+ characters)
- [ ] `DATABASE_URL` uses SSL (`?sslmode=require`)
- [ ] `ENVIRONMENT=production`
- [ ] CORS configured with specific frontend URL
- [ ] Database credentials not in code
- [ ] `.env` files in `.gitignore`
- [ ] API rate limiting considered
- [ ] HTTPS enforced (automatic on Vercel)

## Useful Commands

```bash
# Check deployment status
vercel ls

# View domain info
vercel domains ls

# View environment variables
vercel env ls

# Pull environment variables locally
vercel env pull
```
