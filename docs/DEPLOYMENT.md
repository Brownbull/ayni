# Deployment Guide

This document provides comprehensive deployment procedures, rollback mechanisms, and troubleshooting guides for the Ayni application.

## Table of Contents

- [Overview](#overview)
- [Production Architecture](#production-architecture)
- [Environment Variables](#environment-variables)
- [Deployment Procedures](#deployment-procedures)
- [Rollback Procedures](#rollback-procedures)
- [Health Checks](#health-checks)
- [Troubleshooting](#troubleshooting)

## Overview

Ayni uses a multi-service architecture deployed across two platforms:

- **Backend (Railway)**: FastAPI application, Celery worker, PostgreSQL, and Redis
- **Frontend (Render)**: Static site with CDN

All deployments are automated through GitHub Actions CI/CD pipeline.

## Production Architecture

### Railway Services

The Railway project contains 4 services:

1. **Backend API**
   - FastAPI + Uvicorn server
   - Auto-deploys from `main` branch
   - Start command: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Health check: `/health` endpoint

2. **Celery Worker**
   - Same codebase as backend, different start command
   - Start command: `celery -A app.workers.celery_app worker --loglevel=info`
   - Connects to same PostgreSQL and Redis as backend

3. **PostgreSQL**
   - Managed service (PostgreSQL 17)
   - Automatically provides `DATABASE_URL` to other services

4. **Redis**
   - Managed service (Redis 7)
   - Automatically provides `REDIS_URL` to other services

### Render Service

1. **Frontend Static Site**
   - Vite-built React application
   - Auto-deploys from `main` branch
   - Served via CDN with security headers
   - SPA routing configured (all routes → `/index.html`)

## Environment Variables

### Backend (Railway)

Set these in the Railway dashboard for each service:

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Auto-provided by Railway PostgreSQL | `postgresql://user:pass@host:5432/db` |
| `REDIS_URL` | Auto-provided by Railway Redis | `redis://host:6379/0` |
| `JWT_SECRET` | 64+ character random string for JWT signing | Generate with `openssl rand -hex 32` |
| `FRONTEND_HOST` | Render frontend URL for CORS | `https://ayni.onrender.com` |
| `ENVIRONMENT` | Deployment environment | `production` |
| `PROJECT_NAME` | Application name | `Ayni` |
| `POSTGRES_SERVER` | PostgreSQL server (auto-set) | Auto-provided |
| `POSTGRES_PORT` | PostgreSQL port (auto-set) | `5432` |
| `POSTGRES_USER` | PostgreSQL user (auto-set) | Auto-provided |
| `POSTGRES_PASSWORD` | PostgreSQL password (auto-set) | Auto-provided |
| `POSTGRES_DB` | PostgreSQL database (auto-set) | Auto-provided |

### Frontend (Render)

Set these in the Render dashboard:

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Railway backend API URL | `https://ayni-backend.railway.app/api/v1` |

### GitHub Actions Secrets

Set these in GitHub repository settings → Secrets and variables → Actions:

| Secret | Description | Required |
|--------|-------------|----------|
| `CODECOV_TOKEN` | Codecov API token for coverage reports | Optional |

## Deployment Procedures

### Automated Deployment (Recommended)

1. **Merge to Main Branch**
   ```bash
   git checkout main
   git pull origin main
   git merge feature/your-branch
   git push origin main
   ```

2. **GitHub Actions Runs**
   - Backend CI: Linting, type-checking, tests (coverage >70%)
   - Frontend CI: Linting, type-checking, tests (coverage >70%)

3. **Automatic Deployment**
   - If CI passes, Railway auto-deploys backend + Celery worker
   - Render auto-deploys frontend
   - Health checks verify services are operational

4. **Monitor Deployment**
   - Railway Dashboard: https://railway.app/project/{project-id}
   - Render Dashboard: https://dashboard.render.com/
   - Check logs for any errors during startup

### Manual Deployment

#### Railway (Backend)

If you need to trigger a manual deployment:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# Deploy backend
railway up

# Deploy to specific service
railway up --service backend-api
railway up --service celery-worker
```

#### Render (Frontend)

Manual deployment is not typically needed (auto-deploys on push to main), but you can:

1. Go to Render Dashboard
2. Select the `ayni-frontend` service
3. Click "Manual Deploy" → "Deploy latest commit"

## Rollback Procedures

### Railway Backend Rollback

Railway maintains a history of deployments. To rollback:

**Method 1: Railway CLI (Recommended)**

```bash
# List recent deployments
railway deployments

# Rollback to previous deployment
railway rollback

# Rollback to specific deployment ID
railway rollback <deployment-id>
```

**Method 2: Railway Dashboard**

1. Open Railway dashboard
2. Select the service (backend-api or celery-worker)
3. Go to "Deployments" tab
4. Find the last known-good deployment
5. Click "Redeploy"

**Important Notes:**
- Rollback does NOT affect database state
- Database migrations are NOT automatically reverted
- If migration caused the issue, see "Database Migration Rollback" below

### Render Frontend Rollback

**Method 1: Render Dashboard (Recommended)**

1. Open Render dashboard
2. Select `ayni-frontend` service
3. Go to "Deploys" tab
4. Find the last known-good deployment
5. Click "Redeploy"

**Method 2: Git Revert**

```bash
# Find the commit to revert to
git log --oneline

# Redeploy previous commit
git revert <bad-commit-hash>
git push origin main
```

Render will automatically deploy the reverted code.

### Database Migration Rollback

**WARNING:** Database rollbacks are DANGEROUS and can cause data loss. Test in staging first!

**Step 1: Identify Migration to Rollback**

```bash
# View migration history
railway run alembic history

# View current migration
railway run alembic current
```

**Step 2: Rollback Migration**

```bash
# Rollback one migration
railway run alembic downgrade -1

# Rollback to specific migration
railway run alembic downgrade <revision-id>

# Rollback all migrations (DANGEROUS!)
railway run alembic downgrade base
```

**Step 3: Verify Database State**

```bash
# Check current migration
railway run alembic current

# Connect to database and verify schema
railway run psql $DATABASE_URL
```

**Step 4: Update Application Code**

If you rolled back a migration, you must also rollback the application code to match:

```bash
git revert <migration-commit-hash>
git push origin main
```

### Emergency Rollback (DNS Failover)

If both application and database rollbacks fail, you can temporarily point traffic to a previous deployment:

1. **Keep old deployment alive** in Railway dashboard (don't delete)
2. **Update DNS** to point to old deployment URL
3. **Fix issues** in new deployment
4. **Switch DNS back** once fixed

This approach maintains database state but routes traffic to old code.

## Health Checks

### Backend Health Endpoints

1. **Basic Health Check**: `/health`
   - No external dependencies
   - Always returns `{"status": "healthy"}` if app is running
   - Used by Railway load balancers

2. **Detailed Health Check**: `/api/v1/health`
   - Checks database connectivity
   - Checks Redis connectivity
   - Returns HTTP 200 for healthy, 503 for unhealthy/degraded
   - Response includes detailed status per service

**Example Healthy Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-13T10:00:00Z",
  "services": {
    "database": "healthy",
    "redis": "healthy"
  }
}
```

**Example Unhealthy Response (HTTP 503):**
```json
{
  "status": "unhealthy",
  "timestamp": "2025-11-13T10:00:00Z",
  "services": {
    "database": "healthy",
    "redis": "unhealthy"
  }
}
```

### Testing Health Checks

```bash
# Test basic health check
curl https://ayni-backend.railway.app/health

# Test detailed health check
curl https://ayni-backend.railway.app/api/v1/health

# Test frontend
curl https://ayni.onrender.com/
```

## Troubleshooting

### Common Deployment Failures

#### 1. Backend Deployment Fails: "Port binding error"

**Symptom:** Railway shows "Error: bind: address already in use"

**Cause:** FastAPI not binding to Railway's `$PORT` variable

**Fix:**
```python
# Ensure start command uses $PORT
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

#### 2. Database Migration Fails During Deployment

**Symptom:** Railway logs show "alembic.util.exc.CommandError"

**Cause:** Migration script has errors or conflicts

**Fix:**
```bash
# Test migration locally first
cd backend
alembic upgrade head

# If migration fails, fix it and redeploy
alembic downgrade -1
# Fix migration file
alembic upgrade head
git add .
git commit -m "fix: correct database migration"
git push origin main
```

#### 3. Frontend Deployment Fails: "Build command failed"

**Symptom:** Render build logs show "npm run build" errors

**Cause:** TypeScript errors or missing dependencies

**Fix:**
```bash
# Test build locally
cd frontend
npm install
npm run type-check
npm run build

# Fix TypeScript errors
# Commit and push fixes
git push origin main
```

#### 4. CORS Errors in Production

**Symptom:** Browser console shows "CORS policy blocked"

**Cause:** Frontend URL not in backend CORS allowed origins

**Fix:**
```bash
# Ensure FRONTEND_HOST environment variable is set in Railway
# Value should be: https://ayni.onrender.com (your Render URL)

# Verify in backend/app/core/config.py:
# - FRONTEND_HOST is loaded from environment
# - all_cors_origins includes FRONTEND_HOST
```

#### 5. Celery Worker Not Processing Tasks

**Symptom:** Tasks stay in "pending" state forever

**Cause:** Celery worker not connected to Redis broker

**Fix:**
```bash
# Check Railway logs for celery-worker service
railway logs --service celery-worker

# Ensure REDIS_URL is set correctly
# Restart celery-worker service in Railway dashboard
```

#### 6. CI Tests Pass Locally But Fail in GitHub Actions

**Symptom:** Pytest failures in CI but not locally

**Cause:** Environment differences (PostgreSQL version, Redis, dependencies)

**Fix:**
```bash
# Match CI environment locally using Docker
docker compose up postgres redis

# Run tests against Docker services
cd backend
DATABASE_URL=postgresql://ayni_user:changethis@localhost:5432/ayni_dev \
REDIS_URL=redis://localhost:6379/0 \
uv run pytest

# If still different, check GitHub Actions logs for exact error
```

#### 7. Coverage Below 70% in CI

**Symptom:** CI fails with "Coverage (XX%) is below 70%"

**Cause:** New code not tested or tests not running

**Fix:**
```bash
# Run coverage locally
cd backend
uv run pytest --cov=app --cov-report=term

# Identify untested files
# Add tests for new code
# Ensure all tests pass
uv run pytest
```

### Getting Help

If you encounter an issue not covered here:

1. **Check Logs:**
   - Railway: `railway logs`
   - Render: Dashboard → Logs tab
   - GitHub Actions: Actions tab → Failed workflow

2. **Verify Environment Variables:**
   - Railway Dashboard → Service → Variables tab
   - Render Dashboard → Service → Environment tab

3. **Test Locally:**
   - Run `docker compose up` to match production environment
   - Test deployment commands locally

4. **Contact Platform Support:**
   - Railway: https://railway.app/help
   - Render: https://render.com/docs/support
