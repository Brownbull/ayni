# Architecture Decision Records (ADRs)

## ADR-001: Use FastAPI Cookiecutter with Fresh Tailwind Frontend

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

## ADR-002: PostgreSQL RLS for Multi-Tenant Isolation

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

## ADR-003: Celery + Redis for Background Processing

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

## ADR-004: React Query + Zustand for State Management

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

## ADR-005: gabeda_core for CSV Processing

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

## ADR-006: Early Deployment Strategy

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

## ADR-007: Playwright for Critical Path Testing

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

## ADR-008: Wrapped API Response Format

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
