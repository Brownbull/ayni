# Deployment Success Checklist

This checklist helps verify that the Ayni application is fully deployed and operational.

## Pre-Deployment Checklist

### Backend (Railway)
- [ ] Railway account connected to GitHub repository
- [ ] Backend service linked to repository
- [ ] Auto-deploy enabled for `main` branch
- [ ] PostgreSQL database provisioned
- [ ] Redis instance provisioned

### Frontend (Render)
- [ ] Render account connected to GitHub repository
- [ ] Blueprint deployment selected (not manual configuration)
- [ ] `render.yaml` exists in repository root

---

## Environment Variables

### Railway Backend
- [ ] `FRONTEND_HOST` = `https://ayni-frontend.onrender.com`
- [ ] `POSTGRES_*` variables (auto-set by Railway database)
- [ ] `REDIS_URL` (auto-set by Railway Redis)
- [ ] `JWT_SECRET` (generate secure random string)
- [ ] `PROJECT_NAME` = `Ayni`
- [ ] `GOOGLE_OAUTH_CLIENT_ID` (optional, for Google OAuth)
- [ ] `GOOGLE_OAUTH_CLIENT_SECRET` (optional, for Google OAuth)
- [ ] `SENTRY_DSN` (optional, for error tracking)

### Render Frontend
Variables are set in `render.yaml`:
- [ ] `VITE_API_URL` = `https://ayni-backend-production.up.railway.app/api/v1`
- [ ] `VITE_ENVIRONMENT` = `production`
- [ ] `VITE_SENTRY_DSN` (set during Blueprint deployment, optional)

---

## Build & Deployment

### Backend
```bash
# Check Railway deployment status
railway status

# View recent logs
railway logs --limit 50
```

Expected:
- [ ] Build completes successfully
- [ ] No `ModuleNotFoundError` in logs
- [ ] Service is "Active" in Railway dashboard
- [ ] Health check endpoint responds

### Frontend
- [ ] Build completes without TypeScript errors
- [ ] No missing import errors
- [ ] Deployment shows "Live" status
- [ ] Static files served correctly

---

## Verification Tests

### 1. Backend Health Check

```bash
curl https://ayni-backend-production.up.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-14T...",
  "services": {
    "database": {"status": "healthy", "latency_ms": 10.5},
    "redis": {"status": "healthy", "latency_ms": 5.2}
  }
}
```

- [ ] Returns HTTP 200
- [ ] Database status is "healthy"
- [ ] Redis status is "healthy"

### 2. Frontend Loads

```bash
curl -I https://ayni-frontend.onrender.com
```

- [ ] Returns HTTP 200
- [ ] Content-Type is `text/html`

### 3. SPA Routing Works

```bash
curl -I https://ayni-frontend.onrender.com/login
curl -I https://ayni-frontend.onrender.com/dashboard
```

- [ ] Both return HTTP 200 (not 404)
- [ ] Both serve `index.html` (check Content-Type)

### 4. CORS Configuration

```bash
curl -X OPTIONS https://ayni-backend-production.up.railway.app/api/v1/health \
  -H "Origin: https://ayni-frontend.onrender.com" \
  -H "Access-Control-Request-Method: GET" \
  -i
```

- [ ] Returns `access-control-allow-origin: https://ayni-frontend.onrender.com`
- [ ] Returns `access-control-allow-methods: GET, POST, ...`

### 5. Email/Password Registration

Test in browser:
1. Visit https://ayni-frontend.onrender.com
2. Click "Registrarse"
3. Fill in registration form
4. Submit

- [ ] Registration request succeeds
- [ ] Receives verification email
- [ ] Can verify email via link
- [ ] Can log in after verification

### 6. Email/Password Login

1. Visit https://ayni-frontend.onrender.com/login
2. Enter credentials
3. Click "Iniciar sesión"

- [ ] Login succeeds
- [ ] Redirects to `/dashboard`
- [ ] User profile loads
- [ ] Can navigate app

### 7. Google OAuth Flow

1. Visit https://ayni-frontend.onrender.com/login
2. Click "Continuar con Google"
3. Select Google account
4. Authorize

- [ ] Redirects to Google OAuth consent screen
- [ ] After authorization, redirects to backend callback
- [ ] Backend redirects to frontend with tokens
- [ ] Frontend extracts tokens from URL
- [ ] Redirects to dashboard (not JSON)
- [ ] User profile loads correctly

### 8. Token Refresh

