# Google OAuth 2.0 Setup Guide - Local Development

This guide walks you through setting up Google OAuth 2.0 authentication for local development of the Ayni application.

## Prerequisites

- Google Account
- Backend running on `http://localhost:8000`
- Frontend running on `http://localhost:5173`

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click "Select a project" → "New Project"
3. Enter project name (e.g., "Ayni Local Dev")
4. Click "Create"
5. Wait for project creation to complete and select the new project

## Step 2: Enable Required APIs

1. In the Google Cloud Console, go to "APIs & Services" → "Library"
2. Search for and enable the following APIs:
   - **Google+ API** (or **People API** for newer projects)
   - This is required to access user profile information (email, name)

## Step 3: Configure OAuth Consent Screen

1. Go to "APIs & Services" → "OAuth consent screen"
2. Select **External** user type (for testing with personal Google accounts)
3. Click "Create"
4. Fill in the required fields:
   - **App name**: Ayni (or your preferred name)
   - **User support email**: Your email address
   - **Developer contact information**: Your email address
5. Click "Save and Continue"
6. **Scopes** page:
   - Click "Add or Remove Scopes"
   - Add these scopes (they should be pre-selected):
     - `openid`
     - `email`
     - `profile`
   - Click "Update" then "Save and Continue"
7. **Test users** page:
   - Click "Add Users"
   - Add your Google account email addresses that you want to use for testing
   - Click "Add" then "Save and Continue"
8. Review and click "Back to Dashboard"

## Step 4: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Select **Application type**: Web application
4. **Name**: Ayni Local Development
5. **Authorized JavaScript origins**:
   - Add: `http://localhost:5173` (frontend URL)
6. **Authorized redirect URIs**:
   - Add: `http://localhost:5173/auth/callback` ⚠️ **CRITICAL: This MUST be the frontend callback URL**

   ⚠️ **Common Mistake**: DO NOT use `http://localhost:8000/api/v1/auth/google/callback` (backend URL)

   **Why**: Google redirects the user's browser directly to this URL after authorization. Since the user is interacting with the frontend, the redirect must go to the frontend, not the backend API.

7. Click "Create"
8. A dialog will show your **Client ID** and **Client Secret** - keep this open

## Step 5: Configure Environment Variables

1. Open the project root `.env` file:
   ```bash
   nano /home/khujta/projects/bmad/ayni/.env
   ```

2. Update the Google OAuth configuration section:
   ```env
   # Google OAuth 2.0 Configuration (Story 2.5)
   GOOGLE_OAUTH_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
   GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-your_client_secret_here
   GOOGLE_OAUTH_REDIRECT_URI=http://localhost:5173/auth/callback
   ```

3. Replace with your actual credentials from Step 4

4. Save the file

⚠️ **CRITICAL**: The `GOOGLE_OAUTH_REDIRECT_URI` in `.env` MUST match what you configured in Google Cloud Console in Step 4.

## Step 6: Restart Backend Server

The backend must be restarted to pick up the new environment variables:

```bash
# If running in the background, kill the process
pkill -f "uvicorn app.main:app"

# Or find and kill by port
lsof -ti:8000 | xargs kill -9

# Start the backend server
cd /home/khujta/projects/bmad/ayni/backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

⚠️ **Common Mistake**: Forgetting to restart the backend after updating `.env` will cause a `redirect_uri_mismatch` error because the backend is still using old configuration.

## Step 7: Test OAuth Flow

1. Ensure both backend and frontend are running:
   - Backend: `http://localhost:8000` (check `http://localhost:8000/docs`)
   - Frontend: `http://localhost:5173`

2. Open `http://localhost:5173` in your browser

3. Click "Sign in with Google" button

4. You should be redirected to Google's authorization page

5. Select your test Google account and authorize

6. After authorization:
   - Google redirects to `http://localhost:5173/auth/callback?code=...&state=...`
   - Frontend exchanges code for JWT tokens via backend
   - You're redirected to the dashboard at `http://localhost:5173/dashboard`

7. You should see: "Welcome to Ayni Dashboard - You are successfully logged in!"

## Troubleshooting

### Error: "redirect_uri_mismatch"

**Cause**: The redirect URI configured in Google Cloud Console doesn't match the one sent by the backend.

**Solution**:
1. Verify Google Cloud Console has: `http://localhost:5173/auth/callback`
2. Verify `.env` has: `GOOGLE_OAUTH_REDIRECT_URI=http://localhost:5173/auth/callback`
3. **Restart the backend server** (most common fix)
4. Clear browser cache and cookies for localhost

