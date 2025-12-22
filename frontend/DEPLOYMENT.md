# Frontend Deployment Guide (Vercel)

## Prerequisites
- Vercel account
- Backend API deployed and URL available

## Deployment Steps

### 1. Deploy to Vercel

#### Option A: Via Vercel CLI
```bash
# Install Vercel CLI globally
npm install -g vercel

# Navigate to frontend directory
cd frontend

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
3. Set Root Directory to `frontend`
4. Click Deploy

### 2. Configure Environment Variables

In Vercel Dashboard → Your Project → Settings → Environment Variables:

Add the following:

| Name | Value | Environment |
|------|-------|-------------|
| `NEXT_PUBLIC_API_URL` | `https://your-backend.vercel.app` | Production, Preview, Development |

**Important**: Replace `https://your-backend.vercel.app` with your actual backend URL.

### 3. Redeploy

After setting environment variables:
- Go to Deployments tab
- Click on the latest deployment
- Click "Redeploy"

## Verify Deployment

1. Visit your frontend URL: `https://your-frontend.vercel.app`
2. Open browser console
3. Try to sign up/sign in
4. Check that API requests go to your backend URL
5. Verify no CORS errors

## Local Development

```bash
# Create .env.local file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Install dependencies
npm install

# Run development server
npm run dev
```

Visit: http://localhost:3000

## Troubleshooting

### CORS Errors
- Ensure `FRONTEND_URL` in backend matches your frontend URL
- Check backend CORS middleware configuration

### API Not Found (404)
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check backend is deployed and accessible

### Build Failures
- Check Node.js version (should be 18+)
- Verify all dependencies in package.json
- Review build logs in Vercel dashboard

## Project Structure
```
frontend/
├── src/
│   ├── app/          # Next.js app directory
│   ├── components/   # React components
│   └── lib/          # Utilities and API client
├── public/           # Static assets
├── package.json
├── next.config.ts    # Next.js configuration
├── vercel.json       # Vercel configuration
└── .env.example      # Environment variable template
```

## Useful Commands

```bash
# Build locally to test
npm run build

# Start production build locally
npm start

# Lint code
npm run lint

# View Vercel logs
vercel logs
```
