# Backend Deployment Setup - Railway

Complete guide for deploying the Ayni backend to Railway with PostgreSQL and Redis.

## Prerequisites

- Railway account connected to GitHub
- GitHub repository with Ayni code
- Railway CLI installed (optional but recommended)

## Quick Setup (5 minutes)

### 1. Create Railway Project

```bash
# Install Railway CLI (if not installed)
npm i -g @railway/cli

# Login to Railway
railway login

# Create new project and link to repository
cd backend
railway init
railway link
```

Or use Railway Dashboard:
1. Go to https://railway.app/new
2. Select "Deploy from GitHub repo"
3. Select your repository
4. Railway will auto-detect the backend

### 2. Add PostgreSQL Database

**Via Railway Dashboard:**
1. Go to your project
2. Click "+ New"
3. Select "Database" → "PostgreSQL"
4. Railway automatically sets `DATABASE_URL` environment variable

**Via CLI:**
```bash
railway add --database postgres
```

### 3. Add Redis Cache

**Via Railway Dashboard:**
1. Click "+ New"
2. Select "Database" → "Redis"
3. Railway automatically sets `REDIS_URL` environment variable

**Via CLI:**
```bash
railway add --database redis
```

### 4. Configure Environment Variables

**Required Variables:**

Go to Railway Dashboard → Backend Service → Variables:

```bash
# Frontend URL (for CORS)
FRONTEND_HOST=https://your-frontend.onrender.com

# JWT Configuration
JWT_SECRET=generate-a-secure-64-character-random-string-here

# Application
PROJECT_NAME=Ayni
ENVIRONMENT=production
```

**Auto-Configured by Railway:**
- `DATABASE_URL` - PostgreSQL connection string
- `POSTGRES_USER` - Database username
- `POSTGRES_PASSWORD` - Database password
- `POSTGRES_DB` - Database name
- `REDIS_URL` - Redis connection string

**Optional (for Google OAuth):**
```bash
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-your-secret-here
GOOGLE_OAUTH_REDIRECT_URI=https://your-backend.up.railway.app/api/v1/auth/google/callback
```

**Optional (for monitoring):**
```bash
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

### 5. Deploy

**Auto-deploy (recommended):**
- Railway automatically deploys when you push to `main` branch
- Enable in: Settings → Deploy → Auto Deploy

**Manual deploy:**
```bash
railway up
```

### 6. Get Your Backend URL

```bash
# Via CLI
railway status

# Or check Railway Dashboard → Service → Settings → Domains
```

Your backend URL will be: `https://your-service.up.railway.app`

---

## Detailed Configuration

### Database Migration

Railway runs migrations automatically on deploy if you have a start command configured.

**In `railway.json` or via Railway Dashboard:**
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

**Or manually trigger migrations:**
```bash
railway run alembic upgrade head
```

### Dependencies Management

Railway uses `requirements.txt` for Python dependencies.

**IMPORTANT:** Always regenerate `requirements.txt` after updating `pyproject.toml`:

```bash
cd backend
uv pip compile pyproject.toml -o requirements.txt
git add requirements.txt
git commit -m "chore: update requirements.txt"
git push
```

Railway will detect the change and redeploy automatically.

### Health Check Endpoint

Railway checks `/health` endpoint to verify service is running.

**Endpoint:** `https://your-backend.up.railway.app/health`

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-14T20:00:00+00:00",
  "services": {
    "database": {"status": "healthy", "latency_ms": 10.5},
    "redis": {"status": "healthy", "latency_ms": 5.2}
  }
}
```

---

## Google OAuth Setup (Optional)

### 1. Google Cloud Console Configuration

1. **Create Google Cloud Project**
   - Go to https://console.cloud.google.com
   - Create project: "Ayni"
   - Enable Google+ API or People API

2. **Configure OAuth Consent Screen**
   - Type: External
   - App name: Ayni
   - User support email: your-email@gmail.com
   - Scopes: email, profile, openid

3. **Create OAuth 2.0 Client ID**
   - Type: Web application
   - Name: Ayni Production
   - Authorized redirect URI:
     ```
     https://your-backend.up.railway.app/api/v1/auth/google/callback
     ```
   - **Save the Client ID and Client Secret**

### 2. Add OAuth Variables to Railway

```bash
GOOGLE_OAUTH_CLIENT_ID=xxxxx.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-xxxxx
GOOGLE_OAUTH_REDIRECT_URI=https://your-backend.up.railway.app/api/v1/auth/google/callback
```

### 3. Test OAuth Endpoint

```bash
curl https://your-backend.up.railway.app/api/v1/auth/google/authorize

