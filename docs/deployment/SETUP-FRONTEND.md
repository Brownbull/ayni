# Frontend Deployment Setup - Render

Complete guide for deploying the Ayni React frontend to Render using Blueprint configuration.

## Prerequisites

- Render account connected to GitHub
- GitHub repository with Ayni code
- Backend deployed to Railway (see [SETUP-BACKEND.md](./SETUP-BACKEND.md))

## Quick Setup (5 minutes)

### 1. Deploy from Blueprint

**Go to Render Blueprints:**
https://dashboard.render.com/blueprints

**Click "New Blueprint Instance"**

**Connect Repository:**
1. If first time: Click "Connect GitHub" and authorize Render
2. Select repository: `Brownbull/ayni` (or your fork)
3. Render will detect `render.yaml` in repository root

**Configure Blueprint:**
- Blueprint Name: `ayni-frontend` (or custom name)
- Branch: `main`

**Set Environment Variable:**
- Only `VITE_SENTRY_DSN` needs to be provided manually
- Other variables (`VITE_API_URL`, `VITE_ENVIRONMENT`) are set in `render.yaml`
- Leave `VITE_SENTRY_DSN` blank if not using Sentry

**Click "Deploy Blueprint"**

Render will:
1. Clone repository
2. Run build command
3. Deploy to public URL
4. Configure SPA routing automatically

### 2. Wait for Deployment

Build typically takes 2-3 minutes.

Watch for:
```
==> Build successful 🎉
==> Deploying...
==> Your site is live at https://ayni-frontend.onrender.com
```

### 3. Get Your Frontend URL

Your frontend URL will be: `https://ayni-frontend.onrender.com`

Or custom name: `https://your-service-name.onrender.com`

### 4. Update Backend CORS Configuration

Add your frontend URL to Railway backend:

```bash
# Via Railway CLI
railway variables --set FRONTEND_HOST=https://ayni-frontend.onrender.com

# Or via Railway Dashboard → Backend Service → Variables
```

Railway will auto-redeploy to apply CORS configuration.

---

## What Blueprint Does

The `render.yaml` file in repository root configures:

### Build Configuration
```yaml
buildCommand: cd frontend && npm install --legacy-peer-deps && npm run build
staticPublishPath: frontend/dist
```

### Environment Variables
```yaml
VITE_API_URL: https://ayni-backend-production.up.railway.app/api/v1
VITE_ENVIRONMENT: production
VITE_SENTRY_DSN: (set during deployment)
```

