# Google OAuth 2.0 Production Setup Guide

## Railway + Render Deployment Configuration

**Story:** 2.5 - Google OAuth 2.0 Integration
**Date Created:** 2025-11-14
**Status:** Ready for Production Configuration

---

## Prerequisites

✅ Backend deployed to Railway
✅ Frontend deployed to Render
✅ OAuth code implemented and tested locally
✅ Google account for Google Cloud Console

---

## Step 1: Get Your Production URLs

### Railway Backend URL

```bash
# Option 1: Using Railway CLI
cd backend
railway status

# Look for: "Service URL: https://your-service.up.railway.app"

# Option 2: Railway Dashboard
# 1. Go to https://railway.app
# 2. Select your backend service
# 3. Settings → Domains
# 4. Copy the generated domain
```

**Your Railway Backend URL:**
```
https://_________________.up.railway.app
```

### Render Frontend URL

```bash
# From Render Dashboard:
# 1. Go to https://dashboard.render.com
# 2. Select your frontend service
# 3. Copy the URL from the top
```

**Your Render Frontend URL:**
```
https://_________________.onrender.com
```

---

## Step 2: Google Cloud Console Configuration

### A. Create Google Cloud Project

1. **Go to Google Cloud Console**
   - URL: https://console.cloud.google.com
   - Sign in with your Google account

2. **Create a New Project**
   - Click "Select a project" dropdown (top bar)
   - Click "New Project"
   - Project name: `Ayni` (or your preferred name)
   - Click "Create"

3. **Select Your Project**
   - Wait for project creation
   - Select the project from the dropdown

### B. Enable Required APIs

1. **Navigate to APIs & Services**
   - Left menu → "APIs & Services" → "Library"

2. **Enable Google+ API** (or People API)
   - Search: "Google+ API" or "People API"
   - Click on it
   - Click "Enable"

### C. Configure OAuth Consent Screen

1. **Go to OAuth Consent Screen**
   - Left menu → "APIs & Services" → "OAuth consent screen"

2. **Select User Type**
   - Choose "External" (for public app)
   - Click "Create"

3. **Fill in App Information**
   ```
   App name: Ayni
   User support email: your-email@gmail.com
   App logo: (optional - upload 120x120 px logo)
   Application home page: https://your-frontend.onrender.com
   ```

4. **Add Authorized Domains**
   ```
   railway.app
   onrender.com
   ```

5. **Add Scopes**
   - Click "Add or Remove Scopes"
   - Select:
     - ✅ .../auth/userinfo.email
     - ✅ .../auth/userinfo.profile
     - ✅ openid
   - Click "Update"

6. **Add Test Users** (during development)
   - Add your email and any test user emails
   - Click "Save and Continue"

7. **Review and Confirm**
   - Click "Back to Dashboard"

### D. Create OAuth 2.0 Client ID

1. **Navigate to Credentials**
   - Left menu → "APIs & Services" → "Credentials"

2. **Create OAuth Client ID**
   - Click "+ Create Credentials"
   - Select "OAuth 2.0 Client ID"

3. **Configure Web Application**
   ```
   Application type: Web application
   Name: Ayni Production Client
   ```

4. **Add Authorized Redirect URIs**

   **CRITICAL:** Add ALL of these redirect URIs:

   ```
   # Railway production URL
   https://your-backend.up.railway.app/api/v1/auth/google/callback

   # If you have a custom domain
   https://api.ayni.cl/api/v1/auth/google/callback

   # Development (keep for local testing)
   http://localhost:8000/api/v1/auth/google/callback
   ```

   **Replace `your-backend.up.railway.app` with your actual Railway URL!**

5. **Create Client**
   - Click "Create"
   - **SAVE THE CREDENTIALS:**
     ```
     Client ID: xxxxxxxxxxxx-xxxxxxxxxxxxxxxx.apps.googleusercontent.com
     Client Secret: GOCSPX-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
     ```

---

## Step 3: Configure Railway Backend

### A. Set Environment Variables in Railway

1. **Open Railway Dashboard**
   - Go to https://railway.app
   - Select your backend service

2. **Navigate to Variables**
   - Click "Variables" tab

3. **Add OAuth Environment Variables**

   Click "+ New Variable" for each:

   ```bash
   # Google OAuth Configuration
   GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-your-secret-here
   GOOGLE_OAUTH_REDIRECT_URI=https://your-backend.up.railway.app/api/v1/auth/google/callback

   # Frontend URL (for CORS)
   FRONTEND_HOST=https://your-frontend.onrender.com
   ```

