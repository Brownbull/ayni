# Ayni - Architecture Document

**Project:** Ayni - Multi-location retail analytics SaaS platform
**Author:** Gabe (with BMM Architect agent)
**Date:** 2025-11-12
**Version:** 1.0

---

## Executive Summary

Ayni is a multi-tenant SaaS platform that transforms retail analytics for Chilean and Latin American SMBs. This architecture document defines the technical foundation for building a scalable, secure system that handles multi-location analytics, cross-tenant benchmarking, and real-time dashboard performance.

**Key Architectural Principles:**
- **Multi-tenant isolation** via PostgreSQL Row-Level Security
- **Async-first** design for performance (FastAPI + asyncpg + React Query)
- **Early deployment** strategy to catch integration issues early
- **AI agent consistency** through strict implementation patterns
- **Mobile-first reality** with desktop-first development
- **Chilean-specific** localization throughout

**Technology Stack:** FastAPI + PostgreSQL + React 19 + Tailwind CSS + Celery + Redis + gabeda_core

---

## Project Initialization

### First Implementation Story: Setup Foundation

**Backend Setup:**
```bash
# 1. Generate FastAPI cookiecutter
cookiecutter https://github.com/tiangolo/full-stack-fastapi-postgresql

# 2. Commit to preserve reference
cd ayni
git init && git add . && git commit -m "Original FastAPI template"
git tag v0.1-cookiecutter

# 3. Install additional dependencies
cd backend
pip install celery[redis]==5.5.3 redis fastapi-users[sqlalchemy]==15.0.1 gabeda-core
```

**Frontend Setup (Delete Chakra, Build Fresh Tailwind):**
```bash
# 1. Delete entire frontend from cookiecutter
rm -rf frontend/

# 2. Create fresh React + TypeScript + Vite
npm create vite@latest frontend -- --template react-ts
cd frontend

# 3. Install Tailwind CSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# 4. Install core dependencies
npm install axios react-router-dom @tanstack/react-query@5.90.7 zustand@5.0.8
npm install recharts@3.4.1 react-i18next date-fns

# 5. Configure Tailwind (tailwind.config.js)
# Add content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"]

# 6. Add Tailwind directives to src/index.css
# @tailwind base;
# @tailwind components;
# @tailwind utilities;
```

**Early Deployment (Railway + Render):**
```bash
# After basic setup works locally:

# 1. Deploy backend to Railway
railway login
railway init
railway add postgresql
railway up

# 2. Deploy frontend to Render
# Create render.yaml in root:
# - Build command: cd frontend && npm install && npm run build
# - Publish directory: frontend/dist
# Push to GitHub, connect Render to repository

# 3. Test deployed version IMMEDIATELY
# Fix any deployment issues before continuing development
```

This establishes the base architecture with these decisions already made:
- FastAPI backend with async PostgreSQL
- React 19 + TypeScript + Tailwind CSS frontend
- Deployment infrastructure tested early
- No Chakra/Tailwind conflicts (fresh build)

---

## Decision Summary

| Category | Decision | Version | Affects Epics | Rationale |
| -------- | -------- | ------- | ------------- | --------- |
| **Backend Framework** | FastAPI | Latest (cookiecutter) | All backend epics | Async support, OpenAPI docs, production-ready |
| **Database** | PostgreSQL | 17.5 | All data epics | RLS for multi-tenancy, 5-year support, proven reliability |
| **ORM** | SQLAlchemy | 2.0.44 | All database operations | Async support, mature, excellent documentation |
| **DB Driver** | asyncpg | Latest | All database operations | High-performance async PostgreSQL driver |
| **Database Hosting** | Railway PostgreSQL | Managed | All epics | Same platform as backend, managed backups, simple setup |
| **Background Jobs** | Celery | 5.5.3 | CSV processing, aggregation | Python native, handles 5-min aggregation requirement |
| **Message Broker/Cache** | Redis | 7.x | Background jobs, caching | Required for Celery, enables dashboard caching |
| **User Management** | fastapi-users | 15.0.1 | Authentication, user management | Pre-built OAuth, JWT, email verification, password reset |
| **OAuth Library** | httpx-oauth | Included in fastapi-users | Google OAuth | Async OAuth 2.0, Google integration built-in |
| **CSV Processing Engine** | gabeda_core | ≥Python 3.9, pandas ≥2.1.0 | CSV upload, data processing | Existing analytics engine, 4-case logic, single-loop execution |
| **Frontend Framework** | React | 19 + TypeScript | All frontend epics | Modern, component-based, excellent ecosystem |
| **Build Tool** | Vite | Latest | Frontend build | Fast dev server, HMR, optimized production builds |
| **Styling** | Tailwind CSS | Latest | All UI components | Utility-first, no framework conflicts, fully customizable |
| **UI Components** | shadcn/ui | Latest | Reusable components | Copy-paste components, not a dependency, Tailwind-based |
| **Server State** | TanStack React Query | 5.90.7 | API calls, caching | Auto-refetch, cache management, loading states |
| **UI State** | Zustand | 5.0.8 | Theme, language, UI state | Lightweight (1KB), simple API, localStorage persistence |
| **Charts** | Recharts | 3.4.1 | Dashboard visualizations | React components, beautiful defaults, easy customization |
| **Date Library** | date-fns | Latest | Date formatting, timezone | Lightweight, tree-shakeable, Chilean format support |
| **i18n** | react-i18next | Latest | Localization | Spanish/English support, React integration |
| **API Pattern** | REST | v1 | All API endpoints | Simple, well-understood, versioned (/api/v1/) |
| **Backend Testing** | pytest + pytest-asyncio | Latest | All backend tests | Python standard, async support, 70% coverage goal |
| **Frontend Testing** | Vitest + Playwright | Latest | Component + E2E tests | Vite-native, fast, Chrome DevTools verification |
| **Backend Deployment** | Railway | Managed | Backend hosting | Managed services, PostgreSQL included, simple deployment |
| **Frontend Deployment** | Render | Managed | Frontend hosting | Static site CDN, GitHub integration, auto-deploy |
| **Logging** | structlog/loguru | Latest | All logging | Structured JSON, tenant context, gabeda_core integration |
| **Monitoring** | Railway Logs | Built-in | Operations monitoring | Included with hosting, sufficient for MVP |

---

## Project Structure

