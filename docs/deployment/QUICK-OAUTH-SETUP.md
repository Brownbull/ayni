# Quick OAuth Setup - Production Configuration

## 🚀 5-Minute Setup Guide

### Step 1: Get Your URLs (2 min)

```bash
# Backend URL (Railway)
cd backend && railway status
# Copy the URL: https://________.up.railway.app

# Frontend URL (Render)
# Go to Render dashboard, copy URL
# Should be: https://________.onrender.com
```

### Step 2: Google Cloud Console (2 min)

**URL:** https://console.cloud.google.com

1. **Create Project:** "Ayni"
2. **Enable API:** Google+ API or People API
3. **OAuth Consent Screen:**
   - App name: Ayni
   - Email: your-email@gmail.com
   - Scopes: email, profile, openid
4. **Create Credentials:**
   - Type: Web application
   - Redirect URI: `https://YOUR-RAILWAY-URL.up.railway.app/api/v1/auth/google/callback`
   - **SAVE THE CLIENT_ID AND CLIENT_SECRET!**

### Step 3: Configure Railway (1 min)

**Railway Dashboard → Your Backend Service → Variables**

Add these 3 variables:
```bash
GOOGLE_OAUTH_CLIENT_ID=paste-client-id-here.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=paste-secret-here
GOOGLE_OAUTH_REDIRECT_URI=https://YOUR-RAILWAY-URL/api/v1/auth/google/callback
```

**Important:** Replace `YOUR-RAILWAY-URL` with actual URL!

Railway will auto-redeploy.

### Step 4: Test (< 1 min)

1. Go to: `https://your-frontend.onrender.com/login`
2. Click "Sign in with Google"
3. Authorize with Google
4. Should redirect to dashboard

**Done!** 🎉

---

## ⚠️ Common Issues

**"Redirect URI mismatch"**
→ Railway URL in Google Console doesn't match exactly

**"OAuth not configured" (503)**
→ Check Railway variables are set correctly

**CORS error**
→ Add `FRONTEND_HOST=https://your-frontend.onrender.com` to Railway

---

## 📋 Configuration Template

Copy this and fill in your values:

```bash
# Google Cloud Console
Client ID: _____________________________.apps.googleusercontent.com
Client Secret: GOCSPX-_____________________________
Redirect URI: https://_____________________________.up.railway.app/api/v1/auth/google/callback

# Railway Variables
GOOGLE_OAUTH_CLIENT_ID=(Client ID from above)
GOOGLE_OAUTH_CLIENT_SECRET=(Client Secret from above)
GOOGLE_OAUTH_REDIRECT_URI=(Redirect URI from above)
FRONTEND_HOST=https://_____________________________.onrender.com

# Render Variables (should already exist)
VITE_API_BASE_URL=https://_____________________________.up.railway.app/api/v1
```

---

## 🔍 Quick Test

```bash
# Test OAuth endpoint
curl https://your-backend.railway.app/api/v1/auth/google/authorize

# Should return JSON with "authorization_url"
# If 503: OAuth not configured in Railway
```

---

**Full Guide:** See [oauth-setup-production.md](./oauth-setup-production.md)
