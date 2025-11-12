# Ayni - Multi-Location Retail Analytics Platform

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

### Backend (Railway)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway add postgresql
railway up
```

### Frontend (Render)

1. Push to GitHub
2. Connect Render to repository
3. Configure build settings:
   - **Build Command:** `cd frontend && npm install && npm run build`
   - **Publish Directory:** `frontend/dist`
4. Deploy automatically on git push

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
