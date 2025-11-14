# Fixing SPA Routing on Render

## Problem

When visiting routes like `/login` or `/dashboard` directly or refreshing the page, Render returns a 404 "Not Found" error instead of serving the React app.

## Root Cause

Render's static site serving tries to find physical files at these paths. Since React Router handles routing client-side, these files don't exist, causing 404 errors.

## Solution

The `_redirects` file approach works for Render **only when the service is created from a `render.yaml` blueprint**. Since this service was created via the API/Dashboard, you need to manually configure routing rules.

### Option 1: Configure Routes via Render Dashboard (Recommended)

1. Go to https://dashboard.render.com
2. Select the `ayni-frontend` static site
3. Click "Redirects/Rewrites" tab
4. Add a new rewrite rule:
   - **Source**: `/*`
   - **Destination**: `/index.html`
   - **Action**: `Rewrite`
   - **Status Code**: `200`
5. Click "Save Changes"
6. Render will automatically redeploy

### Option 2: Recreate Service from render.yaml

The `render.yaml` file in the repository root already has the correct routing configuration:

```yaml
routes:
  - type: rewrite
    source: /*
    destination: /index.html
```

To use it:

1. Delete the current `ayni-frontend` service from Render Dashboard
2. Create a new Static Site from the Render Dashboard
3. Connect to the GitHub repository
4. Select "Apply render.yaml"
5. Render will use the configuration from the file

**Advantages:**
- Routes are defined in version control
- Easier to replicate/troubleshoot
- Blueprint-based deployments are more maintainable

**Disadvantages:**
- Need to recreate the service
- May need to update environment variables again

### Option 3: Use Netlify-style _redirects (Not Working Currently)

The `_redirects` file exists in `frontend/public/_redirects`:
```
/* /index.html 200
```

This file should work for Render static sites, but only when using Blueprint-based deployments. For API/Dashboard-created services, it's ignored.

## Verification

After applying the fix:

```bash
# Test /login route
curl -I https://ayni-frontend.onrender.com/login

# Should return:
# HTTP/2 200 (not 404)
# content-type: text/html
```

Visit https://ayni-frontend.onrender.com/login in your browser and refresh - should load the login page.

## Related Issues

- Dashboard also shows 404: Same root cause, fixed by the same solution
- OAuth callback 404: Same issue, configure routes as described above

## Current Status

- ✅ `_redirects` file exists in repository
- ✅ File is included in dist build
- ✅ Service deployed using render.yaml blueprint
- ✅ Routes configured automatically via blueprint

**Status:** ✅ RESOLVED - Service is now deployed using Blueprint (Option 2), which automatically configures SPA routing from `render.yaml`.

## Resolution

The service was successfully migrated to Blueprint-based deployment, which automatically applies the routing configuration from `render.yaml`:

```yaml
routes:
  - type: rewrite
    source: /*
    destination: /index.html
```

All routes now work correctly, including:
- Direct navigation to `/login`, `/dashboard`, etc.
- Page refresh on any route
- OAuth callback at `/auth/callback`

**Deployment Method:** Blueprint via https://dashboard.render.com/blueprints

**Verification:**
```bash
curl -I https://ayni-frontend.onrender.com/login
# Returns: HTTP/2 200
```