### Security Headers
```yaml
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

### SPA Routing
```yaml
routes:
  - type: rewrite
    source: /*
    destination: /index.html
```

This ensures `/login`, `/dashboard`, etc. work on direct navigation and page refresh.

---

## Manual Configuration (Not Recommended)

If you prefer manual setup instead of Blueprint:

### 1. Create New Static Site

1. Go to https://dashboard.render.com
2. Click "New +" → "Static Site"
3. Connect to GitHub repository
4. Configure:
   - Name: `ayni-frontend`
   - Branch: `main`
   - Root Directory: (leave empty)
   - Build Command: `cd frontend && npm install --legacy-peer-deps && npm run build`
   - Publish Directory: `frontend/dist`

### 2. Set Environment Variables

Go to Environment tab:
```bash
VITE_API_URL=https://your-backend.up.railway.app/api/v1
VITE_ENVIRONMENT=production
VITE_SENTRY_DSN=(optional)
```

### 3. Configure SPA Routing

**Go to Redirects/Rewrites tab:**
- Source: `/*`
- Destination: `/index.html`
- Action: `Rewrite`
- Status Code: `200`

**IMPORTANT:** Without this, routes will show 404 on page refresh.

---

## Environment Variables Reference

### Set in render.yaml (Automatic)

| Variable | Value | Description |
|----------|-------|-------------|
| `VITE_API_URL` | `https://ayni-backend-production.up.railway.app/api/v1` | Backend API base URL |
| `VITE_ENVIRONMENT` | `production` | Deployment environment |

### Set During Blueprint Deployment

| Variable | Example | Description |
|----------|---------|-------------|
| `VITE_SENTRY_DSN` | `https://xxx@sentry.io/xxx` | Sentry error tracking (optional) |

### How to Update Variables

**Via Render Dashboard:**
1. Go to service → Environment tab
2. Edit or add variable
3. Click "Save Changes"
4. Render will auto-redeploy

**Note:** Variables set in `render.yaml` cannot be edited in Dashboard. To change them, update `render.yaml` and push to GitHub.

---

## Verification Checklist

After deployment, verify:

- [ ] Frontend URL is accessible
- [ ] Home page loads (redirects to `/login`)
- [ ] Login page loads at `/login`
- [ ] Page refresh on `/login` doesn't show 404
- [ ] "Sign in with Google" button visible
- [ ] Registration form accessible at `/register`
- [ ] Browser console shows no CORS errors
- [ ] API calls reach backend (check Network tab)

**Test Commands:**
```bash
# Homepage loads
curl -I https://ayni-frontend.onrender.com

# SPA routing works (no 404)
curl -I https://ayni-frontend.onrender.com/login
curl -I https://ayni-frontend.onrender.com/dashboard

# All should return HTTP/2 200
```

---

## Testing End-to-End Flow

### 1. Email Registration

1. Visit: `https://ayni-frontend.onrender.com`
2. Click "Registrarse"
3. Fill in form with valid email
4. Submit
5. Check email for verification link
6. Click verification link
7. Log in with credentials

✅ Should redirect to dashboard

### 2. Email Login

1. Visit: `https://ayni-frontend.onrender.com/login`
2. Enter email and password
3. Click "Iniciar sesión"

✅ Should redirect to dashboard
✅ User profile should load

### 3. Google OAuth Login

1. Visit: `https://ayni-frontend.onrender.com/login`
2. Click "Continuar con Google"
3. Select Google account
4. Authorize

✅ Should redirect to Google consent screen
✅ After authorization, should redirect to dashboard (NOT show JSON)
✅ User profile should load

### 4. Protected Routes

**Without logging in:**
1. Visit: `https://ayni-frontend.onrender.com/dashboard`

✅ Should redirect to `/login`

**After logging in:**
1. Navigate to dashboard
2. Refresh page (Ctrl+F5)

✅ Should stay on dashboard (not 404)
✅ Should stay logged in

---

## SPA Routing Explained

### The Problem

Traditional static site hosting treats routes as file paths:
- `/login` → looks for `login.html`
- `/dashboard` → looks for `dashboard.html`

Since these files don't exist (React Router handles routing), server returns 404.

### The Solution

Blueprint configures rewrite rule:
```yaml
routes:
  - type: rewrite
    source: /*
    destination: /index.html
```

**How it works:**
1. User visits `/login`
2. Render serves `index.html` (HTTP 200)
3. React loads and React Router handles `/login` route
4. Login page renders client-side

**Result:** All routes work on direct navigation and page refresh.

---

## Custom Domain (Optional)

### 1. Add Custom Domain in Render

1. Go to service → Settings → Custom Domain
2. Click "Add Custom Domain"
3. Enter your domain: `app.ayni.cl`
4. Render provides DNS instructions

### 2. Configure DNS

Add DNS records at your domain registrar:

**For root domain (ayni.cl):**
```
Type: A
Name: @
Value: 216.24.57.1 (Render's IP)
```

**For subdomain (app.ayni.cl):**
```
Type: CNAME
Name: app
Value: ayni-frontend.onrender.com
```

### 3. Update Backend CORS

Update `FRONTEND_HOST` in Railway:
```bash
FRONTEND_HOST=https://app.ayni.cl
```

### 4. Update OAuth Redirect

If using custom domain for backend too:
1. Update Google Cloud Console redirect URIs
2. Update Railway OAuth variables

---

## Monitoring & Logs

### View Build Logs

**Render Dashboard:**
1. Go to service
2. Click "Events" tab
3. Select deployment
4. View build logs

### View Runtime Logs

Static sites don't have runtime logs (pre-rendered HTML/JS/CSS).

For client-side errors, use:
- Browser console
- Sentry (if configured)

### Check Deployment Status

**Render Dashboard:**
- Green dot = Live
- Orange dot = Deploying
- Red dot = Failed

Click on service to see deployment history.

---

## Rollback

If deployment breaks:

1. Go to service → "Deploys" tab
2. Find last working deployment
3. Click "Redeploy"

Render will restore that version immediately.

---

## Auto-Deploy Configuration

**Enabled by default for Blueprint deployments.**

**How it works:**
1. Push commit to `main` branch
2. Render detects change
3. Triggers new build
4. Deploys if build succeeds

**To disable:**
1. Go to service → Settings
2. Scroll to "Deploy"
3. Toggle "Auto-Deploy"

---

## Build Command Explained

```bash
cd frontend && npm install --legacy-peer-deps && npm run build
```

**Breakdown:**
- `cd frontend` - Enter frontend directory
- `npm install --legacy-peer-deps` - Install dependencies (handles peer dependency conflicts)
- `npm run build` - Run Vite build (outputs to `dist/`)

**Build output:** `frontend/dist/`
- `index.html` - Entry point
- `assets/` - Bundled JS, CSS, images

---

## Production URLs

After setup, save these URLs:

**Frontend:** `https://_________________.onrender.com`
**Login:** `https://_________________.onrender.com/login`
**Dashboard:** `https://_________________.onrender.com/dashboard`
**OAuth Callback:** `https://_________________.onrender.com/auth/callback`

---

## Next Steps

1. ✅ Frontend deployed and accessible
2. → Test authentication flows (email + OAuth)
3. → Set up monitoring (Sentry)
4. → Configure custom domain (optional)
5. → Run deployment success checklist (see [DEPLOYMENT-SUCCESS-CHECKLIST.md](./DEPLOYMENT-SUCCESS-CHECKLIST.md))

---

## Common Commands

There are no CLI commands for Render static sites. All management is via Dashboard:

- View logs: Dashboard → Service → Events
- Trigger deploy: Dashboard → Service → Manual Deploy
- Update variables: Dashboard → Service → Environment
- Configure routing: Dashboard → Service → Redirects/Rewrites

---

## render.yaml Reference

Location: `/render.yaml` (repository root)

```yaml
services:
  - type: web
    name: ayni-frontend
    env: static
    buildCommand: cd frontend && npm install --legacy-peer-deps && npm run build
    staticPublishPath: frontend/dist
    envVars:
      - key: VITE_API_URL
        value: https://ayni-backend-production.up.railway.app/api/v1
      - key: VITE_ENVIRONMENT
        value: production
      - key: VITE_SENTRY_DSN
        sync: false  # Must be set during Blueprint deployment
    headers:
      - path: /*
        name: X-Frame-Options
        value: DENY
      - path: /*
        name: X-Content-Type-Options
        value: nosniff
      - path: /*
        name: Referrer-Policy
        value: strict-origin-when-cross-origin
      - path: /*
        name: Permissions-Policy
        value: geolocation=(), microphone=(), camera=()
    routes:
      - type: rewrite
        source: /*
        destination: /index.html
```

**To update:**
1. Edit `render.yaml` in repository
2. Commit and push to GitHub
3. Render will detect changes and redeploy

---

## Support

For issues, see [TROUBLESHOOTING-FRONTEND.md](./TROUBLESHOOTING-FRONTEND.md)
