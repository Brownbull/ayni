# Ayni Deployment Documentation

Complete deployment guides for the Ayni application on Railway (backend) and Render (frontend).

## Quick Start

### 1. Deploy Backend (Railway)
Follow → **[SETUP-BACKEND.md](./SETUP-BACKEND.md)**

### 2. Deploy Frontend (Render)
Follow → **[SETUP-FRONTEND.md](./SETUP-FRONTEND.md)**

### 3. Verify Deployment
Use → **[DEPLOYMENT-SUCCESS-CHECKLIST.md](./DEPLOYMENT-SUCCESS-CHECKLIST.md)**

---

## Documentation Structure

### 📘 Setup Guides

Complete deployment instructions for first-time setup:

| Document | Purpose | Platform |
|----------|---------|----------|
| **[SETUP-BACKEND.md](./SETUP-BACKEND.md)** | Deploy FastAPI backend with PostgreSQL & Redis | Railway |
| **[SETUP-FRONTEND.md](./SETUP-FRONTEND.md)** | Deploy React frontend using Blueprint | Render |

### 🔧 Troubleshooting Guides

Solutions for common issues:

| Document | Purpose | Platform |
|----------|---------|----------|
| **[TROUBLESHOOTING-BACKEND.md](./TROUBLESHOOTING-BACKEND.md)** | Backend issues (CORS, OAuth, database, etc.) | Railway |
| **[TROUBLESHOOTING-FRONTEND.md](./TROUBLESHOOTING-FRONTEND.md)** | Frontend issues (routing, build errors, etc.) | Render |

### ✅ Verification

| Document | Purpose |
|----------|---------|
| **[DEPLOYMENT-SUCCESS-CHECKLIST.md](./DEPLOYMENT-SUCCESS-CHECKLIST.md)** | Complete verification checklist with test commands |

### 📋 OAuth Setup (Optional)

| Document | Purpose |
|----------|---------|
| **[QUICK-OAUTH-SETUP.md](./QUICK-OAUTH-SETUP.md)** | 5-minute Google OAuth setup guide |

---

## Production URLs

**Frontend:** https://ayni-frontend.onrender.com
**Backend API:** https://ayni-backend-production.up.railway.app/api/v1
**Backend Health:** https://ayni-backend-production.up.railway.app/health

---

## Technology Stack

### Backend (Railway)
- **Framework:** FastAPI (Python 3.11)
- **Database:** PostgreSQL 16
- **Cache:** Redis 7
- **Authentication:** JWT + OAuth 2.0

### Frontend (Render)
- **Framework:** React 18 + TypeScript
- **Build Tool:** Vite 5
- **Routing:** React Router 6
- **Deployment:** Static site with Blueprint

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Browser                       │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS
                         ▼
         ┌───────────────────────────────────┐
         │   Render (Static Frontend)        │
         │   - React SPA                     │
         │   - SPA routing configured        │
         │   - Security headers              │
         └───────────────┬───────────────────┘
                         │ HTTPS (CORS configured)
                         ▼
         ┌───────────────────────────────────┐
         │   Railway (Backend)               │
         │   ┌─────────────────────────────┐ │
         │   │   FastAPI Application       │ │
         │   └─────────────────────────────┘ │
         │   ┌───────────┐  ┌────────────┐  │
         │   │ PostgreSQL│  │   Redis    │  │
         │   └───────────┘  └────────────┘  │
         └───────────────────────────────────┘
```

---

## Common Workflows

### Initial Deployment

1. **Setup Backend**
   - Follow [SETUP-BACKEND.md](./SETUP-BACKEND.md)
   - Deploy to Railway
   - Configure environment variables
   - Get backend URL

2. **Setup Frontend**
   - Follow [SETUP-FRONTEND.md](./SETUP-FRONTEND.md)
   - Deploy to Render using Blueprint
   - Set backend URL in environment
   - Get frontend URL

3. **Configure CORS**
   - Add frontend URL to backend `FRONTEND_HOST`
   - Railway auto-redeploys

4. **Verify**
   - Use [DEPLOYMENT-SUCCESS-CHECKLIST.md](./DEPLOYMENT-SUCCESS-CHECKLIST.md)
   - Test all authentication flows
   - Verify SPA routing works

### Update Backend

```bash
# Make code changes
git add .
git commit -m "feat: new feature"
git push