# Should return JSON with "authorization_url"
# If 503: OAuth not configured
```

---

## CORS Configuration

The backend must allow requests from your frontend domain.

**Required Variable:**
```bash
FRONTEND_HOST=https://your-frontend.onrender.com
```

**Verification:**
```bash
curl -X OPTIONS https://your-backend.up.railway.app/api/v1/health \
  -H "Origin: https://your-frontend.onrender.com" \
  -H "Access-Control-Request-Method: GET" \
  -i

# Should return:
# access-control-allow-origin: https://your-frontend.onrender.com
```

---

## Monitoring & Logs

### View Logs

**Via CLI:**
```bash
railway logs --limit 50
railway logs --tail  # Follow logs in real-time
```

**Via Dashboard:**
1. Go to Railway Dashboard
2. Select backend service
3. Click "Deployments" → Select deployment → "View Logs"

### Check Deployment Status

```bash
railway status

# Shows:
# - Service name
# - Status (Active/Deploying/Failed)
# - URL
# - Recent deployments
```

### Health Monitoring

Set up automated health checks:
```bash
# Add to your monitoring tool (UptimeRobot, etc.)
https://your-backend.up.railway.app/health
```

---

## Environment Variables Reference

### Required

| Variable | Example | Description |
|----------|---------|-------------|
| `FRONTEND_HOST` | `https://ayni-frontend.onrender.com` | Frontend URL for CORS |
| `JWT_SECRET` | `64-char-random-string` | Secret for JWT tokens |
| `PROJECT_NAME` | `Ayni` | Application name |
| `ENVIRONMENT` | `production` | Deployment environment |

### Auto-Configured by Railway

| Variable | Source | Description |
|----------|--------|-------------|
| `DATABASE_URL` | PostgreSQL service | Database connection string |
| `POSTGRES_USER` | PostgreSQL service | Database username |
| `POSTGRES_PASSWORD` | PostgreSQL service | Database password |
| `POSTGRES_DB` | PostgreSQL service | Database name |
| `REDIS_URL` | Redis service | Redis connection string |

### Optional

| Variable | Example | Description |
|----------|---------|-------------|
| `GOOGLE_OAUTH_CLIENT_ID` | `xxx.apps.googleusercontent.com` | Google OAuth client ID |
| `GOOGLE_OAUTH_CLIENT_SECRET` | `GOCSPX-xxx` | Google OAuth secret |
| `GOOGLE_OAUTH_REDIRECT_URI` | `https://xxx.railway.app/api/v1/auth/google/callback` | OAuth callback URL |
| `SENTRY_DSN` | `https://xxx@sentry.io/xxx` | Sentry error tracking |

---

## Verification Checklist

After deployment, verify:

- [ ] Backend URL is accessible
- [ ] Health check returns 200 OK
- [ ] Database connection works (check health endpoint)
- [ ] Redis connection works (check health endpoint)
- [ ] CORS headers present for frontend origin
- [ ] Environment variables set correctly
- [ ] Logs show no errors
- [ ] OAuth endpoint responds (if configured)

**Test Commands:**
```bash
# Health check
curl https://your-backend.up.railway.app/health

# CORS check
curl -X OPTIONS https://your-backend.up.railway.app/api/v1/health \
  -H "Origin: https://your-frontend.onrender.com" \
  -H "Access-Control-Request-Method: GET" \
  -i

# OAuth check (if configured)
curl https://your-backend.up.railway.app/api/v1/auth/google/authorize
```

---

## Production URLs

After setup, save these URLs:

**Backend API:** `https://_________________.up.railway.app/api/v1`
**Health Endpoint:** `https://_________________.up.railway.app/health`
**OAuth Callback:** `https://_________________.up.railway.app/api/v1/auth/google/callback`

---

## Next Steps

1. ✅ Backend deployed and healthy
2. → Set up frontend deployment (see [SETUP-FRONTEND.md](./SETUP-FRONTEND.md))
3. → Configure OAuth (see Google OAuth Setup section above)
4. → Set up monitoring (Sentry, UptimeRobot)

---

## Common Commands

```bash
# Deploy manually
railway up

# View logs
railway logs --tail

# Check status
railway status

# Run migrations
railway run alembic upgrade head

# Connect to database
railway connect postgres

# List environment variables
railway variables

# Set environment variable
railway variables --set KEY=value

# Restart service
railway restart
```

---

## Support

For issues, see [TROUBLESHOOTING-BACKEND.md](./TROUBLESHOOTING-BACKEND.md)
