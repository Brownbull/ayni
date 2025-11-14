# Backend Troubleshooting - Railway

Common issues and solutions for the Ayni backend deployed on Railway.

## Quick Diagnosis

```bash
# Check deployment status
railway status

# View recent logs
railway logs --limit 50

# Check environment variables
railway variables

# Test health endpoint
curl https://your-backend.up.railway.app/health
```

---

## Build & Deployment Issues

### Issue: Missing Dependencies - ModuleNotFoundError

**Symptom:**
```
ModuleNotFoundError: No module named 'httpx_oauth'
```

**Root Cause:**
Railway installs from `requirements.txt`, which was outdated.

**Solution:**
```bash
cd backend
uv pip compile pyproject.toml -o requirements.txt
git add requirements.txt
git commit -m "chore: update requirements.txt"
git push
```

**Prevention:**
Always regenerate `requirements.txt` after updating `pyproject.toml`.

**Fixed in commit:** `c6f5c90`

---

### Issue: Build Fails with Python Version Error

**Symptom:**
```
Error: Python 3.11 required, but 3.9 found
```

**Solution:**
Specify Python version in `runtime.txt` or Railway settings:

```bash
# Create runtime.txt in backend/
echo "python-3.11" > runtime.txt
git add runtime.txt
git commit -m "chore: specify Python version"
git push
```

---

### Issue: Deployment Stuck or Very Slow

**Symptom:**
Build takes 10+ minutes or hangs.

**Solution:**
1. Check Railway status page: https://status.railway.app
2. Cancel and retry deployment
3. Check for circular dependencies in requirements.txt

---

## Database Issues

### Issue: Database Connection Failed

**Symptom:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Root Cause:**
- PostgreSQL service not linked
- DATABASE_URL not set
- PostgreSQL service down

**Solution:**
```bash
# Check if PostgreSQL is linked
railway link

# Check DATABASE_URL exists
railway variables | grep DATABASE_URL

# Restart PostgreSQL service
# Go to Railway Dashboard → PostgreSQL service → Restart
```

---

### Issue: Migration Fails - Table Already Exists

**Symptom:**
```
alembic.util.exc.CommandError: Table 'users' already exists
```

**Solution:**
```bash
# Connect to database
railway connect postgres

# Check current alembic version
SELECT * FROM alembic_version;

# If empty, stamp current version
railway run alembic stamp head

# Then run migrations
railway run alembic upgrade head
```

---

### Issue: Database Connection Pool Exhausted

**Symptom:**
```
sqlalchemy.exc.TimeoutError: QueuePool limit exceeded
```

**Solution:**
Increase connection pool size in `backend/app/core/database.py`:

```python
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,  # Increase from 10
    max_overflow=40,  # Increase from 20
)
```

---

## Redis Issues

### Issue: Redis Connection Failed

**Symptom:**
```
redis.exceptions.ConnectionError: Error connecting to Redis
```

**Root Cause:**
- Redis service not linked
- REDIS_URL not set
- Redis service down

**Solution:**
```bash
# Check if Redis is linked
railway link

# Check REDIS_URL exists
railway variables | grep REDIS_URL

# Restart Redis service
# Go to Railway Dashboard → Redis service → Restart
```

---

### Issue: OAuth State Not Found

**Symptom:**
```
Invalid or expired state parameter
```

**Root Cause:**
Redis not storing state or state expired (5-min TTL).

**Solution:**
1. Verify Redis is running (check health endpoint)
2. Check Redis connection in logs
3. Ensure state TTL is appropriate (currently 5 minutes)

```bash
# Check Redis logs
railway logs --service redis

# Test Redis connection
railway run python -c "import redis; r = redis.from_url('$REDIS_URL'); print(r.ping())"
```

---

## CORS Issues

### Issue: Frontend Blocked by CORS Policy

**Symptom:**
```
Access to XMLHttpRequest blocked by CORS policy:
No 'Access-Control-Allow-Origin' header present
```

**Root Cause:**
`FRONTEND_HOST` environment variable not set.

**Solution:**
```bash
railway variables --set FRONTEND_HOST=https://ayni-frontend.onrender.com

# Or via Railway Dashboard → Backend Service → Variables
# Add: FRONTEND_HOST = https://ayni-frontend.onrender.com
```