4. **Verify Existing Variables**

   Make sure these are already set (from Story 1.5):
   ```bash
   DATABASE_URL=(auto-provided by Railway PostgreSQL)
   REDIS_URL=(auto-provided by Railway Redis)
   JWT_SECRET=your-64-char-secret
   ENVIRONMENT=production
   ```

5. **Save and Redeploy**
   - Railway will automatically redeploy when you save variables

### B. Verify Backend Deployment

```bash
# Check Railway deployment status
railway status

# Check backend logs for OAuth initialization
railway logs

# Look for:
# "Google OAuth client initialized" or similar
```

---

## Step 4: Configure Render Frontend

### A. Set Environment Variables in Render

1. **Open Render Dashboard**
   - Go to https://dashboard.render.com
   - Select your frontend service

2. **Navigate to Environment**
   - Click "Environment" in left sidebar

3. **Add/Update API Base URL**

   ```bash
   Key: VITE_API_BASE_URL
   Value: https://your-backend.up.railway.app/api/v1
   ```

4. **Save Changes**
   - Click "Save Changes"
   - Render will automatically redeploy

---

## Step 5: Test OAuth Flow End-to-End

### A. Basic Connectivity Test

```bash
# Test OAuth authorize endpoint
curl https://your-backend.up.railway.app/api/v1/auth/google/authorize

# Should return JSON with "authorization_url" key
# If you get 503 "not configured" - check Railway environment variables
```

### B. Full OAuth Flow Test

1. **Open Your Frontend**
   - Navigate to: `https://your-frontend.onrender.com/login`

2. **Click "Sign in with Google"**
   - Should redirect to Google consent screen
   - URL should be: `https://accounts.google.com/o/oauth2/auth?...`

3. **Authorize with Google**
   - Select your Google account
   - Click "Allow"

4. **Verify Redirect Chain**
   ```
   Google → Backend callback → Frontend /auth/callback → Dashboard
   ```

5. **Check Backend Logs**
   ```bash
   railway logs --tail 100

   # Look for:
   # "Generated Google OAuth authorization URL with state: ..."
   # "Google OAuth callback for email: your-email@gmail.com"
   # "Google OAuth login successful for: your-email@gmail.com"
   ```

6. **Verify in Database**
   ```bash
   # Connect to Railway PostgreSQL
   railway connect postgres

   # Check OAuth accounts
   SELECT * FROM oauth_accounts ORDER BY created_at DESC LIMIT 5;

   # Should see encrypted tokens
   ```

### C. Test Error Scenarios

1. **Cancel OAuth**
   - Click "Sign in with Google"
   - Click "Cancel" on Google consent screen
   - Should show Spanish error: "Inicio de sesión cancelado"

2. **Invalid State (security test)**
   - Try manually navigating to callback with fake state
   - Should return 400 error: "Invalid or expired state"

3. **Rate Limiting**
   - Make 10+ rapid OAuth requests
   - 11th request should return 429: "Too many OAuth authorization requests"

---

## Step 6: Production Checklist

### Before Going Live

- [ ] **Google Cloud Console**
  - [ ] OAuth consent screen configured
  - [ ] Production redirect URIs added
  - [ ] Test users added (if in testing mode)
  - [ ] Scopes configured (email, profile, openid)

- [ ] **Railway Backend**
  - [ ] GOOGLE_OAUTH_CLIENT_ID set
  - [ ] GOOGLE_OAUTH_CLIENT_SECRET set
  - [ ] GOOGLE_OAUTH_REDIRECT_URI matches Railway URL
  - [ ] FRONTEND_HOST matches Render URL
  - [ ] Backend deployment successful
  - [ ] OAuth endpoints responding (200 OK)

- [ ] **Render Frontend**
  - [ ] VITE_API_BASE_URL points to Railway backend
  - [ ] Frontend deployment successful
  - [ ] OAuth button visible on login page

- [ ] **End-to-End Testing**
  - [ ] OAuth flow completes successfully
  - [ ] User created in database
  - [ ] JWT tokens issued
  - [ ] Redirect to dashboard works
  - [ ] Spanish error messages appear correctly
  - [ ] Rate limiting triggers at 10 requests