1. Log in
2. Wait for access token to expire (or manually test)

- [ ] Frontend automatically refreshes token
- [ ] User stays logged in
- [ ] No manual re-authentication needed

### 9. Protected Routes

Without logging in:
1. Visit https://ayni-frontend.onrender.com/dashboard

- [ ] Redirects to `/login`
- [ ] Shows "Please log in" message

### 10. Page Refresh Persistence

1. Log in successfully
2. Navigate to `/dashboard`
3. Refresh page (Ctrl+F5)

- [ ] Dashboard still loads (not 404)
- [ ] User stays logged in
- [ ] No re-authentication needed

---

## Post-Deployment Configuration

### Optional: Google OAuth Credentials

If Google OAuth is not yet configured:

1. [ ] Create OAuth 2.0 credentials in Google Cloud Console
2. [ ] Set authorized redirect URI: `https://ayni-backend-production.up.railway.app/api/v1/auth/google/callback`
3. [ ] Add `GOOGLE_OAUTH_CLIENT_ID` to Railway
4. [ ] Add `GOOGLE_OAUTH_CLIENT_SECRET` to Railway
5. [ ] Railway will auto-redeploy

### Optional: Custom Domain

Render:
1. [ ] Go to service → Settings → Custom Domain
2. [ ] Add custom domain
3. [ ] Configure DNS records
4. [ ] Update `FRONTEND_HOST` in Railway backend
5. [ ] Update OAuth redirect URI in Google Cloud Console

Railway:
1. [ ] Go to service → Settings → Domains
2. [ ] Add custom domain
3. [ ] Configure DNS records
4. [ ] Update `VITE_API_URL` in Render frontend
5. [ ] Update OAuth redirect URI

### Optional: Monitoring

Sentry:
1. [ ] Create Sentry project
2. [ ] Get Sentry DSN
3. [ ] Add `SENTRY_DSN` to Railway backend
4. [ ] Add `VITE_SENTRY_DSN` to Render frontend
5. [ ] Trigger test errors to verify

---

## Common Issues

### Build Fails with TypeScript Error
- **Fix:** Update to latest `main` branch (contains type-only import fixes)

### CORS Errors
- **Fix:** Verify `FRONTEND_HOST` is set in Railway backend

### 404 on Route Refresh
- **Fix:** Ensure using Blueprint deployment (not manual config)

### OAuth Shows JSON Instead of Dashboard
- **Fix:** Update to latest `main` branch (contains OAuth redirect fix)

### Missing Dependencies Error
- **Fix:** Regenerate `requirements.txt`: `uv pip compile pyproject.toml -o requirements.txt`

---

## Success Criteria

All items below must pass:

✅ Backend health check returns 200
✅ Frontend loads without errors
✅ SPA routing works (no 404 on refresh)
✅ CORS headers present
✅ Email registration flow works end-to-end
✅ Email login works
✅ Google OAuth login works (if configured)
✅ Protected routes redirect to login
✅ Token refresh works automatically
✅ Page refresh maintains login state

---

## Rollback Plan

If deployment fails:

### Render
1. Go to service → Deploys tab
2. Find last working deployment
3. Click "Redeploy"

### Railway
1. Go to service → Deployments tab
2. Find last working deployment
3. Click "Redeploy"

---

## Support

If any checklist item fails:

1. Check logs:
   - Railway: `railway logs`
   - Render: Dashboard → Logs tab

2. Review [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

3. Verify environment variables:
   - Railway: `railway variables`
   - Render: Dashboard → Environment tab

4. Test endpoints with curl

5. Check browser console for frontend errors

---

## Deployment History

Keep track of successful deployments:

| Date | Backend Commit | Frontend Commit | Status | Notes |
|------|----------------|-----------------|--------|-------|
| 2025-11-14 | `2c03230` | `2c03230` | ✅ Success | OAuth redirect fix deployed |
| 2025-11-14 | `c6f5c90` | `4e00303` | ✅ Success | Dependencies & TypeScript fixes |

---

## Next Steps After Successful Deployment

Once all checklist items pass:

1. [ ] Mark Story 2.5 (Google OAuth Integration) as complete
2. [ ] Run code review workflow: `/bmad:bmm:workflows:code-review`
3. [ ] Mark story as done: `/bmad:bmm:workflows:story-done`
4. [ ] Check sprint status for next story
5. [ ] Consider setting up monitoring (Sentry)
6. [ ] Consider configuring custom domains
7. [ ] Update README with production URLs