# Railway auto-deploys from main branch
# Monitor with:
railway logs --tail
```

### Update Frontend

```bash
# Make code changes
git add .
git commit -m "feat: new feature"
git push

# Render auto-deploys from main branch
# Check: Dashboard → Service → Deploys
```

### Update Backend Dependencies

```bash
# Update pyproject.toml
# Then regenerate requirements.txt:
cd backend
uv pip compile pyproject.toml -o requirements.txt
git add requirements.txt
git commit -m "chore: update dependencies"
git push
```

### Rollback

**Backend (Railway):**
- Dashboard → Service → Deployments → Select version → Redeploy

**Frontend (Render):**
- Dashboard → Service → Deploys → Select version → Redeploy

---

## Troubleshooting Quick Reference

### Backend Issues (Railway)

| Issue | Fix | Documentation |
|-------|-----|---------------|
| ModuleNotFoundError | Regenerate requirements.txt | [Guide](./TROUBLESHOOTING-BACKEND.md#issue-missing-dependencies---modulenotfounderror) |
| CORS error | Set FRONTEND_HOST | [Guide](./TROUBLESHOOTING-BACKEND.md#issue-frontend-blocked-by-cors-policy) |
| Database error | Check PostgreSQL service | [Guide](./TROUBLESHOOTING-BACKEND.md#database-issues) |
| Redis error | Check Redis service | [Guide](./TROUBLESHOOTING-BACKEND.md#redis-issues) |
| OAuth 503 | Set OAuth variables | [Guide](./TROUBLESHOOTING-BACKEND.md#issue-oauth-not-configured-503) |

### Frontend Issues (Render)

| Issue | Fix | Documentation |
|-------|-----|---------------|
| 404 on refresh | Use Blueprint deployment | [Guide](./TROUBLESHOOTING-FRONTEND.md#issue-404-on-page-refresh) |
| TypeScript build error | Type-only imports | [Guide](./TROUBLESHOOTING-FRONTEND.md#issue-build-fails-with-typescript-errors) |
| API requests fail | Check VITE_API_URL | [Guide](./TROUBLESHOOTING-FRONTEND.md#issue-api-requests-fail---network-error) |
| Blank page | Check browser console | [Guide](./TROUBLESHOOTING-FRONTEND.md#issue-build-succeeds-but-site-is-blank) |
| OAuth shows JSON | Backend needs update | [Guide](./TROUBLESHOOTING-FRONTEND.md#issue-oauth-shows-json-instead-of-redirecting-to-dashboard) |

---

## Environment Variables

### Backend (Railway)

**Required:**
```bash
FRONTEND_HOST=https://ayni-frontend.onrender.com
JWT_SECRET=<64-char-random-string>
PROJECT_NAME=Ayni
ENVIRONMENT=production
```

**Auto-configured:**
```bash
DATABASE_URL=<auto-set-by-railway>
REDIS_URL=<auto-set-by-railway>
```

**Optional (OAuth):**
```bash
GOOGLE_OAUTH_CLIENT_ID=<from-google-console>
GOOGLE_OAUTH_CLIENT_SECRET=<from-google-console>
GOOGLE_OAUTH_REDIRECT_URI=https://your-backend.up.railway.app/api/v1/auth/google/callback
```

### Frontend (Render)

**Set in render.yaml:**
```bash
VITE_API_URL=https://ayni-backend-production.up.railway.app/api/v1
VITE_ENVIRONMENT=production
```

**Set during deployment:**
```bash
VITE_SENTRY_DSN=<optional>
```

---

## Monitoring

### Backend Health Check

```bash
curl https://ayni-backend-production.up.railway.app/health
```

Expected response:
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

### Frontend Check

```bash
curl -I https://ayni-frontend.onrender.com
# Should return HTTP/2 200
```

### CORS Check

```bash
curl -X OPTIONS https://ayni-backend-production.up.railway.app/api/v1/health \
  -H "Origin: https://ayni-frontend.onrender.com" \
  -H "Access-Control-Request-Method: GET" \
  -i

