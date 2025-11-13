# Ayni - Production Deployment Guide

This guide covers the production deployment on Railway (backend) and Render (frontend), including monitoring, troubleshooting, and rollback procedures.

---

## Production Services Overview

| Service | Platform | URL | Status |
|---------|----------|-----|--------|
| **Frontend** | Render | https://ayni-frontend.onrender.com |  Live |
| **Backend API** | Railway | https://ayni-backend-production.up.railway.app |  Live |
| **Celery Worker** | Railway | (Background service) |  Running |
| **Flower UI** | Railway | https://ayni-flower-production.up.railway.app |  Live |
| **Sentry** | Sentry.io | https://sentry.io/organizations/ayni |  Monitoring |
| **PostgreSQL** | Railway | (Managed service) |  Connected |
| **Redis** | Railway | (Managed service) |  Connected |

---

## Quick Access Links

### Production URLs
- **Frontend App**: https://ayni-frontend.onrender.com
- **Backend API**: https://ayni-backend-production.up.railway.app
- **API Docs**: https://ayni-backend-production.up.railway.app/docs
- **Health Check**: https://ayni-backend-production.up.railway.app/api/v1/health
- **Monitoring Metrics**: https://ayni-backend-production.up.railway.app/api/v1/monitoring/metrics
- **Celery Tasks**: https://ayni-backend-production.up.railway.app/api/v1/monitoring/celery/tasks
- **Flower UI**: https://ayni-flower-production.up.railway.app (Celery monitoring)

### Dashboards
- **Railway Dashboard**: https://railway.app/project/resilient-flow
- **Render Dashboard**: https://dashboard.render.com
- **GitHub Actions CI**: https://github.com/Brownbull/ayni/actions
- **Sentry Error Tracking**: https://sentry.io (Project: ayni)

---

## Deployment Architecture

### Flow Overview

1. **Code Push** → GitHub Repository (main branch)
2. **CI Pipeline** → GitHub Actions runs tests
3. **Auto-Deploy** → Railway (Backend + Celery) & Render (Frontend)
4. **Services** → Backend connects to PostgreSQL & Redis
5. **Frontend** → Connects to Backend API

### Service Dependencies

```
GitHub Repository (Brownbull/ayni)
    |
    +-- Push to main branch
    |
    +-- GitHub Actions CI
    |   |-- Backend Tests (pytest, 70% coverage)
    |   +-- Frontend Tests (Vitest, 70% coverage)
    |
    +-- Auto-Deploy (if tests pass)
        |
        +-- Railway
        |   |-- Backend API (FastAPI)
        |   |-- Celery Worker
        |   |-- PostgreSQL (managed)
        |   +-- Redis (managed)
        |
        +-- Render
            +-- Frontend (React static site)
```

### Production Stack

**Railway Services:**
- Backend API (FastAPI + Uvicorn)
- Celery Worker (background tasks)
- Flower (Celery monitoring UI)
- PostgreSQL 17 (database)
- Redis 7 (cache + message broker)

**Render Service:**
- Frontend (React + Vite static site)

---

## CI/CD Pipeline

### Automated Deployment Flow

1. **Developer pushes to `main` branch**
2. **GitHub Actions CI triggers**:
   - Backend tests (pytest with 70% coverage)
   - Frontend tests (Vitest with 70% coverage)
   - Linting and type checking
3. **If CI passes**:
   - Railway auto-deploys backend + Celery worker
   - Render auto-deploys frontend
4. **Health checks verify services**
5. **Deployment complete** 

### CI Status Badges