**Verification:**
```bash
curl -X OPTIONS https://your-backend.up.railway.app/api/v1/health \
  -H "Origin: https://ayni-frontend.onrender.com" \
  -H "Access-Control-Request-Method: GET" \
  -i

# Should return:
# access-control-allow-origin: https://ayni-frontend.onrender.com
```

---

### Issue: 500 Errors Appear as CORS Errors

**Symptom:**
Browser shows CORS error, but real issue is 500 Internal Server Error.

**Root Cause:**
When endpoint crashes (500), CORS middleware doesn't run. Browser interprets missing CORS headers as CORS error.

**Solution:**
1. Check actual HTTP status code (use curl or Postman)
2. Look at Railway logs for real error
3. Fix underlying 500 error
4. CORS headers will appear once endpoint works

```bash
# Test endpoint directly (bypasses CORS preflight)
curl -i https://your-backend.up.railway.app/api/v1/endpoint

# Check if it's a real 500 or CORS issue
```

---

## OAuth Issues

### Issue: OAuth Not Configured (503)

**Symptom:**
```json
{"error": "Service Unavailable", "detail": "OAuth not configured"}
```

**Root Cause:**
Google OAuth environment variables not set.

**Solution:**
```bash
railway variables --set GOOGLE_OAUTH_CLIENT_ID=xxx.apps.googleusercontent.com
railway variables --set GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-xxx
railway variables --set GOOGLE_OAUTH_REDIRECT_URI=https://your-backend.up.railway.app/api/v1/auth/google/callback
```

**Verification:**
```bash
curl https://your-backend.up.railway.app/api/v1/auth/google/authorize

# Should return JSON with "authorization_url"
```

---

### Issue: OAuth Redirect URI Mismatch

**Symptom:**
```
Error: redirect_uri_mismatch
The redirect URI in the request does not match the authorized redirect URIs
```

**Root Cause:**
Railway URL doesn't exactly match Google Cloud Console configuration.

**Solution:**
1. Get exact Railway URL: `railway status`
2. Go to Google Cloud Console → Credentials
3. Edit OAuth 2.0 Client ID
4. Add exact redirect URI:
   ```
   https://exact-url.up.railway.app/api/v1/auth/google/callback
   ```
5. Save and wait 5 minutes for Google to update

---

### Issue: OAuth Endpoint Returns 500 Error

**Symptom:**
```json
{"error": "Internal Server Error", "detail": "An unexpected error occurred"}
```

**Root Causes & Solutions:**

**1. Wrong Redis type annotation**
```python
# WRONG:
async def endpoint(redis: RedisClient = Depends(RedisClient.get_client)):

# CORRECT:
async def endpoint(redis: Redis = Depends(RedisClient.get_client)):
```

**2. Missing httpx-oauth dependency**
See "Missing Dependencies" section above.

**3. Database connection issue**
Check PostgreSQL service is running and DATABASE_URL is set.

**Fixed in commit:** `2fdeb3e` (Redis type), `c6f5c90` (dependencies)

---

## Environment Variable Issues

### Issue: JWT_SECRET Not Set

**Symptom:**
```
Settings validation error: JWT_SECRET field required
```

**Solution:**
```bash
# Generate secure random string (64 characters)
openssl rand -hex 32

# Set in Railway
railway variables --set JWT_SECRET=<generated-string>
```

---

### Issue: Environment Variables Not Updating

**Symptom:**
Changed variable in Railway Dashboard but app still uses old value.

**Solution:**
Railway auto-redeploys when variables change, but may take a minute:

1. Wait 1-2 minutes for redeployment
2. Check deployment logs to confirm new deployment
3. If still not updated, manually restart:
   ```bash
   railway restart
   ```

---

## Performance Issues

### Issue: Slow API Responses

**Possible Causes:**
1. Database query not optimized
2. N+1 query problem
3. Missing database indexes
4. Connection pool exhausted

**Debug:**
```bash
# Check Railway logs for slow queries
railway logs | grep "slow query"

# Monitor database connections
# Connect to database
railway connect postgres

# Check active connections
SELECT count(*) FROM pg_stat_activity WHERE state = 'active';
```