- [ ] **Security Verification**
  - [ ] HTTPS enforced on all URLs
  - [ ] OAuth tokens encrypted in database
  - [ ] State parameter validated
  - [ ] CSRF protection working

---

## Troubleshooting

### Issue: "OAuth not configured" (503 error)

**Cause:** Backend environment variables not set

**Fix:**
```bash
# Check Railway variables
railway variables

# Verify these exist:
# GOOGLE_OAUTH_CLIENT_ID
# GOOGLE_OAUTH_CLIENT_SECRET
```

### Issue: "Redirect URI mismatch" error from Google

**Cause:** Railway URL doesn't match Google Cloud Console configuration

**Fix:**
1. Get exact Railway URL: `railway status`
2. Go to Google Cloud Console → Credentials
3. Edit OAuth 2.0 Client ID
4. Add exact redirect URI: `https://exact-url.railway.app/api/v1/auth/google/callback`
5. Save and wait 5 minutes for Google to update

### Issue: "Invalid or expired state" in backend logs

**Cause:** Redis not configured or state expired

**Fix:**
```bash
# Verify Redis is connected
railway logs | grep -i redis

# Check Railway Redis service is linked
railway link
```

### Issue: CORS error when clicking "Sign in with Google"

**Cause:** FRONTEND_HOST not set in Railway

**Fix:**
```bash
# Add to Railway variables:
FRONTEND_HOST=https://your-frontend.onrender.com
```

### Issue: OAuth works locally but not in production

**Checklist:**
1. Railway URL in Google Cloud Console redirect URIs?
2. GOOGLE_OAUTH_REDIRECT_URI matches Railway URL exactly?
3. HTTPS used (not HTTP)?
4. Backend deployment successful? (`railway status`)
5. Frontend API URL correct? (Check browser DevTools → Network tab)

---

## Verification Commands

### Check Railway Backend Status
```bash
railway status
railway logs --tail 50
railway variables
```

### Test OAuth Endpoint
```bash
# Test authorize endpoint
curl -v https://your-backend.up.railway.app/api/v1/auth/google/authorize

# Should return 200 with authorization_url
```

### Check Database OAuth Records
```bash
railway connect postgres

SELECT
  u.email,
  oa.oauth_name,
  oa.account_email,
  oa.created_at
FROM oauth_accounts oa
JOIN users u ON oa.user_id = u.id
ORDER BY oa.created_at DESC;
```

---

## Security Notes

### Production Security Checklist

- ✅ **HTTPS Only:** All URLs use HTTPS (enforced by Railway/Render)
- ✅ **Token Encryption:** OAuth tokens encrypted before database storage
- ✅ **State Parameter:** CSRF protection via Redis (5-min TTL)
- ✅ **Rate Limiting:** 10 requests per minute per IP
- ✅ **Secret Management:** Secrets in Railway environment variables (not in code)
- ✅ **OAuth Scope Minimal:** Only email, profile, openid (no excessive permissions)

### After Configuration

**DO NOT:**
- ❌ Commit OAuth secrets to Git
- ❌ Share OAuth credentials publicly
- ❌ Use same credentials for dev and production
- ❌ Disable HTTPS in production

**DO:**
- ✅ Rotate secrets regularly (quarterly)
- ✅ Monitor OAuth login attempts (Sentry)
- ✅ Keep Google Cloud Console access restricted
- ✅ Test OAuth flow after any backend URL change

---

## Next Steps After OAuth Setup

1. **Monitor Usage**
   - Check Railway logs for OAuth activity
   - Monitor Sentry for OAuth errors
   - Review Google Cloud Console quotas

2. **Consider Enhancements**
   - Add more OAuth providers (GitHub, Facebook)
   - Implement OAuth token refresh background job
   - Add account disconnection UI in settings

3. **Documentation**
   - Document OAuth setup in team wiki
   - Update onboarding docs for new developers
   - Create runbook for OAuth troubleshooting

---

## Support Resources

- **Google OAuth Documentation:** https://developers.google.com/identity/protocols/oauth2
- **Railway Documentation:** https://docs.railway.app
- **Render Documentation:** https://render.com/docs
- **Story 2.5 Implementation:** [Backend OAuth Code](../../backend/app/core/oauth.py)

---

**Configuration Status:** ⚠️ PENDING - Complete steps 1-6 above

**Last Updated:** 2025-11-14
**Configured By:** _________________
**Production URL:** https://_________________.onrender.com