View real-time CI status in README:
- Backend CI: ![Backend CI](https://github.com/Brownbull/ayni/actions/workflows/backend-ci.yml/badge.svg)
- Frontend CI: ![Frontend CI](https://github.com/Brownbull/ayni/actions/workflows/frontend-ci.yml/badge.svg)

---

## Monitoring Production

### Health Checks

#### Basic Health Check (Load Balancer)
```bash
curl https://ayni-backend-production.up.railway.app/health
```
**Expected**: `{"status":"healthy"}`

#### Detailed Health Check (All Services)
```bash
curl https://ayni-backend-production.up.railway.app/api/v1/health | jq
```
**Expected**:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-13T13:39:33.916573+00:00",
  "services": {
    "database": {
      "status": "healthy",
      "latency_ms": 129.7
    },
    "redis": {
      "status": "healthy",
      "latency_ms": 60.2
    }
  }
}
```

### Monitoring & Observability

#### Monitoring Endpoints

**System Metrics:**
```bash
# Get comprehensive system metrics
curl https://ayni-backend-production.up.railway.app/api/v1/monitoring/metrics | jq

# Response includes:
# - Application status and uptime
# - Database connection status and latency
# - Redis connection status and latency
# - Celery worker status
# - Request/response statistics
```

**Celery Task Monitoring:**
```bash
# Get Celery worker and task information
curl https://ayni-backend-production.up.railway.app/api/v1/monitoring/celery/tasks | jq

# Response includes:
# - Active workers
# - Registered tasks
# - Task execution statistics
# - Worker pool information
```

#### Flower UI (Celery Monitoring)

Access the Flower web interface for real-time Celery monitoring:

**URL**: https://ayni-flower-production.up.railway.app

**Features:**
- Real-time worker monitoring
- Task history and status tracking
- Task execution details and results
- Worker resource usage graphs
- Task rate limiting controls
- Task retry and revoke capabilities

**Authentication:**
- Credentials are set via `FLOWER_BASIC_AUTH` environment variable in Railway
- Format: `username:password`

#### Sentry Error Tracking

All production errors are automatically captured and reported to Sentry:

**Dashboard**: https://sentry.io/organizations/your-org/projects/ayni/

**What's Tracked:**
- Unhandled exceptions (backend and frontend)
- HTTP errors (4xx, 5xx)
- Database connection errors
- Redis connection failures
- Celery task failures
- Performance metrics (when enabled)

**Alerts Configured:**
1. **Critical Errors**: Immediate notification for new high-priority issues
2. **New Issues**: Daily digest of new error types
3. **Regression Alerts**: Notification when resolved issues reappear

**Performance Monitoring:**
Every API request includes an `X-Response-Time` header showing the request processing time in milliseconds. Monitor these in Sentry's Performance dashboard.

### View Logs

#### Railway Backend Logs
```bash
# Latest logs
railway logs --service ayni-backend

# Follow logs in real-time
railway logs --service ayni-backend -f

# Filter by error level
railway logs --service ayni-backend --filter "@level:error"

# Last 100 lines
railway logs --service ayni-backend --lines 100
```

#### Railway Celery Worker Logs
```bash
# Latest logs
railway logs --service ayni-celery-worker

# Follow logs
railway logs --service ayni-celery-worker -f
```

#### Railway Flower Logs
```bash
# Latest logs
railway logs --service ayni-flower

# Follow logs
railway logs --service ayni-flower -f
```

#### Render Frontend Logs
```bash
# Via Render dashboard
# https://dashboard.render.com � ayni-frontend � Logs
```

### Railway CLI Setup

If not already set up:
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link
```

---

## Environment Variables

### Backend (Railway)

Required environment variables in Railway dashboard:

| Variable | Value | Description |
|----------|-------|-------------|
| `POSTGRES_SERVER` | `${{Postgres.RAILWAY_PRIVATE_DOMAIN}}` | Railway PostgreSQL host |
| `POSTGRES_PORT` | `${{Postgres.PGPORT}}` | PostgreSQL port |
| `POSTGRES_USER` | `${{Postgres.PGUSER}}` | Database user |
| `POSTGRES_PASSWORD` | `${{Postgres.PGPASSWORD}}` | Database password |
| `POSTGRES_DB` | `${{Postgres.PGDATABASE}}` | Database name |
| `REDIS_URL` | `${{Redis.REDIS_URL}}` | Redis connection URL |
| `JWT_SECRET` | `<64+ char random string>` | JWT signing secret |
| `FRONTEND_HOST` | `https://ayni-frontend.onrender.com` | Frontend URL for CORS |
| `ENVIRONMENT` | `production` | Environment name |
| `SECRET_KEY` | `<random string>` | App secret key |
| `FIRST_SUPERUSER` | `admin@ayni.com` | Initial admin email |
| `FIRST_SUPERUSER_PASSWORD` | `<secure password>` | Initial admin password |
| `SENTRY_DSN` | `<from Sentry dashboard>` | Sentry error tracking DSN |
| `SENTRY_ENVIRONMENT` | `production` | Sentry environment name |
| `SENTRY_TRACES_SAMPLE_RATE` | `0.1` | Performance monitoring sample rate (10%) |

### Flower (Railway)

Required environment variables for Flower service in Railway dashboard:

| Variable | Value | Description |
|----------|-------|-------------|
| `REDIS_URL` | `${{Redis.REDIS_URL}}` | Redis connection URL |
| `FLOWER_BASIC_AUTH` | `<username:password>` | Basic auth credentials |
| `POSTGRES_SERVER` | `${{Postgres.RAILWAY_PRIVATE_DOMAIN}}` | PostgreSQL host (needed by celery_app) |
| `POSTGRES_PORT` | `${{Postgres.PGPORT}}` | PostgreSQL port |
| `POSTGRES_USER` | `${{Postgres.PGUSER}}` | Database user |
| `POSTGRES_PASSWORD` | `${{Postgres.PGPASSWORD}}` | Database password |
| `POSTGRES_DB` | `${{Postgres.PGDATABASE}}` | Database name |
| `JWT_SECRET` | `${{ayni-backend.JWT_SECRET}}` | JWT secret (reference from backend) |
| `PROJECT_NAME` | `Ayni` | Project name |
| `FIRST_SUPERUSER` | `${{ayni-backend.FIRST_SUPERUSER}}` | Admin email (reference from backend) |
| `FIRST_SUPERUSER_PASSWORD` | `${{ayni-backend.FIRST_SUPERUSER_PASSWORD}}` | Admin password (reference from backend) |

### Frontend (Render)

Required environment variable in Render dashboard:

| Variable | Value | Description |
|----------|-------|-------------|
| `VITE_API_URL` | `https://ayni-backend-production.up.railway.app/api/v1` | Backend API URL |
| `VITE_SENTRY_DSN` | `<from Sentry dashboard>` | Sentry error tracking DSN for frontend |

---

## Deployment Procedures

### Manual Deployment (Emergency)

#### Redeploy Backend
```bash
# Via Railway CLI
railway up --service ayni-backend

# Via Railway dashboard
# https://railway.app � ayni-backend � Deployments � Redeploy
```

#### Redeploy Frontend
```bash
# Via Render dashboard
# https://dashboard.render.com � ayni-frontend � Manual Deploy � Deploy latest commit
```

### Updating Environment Variables

#### Railway (Backend)
```bash
# Via CLI
railway variables set JWT_SECRET=new_value --service ayni-backend

# Or via Railway dashboard
# https://railway.app � ayni-backend � Variables � Add Variable
```

#### Render (Frontend)
```bash
# Via Render dashboard only
# https://dashboard.render.com � ayni-frontend � Environment � Add Environment Variable
```

---

## Rollback Procedures

### Railway Backend Rollback

#### Option 1: Via Railway CLI
```bash
# List recent deployments
railway deployments --service ayni-backend

# Rollback to previous deployment
railway rollback --service ayni-backend
```

#### Option 2: Via Railway Dashboard
1. Go to https://railway.app/project/resilient-flow
2. Click **ayni-backend** service
3. Go to **Deployments** tab
4. Click **"..."** menu on working deployment
5. Click **"Redeploy"**

**� Important**: Railway rollback only reverts application code, NOT database migrations. See Database Rollback section below.

### Render Frontend Rollback

#### Via Render Dashboard
1. Go to https://dashboard.render.com
2. Click **ayni-frontend** service
3. Go to **Deploys** tab
4. Find the working deployment
5. Click **"Redeploy"** from that commit

### Database Migration Rollback

**� CAUTION**: Database rollbacks are potentially destructive. Always test in staging first.

#### Step 1: Check Current Migration
```bash
# Connect to Railway backend service
railway run --service ayni-backend

# Inside the service shell
alembic current
```

#### Step 2: Rollback One Migration
```bash
# Via Railway CLI
railway run --service ayni-backend alembic downgrade -1

# Or connect to the service and run
alembic downgrade -1
```

#### Step 3: Redeploy Application
```bash
# Redeploy to pick up the reverted schema
railway up --service ayni-backend
```

**Alternative: Restore from Database Backup**

Railway automatically backs up PostgreSQL databases. To restore:
1. Go to Railway dashboard � **Postgres** service
2. Go to **Backups** tab
3. Select backup point
4. Click **"Restore"**

---

## Troubleshooting Production Issues

### Backend API Issues

#### Service Not Responding (502/503 errors)

**Check health:**
```bash
curl https://ayni-backend-production.up.railway.app/health
```

**View logs:**
```bash
railway logs --service ayni-backend --lines 100
```

**Common causes:**
- Database connection failure � Check `POSTGRES_*` env vars
- Redis connection failure � Check `REDIS_URL` env var
- Memory limit exceeded � Check Railway metrics
- Deployment failed � Check build logs

**Resolution:**
1. Check Railway dashboard for service status
2. Review logs for error messages
3. Verify environment variables are set correctly
4. Rollback to previous working deployment if needed

#### Database Connection Errors

**Symptoms:**
```json
{
  "status": "unhealthy",
  "services": {
    "database": {"status": "unhealthy", "error": "connection refused"}
  }
}
```

**Resolution:**
```bash
# Check PostgreSQL service status in Railway dashboard
# https://railway.app � Postgres service

# Verify environment variables
railway variables --service ayni-backend | grep POSTGRES

# Test database connection
railway run --service ayni-backend psql $DATABASE_URL
```

#### Redis Connection Errors

**Symptoms:**
```json
{
  "services": {
    "redis": {"status": "unhealthy", "error": "Connection refused"}
  }
}
```

**Resolution:**
```bash
# Check Redis service status in Railway dashboard
# https://railway.app � Redis service

# Verify REDIS_URL
railway variables --service ayni-backend | grep REDIS

# Test Redis connection
railway run --service ayni-backend redis-cli -u $REDIS_URL ping
```

### Celery Worker Issues

#### Tasks Not Processing

**Check worker status:**
```bash
# View worker logs
railway logs --service ayni-celery-worker

# Check if worker is running
railway ps --service ayni-celery-worker
```

**Resolution:**
1. Check worker logs for errors
2. Verify REDIS_URL is correct
3. Restart worker service:
   ```bash
   railway restart --service ayni-celery-worker
   ```

### Flower Monitoring Issues

#### Flower Not Accessible (502 errors)

**Check Flower service status:**
```bash
# View Flower logs
railway logs --service ayni-flower

# Check if Flower service is running
railway ps --service ayni-flower
```

**Common causes:**
- Missing dependencies (flower package not installed)
- Missing environment variables (REDIS_URL, database configs, JWT_SECRET)
- Incorrect build configuration in nixpacks.toml
- Flower command not found

**Resolution:**
1. Verify all required environment variables are set:
   ```bash
   railway variables --service ayni-flower
   ```
2. Check that `nixpacks.flower.toml` uses `uv sync` to install all dependencies
3. Ensure Root Directory is set to "backend" in Railway settings
4. Verify FLOWER_BASIC_AUTH is set for authentication
5. Redeploy if configuration was changed:
   ```bash
   railway up --service ayni-flower
   ```

#### Cannot Login to Flower

**Resolution:**
```bash
# Check FLOWER_BASIC_AUTH variable
railway variables --service ayni-flower | grep FLOWER

# Format should be: username:password
# Update if needed:
railway variables set FLOWER_BASIC_AUTH=admin:newpassword --service ayni-flower
```

### Frontend Issues

#### CORS Errors in Browser Console

**Symptoms:**
```
Access to fetch at 'https://ayni-backend-production.up.railway.app/api/v1/...'
from origin 'https://ayni-frontend.onrender.com' has been blocked by CORS policy
```

**Resolution:**
```bash
# Check FRONTEND_HOST variable in Railway
railway variables --service ayni-backend | grep FRONTEND_HOST

# Should be: https://ayni-frontend.onrender.com

# If missing or wrong, update it:
railway variables set FRONTEND_HOST=https://ayni-frontend.onrender.com --service ayni-backend

# Redeploy backend
railway up --service ayni-backend
```

#### Frontend Not Loading (White Screen)

**Check build logs in Render dashboard:**
1. Go to https://dashboard.render.com
2. Click **ayni-frontend**
3. Check **Events** tab for build errors

**Common causes:**
- Build command failed (npm install or npm run build)
- Missing `VITE_API_URL` environment variable
- Incorrect publish directory

**Resolution:**
1. Check Render logs for build errors
2. Verify `VITE_API_URL` is set correctly
3. Redeploy with "Clear build cache & deploy"

### Performance Issues

#### High Response Times

**Check metrics:**
```bash
# View database query performance
curl https://ayni-backend-production.up.railway.app/api/v1/health | jq '.services.database.latency_ms'

# View Redis latency
curl https://ayni-backend-production.up.railway.app/api/v1/health | jq '.services.redis.latency_ms'
```

**Resolution:**
- If DB latency > 500ms: Check database size, add indexes
- If Redis latency > 200ms: Check Redis memory usage
- Check Railway metrics dashboard for CPU/memory usage

#### Out of Memory Errors

**Check Railway dashboard:**
- Go to **Metrics** tab
- View memory usage graph

**Resolution:**
1. Increase memory limit in Railway settings
2. Optimize application code (reduce memory usage)
3. Scale to multiple instances (Railway Pro plan)

---

## Production Checklist

### Pre-Deployment
- [ ] All tests passing in CI
- [ ] Code reviewed and approved
- [ ] Environment variables verified
- [ ] Database migrations tested in staging
- [ ] Health checks working locally

### Post-Deployment
- [ ] Health check returning 200 OK
- [ ] Database connection healthy
- [ ] Redis connection healthy
- [ ] Celery worker processing tasks
- [ ] Frontend loading correctly
- [ ] No CORS errors in browser console
- [ ] API endpoints responding correctly
- [ ] Check logs for errors

### Weekly Maintenance
- [ ] Review Railway/Render metrics
- [ ] Check database size and performance
- [ ] Review error logs
- [ ] Verify backups are running
- [ ] Update dependencies if needed

---

## Scaling and Performance

### Horizontal Scaling (Railway Pro)

To handle more traffic:
```bash
# Scale backend to multiple instances
# Via Railway dashboard: Settings � Instances � Adjust count
```

### Database Performance

**Monitor queries:**
```bash
# Connect to database
railway run --service ayni-backend psql $DATABASE_URL

# View slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;
```

**Add indexes:**
```bash
# Create migration for new index
cd backend
uv run alembic revision -m "add_index_on_users_email"

# Edit migration file to add index
# Then deploy
git push origin main
```

### Redis Caching

**Monitor cache hit rate:**
```bash
# Connect to Redis
railway run --service ayni-backend redis-cli -u $REDIS_URL

# Get cache stats
INFO stats
```

---

## Security Best Practices

### Secrets Management

**Never commit secrets to Git:**
- All secrets in Railway/Render environment variables
- Use Railway's secret references: `${{SERVICE.VARIABLE}}`
- Rotate secrets regularly (JWT_SECRET, database passwords)

### Database Security

-  Row-Level Security (RLS) enabled
-  Non-superuser database role
-  SSL connections enforced
-  Regular backups automated

### API Security

-  CORS configured correctly
-  JWT authentication enabled
-  Rate limiting (via Railway)
-  HTTPS only (enforced by Railway/Render)

---

## Additional Resources

### Documentation
- **Full Deployment Guide**: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
- **Local Development**: [run_app.local.md](run_app.local.md)
- **Architecture Docs**: [docs/architecture.md](docs/architecture.md)

### External Links
- **Railway Docs**: https://docs.railway.app
- **Render Docs**: https://render.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **React Docs**: https://react.dev

### Support
- **GitHub Issues**: https://github.com/Brownbull/ayni/issues
- **Railway Support**: https://railway.app/help
- **Render Support**: https://render.com/support

---

## Emergency Contacts

For production emergencies:

1. **Check status pages:**
   - Railway: https://status.railway.app
   - Render: https://status.render.com

2. **Review incident response plan:**
   - See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) � "Troubleshooting"

3. **Rollback if necessary:**
   - Use procedures outlined above
   - Document incident for post-mortem

---

**Last Updated**: 2025-11-13
**Production Status**:  All services operational
