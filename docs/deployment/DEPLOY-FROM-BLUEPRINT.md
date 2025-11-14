# Deploy Ayni Frontend from Blueprint

This guide walks you through deploying the Ayni frontend to Render using the `render.yaml` blueprint.

## Why Use Blueprint Deployment?

✅ **Configuration in version control** - All settings defined in render.yaml
✅ **Automatic routing setup** - SPA routes configured automatically
✅ **Easier to replicate** - Redeploy anytime from the same config
✅ **Environment variables preset** - No manual configuration needed
✅ **Security headers included** - X-Frame-Options, CSP, etc.

## Prerequisites

- ✅ GitHub repository with latest code (commit `e5f713d` or later)
- ✅ Render account connected to GitHub
- ✅ Railway backend deployed and running

## Step-by-Step Deployment

### 1. Go to Render Blueprints

Visit https://dashboard.render.com/blueprints

### 2. Create New Blueprint Instance

Click **"New Blueprint Instance"**

### 3. Connect Repository

- If this is your first time:
  - Click **"Connect GitHub"** or **"Connect GitLab"**
  - Authorize Render to access your repositories
- Select **"Brownbull/ayni"** from the repository list
- If not listed, click **"Configure account"** to grant access

### 4. Configure Blueprint

Render will detect `render.yaml` in the repository root and show:

**Blueprint Name:**
- Default: `bp-ayni-frontend`
- You can keep this or rename it

**Branch:**
- Default: `main`
- This is the branch containing your `render.yaml` file

**Review Configuration:**
Render will display: *"You are deploying from a render.yaml for Brownbull/ayni"*

You'll see:
- **Service Type**: static site
- **Service Name**: ayni-frontend (from render.yaml)

### 5. Set Environment Variables

Under **"Specified configurations"**, you'll see:

**VITE_SENTRY_DSN** (marked as `sync: false` in render.yaml)
- This is the only variable you need to provide manually
- The other variables (`VITE_API_URL`, `VITE_ENVIRONMENT`) are already set in render.yaml
- Enter your Sentry DSN or leave blank if not using Sentry

**Note:** The blueprint only asks for variables marked as `sync: false`. Variables with hardcoded values in render.yaml are applied automatically.

### 6. Deploy Blueprint

Click **"Deploy Blueprint"**

Render will:
1. Clone the repository
2. Run the build command
3. Deploy to a public URL
4. Configure routing automatically

### 7. Wait for Deployment

Watch the build logs. The deployment typically takes 2-3 minutes.

Look for:
```
==> Build successful 🎉
==> Deploying...
==> Your site is live at https://ayni-frontend.onrender.com
```

### 8. Verify Deployment

Test the following:

**1. Home page loads:**
```bash
curl -I https://ayni-frontend.onrender.com
# Should return HTTP/2 200
```

**2. SPA routing works:**
```bash
curl -I https://ayni-frontend.onrender.com/login
# Should return HTTP/2 200 (not 404!)
```

**3. Test in browser:**
- Visit https://ayni-frontend.onrender.com
- Should redirect to `/login`
- Try refreshing on `/login` - should stay on login page
- Click "Sign in with Google" - should redirect to Google OAuth

## Troubleshooting

### Build Fails with TypeScript Errors

**Error:** `'FormEvent' is a type and must be imported using a type-only import`

**Solution:** Already fixed in commit `4e00303`. Make sure you're deploying from the latest `main` branch.

### Environment Variable Not Set

**Symptom:** API calls fail with network errors

**Solution:**
1. Go to service → Environment tab
2. Verify `VITE_API_URL` is set to Railway backend URL
3. Trigger a redeploy if you made changes

### Routes Still Return 404

**Symptom:** Refreshing `/login` or `/dashboard` shows "Not Found"

**Cause:** Blueprint wasn't applied correctly

**Solution:**
1. Check service → Redirects/Rewrites tab
2. Should see: `/*` → `/index.html` (rewrite)
3. If missing, add it manually or recreate service

### OAuth Callback Shows JSON Token

**Symptom:** After Google login, see raw JSON instead of dashboard

**Possible causes:**
1. OAuth callback route not configured (should be fixed by blueprint)
2. Frontend routing issue
3. OAuth callback component not working

**Debug steps:**
1. Check browser console for errors
2. Verify `/auth/callback` route loads index.html
3. Check if OAuthCallback component is rendering

## Post-Deployment Configuration

### Optional: Custom Domain

1. Go to service → Settings
2. Click "Add Custom Domain"
3. Follow DNS configuration instructions

### Optional: Configure Sentry

1. Get Sentry DSN from https://sentry.io
2. Add to service → Environment:
   - Key: `VITE_SENTRY_DSN`
   - Value: `https://...@sentry.io/...`
3. Redeploy

## URLs Reference

**Production URLs:**
- Frontend: https://ayni-frontend.onrender.com
- Backend API: https://ayni-backend-production.up.railway.app
- Backend Health: https://ayni-backend-production.up.railway.app/health

**OAuth Redirect URI:**
```
https://ayni-backend-production.up.railway.app/api/v1/auth/google/callback
```

## Next Steps

After successful deployment:

1. ✅ Test login with email/password
2. ✅ Test Google OAuth login (after configuring credentials)
3. ✅ Test email verification flow
4. ✅ Test dashboard access
5. ✅ Configure monitoring (Sentry)
6. ✅ Set up custom domain (optional)

## Rollback

If you need to rollback to a previous version:

1. Go to service → Deploys tab
2. Find the working deployment
3. Click "Redeploy" on that version

## Support

If you encounter issues:

1. Check build logs in Render Dashboard
2. Review [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
3. Verify environment variables match expected values
4. Test endpoints directly with curl

## Blueprint File Location

The blueprint configuration is in the repository at:
```
/render.yaml
```

Any changes to this file will be applied on the next deployment (for blueprint-based services).
