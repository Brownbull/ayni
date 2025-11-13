# Ayni - Production Setup Guide

Complete guide to setting up Ayni from scratch on Railway (backend) and Render (frontend), including all services, monitoring, and troubleshooting.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Railway Setup (Backend Infrastructure)](#railway-setup-backend-infrastructure)
3. [Render Setup (Frontend)](#render-setup-frontend)
4. [Sentry Setup (Monitoring)](#sentry-setup-monitoring)
5. [Verification & Testing](#verification--testing)
6. [Post-Setup Configuration](#post-setup-configuration)

---

## Prerequisites

Before starting, ensure you have:

- [x] **GitHub Account** with repository: `Brownbull/ayni`
- [x] **Railway Account** (https://railway.app) - Sign up with GitHub
- [x] **Render Account** (https://dashboard.render.com) - Sign up with GitHub
- [x] **Sentry Account** (https://sentry.io) - Sign up (free tier available)
- [x] **Railway CLI** installed: `npm install -g @railway/cli`
- [x] **Project cloned locally** for CLI operations

---

## Railway Setup (Backend Infrastructure)

Railway hosts the backend API, Celery workers, PostgreSQL database, Redis cache, and Flower monitoring UI.

### Step 1: Create Railway Project

1. **Go to Railway Dashboard:** https://railway.app/dashboard
2. **Click "New Project"**
3. **Select "Deploy from GitHub repo"**
4. **Choose repository:** `Brownbull/ayni`
5. **Project Name:** `resilient-flow` (or your preferred name)
6. **Environment:** `production`

### Step 2: Add PostgreSQL Database

1. **In Railway project, click "+ New"**
2. **Select "Database" → "Add PostgreSQL"**
3. **Service Name:** `Postgres` (default)
4. **Wait for provisioning** (~30 seconds)

**PostgreSQL is now available with auto-generated credentials accessible via variables:**
- `${{Postgres.PGHOST}}`
- `${{Postgres.PGPORT}}`
- `${{Postgres.PGUSER}}`
- `${{Postgres.PGPASSWORD}}`
- `${{Postgres.PGDATABASE}}`

### Step 3: Add Redis Cache

1. **Click "+ New"**
2. **Select "Database" → "Add Redis"**
3. **Service Name:** `Redis` (default)
4. **Wait for provisioning** (~20 seconds)

**Redis is now available with:**
- `${{Redis.REDIS_URL}}`

### Step 4: Deploy Backend API Service

1. **Click "+ New" → "GitHub Repo"**
2. **Select:** `Brownbull/ayni` repository
3. **Service Name:** `ayni-backend`
4. **Root Directory:** Leave blank (project root)
5. **Start Command:** Auto-detected (FastAPI with Uvicorn)

**Configure Environment Variables (click Variables tab):**

| Variable | Value | Source |
|----------|-------|--------|
| `PROJECT_NAME` | `Ayni` | Raw |
| `ENVIRONMENT` | `production` | Raw |
| `POSTGRES_SERVER` | `${{Postgres.PGHOST}}` | Reference |
| `POSTGRES_PORT` | `${{Postgres.PGPORT}}` | Reference |
| `POSTGRES_USER` | `${{Postgres.PGUSER}}` | Reference |
| `POSTGRES_PASSWORD` | `${{Postgres.PGPASSWORD}}` | Reference |
| `POSTGRES_DB` | `${{Postgres.PGDATABASE}}` | Reference |
| `REDIS_URL` | `${{Redis.REDIS_URL}}` | Reference |
| `JWT_SECRET` | Generate with: `python -c "import secrets; print(secrets.token_urlsafe(64))"` | Raw |
| `JWT_ALGORITHM` | `HS256` | Raw |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `11520` | Raw |
| `SECRET_KEY` | Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"` | Raw |
| `FRONTEND_HOST` | `https://ayni-frontend.onrender.com` (update after Render setup) | Raw |
| `BACKEND_CORS_ORIGINS` | `["https://ayni-frontend.onrender.com"]` | Raw |
| `FIRST_SUPERUSER` | `admin@ayni.com` | Raw |
| `FIRST_SUPERUSER_PASSWORD` | (Your secure password) | Raw |
| `SENTRY_DSN` | (Get from Sentry setup below) | Raw |
| `SENTRY_ENVIRONMENT` | `production` | Raw |
| `SENTRY_TRACES_SAMPLE_RATE` | `0.1` | Raw |

**Generate Domain:**
1. Go to **Settings → Networking**
2. Click **"Generate Domain"**
3. Save the URL (e.g., `ayni-backend-production.up.railway.app`)

### Step 5: Deploy Celery Worker Service

1. **Click "+ New" → "GitHub Repo"**
2. **Select:** `Brownbull/ayni` repository
3. **Service Name:** `ayni-celery-worker`
4. **Root Directory:** `backend`
5. **Start Command:**
   ```bash
   celery -A app.workers.celery_app worker --loglevel=info --concurrency=4
   ```

**Configure Environment Variables** (copy from ayni-backend):
- All variables from `ayni-backend` service using variable references:
  - `${{ayni-backend.PROJECT_NAME}}`
  - `${{ayni-backend.ENVIRONMENT}}`
  - etc.

### Step 6: Deploy Flower Monitoring UI (Optional)

1. **Click "+ New" → "GitHub Repo"**
2. **Select:** `Brownbull/ayni` repository
3. **Service Name:** `ayni-flower`
4. **Root Directory:** `backend`
5. **Custom Build Command:**
   ```bash
   pip install uv && uv sync
   ```
6. **Start Command:**
   ```bash
   uv run celery -A app.workers.celery_app flower --port=5555 --basic-auth=$FLOWER_BASIC_AUTH
   ```

**Configure Environment Variables:**

| Variable | Value | Source |
|----------|-------|--------|
| `REDIS_URL` | `${{Redis.REDIS_URL}}` | Reference |
| `FLOWER_BASIC_AUTH` | `admin:your-secure-password` | Raw |
| `JWT_SECRET` | `${{ayni-backend.JWT_SECRET}}` | Reference |
| `PROJECT_NAME` | `Ayni` | Raw |
| `FIRST_SUPERUSER` | `${{ayni-backend.FIRST_SUPERUSER}}` | Reference |
| `FIRST_SUPERUSER_PASSWORD` | `${{ayni-backend.FIRST_SUPERUSER_PASSWORD}}` | Reference |
| `POSTGRES_SERVER` | `${{Postgres.PGHOST}}` | Reference |
| `POSTGRES_USER` | `${{Postgres.PGUSER}}` | Reference |
| `POSTGRES_PASSWORD` | `${{Postgres.PGPASSWORD}}` | Reference |
| `POSTGRES_DB` | `${{Postgres.PGDATABASE}}` | Reference |

**Generate Domain:**
1. Go to **Settings → Networking**
2. Click **"Generate Domain"**
3. **Port:** `5555`
4. Save URL (e.g., `ayni-flower-production.up.railway.app`)

### Railway Services Summary

After setup, you should have **5 services** running:

| Service | Type | Status |
|---------|------|--------|
| **Postgres** | Database | ✅ Running |
| **Redis** | Cache/Broker | ✅ Running |
| **ayni-backend** | API Server | ✅ Deployed |
| **ayni-celery-worker** | Background Tasks | ✅ Running |
| **ayni-flower** | Monitoring UI (optional) | ✅ Deployed |

---

## Render Setup (Frontend)

Render hosts the React frontend as a static site.

### Step 1: Create Render Service

1. **Go to Render Dashboard:** https://dashboard.render.com
2. **Click "New" → "Static Site"**
3. **Connect to GitHub** and select: `Brownbull/ayni`
4. **Service Name:** `ayni-frontend`
5. **Branch:** `main`
6. **Root Directory:** `frontend`
7. **Build Command:** `npm install && npm run build`
8. **Publish Directory:** `dist`

### Step 2: Configure Environment Variables

Go to **Environment** tab and add:

| Variable | Value |
|----------|-------|
| `VITE_API_URL` | `https://ayni-backend-production.up.railway.app/api/v1` (from Railway) |
| `VITE_ENVIRONMENT` | `production` |
| `VITE_SENTRY_DSN` | (Get from Sentry setup below) |

### Step 3: Deploy

1. Click **"Create Static Site"**
2. Wait for build (~3-5 minutes)
3. Save the URL (e.g., `ayni-frontend.onrender.com`)

### Step 4: Update Backend CORS

**Go back to Railway** → `ayni-backend` → Variables:
1. Update `FRONTEND_HOST` to: `https://ayni-frontend.onrender.com`
2. Update `BACKEND_CORS_ORIGINS` to: `["https://ayni-frontend.onrender.com"]`
3. Service will auto-redeploy

---

## Sentry Setup (Monitoring)

Sentry provides error tracking and performance monitoring for both frontend and backend.

### Step 1: Create Sentry Account

1. **Go to:** https://sentry.io
2. **Sign up** (free tier includes 5K errors/month)
3. **Create Organization** (or use existing)

### Step 2: Create Backend Project

1. **Click "Create Project"**
2. **Platform:** Python → FastAPI
3. **Project Name:** `ayni-backend`
4. **Alert Frequency:** Default
5. **Copy the DSN** (looks like: `https://xxx@yyy.ingest.sentry.io/zzz`)

### Step 3: Create Frontend Project

1. **Click "Create Project"**
2. **Platform:** JavaScript → React
3. **Project Name:** `ayni-frontend`
4. **Copy the DSN**

### Step 4: Configure Alert Rules

#### Backend Alerts

1. **Go to:** Sentry → `ayni-backend` → Alerts → Create Alert
2. **Name:** "New Issues (Critical Errors)"
3. **Conditions:**
   - ✅ A new issue is created
   - ✅ Sentry marks a new issue as high priority
   - ✅ The issue changes state from resolved to unresolved
4. **Filters:**
   - IF: The issue's category is equal to `error`
5. **Actions:**
   - Send notification to: (Your email)
6. **Action Interval:** 24 hours
7. **Save Rule**

#### Frontend Alerts

Repeat the same process for `ayni-frontend` project.

### Step 5: Add DSNs to Services

**Railway (ayni-backend):**
- Variable: `SENTRY_DSN` = (Backend DSN from step 2)

**Render (ayni-frontend):**
- Variable: `VITE_SENTRY_DSN` = (Frontend DSN from step 3)

Both services will auto-redeploy with monitoring enabled.

---

## Verification & Testing

### Test Backend API

```bash
# Health check
curl https://ayni-backend-production.up.railway.app/api/v1/utils/health-check/

# Monitoring metrics
curl https://ayni-backend-production.up.railway.app/api/v1/monitoring/metrics

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "...",
#   "uptime_seconds": ...,
#   "services": {
#     "database": {"status": "healthy", "latency_ms": ...},
#     "redis": {"status": "healthy", "latency_ms": ...}
#   },
#   "celery_metrics": {
#     "active_tasks": 0,
#     "scheduled_tasks": 0,
#     "pending_tasks": 0,
#     "active_workers": 1,
#     "completed_24h": 0,
#     "failed_24h": 0
#   }
# }
```

### Test Celery Worker

```bash
# Check Celery tasks endpoint
curl https://ayni-backend-production.up.railway.app/api/v1/monitoring/celery/tasks

# Expected: Shows active workers and task stats
```

### Test Flower UI (if deployed)

1. Visit: `https://ayni-flower-production.up.railway.app`
2. Login with credentials from `FLOWER_BASIC_AUTH`
3. Verify worker appears in dashboard
4. Check task history

### Test Sentry Integration

```bash
# Trigger test error
curl https://ayni-backend-production.up.railway.app/api/v1/monitoring/test-error

# Expected: 500 error response
# Check Sentry dashboard - error should appear within 1-2 minutes
```

**Verify in Sentry:**
1. Go to Sentry → `ayni-backend` → Issues
2. Look for error: "This is a test error to verify Sentry integration..."
3. Click issue to see stack trace, environment, etc.
4. Check your email for alert notification

### Test Frontend

1. Visit: `https://ayni-frontend.onrender.com`
2. Frontend should load
3. Check browser console - no CORS errors
4. Verify API calls work

---

## Post-Setup Configuration

### Security Checklist

- [ ] All secrets are stored in Railway/Render (never in Git)
- [ ] `JWT_SECRET` is 64+ characters
- [ ] `FIRST_SUPERUSER_PASSWORD` is strong
- [ ] CORS configured correctly
- [ ] HTTPS enforced (automatic on Railway/Render)
- [ ] Sentry error tracking enabled
- [ ] Sentry alerts configured

### Performance Optimization

- [ ] Database indexes created (via Alembic migrations)
- [ ] Redis caching enabled (automatic)
- [ ] Celery worker concurrency set appropriately
- [ ] Railway metrics monitored

### Monitoring Setup

- [ ] Sentry alerts configured
- [ ] Flower UI accessible (optional)
- [ ] Railway logs accessible via CLI
- [ ] Health endpoints returning 200 OK

### Documentation

- [ ] Save all Railway service URLs
- [ ] Save Render frontend URL
- [ ] Save Sentry project URLs
- [ ] Document FLOWER_BASIC_AUTH credentials
- [ ] Update team documentation

---

## Quick Reference: Where to Get Values

### From Railway

**PostgreSQL:**
- `POSTGRES_SERVER`: Railway → Postgres service → Variables → `PGHOST`
- `POSTGRES_PORT`: `PGPORT`
- `POSTGRES_USER`: `PGUSER`
- `POSTGRES_PASSWORD`: `PGPASSWORD`
- `POSTGRES_DB`: `PGDATABASE`

**Redis:**
- `REDIS_URL`: Railway → Redis service → Variables → `REDIS_URL`

**Backend URL:**
- Railway → ayni-backend → Settings → Networking → Generated Domain

### From Render

**Frontend URL:**
- Render → ayni-frontend → Settings → (Domain shown at top)

### From Sentry

**Backend DSN:**
- Sentry → ayni-backend → Settings → Client Keys (DSN)

**Frontend DSN:**
- Sentry → ayni-frontend → Settings → Client Keys (DSN)

### Generated Secrets

**JWT_SECRET (64+ characters):**
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

**SECRET_KEY (32+ characters):**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**FLOWER_BASIC_AUTH:**
Format: `username:password` (e.g., `admin:your-secure-password-123`)

---

## Troubleshooting Setup Issues

### Railway Services Not Starting

**Symptoms:** Service shows "Crashed" or "Failed"

**Resolution:**
1. Check build logs in Railway dashboard
2. Verify all environment variables are set
3. Check for missing variable references (e.g., `${{Postgres.PGHOST}}`)
4. Review deployment logs for errors

### Database Connection Errors

**Symptoms:** Backend shows "Database unhealthy"

**Resolution:**
1. Verify PostgreSQL service is running in Railway
2. Check `POSTGRES_*` variables are correctly set
3. Ensure variable references are correct: `${{Postgres.PGHOST}}`
4. Test connection: `railway run --service ayni-backend psql $DATABASE_URL`

### Redis Connection Errors

**Symptoms:** Backend shows "Redis unhealthy"

**Resolution:**
1. Verify Redis service is running
2. Check `REDIS_URL` variable is set
3. Ensure format: `redis://default:password@host:port`

### CORS Errors

**Symptoms:** Frontend can't connect to backend

**Resolution:**
1. Verify `FRONTEND_HOST` matches exact Render URL
2. Update `BACKEND_CORS_ORIGINS` to include frontend URL
3. Ensure both variables include `https://` protocol
4. Redeploy backend after updating

### Flower Won't Start

**Symptoms:** 502 error or "No such command 'flower'"

**Resolution:**
1. Verify Root Directory is set to `backend`
2. Check custom build command installs uv: `pip install uv && uv sync`
3. Verify start command uses `uv run`
4. Ensure all required environment variables are set (JWT_SECRET, PROJECT_NAME, etc.)

### Sentry Not Receiving Errors

**Resolution:**
1. Verify `SENTRY_DSN` is set correctly (backend and/or frontend)
2. Check `SENTRY_ENVIRONMENT` is set to `production`
3. Trigger test error: `curl https://...api.../monitoring/test-error`
4. Check Sentry dashboard (errors may take 1-2 minutes to appear)
5. Verify alerts are configured in Sentry dashboard

---

## Complete Setup Checklist

### Railway Setup
- [ ] Project created: `resilient-flow`
- [ ] PostgreSQL database added and running
- [ ] Redis cache added and running
- [ ] Backend API service deployed with all variables
- [ ] Backend domain generated and saved
- [ ] Celery worker service deployed
- [ ] Flower UI service deployed (optional)
- [ ] Flower domain generated and saved (optional)
- [ ] All services showing "Active" status

### Render Setup
- [ ] Static site created: `ayni-frontend`
- [ ] Build settings configured correctly
- [ ] Environment variables set (`VITE_API_URL`, `VITE_SENTRY_DSN`)
- [ ] Deployment successful
- [ ] Frontend URL saved

### Sentry Setup
- [ ] Backend project created
- [ ] Backend DSN added to Railway
- [ ] Frontend project created
- [ ] Frontend DSN added to Render
- [ ] Alert rules configured for both projects
- [ ] Test error verified in Sentry dashboard

### Cross-Service Configuration
- [ ] Backend `FRONTEND_HOST` updated with Render URL
- [ ] Backend `BACKEND_CORS_ORIGINS` includes Render URL
- [ ] Frontend `VITE_API_URL` points to Railway backend
- [ ] Services redeployed after cross-references

### Verification
- [ ] Backend health check returns 200 OK
- [ ] Monitoring metrics endpoint working
- [ ] Celery tasks endpoint showing workers
- [ ] Flower UI accessible (if deployed)
- [ ] Sentry receiving test errors
- [ ] Frontend loads without CORS errors
- [ ] All Railway services showing green status

---

## Next Steps After Setup

1. **Remove test error endpoint** (production security):
   - Remove `/api/v1/monitoring/test-error` from code
   - Commit and push to trigger deployment

2. **Configure database backups**:
   - Railway automatically backs up PostgreSQL
   - Verify in Railway → Postgres → Backups

3. **Set up CI/CD** (if not already configured):
   - GitHub Actions will auto-deploy on push to `main`
   - Tests must pass before deployment

4. **Monitor production**:
   - Check Sentry dashboard regularly
   - Review Railway metrics
   - Monitor Flower for task health

5. **Document credentials**:
   - Save all URLs and credentials securely
   - Share with team members as needed

---

**Setup Complete!** 🎉

All services should now be running in production. Refer to [run_app.remote.md](run_app.remote.md) for ongoing production operations and monitoring.

**Last Updated**: 2025-11-13
