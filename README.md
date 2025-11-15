# Ayni - Multi-Location Retail Analytics Platform

[![Backend CI](https://github.com/Brownbull/ayni/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/Brownbull/ayni/actions/workflows/backend-ci.yml)
[![Frontend CI](https://github.com/Brownbull/ayni/actions/workflows/frontend-ci.yml/badge.svg)](https://github.com/Brownbull/ayni/actions/workflows/frontend-ci.yml)
[![codecov](https://codecov.io/gh/Brownbull/ayni/branch/main/graph/badge.svg)](https://codecov.io/gh/Brownbull/ayni)

**Ayni** is a multi-tenant SaaS platform that transforms retail analytics for Chilean and Latin American SMBs, providing multi-location analytics, cross-tenant benchmarking, and real-time dashboard performance.

## Project Description

Ayni helps retail businesses understand their performance through:
- **Multi-location analytics** with company-level and location-level insights
- **Cross-tenant benchmarking** using k-anonymity for privacy-preserving comparisons
- **CSV-based data ingestion** with intelligent Chilean POS format detection
- **Real-time dashboards** with annual, monthly, and hybrid time granularity
- **Performance index ranking** with color-coded tiers and historical trends

## Tech Stack

### Backend
- **Framework:** FastAPI (async Python web framework)
- **Python Version:** ≥3.11
- **Package Manager:** `uv` (modern, faster alternative to Poetry)
- **Database:** PostgreSQL 17 with Row-Level Security (RLS) for multi-tenancy
- **ORM:** SQLAlchemy 2.0.44 with asyncpg driver
- **Background Jobs:** Celery 5.5.3 + Redis for async task processing
- **Authentication:** fastapi-users 15.0.1 (JWT, OAuth 2.0, email verification)
- **CSV Processing:** gabeda_core (custom analytics engine)
- **Testing:** pytest + pytest-asyncio (target 70% coverage)

### Frontend
- **Framework:** React 19 + TypeScript (strict mode)
- **Build Tool:** Vite
- **Styling:** Tailwind CSS (utility-first, no framework conflicts)
- **State Management:**
  - TanStack React Query 5.90.7 for server state
  - Zustand 5.0.8 for UI state (theme, language, selected company)
- **Charts:** Recharts 3.4.1
- **Localization:** react-i18next (Spanish/English)
- **Date Handling:** date-fns (Chilean format support)
- **Testing:** Vitest + Playwright (target 70% coverage)

### Infrastructure
- **Database Hosting:** Railway PostgreSQL (managed)
- **Backend Deployment:** Railway
- **Frontend Deployment:** Render (static site CDN)
- **Caching/Message Broker:** Redis 7.x
- **Logging:** structlog/loguru (structured JSON)
- **Monitoring:** Railway Logs (built-in)

## Prerequisites

- **Python:** ≥3.11
- **Node.js:** ≥18
- **uv:** Python package manager ([install guide](https://github.com/astral-sh/uv))
- **Docker:** For local PostgreSQL and Redis (optional but recommended)
- **Git:** Version control

## Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ayni
```

### 2. Backend Setup

```bash
cd backend

# Install dependencies with uv
uv sync

# Install gabeda_core from GitHub (not in PyPI)
uv pip install git+https://github.com/Brownbull/gabeda_core.git

# Copy environment template and configure
cp .env.example .env
# Edit .env with your database credentials

# Run database migrations
uv run alembic upgrade head

# Start the development server
uv run uvicorn app.main:app --reload
```

Backend will be available at: `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment template and configure
cp .env.example .env
# Edit .env with your backend API URL

# Start the development server
npm run dev
```

Frontend will be available at: `http://localhost:5173`

### 4. Docker Development (Optional)

For local PostgreSQL and Redis:

```bash
# From project root
docker-compose up -d

# Services will be available at:
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
```

## Database Migrations

This project uses **Alembic** for database schema migrations and includes seed data for local development.

### Migration Commands

```bash
cd backend

# Apply all pending migrations (upgrade to latest)
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1

# Check current migration version
uv run alembic current

# View migration history
uv run alembic history

# Create a new migration (auto-detect model changes)
uv run alembic revision --autogenerate -m "Add new table"

# Rollback to specific revision
uv run alembic downgrade <revision_id>
```

### Seed Data for Development

The project includes a seed script that creates demo data for local development:

```bash
cd backend

# Run seed script manually
uv run python app/db/seeds.py
```

**Demo data includes:**
- 1 demo tenant
- 2 demo users (owner@demo.com, manager@demo.com)
- 1 demo company with Chilean RUT (12.345.678-9)
- 2 demo locations (Main Store, Mall Location)
- Sample transaction data (added in future stories)

**Demo credentials:**
- Owner: `owner@demo.com` / `DemoPass123!`
- Manager: `manager@demo.com` / `DemoPass123!`

⚠️ **WARNING:** Change these credentials before deploying to production!

**Note:** The seed script is idempotent - safe to run multiple times without duplicating data.

### Docker Compose Integration

When using `docker-compose up`, migrations and seeds run automatically via the `prestart` service:

```bash
# Fresh environment setup
docker-compose up -d

# Migrations are applied automatically
# Seed data is created automatically
# Backend API starts after prestart completes
```

### Troubleshooting Migrations

**Issue:** `alembic: command not found`
```bash
# Ensure you're using uv to run commands
uv run alembic upgrade head
```

**Issue:** Database connection refused
```bash
# Ensure PostgreSQL is running
docker-compose up -d db

# Check DATABASE_URL in .env matches your setup
# Default: postgresql+asyncpg://ayni_user:changethis@localhost:5432/ayni_dev
```

**Issue:** Migration conflicts after git merge
```bash
# Check current migration state
uv run alembic current

# View migration tree
uv run alembic history

# If needed, create merge migration
uv run alembic merge heads -m "Merge migration branches"
```

**Issue:** Need to reset database completely
```bash
# ⚠️ WARNING: This deletes all data!
docker-compose down -v  # Stop and remove volumes
docker-compose up -d db # Start fresh database
uv run alembic upgrade head  # Apply all migrations
uv run python app/db/seeds.py  # Recreate seed data
```

## Google OAuth 2.0 Configuration (Optional)

Ayni supports Google OAuth 2.0 for user authentication alongside traditional email/password login.

### Setting Up Google OAuth

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable Google+ API**
   - Navigate to "APIs & Services" → "Library"
   - Search for "Google+ API" (or "People API" for newer projects)
   - Click "Enable"

3. **Configure OAuth Consent Screen**
   - Go to "APIs & Services" → "OAuth consent screen"
   - Fill in required fields:
     - Application name: "Ayni"
     - Support email: your email
     - Logo: Upload your logo (120x120 px)
   - Scopes: `email`, `profile`, `openid`

4. **Create OAuth 2.0 Client ID**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client ID"
   - Application type: "Web application"
   - Name: "Ayni Web Client"
   - Authorized redirect URIs:
     - Development: `http://localhost:8000/api/v1/auth/google/callback`
     - Production: `https://api.ayni.cl/api/v1/auth/google/callback`
   - Click "Create"

5. **Add Credentials to Environment**

   Update your `.env` file with the Client ID and Client Secret:

   ```bash
   # Google OAuth 2.0 Configuration (Story 2.5)
   GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
   GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
   ```

6. **Restart Backend Server**

   ```bash
   # OAuth will be automatically enabled when credentials are present
   uv run uvicorn app.main:app --reload
   ```

### OAuth Security Features

- **State Parameter:** CSRF protection with 5-minute expiration stored in Redis
- **Token Encryption:** Google OAuth tokens are encrypted before database storage
- **HTTPS Enforcement:** Production requires HTTPS for redirect URIs (Google requirement)
- **Account Merging:** Existing email/password users can link their Google account
- **Pre-verified Emails:** Google-authenticated users automatically have verified emails

### OAuth API Endpoints

- `GET /api/v1/auth/google/authorize` - Get Google authorization URL
- `GET /api/v1/auth/google/callback` - OAuth callback handler (returns JWT tokens)

### Testing OAuth Integration

```bash
# Run OAuth-specific tests
cd backend
uv run pytest tests/test_oauth.py -v
```

**Note:** OAuth is optional. If credentials are not configured, the endpoints return HTTP 503 and email/password authentication remains fully functional.

## Password Reset Flow

Ayni provides a secure password reset mechanism for users who forget their passwords.

### How Password Reset Works

1. **Request Reset**
   - User clicks "Forgot Password" on login page
   - Enters their email address
   - System sends password reset email with time-limited token (1 hour expiration)
   - **Security:** Always returns success message to prevent email enumeration

2. **Reset Password**
   - User clicks reset link from email
   - Enters new password (minimum 8 characters)
   - Token is validated and blacklisted to prevent reuse
   - Password is updated with bcrypt hashing
   - All existing sessions are invalidated (user must log in again)
   - Confirmation email is sent notifying password change

### Password Reset API Endpoints

- `POST /api/v1/auth/reset-password` - Request password reset (send email)
- `POST /api/v1/auth/confirm-reset` - Confirm password reset with token and new password

### Security Features

- **Token Expiration:** 1 hour (stricter than access tokens)
- **Email Enumeration Prevention:** Same response for existing/non-existing emails
- **Rate Limiting:** 3 password reset requests per hour per email
- **Token Blacklist:** Reset tokens stored in Redis after use (prevents replay attacks)
- **Session Invalidation:** All refresh tokens revoked after password change
- **Password Validation:** Minimum 8 characters enforced
- **Confirmation Email:** User notified after successful password change

### Configuration

Password reset requires the following environment variables:

```bash
# JWT Configuration (already configured for authentication)
JWT_SECRET=your-64-character-random-secret
EMAIL_RESET_TOKEN_EXPIRE_HOURS=1  # Token expires in 1 hour

# Frontend URL for reset link generation
FRONTEND_HOST=http://localhost:5173

# Email Service Configuration (required for sending emails)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_TLS=true
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAILS_FROM_EMAIL=noreply@ayni.cl
EMAILS_FROM_NAME=Ayni

# Redis (for token blacklist and rate limiting)
REDIS_URL=redis://localhost:6379/0
```

### Testing Password Reset

```bash
# Run password reset tests
cd backend
uv run pytest tests/api/test_auth.py::test_password_reset_request_existing_email -v
uv run pytest tests/api/test_auth.py::test_password_reset_confirm_success -v
uv run pytest tests/api/test_auth.py::test_password_reset_sends_confirmation_email -v
```

### Email Templates

Password reset uses two email templates:

- `backend/app/email-templates/build/reset_password.html` - Password reset request email
- `backend/app/email-templates/build/password_changed.html` - Password change confirmation email

Both templates include:
- Project branding
- User-friendly instructions
- Security recommendations
- Timestamp information

## Running Tests

### Backend Tests

```bash
cd backend
uv run pytest
uv run pytest --cov=app --cov-report=html
```

### Frontend Tests

```bash
cd frontend
npm run test              # Run Vitest unit tests
npm run test:e2e          # Run Playwright E2E tests
npm run test:coverage     # Generate coverage report
```

## Code Quality

### Pre-commit Hooks

This project uses pre-commit hooks for automatic code quality checks:

```bash
# Install pre-commit hooks (first time only)
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

**Configured hooks:**
- **Backend (Python):**
  - Ruff format (modern alternative to Black)
  - Ruff linting (fast Python linter)
- **Frontend (TypeScript):**
  - ESLint (via Biome)
  - Prettier integration

### Linting Commands

```bash
# Backend
cd backend
uv run ruff check .
uv run ruff format .

# Frontend
cd frontend
npm run lint
npm run format
```

## Architecture Highlights

### Multi-Tenancy
- PostgreSQL Row-Level Security (RLS) for data isolation
- Tenant context tracked via `company_id` in all tables
- Automatic filtering at database level

### Async-First Design
- FastAPI with async/await patterns
- asyncpg for high-performance database operations
- Celery for background job processing (CSV uploads, aggregations)

### State Management
- **Server State:** TanStack React Query (auto-refetch, caching, loading states)
- **UI State:** Zustand (theme, language, company selection)

### CSV Processing
- Powered by `gabeda_core` analytics engine
- Intelligent Chilean POS format detection
- Multi-temporal aggregation pipeline (annual → monthly → daily)

### Security
- JWT authentication with refresh tokens
- Google OAuth 2.0 integration
- Role-Based Access Control (RBAC)
- Row-Level Security (RLS) for multi-tenant isolation

## Package Manager Note: uv vs Poetry

**This project uses `uv` instead of Poetry** (as originally specified in architecture docs).

**Rationale:**
- **Modern and Faster:** uv is a next-generation Python package manager written in Rust
- **Poetry-Compatible:** Uses same `pyproject.toml` format
- **Better Performance:** Significantly faster dependency resolution and installation
- **Active Development:** By Astral (creators of Ruff)

**For Contributors Familiar with Poetry:**
```bash
# Poetry equivalent commands:
poetry install    → uv sync
poetry add pkg    → uv add pkg
poetry run cmd    → uv run cmd
```

## Deployment

**Production Deployment Status:**
- **Backend API:** Railway (auto-deploys from `main` branch)
- **Frontend:** Render (auto-deploys from `main` branch)
- **CI/CD:** GitHub Actions (tests must pass before deployment)

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for comprehensive deployment procedures and rollback guides.

### Quick Deploy

Deployments are **fully automated**:

1. Merge PR to `main` branch
2. GitHub Actions runs CI tests (backend + frontend)
3. If tests pass, Railway and Render auto-deploy
4. Health checks verify services are operational

### Manual Deployment (if needed)

#### Backend (Railway)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway link
railway up
```

#### Frontend (Render)

1. Push to GitHub
2. Render dashboard → Manual Deploy → "Deploy latest commit"

Or configure automatic deployment:
1. Connect Render to repository
2. Configure build settings:
   - **Build Command:** `cd frontend && npm install && npm run build`
   - **Publish Directory:** `frontend/dist`
3. Deploy automatically on git push

## Development Workflow

1. **Branch from main:** `git checkout -b feature/your-feature`
2. **Make changes** and commit with descriptive messages
3. **Run tests** to ensure no regressions
4. **Pre-commit hooks** will automatically format and lint
5. **Push and create PR** for review
6. **Merge after approval** and CI passes

## Contributing

- Follow existing code patterns and conventions
- Write tests for new features (target 70% coverage)
- Update documentation when changing behavior
- Use TypeScript strict mode (no `any` types)
- Keep components small and focused

## Project Status

**Current Version:** 1.0 (Initial Setup)
**Epic 1:** Infrastructure & Foundation (In Progress)

See [docs/epics.md](docs/epics.md) for full roadmap and story breakdown.

## Additional Resources

- **Architecture:** [docs/architecture.md](docs/architecture.md)
- **API Documentation:** `http://localhost:8000/docs` (when backend is running)
- **FastAPI Template:** [FastAPI Full Stack](https://github.com/fastapi/full-stack-fastapi-template)
- **React 19 Docs:** [react.dev](https://react.dev/)
- **Tailwind CSS:** [tailwindcss.com](https://tailwindcss.com/)

## License

[Your License Here]

---

**Built with ❤️ for Chilean retail businesses**