```
ayni/
├── backend/                      # FastAPI application
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/              # API version 1
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── auth.py            # fastapi-users routes
│   │   │   │   │   ├── companies.py       # Company CRUD
│   │   │   │   │   ├── locations.py       # Location CRUD
│   │   │   │   │   ├── data.py            # CSV upload/processing
│   │   │   │   │   ├── analytics.py       # Dashboard data
│   │   │   │   │   └── benchmarks.py      # Cross-tenant comparisons
│   │   │   │   └── router.py              # V1 router aggregation
│   │   │   └── deps.py                     # Dependencies (get_db, get_current_user)
│   │   ├── core/
│   │   │   ├── config.py          # Settings (Pydantic BaseSettings)
│   │   │   ├── security.py        # JWT, password hashing
│   │   │   └── logging.py         # Structured logging setup
│   │   ├── models/
│   │   │   ├── user.py            # User model (fastapi-users)
│   │   │   ├── company.py         # Company + RLS policies
│   │   │   ├── location.py        # Location model
│   │   │   ├── transaction.py     # Raw transactions
│   │   │   ├── aggregates.py      # Multi-temporal aggregates
│   │   │   ├── mapping_template.py # CSV column mappings
│   │   │   └── benchmark.py       # Sector benchmarks
│   │   ├── schemas/
│   │   │   ├── user.py            # Pydantic schemas
│   │   │   ├── company.py
│   │   │   ├── location.py
│   │   │   ├── transaction.py
│   │   │   ├── analytics.py
│   │   │   └── response.py        # Wrapped response format
│   │   ├── services/
│   │   │   ├── csv_processor.py   # CSV validation + gabeda_core integration
│   │   │   ├── aggregation.py     # Multi-temporal aggregation logic
│   │   │   ├── benchmarking.py    # Cross-tenant calculations
│   │   │   └── rls.py             # RLS policy management
│   │   ├── workers/
│   │   │   ├── celery_app.py      # Celery configuration
│   │   │   └── tasks.py           # Celery tasks (CSV processing, aggregation)
│   │   ├── db/
│   │   │   ├── base.py            # SQLAlchemy base + session
│   │   │   ├── init_db.py         # Database initialization
│   │   │   └── rls_policies.sql   # PostgreSQL RLS policies
│   │   ├── tests/
│   │   │   ├── unit/              # Unit tests (1 mock + 1 real minimum)
│   │   │   ├── integration/       # API tests with test DB
│   │   │   └── conftest.py        # Pytest fixtures
│   │   └── main.py                # FastAPI app entry point
│   ├── alembic/                   # Database migrations
│   ├── requirements.txt           # Python dependencies
│   ├── Dockerfile                 # Backend container
│   └── .env                       # Environment variables
│
├── frontend/                      # React application (Fresh Tailwind build)
│   ├── src/
│   │   ├── api/
│   │   │   ├── client.ts          # Axios with JWT interceptors
│   │   │   ├── auth.ts            # Auth API calls
│   │   │   ├── companies.ts       # Company API calls
│   │   │   ├── locations.ts       # Location API calls
│   │   │   ├── data.ts            # CSV upload API
│   │   │   └── analytics.ts       # Dashboard data API
│   │   ├── components/
│   │   │   ├── auth/              # Login, Register components
│   │   │   ├── layout/            # Navigation, Header, Footer
│   │   │   ├── dashboard/         # Dashboard cards, charts
│   │   │   ├── upload/            # CSV upload + column mapping
│   │   │   ├── locations/         # Location management
│   │   │   └── common/            # Reusable UI components
│   │   ├── hooks/
│   │   │   ├── useAuth.ts         # Authentication hook
│   │   │   ├── useCompany.ts      # Company context hook
│   │   │   └── useAnalytics.ts    # Dashboard data hooks
│   │   ├── pages/
│   │   │   ├── Login.tsx
│   │   │   ├── Dashboard.tsx      # Main dashboard
│   │   │   ├── MonthlyView.tsx    # Monthly deep dive
│   │   │   ├── LocationView.tsx   # Location-specific view
│   │   │   ├── Upload.tsx         # CSV upload page
│   │   │   └── Settings.tsx       # Company/user settings
│   │   ├── store/
│   │   │   ├── uiStore.ts         # Zustand: theme, language, selected company
│   │   │   └── types.ts           # TypeScript types
│   │   ├── utils/
│   │   │   ├── format.ts          # Chilean number/date formatting
│   │   │   ├── i18n.ts            # react-i18next setup
│   │   │   └── constants.ts       # App constants
│   │   ├── styles/
│   │   │   └── index.css          # Tailwind imports
│   │   ├── tests/
│   │   │   ├── components/        # Vitest component tests
│   │   │   └── e2e/               # Playwright E2E tests
│   │   ├── App.tsx                # Root component
│   │   └── main.tsx               # Entry point
│   ├── public/                    # Static assets
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts             # Vite configuration
│   ├── tailwind.config.js         # Tailwind CSS config
│   ├── tsconfig.json              # TypeScript config
│   └── playwright.config.ts       # Playwright E2E config
│
├── docs/                          # Documentation
│   ├── PRD.md
│   ├── ux-design-specification.md
│   ├── architecture.md            # This document
│   └── Gabe_concerns.md          # Deployment & testing concerns
│
├── .github/
│   └── workflows/
│       ├── backend-tests.yml      # CI for backend
│       └── frontend-tests.yml     # CI for frontend
│
├── docker-compose.yml             # Local development
└── README.md
```

---

## Epic to Architecture Mapping

| Epic | Backend Components | Frontend Components | Database Tables | External Services |
|------|-------------------|---------------------|-----------------|-------------------|
| **Authentication & User Management** | `api/v1/endpoints/auth.py`, fastapi-users | `pages/Login.tsx`, `hooks/useAuth.ts` | `users` | Google OAuth |
| **Company Management** | `api/v1/endpoints/companies.py`, RLS policies | `components/companies/`, `hooks/useCompany.ts` | `companies` | - |
| **Multi-Location Support** | `api/v1/endpoints/locations.py` | `pages/LocationView.tsx`, `components/locations/` | `locations` | - |
| **CSV Upload & Column Mapping** | `api/v1/endpoints/data.py`, `services/csv_processor.py` | `pages/Upload.tsx`, `components/upload/ColumnMapper.tsx` | `transactions`, `mapping_templates` | gabeda_core |
| **Multi-Temporal Aggregation** | `workers/tasks.py`, `services/aggregation.py` | N/A (background processing) | `aggregates_hourly`, `aggregates_daily`, `aggregates_weekly`, `aggregates_monthly`, `aggregates_quarterly`, `aggregates_yearly` | Celery + Redis |
| **Dashboard Analytics** | `api/v1/endpoints/analytics.py` | `pages/Dashboard.tsx`, `components/dashboard/` | `aggregates_*`, `companies`, `locations` | - |
| **Cross-Tenant Benchmarking** | `api/v1/endpoints/benchmarks.py`, `services/benchmarking.py` | `components/dashboard/PercentileCard.tsx` | `benchmarks`, `sector_averages` | - |
| **Internationalization** | API responses with i18n | react-i18next, `utils/i18n.ts` | - | - |
| **Billing & Subscriptions** (Post-MVP) | Stripe integration endpoints | `pages/Billing.tsx` | `subscriptions`, `payments` | Stripe |

---

## Technology Stack Details

### Backend Stack

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

### Frontend Stack

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

### Infrastructure

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

## Integration Points

### Backend ↔ Frontend

**Protocol:** REST API with JSON
**Base URL:** `https://api.ayni.cl/api/v1/` (production)
**Authentication:** JWT Bearer tokens in `Authorization` header

**Request Format:**
```json
POST /api/v1/companies
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "name": "Mi Empresa",
  "country": "Chile",
  "identifier": "12.345.678-9"
}
```

**Response Format (Success):**
```json
{
  "status": "success",
  "data": {
    "id": 123,
    "name": "Mi Empresa",
    "country": "Chile",
    "identifier": "12.345.678-9",
    "created_at": "2025-11-12T10:30:00-03:00"
  },
  "message": null
}
```

**Response Format (Error):**
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": [
    {
      "field": "identifier",
      "message": "RUT inválido para Chile"
    }
  ]
}
```

### Backend ↔ Database

**Connection:** SQLAlchemy async engine with asyncpg
**Tenant Isolation:** PostgreSQL Row-Level Security (RLS)
**Connection Pool:** Min 5, Max 20 connections

**RLS Context Setup (Every Request):**
```python
# Set tenant context from JWT token
await session.execute(
    text("SELECT set_config('app.current_tenant', :tenant_id, false)"),
    {"tenant_id": current_user.tenant_id}
)

# All subsequent queries automatically filtered by tenant_id
```

**Migration Strategy:**
```bash
# Create new migration
alembic revision --autogenerate -m "Add locations table"

# Apply migrations
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### Backend ↔ Celery/Redis

**Message Broker:** Redis (same instance as cache)
**Task Routing:** Default queue for all tasks (MVP)
**Result Backend:** Redis