# Should include: access-control-allow-origin: https://ayni-frontend.onrender.com
```

### Logs

**Backend:**
```bash
railway logs --tail
```

**Frontend:**
- Dashboard → Service → Logs (build logs only)
- Browser DevTools → Console (runtime errors)

---

## Security Best Practices

### Secrets Management
- ✅ All secrets in environment variables (never in code)
- ✅ Different secrets for dev/production
- ✅ Rotate JWT_SECRET quarterly
- ✅ Keep OAuth credentials private

### HTTPS
- ✅ Railway provides HTTPS automatically
- ✅ Render provides HTTPS automatically
- ✅ OAuth requires HTTPS (enforced by Google)

### CORS
- ✅ Backend allows only configured frontend origin
- ✅ Credentials allowed for authenticated requests

### Headers
- ✅ Security headers configured via render.yaml
- ✅ X-Frame-Options: DENY
- ✅ X-Content-Type-Options: nosniff
- ✅ Referrer-Policy: strict-origin-when-cross-origin

---

## Cost Optimization

### Free Tier Limits

**Railway:**
- $5 free credit per month
- Resources shared across all services
- Scales to 8GB RAM, 8 vCPU

**Render:**
- Free for static sites (no limits)
- Cold start after 15 min inactivity
- Shared CDN bandwidth

### Upgrade Triggers

**Railway:** Upgrade when:
- Free credit exhausted
- Need always-on backend
- Higher resource limits needed

**Render:** Upgrade when:
- Need custom domain with SSL
- Want faster cold starts
- Need priority builds

---

## Recent Deployments

| Date | Backend Commit | Frontend Commit | Status | Notes |
|------|----------------|-----------------|--------|-------|
| 2025-11-14 | `2c03230` | `2c03230` | ✅ Live | OAuth redirect flow |
| 2025-11-14 | `c6f5c90` | `4e00303` | ✅ Live | Dependencies & TypeScript fixes |

---

## Next Steps After Deployment

1. ✅ Backend and frontend deployed
2. → Configure Google OAuth (optional) - [QUICK-OAUTH-SETUP.md](./QUICK-OAUTH-SETUP.md)
3. → Set up monitoring (Sentry)
4. → Configure custom domains (optional)
5. → Set up automated backups
6. → Create staging environment

---

## Support & Resources

### Documentation
- [Railway Docs](https://docs.railway.app)
- [Render Docs](https://render.com/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [React Docs](https://react.dev)

### Status Pages
- [Railway Status](https://status.railway.app)
- [Render Status](https://status.render.com)

### Community
- [Railway Discord](https://discord.gg/railway)
- [Render Community](https://community.render.com)

### Internal Docs
- Backend setup: [SETUP-BACKEND.md](./SETUP-BACKEND.md)
- Frontend setup: [SETUP-FRONTEND.md](./SETUP-FRONTEND.md)
- Backend issues: [TROUBLESHOOTING-BACKEND.md](./TROUBLESHOOTING-BACKEND.md)
- Frontend issues: [TROUBLESHOOTING-FRONTEND.md](./TROUBLESHOOTING-FRONTEND.md)
- Verification: [DEPLOYMENT-SUCCESS-CHECKLIST.md](./DEPLOYMENT-SUCCESS-CHECKLIST.md)

---

## Contributing

When updating deployment docs:

1. Test changes in production first
2. Update relevant guide (setup or troubleshooting)
3. Update this README if structure changes
4. Document commit hash for fixes
5. Update "Recent Deployments" table

---

**Last Updated:** 2025-11-14
**Deployment Status:** ✅ Production Ready
**Documentation Version:** 2.0 (Consolidated)
