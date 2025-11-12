# Decision Summary

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
