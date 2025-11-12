# Technology Stack Details

## Backend Stack

**Core Framework:**
- **FastAPI** (latest from cookiecutter): Async web framework
- **Uvicorn**: ASGI server
- **Python**: ≥3.9 (required by gabeda_core)

**Database:**
- **PostgreSQL 17.5**: Primary database with RLS
- **SQLAlchemy 2.0.44**: ORM with async support
- **asyncpg**: High-performance async PostgreSQL driver
- **Alembic**: Database migrations

**Authentication:**
- **fastapi-users 15.0.1**: User management system
- **httpx-oauth**: Google OAuth integration (included)
- **python-jose**: JWT handling
- **bcrypt**: Password hashing (cost factor 12)

**Background Processing:**
- **Celery 5.5.3**: Distributed task queue
- **Redis 7.x**: Message broker + cache
- **gabeda_core**: CSV processing engine (pandas ≥2.1.0, numpy ≥1.24.0)

**Utilities:**
- **Pydantic**: Data validation and settings
- **structlog** or **loguru**: Structured logging
- **python-multipart**: File upload handling

**Testing:**
- **pytest**: Test framework
- **pytest-asyncio**: Async test support
- **httpx**: Test client for FastAPI
- **pytest-cov**: Code coverage

## Frontend Stack

**Core Framework:**
- **React 19**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool and dev server

**Styling:**
- **Tailwind CSS** (latest): Utility-first CSS
- **shadcn/ui**: Copy-paste component library
- **PostCSS**: CSS processing
- **Autoprefixer**: CSS vendor prefixes

**State Management:**
- **@tanstack/react-query 5.90.7**: Server state
- **zustand 5.0.8**: UI state (theme, language, selected company)

**Routing & Navigation:**
- **react-router-dom**: Client-side routing

**Data Visualization:**
- **recharts 3.4.1**: Charts and graphs

**HTTP Client:**
- **axios**: API requests with interceptors

**Utilities:**
- **date-fns**: Date manipulation and formatting
- **react-i18next**: Internationalization (Spanish/English)

**Testing:**
- **Vitest**: Unit and component tests
- **@testing-library/react**: Component testing utilities
- **Playwright**: E2E testing with browser automation

## Infrastructure

**Development:**
- **Docker**: Local containerization
- **docker-compose**: Multi-service orchestration

**Deployment:**
- **Railway**: Backend + PostgreSQL hosting
- **Render**: Frontend static site hosting
- **GitHub Actions**: CI/CD pipelines

**Monitoring:**
- **Railway Logs**: Application logging (MVP)
- **Sentry** (future): Error tracking
- **Datadog** (future): Performance monitoring

---
