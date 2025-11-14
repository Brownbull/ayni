# Frontend Troubleshooting - Render

Common issues and solutions for the Ayni React frontend deployed on Render.

## Quick Diagnosis

**Check Render Dashboard:**
- Service status (Live/Deploying/Failed)
- Build logs
- Recent deployments

**Test Frontend:**
```bash
# Homepage loads
curl -I https://ayni-frontend.onrender.com

# Routes work (no 404)
curl -I https://ayni-frontend.onrender.com/login
curl -I https://ayni-frontend.onrender.com/dashboard

# Check browser console for errors
```

---

## Build Issues

### Issue: Build Fails with TypeScript Errors

**Symptom:**
```
error TS1484: 'FormEvent' is a type and must be imported using a type-only
import when 'verbatimModuleSyntax' is enabled.
```

**Root Cause:**
TypeScript's `verbatimModuleSyntax` requires type-only imports.

**Solution:**
Update imports to use `type` keyword:

```typescript
// WRONG:
import { useState, FormEvent } from 'react'

// CORRECT:
import { useState, type FormEvent } from 'react'
```

**Fixed in commit:** `4e00303`

**Prevention:**
Always use type-only imports for types:
```typescript
import { type ComponentType, type FC } from 'react'
```

---

### Issue: Build Fails - npm install Errors

**Symptom:**
```
npm ERR! Could not resolve dependency
npm ERR! peer dependency conflicts
```

**Root Cause:**
Peer dependency conflicts in npm.

**Solution:**
Build command uses `--legacy-peer-deps` flag (already configured in render.yaml):

```yaml
buildCommand: cd frontend && npm install --legacy-peer-deps && npm run build
```

If still failing:
1. Check Render build logs for specific error
2. Update package versions locally and test
3. Commit fixed package.json/package-lock.json
4. Push to trigger redeploy

---

### Issue: Build Succeeds but Site is Blank

**Symptom:**
- Build shows success
- Site loads but shows white/blank page
- Browser console shows errors

**Root Cause:**
- JavaScript errors preventing React from rendering
- Incorrect base path in Vite config
- Missing environment variables

**Solution:**

**1. Check browser console:**
Open DevTools (F12) → Console tab for errors

**2. Check environment variables:**
```bash
# Verify VITE_API_URL is set correctly
# Dashboard → Service → Environment
```

**3. Check network requests:**
DevTools → Network tab → Look for failed requests

**4. Verify build output:**
Check build logs for warnings about missing assets

---

## Routing Issues

### Issue: 404 on Page Refresh

**Symptom:**
- Navigating to `/login` works initially
- Refreshing page shows "Not Found"
- Works fine on localhost

**Root Cause:**
SPA routing not configured in Render.

**Solution (Already Applied via Blueprint):**
Blueprint deployment automatically configures routing from `render.yaml`:

```yaml
routes:
  - type: rewrite
    source: /*
    destination: /index.html
```

**If manually deployed (not Blueprint):**
1. Go to Render Dashboard → Service → Redirects/Rewrites
2. Add rewrite rule:
   - Source: `/*`
   - Destination: `/index.html`
   - Action: `Rewrite`
   - Status Code: `200`
3. Save changes

**Verification:**
```bash
curl -I https://ayni-frontend.onrender.com/login

# Should return HTTP/2 200 (not 404)
```

**Fixed via:** Blueprint deployment

---

### Issue: OAuth Callback Shows 404

**Symptom:**
After Google login, redirect to `/auth/callback` shows "Not Found".

**Root Cause:**
Same as above - SPA routing not configured.

**Solution:**
Ensure Blueprint deployment or manual routing configuration applied (see above).

---

## API Connection Issues

### Issue: API Requests Fail - Network Error

**Symptom:**
```
Failed to fetch
Network error
ERR_CONNECTION_REFUSED
```

**Root Cause:**
- Backend URL incorrect or backend is down
- CORS not configured on backend

**Solution:**

**1. Verify API URL:**
```bash
# Check environment variable
# Dashboard → Service → Environment → VITE_API_URL

# Should be:
VITE_API_URL=https://ayni-backend-production.up.railway.app/api/v1
```

**2. Test backend is reachable:**
```bash
curl https://ayni-backend-production.up.railway.app/health

# Should return JSON with "status": "healthy"
```

**3. Check backend CORS:**
```bash
curl -X OPTIONS https://ayni-backend-production.up.railway.app/api/v1/health \
  -H "Origin: https://ayni-frontend.onrender.com" \
  -H "Access-Control-Request-Method: GET" \
  -i

# Should include:
# access-control-allow-origin: https://ayni-frontend.onrender.com
```

**4. If CORS missing:**
Add to Railway backend:
```bash
FRONTEND_HOST=https://ayni-frontend.onrender.com
```

---

### Issue: CORS Error in Browser Console

