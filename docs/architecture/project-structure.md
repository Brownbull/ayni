# Project Structure

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
