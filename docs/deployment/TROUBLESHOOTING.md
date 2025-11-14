# Deployment Troubleshooting Guide

This guide documents common deployment issues and their solutions for the Ayni application deployed on Railway (backend) and Render (frontend).

## Table of Contents
- [Build Failures](#build-failures)
- [CORS Errors](#cors-errors)
- [OAuth Issues](#oauth-issues)
- [Routing Issues](#routing-issues)
- [General Debugging](#general-debugging)

---

## Build Failures

### Issue: Render Frontend Build Fails with TypeScript Errors

**Symptom:**
```
error TS1484: 'FormEvent' is a type and must be imported using a type-only
import when 'verbatimModuleSyntax' is enabled.
```

**Root Cause:**
TypeScript's `verbatimModuleSyntax` setting requires types to be imported using the `type` keyword.

**Solution:**
Change imports to use type-only syntax:
```typescript
// Before
import { useState, FormEvent } from 'react'

// After
import { useState, type FormEvent } from 'react'
```

**Fixed in commit:** `4e00303`

---

### Issue: Railway Backend Build Missing Dependencies

**Symptom:**
Backend deployment fails or crashes at runtime with `ModuleNotFoundError: No module named 'httpx_oauth'`

**Root Cause:**
Railway installs dependencies from `requirements.txt`, which was outdated and missing newly added packages.

**Solution:**
Regenerate `requirements.txt` from `pyproject.toml`:
```bash
cd backend
uv pip compile pyproject.toml -o requirements.txt
git add requirements.txt
git commit -m "chore: update requirements.txt"
git push
```

**Fixed in commit:** `c6f5c90`

**Prevention:**
Always regenerate `requirements.txt` after adding new dependencies to `pyproject.toml`.

---

## CORS Errors

### Issue: Frontend Blocked by CORS Policy

**Symptom:**
```
Access to XMLHttpRequest at 'https://ayni-backend-production.up.railway.app/api/v1/...'
from origin 'https://ayni-frontend.onrender.com' has been blocked by CORS policy:
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

**Root Cause:**
The backend's CORS configuration requires `FRONTEND_HOST` environment variable to allow the Render frontend origin.

**Solution:**
Set the `FRONTEND_HOST` environment variable in Railway:
```bash
railway variables --set FRONTEND_HOST=https://ayni-frontend.onrender.com
```

Or via Railway Dashboard:
1. Go to your Railway project
2. Select the backend service
3. Navigate to Variables tab
4. Add: `FRONTEND_HOST` = `https://ayni-frontend.onrender.com`

**Note:** Railway will automatically redeploy when environment variables change.

**Verification:**
Test CORS preflight:
```bash
curl -X OPTIONS https://ayni-backend-production.up.railway.app/api/v1/health \
  -H "Origin: https://ayni-frontend.onrender.com" \
  -H "Access-Control-Request-Method: GET" \
  -i
```

Should return:
```
access-control-allow-origin: https://ayni-frontend.onrender.com
```

---

### Issue: 500 Errors Appear as CORS Errors

**Symptom:**
Browser shows CORS error, but the real issue is a 500 Internal Server Error.

**Root Cause:**
When an endpoint crashes with a 500 error, the error occurs before the CORS middleware can add headers. Browsers interpret the missing CORS headers as a CORS violation.

**Solution:**
1. Check the actual HTTP status code (500 vs 403/404)
2. Look at Railway logs for the actual error
3. Fix the underlying 500 error
4. CORS headers will appear once the endpoint works

**Debugging:**
```bash
# Test endpoint directly (not from browser)
curl -i https://ayni-backend-production.up.railway.app/api/v1/endpoint

# Check if it's a real 500 error or CORS issue
```

---

## OAuth Issues

### Issue: OAuth Endpoint Returns 500 Error

**Symptom:**
```json
{"error":"Internal Server Error","detail":"An unexpected error occurred..."}
```

**Root Causes & Solutions:**

**1. Missing httpx-oauth dependency**
- **Symptom:** `ModuleNotFoundError: No module named 'httpx_oauth'` in logs
- **Solution:** Regenerate requirements.txt (see [Build Failures](#issue-railway-backend-build-missing-dependencies))

**2. Wrong type annotation**
- **Symptom:** Dependency injection fails silently
- **Fix:** Use `redis: Redis` instead of `redis: RedisClient` in function parameters
- **Fixed in commit:** `2fdeb3e`

**3. OAuth credentials not configured**
- **Expected behavior:** Should return 503 with helpful message
- **Solution:** Configure Google OAuth credentials (see QUICK-OAUTH-SETUP.md)

---

### Issue: OAuth Works Locally But Not in Production

**Checklist:**
1. ✅ Verify `httpx-oauth` in requirements.txt
2. ✅ Verify Railway deployed successfully
3. ✅ Check Railway environment variables include:
   - `GOOGLE_OAUTH_CLIENT_ID`
   - `GOOGLE_OAUTH_CLIENT_SECRET`
   - `GOOGLE_OAUTH_REDIRECT_URI`
4. ✅ Verify redirect URI in Google Cloud Console matches Railway URL
5. ✅ Ensure HTTPS is used (Google OAuth requires it)

---

## Routing Issues

### Issue: Frontend Shows "Not Found" on Page Refresh

**Symptom:**
- Navigating to `/dashboard` or `/login` works initially
- Refreshing the page shows "Not Found"
- Works fine on localhost

**Root Cause:**
Render tries to serve routes as static files. When you visit `/dashboard`, there's no actual `dashboard.html` file, so Render returns 404.

**Solution:**
Add a `_redirects` file to handle SPA routing:

1. Create `/frontend/public/_redirects`:
```
/* /index.html 200
```

2. Commit and push:
```bash
git add frontend/public/_redirects
git commit -m "fix: add _redirects for SPA routing"
git push
```

3. Vite automatically copies files from `public/` to `dist/` during build
4. Render reads `_redirects` and serves `index.html` for all routes
5. React Router handles client-side routing

**Fixed in commit:** `77b7bc3`

**Verification:**
After deployment, test:
1. Visit https://ayni-frontend.onrender.com/dashboard
2. Refresh the page (Ctrl+F5)
3. Should show dashboard, not "Not Found"

---

### Issue: OAuth Callback Shows JSON Instead of Redirecting to Dashboard

**Symptom:**
After Google OAuth login, browser shows raw JSON with access token instead of redirecting to dashboard.

**Root Cause:**
Backend OAuth callback endpoint was returning JSON response instead of redirecting to frontend.

**Solution:**
This is now fixed in commit `2c03230`. The backend now redirects to the frontend with tokens as URL parameters.

**How it works now:**
1. Google redirects to backend `/api/v1/auth/google/callback`
2. Backend validates OAuth code, creates/links user account
3. Backend generates JWT tokens
4. Backend redirects to `{FRONTEND_HOST}/auth/callback?access_token=...&refresh_token=...`
5. Frontend OAuthCallback component extracts tokens from URL
6. Frontend stores tokens in localStorage
7. Frontend loads user profile
8. Frontend redirects to `/dashboard`

**Verification:**
After deploying the fix, test OAuth login:
1. Click "Sign in with Google"
2. Authorize on Google
3. Should redirect to dashboard (not show JSON)

**Fixed in commit:** `2c03230`

---

## General Debugging

### Railway Backend Logs

**View logs:**
```bash
railway logs --service ayni-backend
```

**Common issues to look for:**
- ModuleNotFoundError (missing dependencies)
- Connection errors (database, Redis)
- Unhandled exceptions
- Environment variable issues

---

### Render Frontend Logs

**Access logs:**
1. Go to Render Dashboard
2. Select `ayni-frontend` service
3. Click "Logs" tab

**Common issues:**
- Build failures (TypeScript errors)
- Missing environment variables
- Static file serving issues

---

### Environment Variables Checklist

**Railway Backend:**
- ✅ `FRONTEND_HOST` - Render frontend URL
- ✅ `POSTGRES_*` - Database credentials (auto-set by Railway)
- ✅ `REDIS_URL` - Redis connection string (auto-set by Railway)
- ✅ `JWT_SECRET` - Secret for JWT tokens
- ✅ `PROJECT_NAME` - Application name
- ⚠️ `GOOGLE_OAUTH_CLIENT_ID` - Optional, for OAuth
- ⚠️ `GOOGLE_OAUTH_CLIENT_SECRET` - Optional, for OAuth
- ⚠️ `SENTRY_DSN` - Optional, for error tracking

**Render Frontend:**
- ✅ `VITE_API_URL` - Railway backend URL (with https://)
- ⚠️ `VITE_SENTRY_DSN` - Optional, for error tracking
- ⚠️ `VITE_ENVIRONMENT` - Optional, deployment environment

---

### Health Check Endpoints

**Backend health check:**
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

**Frontend health check:**
```bash
curl https://ayni-frontend.onrender.com
```

Should return HTML (not 404).

---

## Quick Diagnosis Flowchart

```
Issue: Frontend can't connect to backend
├─ Check CORS headers (curl -i)
│  ├─ Missing → Set FRONTEND_HOST in Railway
│  └─ Present → Continue
├─ Check HTTP status code
│  ├─ 500 → Check Railway logs for error
│  ├─ 503 → Service not configured (OAuth?)
│  ├─ 404 → Check endpoint URL
│  └─ 200 → Not a backend issue
└─ Check browser console for frontend errors
```

---

## Support

If you encounter an issue not covered here:

1. **Check logs first**
   - Railway: `railway logs`
   - Render: Dashboard → Logs tab

2. **Verify environment variables**
   - Railway: `railway variables`
   - Render: Dashboard → Environment tab

3. **Test endpoints directly**
   ```bash
   curl -i https://ayni-backend-production.up.railway.app/api/v1/health
   ```

4. **Check deployment status**
   - Railway: `railway status`
   - Render: Dashboard shows deployment status

5. **Document and report**
   - Copy error messages
   - Include reproduction steps
   - Share relevant logs