**Symptom:**
```
Access to fetch at 'https://...' from origin 'https://ayni-frontend.onrender.com'
has been blocked by CORS policy
```

**Root Cause:**
Backend `FRONTEND_HOST` not set or incorrect.

**Solution:**
Set in Railway backend (see [TROUBLESHOOTING-BACKEND.md](./TROUBLESHOOTING-BACKEND.md#cors-issues))

---

## OAuth Issues

### Issue: OAuth Shows JSON Instead of Redirecting to Dashboard

**Symptom:**
After Google login, browser shows raw JSON with access token.

**Root Cause:**
This was a backend issue, now fixed. Backend should redirect to frontend.

**Verification:**
OAuth flow should be:
1. Click "Sign in with Google"
2. Redirect to Google consent screen
3. After authorization → Backend callback
4. Backend redirects to frontend `/auth/callback?access_token=...`
5. Frontend extracts tokens and redirects to `/dashboard`

**If still seeing JSON:**
1. Check backend is latest version (commit `2c03230` or later)
2. Check backend logs for OAuth callback
3. Verify backend FRONTEND_HOST is set

**Fixed in commit:** `2c03230`

---

### Issue: OAuth Callback Infinite Loading

**Symptom:**
After Google login, redirect to frontend `/auth/callback` but shows loading spinner forever.

**Root Cause:**
- `OAuthCallback.tsx` component error
- Tokens not in URL parameters
- `useAuth` hook not working

**Debug:**

**1. Check browser console for errors:**
F12 → Console tab

**2. Check URL has tokens:**
Should be: `/auth/callback?access_token=...&refresh_token=...`

**3. Check Network tab:**
F12 → Network → Look for failed user profile request

**4. Check localStorage:**
F12 → Application → Local Storage → Tokens should be stored

---

## Environment Variables Issues

### Issue: Environment Variables Not Applied

**Symptom:**
Changed `VITE_API_URL` but frontend still uses old URL.

**Root Cause:**
Vite bakes environment variables into build at build time.

**Solution:**
Trigger new deployment after changing variables:

**Via Render Dashboard:**
1. Change variable
2. Click "Save Changes"
3. Render auto-deploys

**Or manually trigger:**
1. Dashboard → Service → Manual Deploy
2. Click "Deploy latest commit"

**Verification:**
Check browser DevTools → Network tab → API requests should use new URL.

---

### Issue: VITE_API_URL Has Wrong Value

**Symptom:**
API calls go to wrong URL.

**Solution:**
Check and update in Render:

**Via Dashboard:**
1. Service → Environment
2. Check `VITE_API_URL` value
3. Should be: `https://ayni-backend-production.up.railway.app/api/v1`
4. No trailing slash!

**Via render.yaml (Blueprint):**
```yaml
envVars:
  - key: VITE_API_URL
    value: https://ayni-backend-production.up.railway.app/api/v1
```

---

## Authentication Issues

### Issue: Can't Login - Credentials Correct

**Symptom:**
Enter valid email/password but login fails.

**Root Cause:**
Backend issue, not frontend.

**Debug:**
1. F12 → Network tab
2. Look at login request response
3. Check status code and error message

**Common backend issues:**
- 500: Backend error (check Railway logs)
- 401: Invalid credentials
- 403: Email not verified
- 429: Rate limited

---

### Issue: Login Succeeds but Redirects to Login Again

**Symptom:**
Login returns success, but immediately redirects back to `/login`.

**Root Cause:**
- Tokens not being stored in localStorage
- Protected route auth check failing
- User profile request failing

**Debug:**

**1. Check localStorage:**
F12 → Application → Local Storage
Should have: `access_token`, `refresh_token`

**2. Check user profile request:**
F12 → Network → Look for `/users/me` request
Should return user data

**3. Check auth hook:**
Console → `useAuth.getState().user` should have user data

---

### Issue: Logged In but Shows as Logged Out After Refresh

**Symptom:**
Login successful, but refreshing page shows login screen again.

**Root Cause:**
- Tokens not persisting in localStorage
- Token validation failing
- Auth state not rehydrating

**Debug:**

**1. Check localStorage persists:**
Login → Check localStorage → Refresh → Check localStorage again
Tokens should still be there

**2. Check token validation:**
F12 → Network → Look for failed `/users/me` request after refresh

**3. Check auth initialization:**
Look for auth hook initialization in console logs

---

## Performance Issues

### Issue: Slow Initial Load

**Symptom:**
First page load takes 5+ seconds.

**Possible Causes:**
1. Large bundle size
2. Render cold start
3. Backend cold start (Railway)

**Solutions:**

**1. Check bundle size:**
Build logs show chunk sizes - look for large chunks

**2. Code splitting:**
Lazy load routes:
```typescript
const Dashboard = lazy(() => import('./pages/Dashboard'))
```

**3. Free tier cold starts:**
Both Render and Railway free tiers spin down after inactivity
- Upgrade to paid tier for always-on
- Or accept 30-second initial load

---

### Issue: Slow Subsequent Navigation

**Symptom:**
First load fine, but navigating between pages is slow.

**Root Cause:**
- API requests slow
- Large data fetching on each page
- No caching

**Debug:**
F12 → Network → Check API request times

**Solutions:**
- Add loading states
- Implement caching (React Query)
- Optimize API responses (backend)

---

## Deployment Issues

### Issue: Deployment Stuck at "Build Running"

**Symptom:**
Build takes 10+ minutes or hangs.

**Solution:**
1. Check Render status page: https://status.render.com
2. Cancel and retry deployment:
   - Dashboard → Service → Cancel Deploy
   - Click "Manual Deploy"

---

### Issue: Deploy Succeeds but Old Version Shows

**Symptom:**
Deployed new version but browser shows old UI.

**Root Cause:**
Browser cache.

**Solution:**

**1. Hard refresh:**
- Chrome/Firefox: Ctrl+Shift+R
- Mac: Cmd+Shift+R

**2. Clear cache:**
F12 → Network → Disable cache (checkbox)

**3. Verify deployment:**
Check Render Dashboard → Service → Deploys
Ensure latest commit is "Live"

---

## Browser-Specific Issues

### Issue: Works in Chrome but Not Safari/Firefox

**Symptom:**
Site works fine in Chrome but broken in other browsers.

**Root Cause:**
- Using unsupported JavaScript features
- Browser-specific CSS issues
- Different CORS handling

**Debug:**
1. Open browser DevTools
2. Check Console for errors
3. Check Network tab for failed requests

**Solution:**
- Use polyfills for unsupported features
- Test in multiple browsers before deploying
- Use autoprefixer for CSS

---

## Monitoring & Debugging

### View Build Logs

**Render Dashboard:**
1. Go to Service
2. Click "Events" tab
3. Select deployment
4. View build logs

**Look for:**
- TypeScript errors
- Build warnings
- Failed dependencies
- Successful build confirmation

---

### Browser DevTools Debugging

**Console (F12 → Console):**
- JavaScript errors
- API response errors
- React warnings

**Network (F12 → Network):**
- Failed API requests
- Status codes
- Response payloads
- Request headers (check CORS)

**Application (F12 → Application):**
- localStorage tokens
- Session storage
- Cookies

**Sources (F12 → Sources):**
- Set breakpoints
- Step through code
- Inspect variables

---

## Rollback

If deployment breaks:

**Via Render Dashboard:**
1. Service → Deploys tab
2. Find last working deployment
3. Click "Redeploy"

Render restores that version immediately.

---

## Common Error Messages

### "Failed to fetch"

**Cause:** Backend unreachable or CORS issue
**Fix:** Check backend URL and CORS configuration

### "Network request failed"

**Cause:** Backend down or network issue
**Fix:** Test backend health endpoint

### "Unexpected token '<' in JSON"

**Cause:** API returned HTML (likely 404) instead of JSON
**Fix:** Check API endpoint URL is correct

### "Cannot read property 'user' of undefined"

**Cause:** Auth state not initialized
**Fix:** Check auth hook initialization

### "Access denied"

**Cause:** Missing authentication token or invalid token
**Fix:** Check localStorage has valid tokens

---

## Emergency Debugging Checklist

When something breaks:

1. [ ] Check Render deployment status (Live/Failed?)
2. [ ] Open browser DevTools → Console (any errors?)
3. [ ] Check Network tab (failed requests?)
4. [ ] Verify environment variables (correct API URL?)
5. [ ] Test backend health endpoint (backend up?)
6. [ ] Check backend CORS (FRONTEND_HOST set?)
7. [ ] Try hard refresh (Ctrl+Shift+R)
8. [ ] Check localStorage (tokens present?)
9. [ ] Review recent code changes
10. [ ] Try rollback to last working version

---

## Most Common Issues (Quick Reference)

| Issue | Quick Fix |
|-------|-----------|
| 404 on refresh | Configure SPA routing (Blueprint auto-fixes) |
| TypeScript build error | Use type-only imports |
| CORS error | Set FRONTEND_HOST in Railway backend |
| Blank page | Check browser console for errors |
| API requests fail | Verify VITE_API_URL is correct |
| OAuth shows JSON | Update backend to latest version |
| Can't login | Check backend health and logs |
| Slow initial load | Free tier cold start (expected) |
| Old version shows | Hard refresh (Ctrl+Shift+R) |
| Environment vars not applied | Redeploy after changing variables |

---

## Support Resources

- **Render Documentation:** https://render.com/docs
- **Render Status:** https://status.render.com
- **Render Community:** https://community.render.com
- **Ayni Setup Guide:** [SETUP-FRONTEND.md](./SETUP-FRONTEND.md)
- **Backend Issues:** [TROUBLESHOOTING-BACKEND.md](./TROUBLESHOOTING-BACKEND.md)