**Task Definition:**
```python
from app.workers.celery_app import celery_app

@celery_app.task(bind=True, max_retries=3)
def process_csv_task(self, file_path: str, company_id: int, mapping_id: int):
    try:
        # Use gabeda_core for processing
        from gabeda.core import process_data
        result = process_data(file_path, mapping_id)

        # Trigger aggregation after processing
        trigger_aggregation.delay(company_id)

        return {"status": "success", "rows": result.count}
    except Exception as exc:
        # Exponential backoff: 60s, 120s, 240s
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

**Task Invocation:**
```python
# From API endpoint
task = process_csv_task.delay(file_path, company_id, mapping_id)
return {"task_id": task.id, "status": "processing"}
```

### Backend ↔ gabeda_core

**Integration:** Python package import (gabeda-core)
**Logging:** Configure gabeda_core logger to use app logger
**Data Flow:** CSV file → Validation → gabeda_core processing → Database
**Validation Pattern:** From notebook `03_consolidated_all_models.ipynb`

**Complete Validation + Processing Flow:**
```python
from gabeda.preprocessing.loaders import DataLoader
from gabeda.preprocessing.validators import DataValidator
from gabeda.preprocessing.schema import SchemaProcessor
from gabeda.preprocessing.synthetic import SyntheticEnricher
from app.core.logging import logger

# Configure gabeda_core logger
import logging
gabeda_logger = logging.getLogger('gabeda')
gabeda_logger.addHandler(logger.handlers[0])

# ============================================================
# STEP 1: Load raw CSV
# ============================================================
loader = DataLoader()
raw_data = loader.load_csv(file_path)
logger.info(f"Loaded raw data: {raw_data.shape}", tenant_id=company_id)

# ============================================================
# STEP 2: Phase 1 Validation - Schema & Structure
# ============================================================
validator = DataValidator()
required_cols = [spec['source_column'] for spec in mapping_template.items()]

validation = validator.validate_all(
    df=raw_data,
    required_cols=required_cols,
    data_schema=mapping_template,
    default_formats=default_formats
)

if not validation.is_valid:
    logger.error("Validation failed", tenant_id=company_id, errors=validation.errors)
    return ValidationError(
        message="Validación fallida",
        errors=validation.errors,
        rejected_rows=len(raw_data),
        total_rows=len(raw_data)
    )

# Log warnings (non-blocking)
if validation.warnings:
    logger.warning(f"Validation warnings: {len(validation.warnings)}",
                   tenant_id=company_id, warnings=validation.warnings[:5])

# ============================================================
# STEP 3: Process schema (column mapping + type conversion)
# ============================================================
schema_processor = SchemaProcessor()
preprocessed_df = schema_processor.process_schema(raw_data, mapping_template).df
logger.info(f"Schema processed: {preprocessed_df.shape}", tenant_id=company_id)

# ============================================================
# STEP 4: Synthetic enrichment (optional)
# ============================================================
enricher = SyntheticEnricher(synthetic_model_name='synthetic')
preprocessed_df = enricher.enrich(data=preprocessed_df)

# ============================================================
# STEP 5: Phase 2 Validation - Row-level required fields
# ============================================================
validated_df, reject_result = validator.validate_row_level_required_fields(
    df=preprocessed_df,
    data_schema=mapping_template,
    save_to_file=False
)

# Log data quality metrics
logger.info(
    "Validation complete",
    tenant_id=company_id,
    total_rows=len(preprocessed_df),
    clean_rows=len(validated_df),
    rejected_rows=len(reject_result.rejected_rows) if reject_result.rejected_rows is not None else 0,
    rejection_rate=f"{(len(reject_result.rejected_rows) / len(preprocessed_df) * 100):.2f}%" if reject_result.rejected_rows is not None else "0.00%"
)

# ============================================================
# STEP 6: Process validated data with gabeda_core
# ============================================================
from gabeda.core import process_data

result = process_data(
    data=validated_df,
    mapping_template=mapping_template,
    company_id=company_id
)

# ============================================================
# STEP 7: Return results
# ============================================================
return ProcessingResult(
    validated_df=validated_df,
    rejected_rows=reject_result.rejected_rows,
    processing_result=result,
    metrics={
        "total_rows": len(preprocessed_df),
        "clean_rows": len(validated_df),
        "rejected_rows": len(reject_result.rejected_rows) if reject_result.rejected_rows is not None else 0
    }
)
```

**Validation Classes from gabeda_core:**
- `DataValidator.validate_all()`: Schema + structure validation
  - Checks: Column existence, data types, date formats, numeric formats, duplicate IDs
- `DataValidator.validate_row_level_required_fields()`: Row-level validation
  - Checks: Required fields not null, valid ranges, business logic constraints
- Returns: `ValidationResult` with `is_valid`, `errors`, `warnings`

### Frontend ↔ React Query

**Cache Strategy:**
- **Dashboard data:** 5-minute cache, auto-refetch
- **User profile:** 1-hour cache
- **Company list:** Cached until mutation

**Query Example:**
```typescript
import { useQuery } from '@tanstack/react-query';
import { fetchDashboardData } from '@/api/analytics';

function Dashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard', companyId, year],
    queryFn: () => fetchDashboardData(companyId, year),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: true,
  });

  if (isLoading) return <DashboardSkeleton />;
  if (error) return <ErrorToast message={error.message} />;

  return <DashboardView data={data.data} />;
}
```

**Mutation Example:**
```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { uploadCSV } from '@/api/data';

function UploadPage() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: uploadCSV,
    onSuccess: () => {
      // Invalidate dashboard cache
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      toast.success('CSV procesado exitosamente');
    },
  });

  return <UploadForm onSubmit={mutation.mutate} />;
}
```

---

## Data Architecture

### Database Schema

**Core Tables:**

```sql
-- Users (managed by fastapi-users)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(320) UNIQUE NOT NULL,
    hashed_password VARCHAR(1024) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Companies (multi-tenant)
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    owner_id UUID NOT NULL REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    country VARCHAR(2) NOT NULL, -- ISO 3166-1 alpha-2
    identifier VARCHAR(50) NOT NULL, -- RUT for Chile, other for non-Chile
    industry VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(identifier)
);

-- Row-Level Security Policy
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON companies
    USING (id = current_setting('app.current_tenant', TRUE)::INTEGER);

-- Locations (1-N per company)
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    address TEXT, -- For physical stores
    website VARCHAR(500), -- For web-based businesses
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- RLS for locations
ALTER TABLE locations ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON locations
    USING (company_id = current_setting('app.current_tenant', TRUE)::INTEGER);

-- Raw Transactions
CREATE TABLE transactions (
    id BIGSERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    location_id INTEGER NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
    transaction_datetime TIMESTAMP NOT NULL,
    transaction_id VARCHAR(100) NOT NULL,
    product_id VARCHAR(100) NOT NULL,
    quantity DECIMAL(10, 2) NOT NULL,
    price_total DECIMAL(12, 2) NOT NULL,
    cost_total DECIMAL(12, 2),
    margin DECIMAL(12, 2),
    customer_id VARCHAR(100),
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(company_id, transaction_id)
);

-- Partitioned by company_id for scale
CREATE INDEX idx_transactions_company_datetime
    ON transactions(company_id, transaction_datetime DESC);

-- RLS for transactions
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON transactions
    USING (company_id = current_setting('app.current_tenant', TRUE)::INTEGER);