**Solutions:**
- Add database indexes
- Use eager loading for relationships
- Increase connection pool size
- Use Redis caching

---

### Issue: High Memory Usage

**Symptom:**
Service crashes or restarts frequently.

**Solution:**
1. Check Railway metrics (Dashboard → Service → Metrics)
2. Upgrade Railway plan if needed
3. Optimize code:
   - Close database connections properly
   - Use connection pooling
   - Avoid loading large datasets into memory

---

## Logging & Debugging

### View Logs

**Recent logs:**
```bash
railway logs --limit 50
```

**Follow logs in real-time:**
```bash
railway logs --tail
```

**Filter by keyword:**
```bash
railway logs | grep -i error
railway logs | grep -i oauth
```

---

### Common Log Patterns

**Successful startup:**
```
INFO: Started server process
INFO: Waiting for application startup
INFO: Application startup complete
INFO: Uvicorn running on http://0.0.0.0:8000
```

**Database connection:**
```
INFO: Database connection established
INFO: Running migrations
```

**OAuth initialization:**
```
INFO: Google OAuth client initialized
```

**Common errors:**
```
ERROR: Could not connect to database
ERROR: Redis connection failed
ERROR: Environment variable not set
```

---

## Health Check Failures

### Issue: Health Check Returns Unhealthy

**Symptom:**
```json
{
  "status": "unhealthy",
  "services": {
    "database": {"status": "unhealthy", "error": "connection failed"},
    "redis": {"status": "healthy"}
  }
}
```

**Solution:**
Check specific service that's unhealthy:

**Database unhealthy:**
```bash
# Check PostgreSQL service status
railway status

# Restart PostgreSQL
# Dashboard → PostgreSQL service → Restart
```

**Redis unhealthy:**
```bash
# Check Redis service status
railway status

# Restart Redis
# Dashboard → Redis service → Restart
```

---

## Rollback

If deployment breaks:

**Via Railway Dashboard:**
1. Go to backend service → Deployments
2. Find last working deployment
3. Click "Redeploy"

**Via CLI:**
```bash
# View deployment history
railway status

# Note: Railway CLI doesn't support rollback directly
# Use Dashboard for rollback
```

---

## Emergency Debugging

### Access Production Shell

```bash
# Run interactive Python shell
railway run python

# Run specific command
railway run alembic current

# Connect to database
railway connect postgres
```

---

### Check Service Status

```bash
# Railway service status
railway status

# Health endpoint
curl https://your-backend.up.railway.app/health

# Specific endpoint
curl https://your-backend.up.railway.app/api/v1/health

# With auth token
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-backend.up.railway.app/api/v1/users/me
```

---

## Support Resources

- **Railway Documentation:** https://docs.railway.app
- **Railway Status:** https://status.railway.app
- **Railway Discord:** https://discord.gg/railway
- **Ayni Setup Guide:** [SETUP-BACKEND.md](./SETUP-BACKEND.md)

---

## Checklist for 500 Errors

When debugging 500 errors:

1. [ ] Check Railway logs for stack trace
2. [ ] Verify all environment variables set
3. [ ] Test database connection (health endpoint)
4. [ ] Test Redis connection (health endpoint)
5. [ ] Check recent code changes
6. [ ] Test endpoint with curl (bypass browser)
7. [ ] Review recent Railway deployments
8. [ ] Check Railway status page
9. [ ] Try rollback to last working version
10. [ ] Check for missing dependencies

---

## Most Common Issues (Quick Reference)

| Issue | Quick Fix |
|-------|-----------|
| ModuleNotFoundError | Regenerate requirements.txt |
| CORS error | Set FRONTEND_HOST |
| OAuth 503 | Set OAuth environment variables |
| Database connection failed | Check PostgreSQL service running |
| Redis connection failed | Check Redis service running |
| 500 on endpoints | Check Railway logs |
| Migrations fail | Check alembic version table |
| Slow responses | Check database queries |
| Service crashes | Check memory usage |
| Environment vars not updating | Wait for auto-redeploy or restart |
