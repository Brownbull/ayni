# Deployment Documentation

This directory contains comprehensive documentation for deploying the Ayni application to production.

## Quick Start

1. **Deploy Backend to Railway**: Backend is already deployed and configured
2. **Deploy Frontend to Render**: Follow [DEPLOY-FROM-BLUEPRINT.md](./DEPLOY-FROM-BLUEPRINT.md)
3. **Verify Deployment**: Use [DEPLOYMENT-SUCCESS-CHECKLIST.md](./DEPLOYMENT-SUCCESS-CHECKLIST.md)

## Production URLs

- **Frontend**: https://ayni-frontend.onrender.com
- **Backend API**: https://ayni-backend-production.up.railway.app/api/v1
- **Backend Health**: https://ayni-backend-production.up.railway.app/health

## Documentation Index

### Deployment Guides

- **[DEPLOY-FROM-BLUEPRINT.md](./DEPLOY-FROM-BLUEPRINT.md)** - Step-by-step guide for deploying frontend using Render Blueprint
- **[DEPLOYMENT-SUCCESS-CHECKLIST.md](./DEPLOYMENT-SUCCESS-CHECKLIST.md)** - Comprehensive checklist to verify successful deployment

### Troubleshooting

- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Common deployment issues and solutions
  - Build failures (TypeScript, dependencies)
  - CORS errors
  - OAuth issues
  - Routing issues
  - General debugging

### Specific Issues (Resolved)

- **[RENDER-SPA-ROUTING-FIX.md](./RENDER-SPA-ROUTING-FIX.md)** - SPA routing 404 errors (now resolved via Blueprint)

### OAuth Configuration

- **[QUICK-OAUTH-SETUP.md](./QUICK-OAUTH-SETUP.md)** - Quick setup guide for Google OAuth
- **[oauth-setup-production.md](./oauth-setup-production.md)** - Production OAuth configuration

## Architecture Overview

### Backend (Railway)

**Services:**
- FastAPI application
- PostgreSQL database
- Redis cache

**Environment Variables:**
- `FRONTEND_HOST` - Render frontend URL (for CORS)
- `JWT_SECRET` - Secret for JWT tokens
- `GOOGLE_OAUTH_CLIENT_ID` - Google OAuth credentials (optional)
- `GOOGLE_OAUTH_CLIENT_SECRET` - Google OAuth credentials (optional)
- Database and Redis URLs (auto-configured by Railway)

### Frontend (Render)

**Configuration:**
- Blueprint-based deployment from `render.yaml`
- Static site with SPA routing
- Security headers configured

**Environment Variables:**
- `VITE_API_URL` - Railway backend URL
- `VITE_ENVIRONMENT` - Deployment environment
- `VITE_SENTRY_DSN` - Sentry monitoring (optional)

## Key Features Deployed

✅ **Authentication:**
- Email/password registration and login
- Email verification flow
- JWT token authentication with refresh tokens
- Google OAuth 2.0 integration

✅ **Security:**
- CORS configuration
- Security headers (X-Frame-Options, CSP, etc.)
- JWT token expiration and refresh

✅ **User Experience:**
- SPA routing (no 404 on refresh)
- OAuth callback redirect flow
- Protected routes
- Persistent login state

## Common Workflows

### Deploy Frontend Changes

1. Push changes to `main` branch
2. Render auto-deploys from GitHub
3. Wait 2-3 minutes for build
4. Verify deployment with checklist

### Deploy Backend Changes

1. Push changes to `main` branch
2. Railway auto-deploys from GitHub
3. Check logs: `railway logs`
4. Verify health endpoint

### Update Backend Dependencies

1. Update `pyproject.toml`
2. Regenerate requirements.txt:
   ```bash
   cd backend
   uv pip compile pyproject.toml -o requirements.txt
   git add requirements.txt
   git commit -m "chore: update requirements.txt"
   git push
   ```
3. Railway auto-deploys

### Rollback Deployment

