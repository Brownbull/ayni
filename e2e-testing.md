# Ayni - E2E Testing Guide

Complete guide to running end-to-end (E2E) tests for Ayni using Playwright, both locally and against production environments (Railway + Render).

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Local Testing Setup](#local-testing-setup)
4. [Running E2E Tests Locally](#running-e2e-tests-locally)
5. [Remote Testing (Production)](#remote-testing-production)
6. [Test Suites Overview](#test-suites-overview)
7. [Troubleshooting](#troubleshooting)
8. [CI/CD Integration](#cicd-integration)

---

## Overview

Ayni's E2E test suite uses **Playwright** to test complete user workflows across the frontend and backend. Tests cover:

- **Authentication Flow**: Registration, login, logout, email verification
- **JWT Token Management**: Access tokens, refresh tokens, token rotation
- **Protected Routes**: Authenticated API endpoints
- **Frontend Interceptors**: Automatic token refresh, error handling

**Test Framework**: Playwright 1.56.1
**Test Location**: `frontend/e2e/`
**Configuration**: `frontend/playwright.config.ts`

---

## Prerequisites

Before running E2E tests, ensure you have:

- [x] **Node.js** (v18+) and **npm** installed
- [x] **Python 3.11+** with **uv** package manager
- [x] **PostgreSQL** database accessible (local or remote)
- [x] **Docker** (for local PostgreSQL - optional)
- [x] **Playwright** browsers installed (`npx playwright install chromium`)
- [x] **Project cloned locally**

### Install Playwright

```bash
cd frontend
npm install
npx playwright install chromium
```

This downloads Chromium browser binaries needed for E2E tests.

---

## Local Testing Setup

To run E2E tests locally, you need **both backend and frontend services running**.

### Step 1: Start Local PostgreSQL Database

You have three options:

#### Option A: Docker Compose (Recommended)

```bash
# From project root
cd backend
POSTGRES_USER=ayni_user POSTGRES_PASSWORD=changethis POSTGRES_DB=ayni_dev docker compose up -d
```

Verify database is running:
```bash
docker ps | grep postgres
# Expected: Shows postgres container running on port 5432
```

#### Option B: Docker Run (Manual)

```bash
docker run --name ayni-postgres \
  -e POSTGRES_USER=ayni_user \
  -e POSTGRES_PASSWORD=changethis \
  -e POSTGRES_DB=ayni_dev \
  -p 5432:5432 \
  -d postgres:15
```

#### Option C: System PostgreSQL

If you have PostgreSQL installed locally:

```bash
# Create test database
createdb ayni_dev

# Update backend/.env with connection details
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=ayni_dev
```

### Step 2: Start Backend API Server

```bash
# From project root
cd backend

# Create virtual environment and install dependencies (first time only)
uv sync

# Run database migrations
uv run alembic upgrade head

# Start FastAPI backend on port 8000
uv run uvicorn app.main:app --reload --port 8000
```

**Verify backend is running:**

```bash
curl http://localhost:8000/api/v1/utils/health-check/

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "...",
#   "services": {
#     "database": {"status": "healthy", "latency_ms": ...},
#     "redis": {"status": "healthy", "latency_ms": ...}
#   }
# }
```

> **Note**: Some tests work without Redis, but for full functionality, start Redis:
> ```bash
> docker run --name ayni-redis -p 6379:6379 -d redis:7
> ```

### Step 3: Start Frontend Development Server

**Open a new terminal window:**

```bash
# From project root
cd frontend

# Install dependencies (first time only)
npm install

# Start Vite dev server on port 5173
npm run dev
```

**Verify frontend is running:**

Open browser to http://localhost:5173 - you should see the Ayni login page.

### Step 4: Environment Variables

Ensure `frontend/.env` has correct backend URL:

```bash
# frontend/.env
VITE_API_URL=http://localhost:8000
```

---

## Running E2E Tests Locally

Once all services are running (PostgreSQL, backend, frontend), run the E2E tests.

### Test Execution Commands

```bash
# From frontend directory
cd frontend

# Run all E2E tests (headless mode)
npm run test:e2e

# Run E2E tests with UI (interactive mode)
npm run test:e2e:ui

# Run E2E tests in headed mode (see browser)
npm run test:e2e:headed

# Run specific test file
npx playwright test e2e/auth-token-refresh.spec.ts

# Run specific test by name
npx playwright test -g "Login should return both access and refresh tokens"
```

### Expected Output (Successful Run)

```
Running 8 tests using 1 worker

  ✓  1 auth-token-refresh.spec.ts:55:3 › JWT Token Refresh Flow › AC#1: Login should return both access and refresh tokens (2.5s)
  ✓  2 auth-token-refresh.spec.ts:84:3 › JWT Token Refresh Flow › AC#3: Should refresh access token when expired (3.1s)
  ✓  3 auth-token-refresh.spec.ts:132:3 › JWT Token Refresh Flow › AC#4: Token rotation - old refresh token should be invalidated (2.8s)
  ✓  4 auth-token-refresh.spec.ts:167:3 › JWT Token Refresh Flow › AC#2 & AC#4: Logout should revoke all refresh tokens (2.6s)
  ✓  5 auth-token-refresh.spec.ts:201:3 › JWT Token Refresh Flow › AC#5: Protected endpoints should validate JWT tokens (3.2s)
  ✓  6 auth-token-refresh.spec.ts:237:3 › JWT Token Refresh Flow › Frontend axios interceptor handles 401 with automatic refresh (4.1s)
  ✓  7 auth-token-refresh.spec.ts:275:3 › JWT Token Refresh Flow › Refresh lock prevents concurrent refresh requests (3.5s)
  ✓  8 auth-token-refresh.spec.ts:316:3 › JWT Token Refresh Flow › Max retry limit prevents infinite refresh loops (4.3s)

  8 passed (26.1s)

To open last HTML report run:
  npx playwright show-report
```

### Debug Failed Tests

```bash
# Run tests with debug flag
npx playwright test --debug

# Generate trace files on failure
npx playwright test --trace on

# View HTML report after test run
npx playwright show-report
```

---

## Remote Testing (Production)

E2E tests can run against production environments on Railway (backend) and Render (frontend).

### Prerequisites for Remote Testing

- [x] **Production services deployed** (see [setup.production.md](setup.production.md))
- [x] **Backend URL**: Railway domain (e.g., `https://ayni-backend-production.up.railway.app`)
- [x] **Frontend URL**: Render domain (e.g., `https://ayni-frontend.onrender.com`)

### Configure Remote Testing

Update Playwright configuration to target production:

```typescript
// frontend/playwright.config.ts
export default defineConfig({
  use: {
    baseURL: 'https://ayni-frontend.onrender.com',  // Your Render URL
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  webServer: undefined,  // Disable local dev server for remote testing
})
```

Or use environment variables (recommended):

```bash
# frontend/.env.remote-testing
VITE_API_URL=https://ayni-backend-production.up.railway.app
BASE_URL=https://ayni-frontend.onrender.com
```

### Run Tests Against Production

```bash
cd frontend

# Set API URL to production backend
export VITE_API_URL=https://ayni-backend-production.up.railway.app

# Run tests against production frontend
npx playwright test --config=playwright.config.remote.ts

# Or override baseURL via CLI
npx playwright test --config playwright.config.ts \
  --project=chromium \
  -g "Login should return both access and refresh tokens" \
  --headed
```

### Remote Testing Configuration (Alternative)

Create a separate config for remote testing:

```bash
# frontend/playwright.config.remote.ts
import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,  // Avoid overwhelming production
  retries: 2,
  workers: 1,
  reporter: 'html',
  use: {
    baseURL: process.env.BASE_URL || 'https://ayni-frontend.onrender.com',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
})
```

Run with:
```bash
BASE_URL=https://ayni-frontend.onrender.com \
npx playwright test --config=playwright.config.remote.ts
```

### Remote Testing Considerations

**⚠️ Important Notes:**

1. **Test User Cleanup**: Remote tests create real user accounts. Consider:
   - Using dedicated test user emails (e.g., `e2e-test-user-${timestamp}@example.com`)
   - Implementing test user cleanup scripts
   - Using a separate test environment/database

2. **Rate Limiting**: Production may have rate limits. Run tests with:
   - Lower concurrency (`workers: 1`)
   - Retry delays
   - Sequential execution (`fullyParallel: false`)

3. **Data Persistence**: Tests may leave data in production database. Consider:
   - Using test-specific email domains
   - Running cleanup scripts after tests
   - Using a staging environment instead of production

4. **Performance**: Remote tests are slower due to network latency. Expect 2-3x longer execution time.

### Railway + Render Remote Testing Workflow

```bash
# 1. Verify production services are healthy
curl https://ayni-backend-production.up.railway.app/api/v1/utils/health-check/

# 2. Set environment variables
export VITE_API_URL=https://ayni-backend-production.up.railway.app
export BASE_URL=https://ayni-frontend.onrender.com

# 3. Run E2E tests against production
cd frontend
npx playwright test --config playwright.config.remote.ts --workers=1

# 4. View results
npx playwright show-report
```

---

## Test Suites Overview

### Authentication Flow Tests (`e2e/auth-token-refresh.spec.ts`)

Covers Story 2.3 (JWT Token Generation & Refresh) acceptance criteria:

| Test | Description | AC Covered |
|------|-------------|------------|
| **Login with tokens** | Verifies both access and refresh tokens returned on login | AC#1 |
| **Token refresh** | Tests automatic token refresh when access token expires | AC#3 |
| **Token rotation** | Ensures old refresh token invalidated after rotation | AC#4 |
| **Logout revocation** | Verifies logout revokes all refresh tokens | AC#2, AC#4 |
| **Protected endpoints** | Tests JWT validation on protected API routes | AC#5 |
| **Axios interceptor** | Tests automatic refresh on 401 responses | Frontend |
| **Refresh lock** | Prevents concurrent refresh requests | Frontend |
| **Max retry limit** | Prevents infinite refresh loops | Frontend |

### Test Data

Tests create temporary users:
- **Email**: `e2e-test-user@example.com`
- **Password**: `testpassword123`
- **Cleanup**: `beforeEach` and `afterEach` hooks handle setup/teardown

---

## Troubleshooting

### Issue: Tests fail with "Connection refused"

**Symptoms**: `ECONNREFUSED localhost:8000` or `ECONNREFUSED localhost:5173`

**Resolution**:
1. Verify backend is running: `curl http://localhost:8000/api/v1/utils/health-check/`
2. Verify frontend is running: Open http://localhost:5173 in browser
3. Check ports are not in use: `lsof -i :8000` and `lsof -i :5173`
4. Restart backend: `cd backend && uv run uvicorn app.main:app --reload --port 8000`
5. Restart frontend: `cd frontend && npm run dev`

### Issue: Database connection errors

**Symptoms**: `Database unhealthy` or `Connection to database failed`

**Resolution**:
1. Verify PostgreSQL is running: `docker ps | grep postgres` or `pg_isready`
2. Check database credentials in `backend/.env`:
   ```
   POSTGRES_SERVER=localhost
   POSTGRES_PORT=5432
   POSTGRES_USER=ayni_user
   POSTGRES_PASSWORD=changethis
   POSTGRES_DB=ayni_dev
   ```
3. Run migrations: `cd backend && uv run alembic upgrade head`
4. Restart PostgreSQL container: `docker restart ayni-postgres`

### Issue: "User already exists" errors

**Symptoms**: Tests fail with `400 Bad Request - User already exists`

**Resolution**:
1. Tests should clean up users, but manual cleanup:
   ```sql
   -- Connect to database
   docker exec -it ayni-postgres psql -U ayni_user -d ayni_dev

   -- Delete test user
   DELETE FROM "user" WHERE email = 'e2e-test-user@example.com';
   \q
   ```
2. Or reset test database:
   ```bash
   cd backend
   uv run alembic downgrade base
   uv run alembic upgrade head
   ```

### Issue: Playwright browsers not installed

**Symptoms**: `Executable doesn't exist at ...`

**Resolution**:
```bash
cd frontend
npx playwright install chromium

# Or install all browsers
npx playwright install
```

### Issue: Tests timeout waiting for navigation

**Symptoms**: `Timeout 5000ms exceeded waiting for URL`

**Resolution**:
1. Increase timeout in test:
   ```typescript
   await page.waitForURL('**/dashboard', { timeout: 10000 })
   ```
2. Check frontend dev server logs for errors
3. Verify login form selectors match current UI:
   ```typescript
   await page.fill('input[name="email"]', TEST_USER.email)
   await page.fill('input[name="password"]', TEST_USER.password)
   ```

### Issue: Remote tests fail with CORS errors

**Symptoms**: `CORS policy: No 'Access-Control-Allow-Origin' header`

**Resolution**:
1. Verify Railway backend `BACKEND_CORS_ORIGINS` includes Render URL
2. Check Railway `FRONTEND_HOST` matches Render URL exactly
3. Ensure both URLs use `https://` protocol
4. Redeploy backend after updating CORS settings

### Issue: Remote tests fail with 401 errors

**Symptoms**: All authenticated requests return 401

**Resolution**:
1. Verify `VITE_API_URL` points to correct backend
2. Check JWT tokens in browser localStorage:
   ```bash
   # In Playwright test
   const token = await page.evaluate(() => localStorage.getItem('access_token'))
   console.log('Access Token:', token)
   ```
3. Verify backend `JWT_SECRET` is set in Railway
4. Check token expiration times (`ACCESS_TOKEN_EXPIRE_MINUTES`)

### Issue: Tests pass locally but fail in CI

**Resolution**:
1. Check CI environment has PostgreSQL available
2. Verify all environment variables set in CI
3. Ensure database migrations run before tests
4. Check CI worker resources (memory, CPU)
5. Review CI logs for specific error messages

---

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: ayni_user
          POSTGRES_PASSWORD: changethis
          POSTGRES_DB: ayni_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install uv
        run: pip install uv

      - name: Setup backend
        working-directory: ./backend
        run: |
          uv sync
          uv run alembic upgrade head

      - name: Start backend
        working-directory: ./backend
        run: |
          uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 &
          sleep 5

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install frontend dependencies
        working-directory: ./frontend
        run: npm ci

      - name: Install Playwright browsers
        working-directory: ./frontend
        run: npx playwright install chromium --with-deps

      - name: Run E2E tests
        working-directory: ./frontend
        env:
          VITE_API_URL: http://localhost:8000
        run: npm run test:e2e

      - name: Upload Playwright report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: frontend/playwright-report/
          retention-days: 30
```

---

## Test Coverage Summary

### Current E2E Test Coverage

- **Authentication**: ✅ Registration, login, logout
- **JWT Tokens**: ✅ Access token, refresh token, rotation
- **Token Refresh**: ✅ Automatic refresh on expiration
- **Token Invalidation**: ✅ Logout revokes tokens, old tokens rejected
- **Protected Routes**: ✅ JWT validation on API endpoints
- **Frontend Interceptors**: ✅ Axios 401 handling, refresh lock
- **Error Handling**: ✅ Max retry limits, invalid tokens

### Planned Test Coverage

- **Email Verification**: Email verification flow (Story 2.2)
- **Multi-tenancy**: Tenant isolation, RLS verification
- **User Management**: Profile updates, password reset
- **Error Scenarios**: Network failures, server errors
- **Performance**: Load testing, concurrent users

---

## Quick Reference: Service URLs

### Local Development

| Service | URL | Status Check |
|---------|-----|--------------|
| Frontend | http://localhost:5173 | Open in browser |
| Backend API | http://localhost:8000 | `curl http://localhost:8000/api/v1/utils/health-check/` |
| PostgreSQL | localhost:5432 | `docker ps \| grep postgres` |
| Redis | localhost:6379 | `docker ps \| grep redis` |

### Production (Railway + Render)

| Service | URL | Status Check |
|---------|-----|--------------|
| Frontend (Render) | https://ayni-frontend.onrender.com | Open in browser |
| Backend API (Railway) | https://ayni-backend-production.up.railway.app | `curl https://.../api/v1/utils/health-check/` |
| Flower UI (Railway) | https://ayni-flower-production.up.railway.app | Open in browser |

---

## Complete Testing Checklist

### Local E2E Testing
- [ ] PostgreSQL running (Docker or system)
- [ ] Database migrations applied (`alembic upgrade head`)
- [ ] Backend API running on port 8000
- [ ] Frontend dev server running on port 5173
- [ ] `VITE_API_URL=http://localhost:8000` in frontend/.env
- [ ] Playwright browsers installed (`npx playwright install chromium`)
- [ ] All E2E tests passing (`npm run test:e2e`)

### Remote E2E Testing
- [ ] Production backend deployed and healthy (Railway)
- [ ] Production frontend deployed and accessible (Render)
- [ ] `VITE_API_URL` points to Railway backend
- [ ] `BASE_URL` set to Render frontend
- [ ] Remote config created (`playwright.config.remote.ts`)
- [ ] Test user cleanup strategy defined
- [ ] E2E tests pass against production

### CI/CD Integration
- [ ] GitHub Actions workflow created
- [ ] PostgreSQL service configured in CI
- [ ] Backend starts successfully in CI
- [ ] Frontend builds successfully in CI
- [ ] Playwright browsers installed in CI
- [ ] E2E tests run automatically on PR
- [ ] Test reports uploaded as artifacts

---

**E2E Testing Setup Complete!** ✅

Refer to [setup.production.md](setup.production.md) for production deployment and [run_app.remote.md](run_app.remote.md) for ongoing production operations.

**Last Updated**: 2025-11-14
