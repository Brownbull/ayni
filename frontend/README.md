# Ayni - Multi-location Retail Analytics SaaS

Ayni is a multi-tenant SaaS platform that transforms retail analytics for Chilean and Latin American SMBs.

## Tech Stack

### Backend
- **FastAPI** - Async web framework
- **PostgreSQL 17.5** - Database with Row-Level Security
- **SQLModel** - ORM with async support
- **Celery 5.5.3** - Background task processing
- **Redis** - Message broker and caching
- **fastapi-users 15.0.1** - Authentication (OAuth, JWT)
- **Python 3.11+** - Required

### Frontend
- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **TanStack React Query 5.90.7** - Server state management
- **Zustand 5.0.8** - UI state management
- **Recharts 3.4.1** - Charts and visualizations
- **react-i18next** - Internationalization (Spanish/English)
- **date-fns** - Date utilities

## Project Structure

```
ayni/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── core/        # Config, security, logging
│   │   ├── models/      # SQLModel models
│   │   ├── alembic/     # Database migrations
│   │   └── tests/       # Unit + integration tests
│   └── pyproject.toml
├── frontend/            # React application
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── api/         # API client
│   │   ├── hooks/       # Custom hooks
│   │   ├── store/       # Zustand stores
│   │   └── utils/       # Utilities
│   └── package.json
├── docs/                # Documentation
└── docker-compose.yml   # Local development
```

## Getting Started

### Prerequisites

- Python ≥3.11
- Node.js ≥18
- PostgreSQL 17.5
- Redis 7.x
- [uv](https://github.com/astral-sh/uv) (Python package manager)

### Backend Setup

```bash
# Navigate to backend
cd backend

# Sync dependencies with uv
uv sync

# Install gabeda-core from GitHub (CSV processing engine)
uv pip install git+https://github.com/Brownbull/gabeda_core.git

# Run database migrations
uv run alembic upgrade head

# Start development server
uv run uvicorn app.main:app --reload
```

The backend will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Docker Development (Optional)

```bash
# Start all services (PostgreSQL, Redis, Backend, Frontend)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Development Workflow

### Running Tests

**Backend:**
```bash
cd backend
uv run pytest tests/ -v
uv run pytest --cov=app --cov-report=html
```

**Frontend:**
```bash
cd frontend
npm run test
npm run test:e2e  # Playwright E2E tests
```

### Code Quality

**Backend:**
```bash
cd backend
uv run ruff check .
uv run mypy .
```

**Frontend:**
```bash
cd frontend
npm run lint
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Architecture Highlights

- **Multi-tenant Isolation**: PostgreSQL Row-Level Security (RLS)
- **Async-first**: FastAPI + asyncpg + React Query
- **Mobile-first**: Responsive design with Tailwind CSS
- **Chilean Localization**: Date/currency formatting, Spanish/English i18n

## Deployment

- **Backend**: Railway (with managed PostgreSQL)
- **Frontend**: Render (static site)
- **CI/CD**: GitHub Actions

## Documentation

- [Architecture](docs/architecture.md)
- [PRD](docs/PRD.md)
- [UX Design](docs/ux-design-specification.md)

## Contributing

1. Create a feature branch
2. Make changes with tests
3. Run pre-commit hooks
4. Submit PR

## License

Proprietary - All rights reserved

---

**Version**: 0.1.0
**Status**: In Development