### Error: "Invalid or expired state parameter"

**Cause**: The OAuth callback is being called twice due to React StrictMode.

**Solution**: Already fixed in code with `useRef` in `OAuthCallback.tsx`. If you still see this:
1. Check that `hasProcessed.current` guard is in place
2. Verify Redis is running (state is stored in Redis)

### Error: "Error al conectar con Google"

**Causes**:
1. Backend response format doesn't match frontend expectations
2. Network error communicating with backend
3. Missing `get` parameter in Zustand store

**Solutions**:
1. Verify `handleGoogleCallback` returns `TokenResponse` type (not nested `data` object)
2. Verify `useAuth` store has `(set, get)` parameters
3. Check browser console for actual error
4. Check backend logs for specific error

### Error: Blank frontend page

**Cause**: TypeScript type imports causing runtime errors.

**Solution**: Ensure all type-only imports use the `type` keyword:
```typescript
import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'
```

### Error: 404 on OAuth endpoints

**Cause**: API URL duplication (appending `/api/v1` when it's already in base URL).

**Solution**: Verify `client.ts` has:
```typescript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
export const apiClient = axios.create({
  baseURL: API_URL,  // NOT: `${API_URL}/api/v1`
})
```

### Error: Database timezone errors

**Cause**: Using timezone-aware datetimes (`datetime.now(timezone.utc)`) with PostgreSQL `TIMESTAMP WITHOUT TIME ZONE`.

**Solution**: Use `datetime.utcnow()` throughout the backend (already fixed).

### Testing with Multiple Google Accounts

1. Use Chrome incognito/private windows for each account
2. Or add multiple test users in Google Cloud Console OAuth consent screen
3. Or use different browsers for different accounts

## Production Deployment

For production, you'll need to:

1. Create a new OAuth 2.0 Client ID with production URLs
2. Update authorized redirect URIs to use your production frontend URL:
   - Example: `https://app.ayni.cl/auth/callback`
3. Update environment variables on your hosting platform:
   - Railway backend: Set `GOOGLE_OAUTH_REDIRECT_URI=https://app.ayni.cl/auth/callback`
   - Frontend: Build with `VITE_API_URL=https://api.ayni.cl/api/v1`
4. Move OAuth consent screen from "Testing" to "Production" (requires verification)

## Security Notes

- Never commit `.env` file to version control
- OAuth tokens are encrypted in the database using `encrypt_token()`
- State parameter provides CSRF protection (stored in Redis with 10-minute expiration)
- Rate limiting: 10 requests/minute per IP on OAuth endpoints
- Refresh tokens are rotated on each use

## Architecture Overview

```
User Browser
    ↓
1. Click "Sign in with Google" (Frontend)
    ↓
2. GET /api/v1/auth/google/authorize (Backend)
    ↓
3. Redirect to Google authorization page
    ↓
4. User authorizes on Google
    ↓
5. Google redirects to http://localhost:5173/auth/callback?code=...&state=...
    ↓
6. Frontend calls GET /api/v1/auth/google/callback?code=...&state=... (Backend)
    ↓
7. Backend exchanges code for Google tokens
    ↓
8. Backend creates/links user account
    ↓
9. Backend returns JWT access_token + refresh_token
    ↓
10. Frontend stores tokens in localStorage
    ↓
11. Frontend fetches user profile from /users/me
    ↓
12. Frontend redirects to /dashboard
```

## Files Modified for OAuth Integration

- `backend/app/api/routes/auth.py` - OAuth endpoints
- `backend/app/core/oauth.py` - Google OAuth client
- `backend/app/models.py` - OAuthAccount model
- `backend/app/core/security.py` - Token encryption/JWT generation
- `backend/app/services/token_service.py` - Refresh token management
- `frontend/src/api/auth.ts` - OAuth API calls
- `frontend/src/hooks/useAuth.ts` - OAuth state management
- `frontend/src/pages/OAuthCallback.tsx` - OAuth callback handler
- `frontend/src/pages/Login.tsx` - "Sign in with Google" button
- `.env` - OAuth credentials configuration

## Support

If you encounter issues not covered here, check:
1. Backend logs: Check the terminal running uvicorn
2. Frontend console: Open browser DevTools (F12) → Console
3. Network tab: Check request/response details
4. Google Cloud Console: "APIs & Services" → "Credentials" → check configuration