**Render:**
1. Go to service → Deploys tab
2. Find last working deployment
3. Click "Redeploy"

**Railway:**
1. Go to service → Deployments tab
2. Find last working deployment
3. Click "Redeploy"

## Troubleshooting Quick Reference

| Issue | Quick Fix | Documentation |
|-------|-----------|---------------|
| Build fails with TypeScript errors | Update to latest main branch | [TROUBLESHOOTING.md](./TROUBLESHOOTING.md#issue-render-frontend-build-fails-with-typescript-errors) |
| CORS errors | Set `FRONTEND_HOST` in Railway | [TROUBLESHOOTING.md](./TROUBLESHOOTING.md#issue-frontend-blocked-by-cors-policy) |
| 404 on route refresh | Use Blueprint deployment | [RENDER-SPA-ROUTING-FIX.md](./RENDER-SPA-ROUTING-FIX.md) |
| OAuth shows JSON | Update to latest main branch | [TROUBLESHOOTING.md](./TROUBLESHOOTING.md#issue-oauth-callback-shows-json-instead-of-redirecting-to-dashboard) |
| Missing dependencies | Regenerate requirements.txt | [TROUBLESHOOTING.md](./TROUBLESHOOTING.md#issue-railway-backend-build-missing-dependencies) |

## Monitoring & Logs

### View Logs

**Railway:**
```bash
railway logs --limit 50
```

**Render:**
- Dashboard → Service → Logs tab

### Health Checks

**Backend:**
```bash
curl https://ayni-backend-production.up.railway.app/health
```

**Frontend:**
```bash
curl -I https://ayni-frontend.onrender.com
```

### Check Deployment Status

**Railway:**
```bash
railway status
```

**Render:**
- Dashboard → Service → Deploys tab

## Security Considerations

### Production Secrets

Never commit to repository:
- `JWT_SECRET`
- `GOOGLE_OAUTH_CLIENT_SECRET`
- `SENTRY_DSN`
- Database passwords

### HTTPS Enforcement

- ✅ Railway provides HTTPS automatically
- ✅ Render provides HTTPS automatically
- ✅ OAuth requires HTTPS (enforced by Google)

### CORS Configuration

- Backend allows only configured frontend origin
- Preflight requests handled correctly
- Credentials allowed for authenticated requests

## Performance Optimization

### Frontend
- Vite build optimization enabled
- Static assets served via Render CDN
- Gzip compression enabled

### Backend
- Database connection pooling
- Redis caching for OAuth state
- Health check endpoint lightweight

## Future Enhancements

Potential improvements:
- [ ] Custom domains
- [ ] CDN configuration
- [ ] Advanced monitoring with Sentry
- [ ] Rate limiting
- [ ] Database backups configuration
- [ ] Staging environment
- [ ] CI/CD pipeline enhancements

## Support

For issues not covered in this documentation:

1. Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
2. Review [DEPLOYMENT-SUCCESS-CHECKLIST.md](./DEPLOYMENT-SUCCESS-CHECKLIST.md)
3. Check service logs (Railway/Render)
4. Test endpoints with curl
5. Verify environment variables

## Recent Changes

| Date | Change | Commit | Documentation |
|------|--------|--------|---------------|
| 2025-11-14 | OAuth redirect flow | `2c03230` | [TROUBLESHOOTING.md](./TROUBLESHOOTING.md#issue-oauth-callback-shows-json-instead-of-redirecting-to-dashboard) |
| 2025-11-14 | Blueprint deployment | - | [DEPLOY-FROM-BLUEPRINT.md](./DEPLOY-FROM-BLUEPRINT.md) |
| 2025-11-14 | TypeScript fixes | `4e00303` | [TROUBLESHOOTING.md](./TROUBLESHOOTING.md#issue-render-frontend-build-fails-with-typescript-errors) |
| 2025-11-14 | Dependencies fix | `c6f5c90` | [TROUBLESHOOTING.md](./TROUBLESHOOTING.md#issue-railway-backend-build-missing-dependencies) |