-- CSV Mapping Templates
CREATE TABLE mapping_templates (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    mapping JSONB NOT NULL, -- Column mappings
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Aggregates (Multi-Temporal)
CREATE TABLE aggregates_daily (
    id BIGSERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    location_id INTEGER NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    revenue DECIMAL(12, 2) NOT NULL,
    transactions_count INTEGER NOT NULL,
    avg_transaction DECIMAL(12, 2),
    growth_pct DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(company_id, location_id, date)
);

-- Similar tables: aggregates_hourly, aggregates_weekly,
-- aggregates_monthly, aggregates_quarterly, aggregates_yearly

-- Benchmarks (Cross-Tenant)
CREATE TABLE sector_averages (
    id SERIAL PRIMARY KEY,
    industry VARCHAR(100) NOT NULL,
    country VARCHAR(2) NOT NULL,
    period_type VARCHAR(20) NOT NULL, -- monthly, yearly
    period_date DATE NOT NULL,
    avg_revenue DECIMAL(12, 2) NOT NULL,
    company_count INTEGER NOT NULL, -- For transparency
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(industry, country, period_type, period_date)
);

-- No RLS on sector_averages (aggregated, anonymous data)
```

### Data Flow

**CSV Upload Flow (with gabeda_core Validation):**

**Step 1: File Upload → Preview (Frontend)**
1. User selects CSV file
2. Frontend reads first 10 rows client-side
3. Display preview table to user
4. Show detected columns

**Step 2: Column Mapping UI (Frontend)**
1. Display column mapping interface:
   - CSV columns (from file header) → System columns (in_dt, in_trans_id, etc.)
   - Dropdown to map each CSV column to system column
   - Format selector per column:
     - Date format: DD/MM/YYYY, YYYY-MM-DD, MM/DD/YYYY HH:MM, etc.
     - Number format: Integer, Decimal (with thousands/decimal separators)
     - Text format: String
2. Allow saving mapping as template for future uploads
3. Pre-validation (client-side):
   - Required columns mapped (in_dt, in_trans_id, in_product_id, in_quantity, in_price_total)
   - No duplicate mappings
   - File size < MAX_SIZE (10MB)

**Step 3: Upload → Backend Validation (gabeda_core pattern)**
1. POST to `/api/v1/data/upload` with file + mapping
2. Backend saves to `/tmp/uploads/{uuid}.csv`
3. **Phase 1: Schema & Structure Validation** (before processing):
   ```python
   validator = DataValidator()
   validation = validator.validate_all(
       df=raw_data,
       required_cols=required_cols,
       data_schema=mapping_template,
       default_formats=default_formats
   )
   ```

   Checks:
   - ✓ File can be read as CSV
   - ✓ Mapped columns exist in CSV
   - ✓ Required columns present (in_dt, in_trans_id, in_product_id, in_quantity, in_price_total)
   - ✓ Column data types match expected types
   - ✓ Date format can parse dates
   - ✓ Numeric columns contain valid numbers
   - ✓ No duplicate transaction IDs

   If validation fails:
   - Return error response with specific validation messages
   - User sees errors in UI (Spanish)
   - User can fix mapping or CSV and retry

**Step 4: If Valid → Process Schema (Backend)**
1. Apply column mapping (CSV columns → system columns)
2. Convert data types (dates, numbers, strings)
3. Apply number format parsing (Chilean formats: 1.234.567,89)
4. Enrich with synthetic columns (if needed by gabeda_core)

**Step 5: Row-Level Validation (Backend)**
1. **Phase 2: Row-Level Required Fields Validation**:
   ```python
   validated_df, reject_result = validator.validate_row_level_required_fields(
       df=preprocessed_df,
       data_schema=mapping_template
   )
   ```

   Checks per row:
   - ✓ Required fields not null
   - ✓ Dates within reasonable range
   - ✓ Quantities > 0
   - ✓ Prices > 0
   - ✓ Transaction IDs unique

   Result:
   - `validated_df`: Clean rows ready for processing
   - `reject_result`: Rejected rows with reasons

   Data quality report:
   - Total rows: X
   - Clean rows: Y
   - Rejected rows: Z (with reasons)

**Step 6: Queue Processing (Backend)**
1. If validation passed:
   - Create Celery task with validated data
   - Return task_id to user
   - Status: "processing"
2. If validation failed:
   - Return error response with rejected rows
   - User can download rejected rows CSV
   - User fixes data and re-uploads

**Step 7: Celery Worker Processing**
1. Use gabeda_core to process validated CSV:
   ```python
   result = gabeda_core.process_data(file_path, mapping_template)
   ```
2. Insert into `transactions` table in batches (1000 rows/batch)
3. Trigger multi-temporal aggregation pipeline
4. Delete temp file
5. Update task status: "completed"
6. Log data quality metrics:
   - Rows processed
   - Processing time
   - Any warnings

**Step 8: User Notification (Frontend)**
1. Poll `/api/v1/data/status/{task_id}` every 2 seconds
2. Show progress:
   - "Validando archivo..." (validating)
   - "Procesando 3.421 transacciones..." (processing)
   - "¡Datos actualizados!" (complete)
3. If errors:
   - Display validation errors
   - Option to download rejected rows
   - Retry button

**Validation Error Response Format:**
```json
{
  "status": "error",
  "message": "Validación fallida",
  "errors": [
    {
      "type": "missing_column",
      "column": "in_dt",
      "message": "Columna requerida 'in_dt' no encontrada en CSV"
    },
    {
      "type": "invalid_format",
      "column": "in_dt",
      "row": 15,
      "value": "invalid-date",
      "message": "Formato de fecha inválido en fila 15: 'invalid-date'"
    },
    {
      "type": "duplicate_transaction",
      "column": "in_trans_id",
      "rows": [23, 45],
      "value": "TXN-12345",
      "message": "ID de transacción duplicado: 'TXN-12345' en filas 23, 45"
    }
  ],
  "rejected_rows": 3,
  "total_rows": 100,
  "rejection_rate": 3.0
}
```

**Aggregation Pipeline Flow:**
1. Triggered by Celery task (scheduled nightly + on-demand after upload)
2. For each company/location:
   - Calculate hourly aggregates from transactions
   - Roll up to daily aggregates
   - Roll up to weekly, monthly, quarterly, yearly
3. Store in respective `aggregates_*` tables
4. Invalidate Redis cache for affected dashboards
5. Log completion with row counts

**Benchmarking Flow:**
1. Scheduled Celery task runs nightly
2. For each industry + country:
   - Aggregate monthly revenue across all companies (anonymized)
   - Calculate percentiles (25th, 50th, 75th, 90th)
   - Store in `sector_averages` table
3. API endpoint calculates user's percentile on-demand
4. Cache results in Redis (24h TTL)

---

## API Contracts

### Authentication Endpoints

**Register:**
```
POST /api/v1/auth/register
Body: {"email": "user@example.com", "password": "SecurePass123!"}
Response: {"status": "success", "data": {"id": "uuid", "email": "user@example.com"}}
```

**Login:**
```
POST /api/v1/auth/login
Body: {"username": "user@example.com", "password": "SecurePass123!"}
Response: {
  "status": "success",
  "data": {
    "access_token": "jwt_token",
    "token_type": "bearer",
    "expires_in": 86400
  }
}
```

**Google OAuth:**
```
GET /api/v1/auth/google/authorize
Response: {"authorization_url": "https://accounts.google.com/..."}

GET /api/v1/auth/google/callback?code=...
Response: {"status": "success", "data": {"access_token": "...", "token_type": "bearer"}}
```

### Company Endpoints

**List Companies:**
```
GET /api/v1/companies
Headers: Authorization: Bearer {token}
Response: {
  "status": "success",
  "data": [
    {"id": 1, "name": "Mi Empresa", "country": "CL"}
  ]
}
```

**Create Company:**
```
POST /api/v1/companies
Headers: Authorization: Bearer {token}
Body: {
  "name": "Mi Empresa",
  "country": "CL",
  "identifier": "12.345.678-9",
  "first_location": {
    "name": "Casa Matriz",
    "address": "Av. Providencia 123, Santiago"
  }
}
Response: {
  "status": "success",
  "data": {
    "id": 1,
    "name": "Mi Empresa",
    "locations": [{"id": 1, "name": "Casa Matriz", "is_primary": true}]
  }
}
```

### Location Endpoints

**List Locations:**
```
GET /api/v1/companies/{company_id}/locations
Response: {
  "status": "success",
  "data": [
    {"id": 1, "name": "Casa Matriz", "address": "...", "is_primary": true},
    {"id": 2, "name": "Sucursal Las Condes", "address": "...", "is_primary": false}
  ]
}
```

**Add Location:**
```
POST /api/v1/companies/{company_id}/locations
Body: {"name": "Nueva Sucursal", "address": "..."}
Response: {"status": "success", "data": {"id": 3, "name": "Nueva Sucursal"}}
```

### Data Endpoints

**Preview CSV (Before Upload):**
```
POST /api/v1/data/preview
Headers: Content-Type: multipart/form-data
Body: file={csv_file}
Response: {
  "status": "success",
  "data": {
    "columns": ["in_dt", "in_trans_id", "in_product_id", "in_quantity", "in_price_total"],
    "preview": [
      {"in_dt": "01/10/2025 10:30", "in_trans_id": "TXN-001", "in_product_id": "PROD1", "in_quantity": "5", "in_price_total": "1.234,56"},
      // ... 9 more rows
    ],
    "row_count": 3421,
    "file_size_mb": 2.5
  }
}
```

**Upload CSV (with Mapping):**
```
POST /api/v1/data/upload
Headers: Content-Type: multipart/form-data
Body: {
  file={csv_file},
  location_id={id},
  mapping={
    "in_dt": {"source_column": "Fecha", "dtype": "date", "format": "%d/%m/%Y %H:%M"},
    "in_trans_id": {"source_column": "ID Transacción", "dtype": "str"},
    "in_product_id": {"source_column": "Producto", "dtype": "str"},
    "in_quantity": {"source_column": "Cantidad", "dtype": "float"},
    "in_price_total": {"source_column": "Total", "dtype": "float"}
  }
}

Response (Success - Validation Passed):
{
  "status": "success",
  "data": {
    "task_id": "uuid",
    "status": "processing",
    "estimated_time": "30 seconds",
    "rows_to_process": 3421
  }
}

Response (Error - Validation Failed):
{
  "status": "error",
  "message": "Validación fallida",
  "errors": [
    {
      "type": "missing_column",
      "column": "in_dt",
      "message": "Columna requerida 'in_dt' no encontrada en CSV"
    },
    {
      "type": "invalid_format",
      "column": "in_dt",
      "row": 15,
      "value": "invalid-date",
      "message": "Formato de fecha inválido en fila 15"
    }
  ],
  "rejected_rows": 3,
  "total_rows": 100,
  "rejection_rate": 3.0,
  "rejected_rows_download_url": "/api/v1/data/rejected/{task_id}.csv"
}
```

**Check Upload Status:**
```
GET /api/v1/data/status/{task_id}
Response: {
  "status": "success",
  "data": {
    "task_id": "uuid",
    "status": "completed",
    "rows_processed": 3421,
    "errors": []
  }
}
```

### Analytics Endpoints

**Get Dashboard Data:**
```
GET /api/v1/analytics/dashboard?company_id=1&year=2025&view=annual
Response: {
  "status": "success",
  "data": {
    "company": {"id": 1, "name": "Mi Empresa"},
    "year": 2025,
    "months": [
      {
        "month": 1,
        "revenue": 1234567,
        "growth_pct": 12.5,
        "performance_index": 85,
        "alert_level": "success"
      },
      // ... 11 more months
    ],
    "locations": [
      {
        "location_id": 1,
        "name": "Casa Matriz",
        "revenue": 5000000,
        "performance": "high"
      }
    ]
  }
}
```

**Get Benchmark Data:**
```
GET /api/v1/analytics/benchmarks?company_id=1&period=monthly&date=2025-11
Response: {
  "status": "success",
  "data": {
    "your_revenue": 1234567,
    "sector_average": 980000,
    "percentile": 68,
    "rank_tier": "blue",
    "sector_info": {
      "industry": "Retail",
      "country": "CL",
      "company_count": 150
    }
  }
}
```

---

## Security Architecture

### Authentication & Authorization

**JWT Token Structure:**
```json
{
  "sub": "user_uuid",
  "tenant_id": 123,
  "role": "owner",
  "permissions": ["read", "write", "manage_users"],
  "exp": 1731441000,
  "iat": 1731354600
}
```

**Token Lifecycle:**
- **Access Token:** 24-hour expiration
- **Refresh Token:** 30-day expiration, rotated on use
- **Storage:** Frontend stores in memory + httpOnly cookie (refresh token)

**Password Security:**
- **Hashing:** bcrypt with cost factor 12
- **Validation:** Minimum 8 characters, uppercase, lowercase, number
- **Reset:** Time-limited token (1 hour), email verification required

### Multi-Tenant Isolation

**Database Level (PostgreSQL RLS):**
```sql
-- Enable RLS on all tenant tables
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE locations ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE aggregates_daily ENABLE ROW LEVEL SECURITY;

-- Isolation policy
CREATE POLICY tenant_isolation_policy ON {table_name}
    USING (company_id = current_setting('app.current_tenant', TRUE)::INTEGER);

-- Set context on every request
SELECT set_config('app.current_tenant', '123', false);
```

**Application Level:**
```python
# Middleware sets tenant context from JWT
@app.middleware("http")
async def set_tenant_context(request: Request, call_next):
    # Extract tenant_id from JWT token
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = jwt.decode(token, SECRET_KEY)
    tenant_id = payload.get("tenant_id")

    # Set PostgreSQL RLS context
    async with get_db() as session:
        await session.execute(
            text("SELECT set_config('app.current_tenant', :tenant_id, false)"),
            {"tenant_id": tenant_id}
        )

    response = await call_next(request)
    return response
```

**Validation:**
- ❌ NEVER accept tenant_id from client requests
- ✅ ALWAYS derive tenant_id from authenticated JWT token
- ✅ ALWAYS set RLS context before any database query
- ✅ Log all cross-tenant access attempts as security incidents

### Data Protection

**Encryption:**
- **In Transit:** TLS 1.3 for all connections
- **At Rest:** PostgreSQL encryption (Railway managed)
- **Passwords:** bcrypt hashed, never stored plain

**Input Validation:**
- **API Level:** Pydantic schemas validate all inputs
- **SQL Injection:** Prevented by SQLAlchemy parameterized queries
- **XSS:** React escapes all user input by default
- **CSRF:** SameSite cookies + custom headers

**Rate Limiting:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/data/upload")
@limiter.limit("10/hour")  # 10 uploads per hour per IP
async def upload_csv(...):
    pass
```

### Compliance

**Chilean Data Protection Law 19.628:**
- Users can request data deletion (GDPR-like right)
- Audit logs retained for 1 year
- Data exports available in machine-readable format

**Security Headers:**
```python
@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response
```

---

## Implementation Patterns (Agent Consistency Rules)

### NAMING PATTERNS

**Backend (Python):**
- Files: `snake_case.py` (e.g., `csv_processor.py`)
- Classes: `PascalCase` (e.g., `CompanyService`)
- Functions: `snake_case` (e.g., `process_csv_file`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_FILE_SIZE`)
- Database Tables: `snake_case` plural (e.g., `companies`, `transactions`)
- Database Columns: `snake_case` (e.g., `company_id`, `created_at`)

**Frontend (TypeScript):**
- Component Files: `PascalCase.tsx` (e.g., `Dashboard.tsx`)
- Utility Files: `camelCase.ts` (e.g., `formatCurrency.ts`)
- Components: `PascalCase` (e.g., `UploadCSV`)
- Functions: `camelCase` (e.g., `fetchDashboardData`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `API_BASE_URL`)
- Interfaces: `PascalCase` with `I` prefix (e.g., `IUser`)
- Types: `PascalCase` (e.g., `CompanyData`)

**API Endpoints:**
- Format: `/api/v1/resource` (plural nouns)
- Parameters: `{id}` not `:id`
- Query params: `snake_case` (e.g., `?company_id=123`)
- Examples:
  - ✅ `/api/v1/companies/{id}/locations`
  - ❌ `/api/v1/company/:id/location`

### STRUCTURE PATTERNS

**Backend:**
- Tests co-located in `tests/` directory, mirror source structure
- One service per file, each handles one domain
- Models in separate files: one model per file in `models/`

**Frontend:**
- Components organized by feature, not by type
  - ✅ `components/dashboard/MonthlyCard.tsx`
  - ❌ `components/cards/MonthlyCard.tsx`
- Tests co-located with components
  - `components/dashboard/MonthlyCard.tsx`
  - `components/dashboard/MonthlyCard.test.tsx`
- One component per file

### FORMAT PATTERNS

**API Response Wrapper (MANDATORY):**
```json
{
  "status": "success",
  "data": {...},
  "message": null
}
```

**Error Response (MANDATORY):**
```json
{
  "status": "error",
  "message": "User-friendly message in Spanish",
  "errors": [
    {"field": "email", "message": "Invalid format"}
  ]
}
```

**Date Format in API:**
- Send: ISO 8601 with timezone: `"2025-11-12T10:30:00-03:00"`
- Receive: ISO 8601 UTC: `"2025-11-12T13:30:00Z"`
- Display: DD/MM/YYYY (Chilean format)

**Numbers in JSON:**
- Currency: Raw numbers (no formatting): `1234567`
- Percentages: Decimals: `0.685` (not `68.5`)
- Frontend formats for display

**Chilean Formatting:**
```typescript
// Currency
const formatCurrency = (amount: number) =>
  new Intl.NumberFormat('es-CL', {
    style: 'currency',
    currency: 'CLP',
    minimumFractionDigits: 0
  }).format(amount);
// Output: $1.234.567

// Numbers
const formatNumber = (num: number) =>
  new Intl.NumberFormat('es-CL').format(num);
// Output: 1.234.567,89
```

### COMMUNICATION PATTERNS

**Database Queries (MANDATORY):**
```python
# ALWAYS use async
result = await session.execute(select(Company).where(...))

# ALWAYS filter by tenant (RLS handles this, but for clarity)
await session.execute(
    text("SELECT set_config('app.current_tenant', :tenant_id, false)"),
    {"tenant_id": current_user.tenant_id}
)

# ALWAYS use transactions for writes
async with session.begin():
    session.add(new_company)
    await session.commit()
```

**API Calls (Frontend - MANDATORY):**
```typescript
// ALWAYS use React Query
const { data, isLoading } = useQuery({
  queryKey: ['companies'],
  queryFn: fetchCompanies,
});

// NEVER use bare axios/fetch in components
// ❌ Bad: axios.get('/api/companies')
// ✅ Good: useQuery with React Query
```

### LIFECYCLE PATTERNS

**Loading States:**
- Backend: Return 202 Accepted for async operations
- Frontend: Skeleton screens (not spinners)

**Error Recovery:**
- Backend: Celery tasks retry 3 times, exponential backoff
- Frontend: React Query retries 3 times for failed requests

**State Management:**
- Server State: React Query (auto-refetch every 5 minutes)
- UI State: Zustand (persisted to localStorage)

### CONSISTENCY PATTERNS

**Dates Everywhere:**
- Backend: Store UTC, convert to Santiago timezone for display
- Frontend: Use `date-fns` for all date operations
- Display: DD/MM/YYYY (Chilean format)

**Currency Everywhere:**
- Backend: Store as DECIMAL(12, 2)
- Frontend: Format with `Intl.NumberFormat('es-CL')`
- Display: $1.234.567 CLP

**Error Messages:**
- Primary: Spanish (Chilean Spanish)
- Include: English translation in `message_en` field
- User-facing: Never show stack traces

**Logging Everywhere:**
- Include: `tenant_id`, `user_id`, `request_id` in all logs
- Format: Structured JSON
- Level: INFO (operations), ERROR (failures), WARNING (security)

### SECURITY PATTERNS (CRITICAL)

**Tenant Isolation:**
```python
# MANDATORY: Set RLS context on every request
await session.execute(
    text("SELECT set_config('app.current_tenant', :tenant_id, false)"),
    {"tenant_id": current_user.tenant_id}
)
```

**Authentication:**
```python
# MANDATORY: Use dependency injection
from app.api.deps import get_current_active_user

@router.get("/companies")
async def get_companies(
    current_user: User = Depends(get_current_active_user)
):
    # tenant_id from current_user, NEVER from request
    pass
```

**Frontend:**
```typescript
// MANDATORY: Always include auth token
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
```

---

## Testing Strategy

### Testing Philosophy

**Key Principles (From Gabe's Concerns):**
- **At most 1 mocking test** per function/component
- **At least 1 integration test** using real components/data
- **Prioritize real-world testing** over mocked tests
- **Critical paths MUST be tested** with Playwright + Chrome DevTools
- **Verify actual page renders**, not blank screens

### Backend Testing

**Unit Tests (pytest):**
```python
# At most 1 mock test
def test_csv_processor_with_mock(mocker):
    mock_gabeda = mocker.patch('app.services.csv_processor.process_data')
    mock_gabeda.return_value = MockResult(count=100)

    result = process_csv("fake.csv", mapping_id=1)
    assert result.count == 100

# At least 1 real test
def test_csv_processor_real(test_db, sample_csv_file):
    result = process_csv(sample_csv_file, mapping_id=1)

    # Verify data in real test database
    transactions = test_db.query(Transaction).all()
    assert len(transactions) == 100
```

**Integration Tests (pytest + TestClient):**
```python
def test_upload_csv_endpoint(client, auth_headers, sample_csv):
    response = client.post(
        "/api/v1/data/upload",
        headers=auth_headers,
        files={"file": sample_csv}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "task_id" in data["data"]
```

**RLS Tests:**
```python
def test_tenant_isolation(test_db):
    # Create two companies
    company1 = create_company(name="Company 1")
    company2 = create_company(name="Company 2")

    # Set RLS context to company1
    test_db.execute(
        text("SELECT set_config('app.current_tenant', :id, false)"),
        {"id": company1.id}
    )

    # Should only see company1
    companies = test_db.query(Company).all()
    assert len(companies) == 1
    assert companies[0].id == company1.id
```

**Coverage Target:** 70% overall, 90% for critical paths (auth, RLS, CSV processing)

### Frontend Testing

**Component Tests (Vitest):**
```typescript
// At most 1 mock test
test('Dashboard renders with mock data', () => {
  const mockData = { revenue: 1234567, growth: 12.5 };
  render(<Dashboard data={mockData} />);
  expect(screen.getByText('$1.234.567')).toBeInTheDocument();
});

// At least 1 real test
test('Dashboard fetches and renders real data', async () => {
  render(<Dashboard companyId={1} />);

  // Wait for React Query to fetch
  await waitFor(() => {
    expect(screen.getByText(/revenue/i)).toBeInTheDocument();
  });

  // Verify real data rendered
  expect(screen.getByRole('heading', { name: /Mi Empresa/i })).toBeInTheDocument();
});
```

**E2E Tests (Playwright - MANDATORY for Critical Paths):**
```typescript
// Test critical user flows
test('Complete CSV upload flow', async ({ page }) => {
  // 1. Login
  await page.goto('http://localhost:5173/login');
  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');

  // 2. Verify dashboard loads (not blank)
  await expect(page.locator('h1')).toContainText('Dashboard');

  // 3. Navigate to upload
  await page.click('a[href="/upload"]');

  // 4. Upload CSV
  await page.setInputFiles('input[type="file"]', 'test-data.csv');
  await page.click('button:has-text("Upload")');

  // 5. Wait for processing
  await expect(page.locator('.processing-status')).toContainText('Processing');
  await expect(page.locator('.success-message')).toBeVisible({ timeout: 30000 });

  // 6. Verify dashboard updated
  await page.goto('http://localhost:5173/dashboard');
  await expect(page.locator('.revenue-card')).toBeVisible();

  // 7. Check console for errors (Chrome DevTools)
  const logs = await page.evaluate(() => console.log);
  expect(logs).not.toContain('error');
});

// Test blank page issue (from Gabe's concerns)
test('All pages render content, not blank screens', async ({ page }) => {
  const pages = ['/dashboard', '/upload', '/locations', '/settings'];

  for (const path of pages) {
    await page.goto(`http://localhost:5173${path}`);

    // Verify page has content
    const bodyText = await page.textContent('body');
    expect(bodyText.length).toBeGreaterThan(0);

    // Check for React errors
    await expect(page.locator('.error-boundary')).not.toBeVisible();

    // Check console
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') errors.push(msg.text());
    });
    expect(errors).toHaveLength(0);
  }
});
```

**Chrome DevTools Verification:**
- Check console for errors on every page
- Verify network requests return 200/201
- Confirm React components mounted
- No blank screens or error boundaries

### Deployment Testing (Early & Continuous)

**Local Testing First:**
```bash
# Backend
cd backend
pytest tests/ -v --cov=app --cov-report=term

# Frontend
cd frontend
npm run test
npm run test:e2e
```

**Deployment Testing (After Each Feature):**
1. Deploy to Railway (backend) + Render (frontend)
2. Run Playwright tests against deployed URLs
3. Check Railway logs for errors
4. Verify database migrations applied
5. Test from mobile device (real-world scenario)

**CI/CD Pipeline (.github/workflows/):**
```yaml
# backend-tests.yml
name: Backend Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest tests/ --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

# frontend-tests.yml
name: Frontend Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          cd frontend
          npm ci
          npm run test
          npm run test:e2e
```

---

## Performance Considerations

### Dashboard Load Performance (NFR1.1: <2 seconds)

**Strategy:**
1. **Database Aggregates:** Pre-calculated in `aggregates_*` tables
2. **Redis Caching:** Dashboard data cached for 1 hour
3. **Query Optimization:** Indexed columns (company_id, date)
4. **Pagination:** Limit results to current year by default

**Implementation:**
```python
@router.get("/analytics/dashboard")
@cache(expire=3600)  # 1-hour cache
async def get_dashboard(company_id: int, year: int = 2025):
    # Query pre-calculated aggregates (fast)
    monthly_data = await session.execute(
        select(AggregateMonthly)
        .where(AggregateMonthly.company_id == company_id)
        .where(extract('year', AggregateMonthly.date) == year)
        .order_by(AggregateMonthly.date)
    )

    return {"status": "success", "data": monthly_data}
```

### CSV Processing Performance (NFR1.5: 100K in <30 seconds)

**Strategy:**
1. **Batch Inserts:** Use SQLAlchemy bulk_insert_mappings
2. **gabeda_core:** Single-loop execution for efficiency
3. **Celery:** Async processing, doesn't block API
4. **Validation:** Pre-validate before DB operations

**Implementation:**
```python
from sqlalchemy.dialects.postgresql import insert

@celery_app.task
def process_csv_task(file_path, company_id, mapping):
    # Use gabeda_core for parsing
    result = gabeda_core.process_data(file_path, mapping)

    # Batch insert (1000 rows at a time)
    batch_size = 1000
    for i in range(0, len(result.rows), batch_size):
        batch = result.rows[i:i+batch_size]

        stmt = insert(Transaction).values(batch)
        session.execute(stmt)
        session.commit()

    # Trigger aggregation
    trigger_aggregation.delay(company_id)
```

### API Response Time (NFR1.8: <500ms p95)

**Strategy:**
1. **Async Operations:** FastAPI + asyncpg
2. **Connection Pooling:** Reuse database connections
3. **Minimal Business Logic:** Keep endpoints thin
4. **Caching:** Redis for frequently accessed data

**Monitoring:**
```python
from prometheus_client import Histogram

request_duration = Histogram('request_duration_seconds', 'Request duration')

@app.middleware("http")
async def monitor_performance(request, call_next):
    with request_duration.time():
        response = await call_next(request)
    return response
```

### Frontend Performance

**Bundle Size (<1MB initial load):**
- Code splitting by route
- Lazy load components below fold
- Tree-shake unused dependencies

**Time to Interactive (<3 seconds):**
- Skeleton screens while loading
- Prefetch critical data
- Service worker caching (PWA)

**Chart Rendering (60fps):**
- Recharts optimized for performance
- Limit data points (aggregate if >1000)
- Virtualize long lists

---

## Deployment Architecture

### Development Environment

**Local Setup:**
```bash
# Backend (FastAPI + PostgreSQL + Redis)
docker-compose up -d

# Frontend (Vite dev server)
cd frontend
npm run dev
```

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:17.5
    environment:
      POSTGRES_DB: ayni_dev
      POSTGRES_USER: ayni
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    command: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    environment:
      DATABASE_URL: postgresql+asyncpg://ayni:dev_password@postgres/ayni_dev
      REDIS_URL: redis://redis:6379

  celery:
    build: ./backend
    command: celery -A app.workers.celery_app worker --loglevel=info
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:
```

### Production Deployment

**Backend (Railway):**
```yaml
# railway.toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"

[[services]]
name = "backend"
replicas = 2  # For high availability

[[services]]
name = "celery-worker"
command = "celery -A app.workers.celery_app worker --loglevel=info"
replicas = 1

[[services]]
name = "postgres"
type = "postgres"

[[services]]
name = "redis"
type = "redis"
```

**Environment Variables (Railway):**
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/ayni
REDIS_URL=redis://host:6379
SECRET_KEY=<random-secret>
GOOGLE_OAUTH_CLIENT_ID=<google-client-id>
GOOGLE_OAUTH_CLIENT_SECRET=<google-secret>
ENVIRONMENT=production
```

**Frontend (Render):**
```yaml
# render.yaml
services:
  - type: web
    name: ayni-frontend
    env: static
    buildCommand: cd frontend && npm install && npm run build
    staticPublishPath: frontend/dist
    headers:
      - path: /*
        name: X-Frame-Options
        value: DENY
      - path: /*
        name: X-Content-Type-Options
        value: nosniff
    routes:
      - type: rewrite
        source: /*
        destination: /index.html
```

**Environment Variables (Render):**
```bash
VITE_API_URL=https://api.ayni.cl
VITE_ENVIRONMENT=production
```

### Database Migrations

**Alembic Commands:**
```bash
# Create migration
alembic revision --autogenerate -m "Add locations table"

# Review migration file
# Edit if needed (e.g., add RLS policies manually)

# Apply to local
alembic upgrade head

# Apply to production (Railway)
railway run alembic upgrade head
```

**Manual RLS Setup (in migration):**
```python
# alembic/versions/xxx_add_rls.py
from alembic import op

def upgrade():
    # Enable RLS
    op.execute("ALTER TABLE companies ENABLE ROW LEVEL SECURITY;")

    # Create policy
    op.execute("""
        CREATE POLICY tenant_isolation_policy ON companies
        USING (id = current_setting('app.current_tenant', TRUE)::INTEGER);
    """)

def downgrade():
    op.execute("DROP POLICY tenant_isolation_policy ON companies;")
    op.execute("ALTER TABLE companies DISABLE ROW LEVEL SECURITY;")
```

### Backup & Recovery

**Automated Backups (Railway):**
- Daily automatic backups (included)
- 30-day retention
- Point-in-time recovery within 24 hours

**Manual Backup:**
```bash
# Download backup from Railway
railway db:backup download

# Restore to local
psql -U ayni ayni_dev < backup.sql
```

### Monitoring & Alerts

**Railway Logs:**
- Real-time logs in Railway dashboard
- Filter by service (backend, celery, postgres)
- Search by tenant_id, user_id, error level

**Future Monitoring (Post-MVP):**
- Sentry for error tracking
- Datadog for performance monitoring
- Uptime monitoring (UptimeRobot)

---

## Development Environment Setup

### Prerequisites

**Required:**
- Python ≥3.9
- Node.js ≥18
- PostgreSQL 17.5 (via Docker)
- Redis 7.x (via Docker)
- Git

**Optional:**
- Docker Desktop (for local development)
- Railway CLI (for deployment)
- Playwright browsers (for E2E testing)

### Setup Commands

**Clone and Initialize:**
```bash
# Clone repository
git clone <repository-url>
cd ayni

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install gabeda-core  # Add if not in requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your settings

# Run migrations
alembic upgrade head

# Frontend setup
cd ../frontend
npm install

# Start development servers
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Celery worker
cd backend
celery -A app.workers.celery_app worker --loglevel=info

# Terminal 3: Frontend
cd frontend
npm run dev
```

**Docker Development:**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### IDE Configuration

**VSCode (Recommended):**
```json
// .vscode/settings.json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

**Extensions:**
- Python
- Pylance
- ESLint
- Prettier
- Tailwind CSS IntelliSense

---

## Architecture Decision Records (ADRs)

### ADR-001: Use FastAPI Cookiecutter with Fresh Tailwind Frontend

**Context:** Need to avoid Chakra/Tailwind conflicts while leveraging proven FastAPI setup.

**Decision:** Use FastAPI cookiecutter backend, delete entire frontend, build fresh with React + Tailwind.

**Rationale:**
- Cookiecutter provides production-ready backend (auth, DB, Docker)
- Deleting frontend avoids weeks of Chakra migration
- Fresh Tailwind build is cleaner and Ayni-specific
- Same development time, better long-term maintainability

**Consequences:**
- First story must delete frontend and rebuild
- Need to reference cookiecutter auth patterns
- Cleaner codebase optimized for Ayni

### ADR-002: PostgreSQL RLS for Multi-Tenant Isolation

**Context:** Need database-level tenant isolation for security.

**Decision:** Use PostgreSQL Row-Level Security policies.

**Rationale:**
- Enforces isolation at database level (cannot be bypassed in code)
- No risk of forgetting WHERE tenant_id clauses
- PostgreSQL 17.5 has mature, performant RLS
- Aligns with security best practices

**Consequences:**
- Must set RLS context on every request
- Requires PostgreSQL (not MySQL/MongoDB)
- Adds complexity to database setup

### ADR-003: Celery + Redis for Background Processing

**Context:** CSV processing and aggregation must not block API requests.

**Decision:** Use Celery with Redis as broker.

**Rationale:**
- Proven Python async task system
- Redis already needed for caching
- Handles retries, monitoring, scheduling
- Meets 5-minute aggregation requirement

**Consequences:**
- Adds Redis infrastructure dependency
- Requires separate Celery worker process
- More complex deployment (3 services: API, Celery, Redis)

### ADR-004: React Query + Zustand for State Management

**Context:** Need to manage server state (API data) and UI state (theme, language).

**Decision:** Use React Query for server state, Zustand for UI state.

**Rationale:**
- React Query handles caching, refetching, loading states automatically
- Zustand is lightweight (1KB) for simple UI state
- Complementary, not overlapping
- Modern React best practices

**Consequences:**
- Two state libraries instead of one
- Learning curve for both
- Excellent DX and performance

### ADR-005: gabeda_core for CSV Processing

**Context:** CSV processing requires complex analytics logic.

**Decision:** Integrate existing gabeda_core library.

**Rationale:**
- Already implements 4-case analytics logic
- Single-loop execution for performance
- Proven in production
- Avoids reinventing the wheel

**Consequences:**
- Dependency on external library
- Must configure gabeda_core logging
- Python ≥3.9 requirement

### ADR-006: Early Deployment Strategy

**Context:** Previous iteration had deployment issues discovered late (from Gabe's concerns).

**Decision:** Deploy to Railway + Render after basic setup, test continuously.

**Rationale:**
- Catch integration issues early
- Validate infrastructure works before building features
- Incremental deployments reduce risk
- Real-world testing on deployed environment

**Consequences:**
- More upfront deployment work
- Railway/Render costs start earlier
- Better long-term confidence in deployment

### ADR-007: Playwright for Critical Path Testing

**Context:** Previous iteration had blank page issues not caught by unit tests (from Gabe's concerns).

**Decision:** Mandatory Playwright E2E tests for all critical user paths.

**Rationale:**
- Validates actual browser behavior
- Catches blank screens, console errors
- Chrome DevTools verification included
- Real-world user experience testing

**Consequences:**
- More comprehensive test suite
- Longer test execution time
- Higher confidence in production releases

### ADR-008: Wrapped API Response Format

**Context:** Need consistent API responses for AI agent compatibility.

**Decision:** All responses wrapped in `{status, data, message}` format.

**Rationale:**
- Consistent structure for success and error
- AI agents can't use different formats
- Frontend always knows where to find data
- Industry standard pattern

**Consequences:**
- Extra nesting in responses
- Slightly larger payload size
- Absolute consistency across all endpoints

---

## Summary

**Ayni Architecture is Ready for Implementation**

This architecture document provides the complete technical foundation for building Ayni, from authentication to analytics, from multi-tenancy to mobile-first UX.

**Key Architectural Strengths:**
1. ✅ **Multi-tenant isolation** enforced at database level (PostgreSQL RLS)
2. ✅ **Performance targets met** through caching, aggregates, async operations
3. ✅ **AI agent consistency** via strict implementation patterns
4. ✅ **Early deployment** strategy prevents late-stage integration issues
5. ✅ **Testing first** with Playwright verification of all critical paths
6. ✅ **Chilean-specific** localization throughout (dates, currency, language)
7. ✅ **Proven technologies** with latest stable versions (verified 2025)
8. ✅ **gabeda_core integration** for analytics processing

**Implementation Sequence:**
1. **Week 1:** Project initialization (cookiecutter + fresh Tailwind frontend)
2. **Week 1:** Deploy to Railway + Render, validate infrastructure
3. **Weeks 2-3:** Authentication (fastapi-users + OAuth)
4. **Weeks 4-5:** Company/Location management with RLS
5. **Weeks 6-8:** CSV upload + gabeda_core + Celery processing
6. **Weeks 9-10:** Multi-temporal aggregation pipeline
7. **Weeks 11-12:** Dashboard analytics with React Query + Recharts
8. **Weeks 13-14:** Cross-tenant benchmarking
9. **Week 15:** E2E testing with Playwright, deployment verification
10. **Week 16:** Beta launch

**All 90 functional requirements have architectural support.**
**All 60 non-functional requirements are addressed.**
**Zero architectural gaps for MVP.**

---

**Next Steps:**
1. ✅ Architecture complete
2. ➡️ Run `solutioning-gate-check` to validate before implementation
3. ➡️ Run `sprint-planning` to create sprint status file
4. ➡️ Run `create-story` to start implementation

---

_This architecture was created through collaborative facilitation between Gabe and the BMM Architect agent, using the BMAD Method architecture workflow v1.3.2._

_Date: 2025-11-12_
