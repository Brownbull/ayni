# ayni - Epic Breakdown

**Author:** Gabe
**Date:** 2025-11-12
**Project Level:** Level 3 (Multi-tenant SaaS)
**Target Scale:** 154 Functional Requirements + 89 Non-Functional Requirements

---

## Overview

This document provides the complete epic and story breakdown for ayni, decomposing the requirements from the [PRD](./PRD.md) into implementable stories.

### Epic Summary

Ayni is structured around 8 core epics that deliver sequential value from foundation to competitive intelligence:

1. **Foundation & Project Infrastructure** - Technical bedrock enabling all subsequent work
2. **Authentication & User Management** - Secure access and team collaboration
3. **Company & Multi-Location Setup** - First magical moment (playground demo + business structure)
4. **Data Pipeline & CSV Processing** - The moat (automated multi-temporal aggregation)
5. **Core Dashboards & Navigation** - Core product value (instant insights from transaction data)
6. **Performance Index & Gamification** - Engagement layer ("Warcraft Logs for Business")
7. **Cross-Tenant Benchmarking** - Unique differentiator (percentile revelation + network effects)
8. **Localization, Billing & Essential Features** - Chilean market fit + monetization

Each epic follows vertical slice principles, delivering complete functionality from database to UI. Stories are sized for single dev agent completion in one focused session.

### Critical Dependencies & Implementation Sequencing

**CRITICAL PATH (Blocks MVP Launch):**
1.1 → 1.2 → 1.4 → 4.5 → **4.6 (THE MOAT)** → 5.1 → Launch

**Cross-Epic Dependencies:**
- **Epic 1** blocks ALL other epics (foundation)
- **Epic 2** (Auth) blocks: Epic 3, 4, 7, 8 (user context required)
- **Epic 4 Story 4.6** (Aggregation Pipeline) blocks: All of Epic 5, 6, 7 (no dashboards without aggregated data)
- **Epic 7 Story 7.2** (Opt-in flow) must complete BEFORE 7.1 (benchmarking engine)

**Recommended Phasing:**
- **Phase 1 (Week 1-2):** Epic 1 complete (including Story 1.9 observability) + Story 8.1 (i18n setup early)
- **Phase 2 (Week 3-4):** Epic 2 complete + Epic 3.1, 3.6, 3.5, 3.4, 3.7
- **Phase 3 (Week 5-7):** Epic 4 complete (CRITICAL - enables all dashboards) + Epic 3.2 (playground with hardcoded data) - **+1 week buffer for aggregation complexity**
- **Phase 3.5 (Day after Phase 3):** Chilean market validation checkpoint - 10 user tests with playground demo
- **Phase 4 (Week 8-9):** Epic 5.1-5.4, 5.7-5.8 → then Epic 3.3 → Epic 5.5-5.6
- **Phase 5 (Week 10):** Epic 6 complete
- **Phase 6 (Week 11-12):** Epic 7 (resequence: 7.2 → 7.5 → 7.1 → 7.6 → 7.3 → 7.4)
- **Phase 7 (Week 13-14):** Epic 8.2-8.8 complete (billing & launch prep)

**Impact Analysis - What Breaks If Key Stories Fail:**
- **Story 1.2 fails:** ALL epics blocked (no multi-tenancy)
- **Story 4.6 fails:** No dashboards, MVP dead
- **Story 2.3 fails:** No auth, no company switching
- **Story 7.1 fails:** Unique differentiator lost, but still launchable
- **Story 8.4 fails:** No monetization, but can launch free tier

### Critical Failure Modes & Prevention (Top 5 Risks)

**1. Story 4.6 Aggregation Timeout (1M+ transactions)**
- **Risk:** CATASTROPHIC - The moat fails, dashboards never load
- **Prevention:** Implement incremental aggregation (only reaggregate changed periods)
- **Action:** Add Story 4.6.1 for incremental strategy

**2. Story 1.2 RLS Misconfiguration (tenant data leaks)**
- **Risk:** CATASTROPHIC - Legal liability, trust destroyed
- **Prevention:** Automated cross-tenant security tests in CI pipeline
- **Action:** Add Story 1.8 for multi-tenant security audit suite

**3. Story 2.6 RBAC Gaps (missing permission checks)**
- **Risk:** CRITICAL - Privilege escalation, unauthorized access
- **Prevention:** Automated endpoint scanner flagging missing @require_role decorators
- **Action:** Add Story 2.6.1 for RBAC audit tool

**4. Story 7.1 k-Anonymity Edge Cases**
- **Risk:** CRITICAL - Benchmarking breaks at k=10 threshold; outliers skew averages
- **Prevention:** Use MEDIAN instead of AVG; increase threshold to k=11 for safety buffer
- **Action:** Update Story 7.1 technical notes with outlier filtering

**5. Story 8.5 Usage Tracking Race Conditions**
- **Risk:** HIGH - Users wrongly blocked at limits due to double-counting
- **Prevention:** Use atomic database increments with idempotency keys
- **Action:** Update Story 8.5 technical notes with atomic operations

---

## Epic 1: Foundation & Project Infrastructure

**Goal:** Establish the technical foundation that enables all subsequent development - project structure, deployment pipeline, database schema with PostgreSQL RLS multi-tenancy, and core infrastructure services.

**Business Value:** Creates the bedrock upon which all features are built. Without this foundation, no other stories can be implemented.

### Story 1.1: Project Initialization & Monorepo Setup

As a **developer**,
I want a properly structured monorepo with backend and frontend scaffolding,
So that the team can start building features with consistent tooling and conventions.

**Acceptance Criteria:**

**Given** a new project initialization
**When** the repository is set up
**Then** the monorepo structure includes:
- `/backend` with FastAPI, Python 3.11+, Poetry for dependency management
- `/frontend` with React 19, TypeScript strict mode, Vite, Tailwind CSS
- Root-level configuration files (`.gitignore`, `README.md`, `docker-compose.yml`)

**And** both backend and frontend have working dev servers that can be started locally

**And** pre-commit hooks are configured for linting (Black, Ruff for Python; ESLint, Prettier for TypeScript)

**Prerequisites:** None (first story)

**Technical Notes:** Use Poetry for Python dependencies, pnpm for Node packages. Set up GitHub repository with main branch protection.

---

### Story 1.2: PostgreSQL Database Setup with RLS Foundation

As a **developer**,
I want PostgreSQL database with Row-Level Security (RLS) configured for multi-tenancy,
So that all tenant data is automatically isolated at the database level.

**Acceptance Criteria:**

**Given** a PostgreSQL 15+ instance
**When** the database schema is initialized
**Then** the following core tables exist:
- `tenants` (id, created_at, updated_at)
- `users` (id, tenant_id, email, hashed_password, role, created_at)
- `companies` (id, tenant_id, name, identifier, country, industry, created_at)
- `locations` (id, company_id, name, address, website, is_primary, created_at)

**And** RLS policies are enabled on all tables filtering by `tenant_id`

**And** database migrations are managed via Alembic

**And** connection pooling is configured for production scalability

**Prerequisites:** Story 1.1 (project structure)

**Technical Notes:** Use PostgreSQL RLS with JWT token containing tenant_id claim. Reference NFR2.11-2.14 for tenant isolation requirements. Set up database on Railway or similar managed PostgreSQL service.

---

### Story 1.3: Core API Structure & Health Endpoints

As a **developer**,
I want a FastAPI application with core middleware and health check endpoints,
So that we have a working API foundation with proper error handling and monitoring.

**Acceptance Criteria:**

**Given** the FastAPI backend is running
**When** API requests are made
**Then** the following endpoints respond successfully:
- `GET /health` - Returns 200 with `{"status": "healthy"}`
- `GET /api/v1/health` - Returns detailed health info (database connection, Redis status)

**And** CORS middleware is configured for frontend origin

**And** request logging middleware captures all requests with request IDs

**And** global exception handlers catch and format errors consistently

**And** API documentation is auto-generated at `/docs` (Swagger UI)

**Prerequisites:** Story 1.1, 1.2

**Technical Notes:** Use FastAPI dependency injection for database sessions. Configure uvicorn with auto-reload for development. Set up structured logging with request context.

---

### Story 1.4: Redis Integration for Caching & Background Jobs

As a **developer**,
I want Redis integrated for caching and Celery task queue,
So that we can cache expensive queries and process background jobs asynchronously.

**Acceptance Criteria:**

**Given** Redis is running locally and in production
**When** the application starts
**Then** Redis connection is established and verified in health check

**And** Celery worker is configured with Redis as broker and result backend

**And** a sample background task can be queued and executed

**And** caching utilities are available for database query results

**Prerequisites:** Story 1.1, 1.3

**Technical Notes:** Use `redis-py` for Python client. Configure Celery with task routing and retry policies. Set up Redis on Railway or similar managed service for production.

---

### Story 1.5: CI/CD Pipeline & Deployment to Railway

As a **developer**,
I want automated CI/CD pipeline deploying to Railway on main branch commits,
So that changes are automatically tested and deployed to production.

**Acceptance Criteria:**

**Given** code is pushed to the main branch
**When** GitHub Actions workflow runs
**Then** the following steps execute successfully:
- Backend tests run (pytest with coverage >70%)
- Frontend tests run (Vitest with coverage >70%)
- Backend deploys to Railway (PostgreSQL + Redis + FastAPI)
- Frontend deploys to Render or Vercel with CDN

**And** deployment status is visible in GitHub PR checks

**And** rollback mechanism is documented for failed deployments

**Prerequisites:** Story 1.1, 1.2, 1.3, 1.4

**Technical Notes:** Use Railway for backend (includes PostgreSQL + Redis managed services). Use Render or Vercel for frontend static hosting. Configure environment variables in Railway dashboard. Set up health check monitoring.

---

### Story 1.6: Environment Configuration & Secrets Management

As a **developer**,
I want environment-specific configuration and secure secrets management,
So that sensitive data is never committed and environments are properly isolated.

**Acceptance Criteria:**

**Given** different environments (local, staging, production)
**When** the application starts
**Then** configuration is loaded from environment variables

**And** `.env.example` files document all required variables

**And** sensitive values (database URLs, API keys, JWT secrets) are stored in Railway/Vercel environment variables

**And** local development uses `.env` files (git-ignored)

**And** configuration validation fails fast on missing required variables

**Prerequisites:** Story 1.1, 1.5

**Technical Notes:** Use Pydantic Settings for type-safe configuration in Python. Document all environment variables in README. Use Railway's built-in secrets management for production.

---

### Story 1.7: Database Seeding & Migration Strategy

As a **developer**,
I want database migrations and seed data for development,
So that new developers can quickly set up a working local environment.

**Acceptance Criteria:**

**Given** a fresh database instance
**When** migrations and seeds are run
**Then** all tables are created with proper indexes and constraints

**And** seed data includes:
- 1 demo tenant
- 2 demo users (owner, manager)
- 1 demo company with 2 locations
- Sample transaction data for testing

**And** migration commands are documented in README

**And** rollback procedures are tested and documented

**Prerequisites:** Story 1.2

**Technical Notes:** Use Alembic for migrations. Create `seeds.py` script for development data. Document migration workflow: `alembic upgrade head`, `python seeds.py`. Test migrations on fresh database before merging.

---

### Story 1.8: Multi-Tenant Security Audit Suite

As a **developer**,
I want automated tests that verify tenant isolation,
So that we prevent catastrophic cross-tenant data leaks.

**Acceptance Criteria:**

**Given** the PostgreSQL RLS policies are configured
**When** the security audit test suite runs
**Then** automated tests attempt cross-tenant data access and verify all attempts are blocked

**And** tests validate RLS policies exist on ALL tables with tenant_id

**And** tests verify JWT token tenant_id is properly enforced in queries

**And** tests run in CI pipeline on every PR (blocking merge if failed)

**And** test suite includes scenarios:
- User A attempts to query User B's company data (different tenants)
- API request with manipulated JWT tenant_id claim
- Direct database query bypassing application layer

**And** security audit report is generated showing all tested scenarios

**Prerequisites:** Story 1.2, 2.3 (RLS + JWT)

**Technical Notes:** Use pytest fixtures to create multi-tenant test data. Mock JWT tokens with different tenant_ids. Reference NFR2.11-2.14 for isolation requirements. **FAILURE PREVENTION:** This story prevents Story 1.2's catastrophic failure mode (tenant data leaks).

---

### Story 1.9: Observability & Monitoring Setup

As a **developer**,
I want comprehensive observability and monitoring,
So that we detect and fix issues before users experience them.

**Acceptance Criteria:**

**Given** the application is running in production
**When** errors or performance issues occur
**Then** monitoring systems capture and alert on critical events

**And** error tracking is configured (Sentry or similar):
- JavaScript errors from frontend
- Python exceptions from backend
- Error grouping and stack traces

**And** performance monitoring tracks:
- API response times (p50, p95, p99)
- Database query performance
- Frontend page load times

**And** Celery task monitoring shows:
- Aggregation job status (running, failed, completed)
- Task queue depth
- Failed task retry attempts

**And** alerts are configured for:
- API error rate >1%
- Aggregation job failures
- Database connection failures
- Webhook delivery failures (Story 8.7)

**And** dashboard displays key metrics: uptime, error rates, response times

**Prerequisites:** Story 1.3, 1.4 (API + Celery)

**Technical Notes:** Use Sentry for error tracking. Use built-in FastAPI middleware for performance metrics. Celery monitoring via Flower or similar. Set up alert channels (email/Slack). **FAILURE PREVENTION:** Prevents silent failures (aggregation stops, webhooks fail, users can't log in) that cause churn. Reference NFR3.1-3.5.

---

## Epic 2: Authentication & User Management

**Goal:** Enable users to securely access the platform with email/password or Google OAuth, manage team members with role-based permissions, and handle password resets and email verification.

**Business Value:** Security and access control are non-negotiable for B2B SaaS. This epic enables users to safely invite their team with appropriate permission levels.

### Story 2.1: Email/Password Registration & Login

As a **business owner**,
I want to register with my email and password,
So that I can create an account and access the platform securely.

**Acceptance Criteria:**

**Given** the registration form is displayed
**When** I provide valid email and password (minimum 8 characters)
**Then** a new user account is created with hashed password (bcrypt cost factor 12)

**And** an email verification link is sent to the provided email

**And** I am redirected to a "Check your email" confirmation page

**And** JWT tokens (access + refresh) are generated but not activated until email verified

**And** API endpoints exist: `POST /api/auth/register`, `POST /api/auth/login`

**Prerequisites:** Story 1.2, 1.3 (database, API structure)

**Technical Notes:** Use bcrypt for password hashing. JWT tokens include: user_id, tenant_id, role, email. Access token expires in 24h, refresh token in 30 days. Reference FR1.1-1.3.

---

### Story 2.2: Email Verification Flow

As a **new user**,
I want to verify my email address,
So that my account is activated and I can access the platform.

**Acceptance Criteria:**

**Given** I receive an email verification link
**When** I click the verification link
**Then** my email is marked as verified in the database

**And** I am redirected to the login page with a success message

**And** I can now successfully log in with my credentials

**And** verification tokens expire after 24 hours

**And** I can request a new verification email if the token expires

**Prerequisites:** Story 2.1

**Technical Notes:** Use signed JWT tokens for email verification links. Store verification status in `users.email_verified` boolean field. Reference NFR2.10.

---

### Story 2.3: JWT Token Generation & Refresh

As a **logged-in user**,
I want my session to persist for 30 days via refresh tokens,
So that I don't have to log in repeatedly while maintaining security.

**Acceptance Criteria:**

**Given** I successfully log in
**When** the API generates tokens
**Then** I receive an access token (24h expiration) and refresh token (30d expiration)

**And** the refresh token is stored securely (httpOnly cookie or secure storage)

**And** I can use `POST /api/auth/refresh` to get a new access token before expiration

**And** refresh tokens are rotated on each use (old token invalidated)

**And** all protected API endpoints validate JWT tokens via middleware

**Prerequisites:** Story 2.1, 2.2

**Technical Notes:** JWT payload includes: user_id, tenant_id, role, email, exp. Use FastAPI Depends for token validation middleware. **SECURITY CRITICAL:** JWT secret MUST be 64+ character random string. Add secret scanning to CI pipeline. Rotate secrets quarterly. Store in environment variables only (never commit). Reference NFR2.6-2.7, FR1.3. **FAILURE PREVENTION:** Prevents catastrophic account takeover from weak/leaked secrets.

---

### Story 2.4: Password Reset Flow

As a **user who forgot their password**,
I want to request a password reset via email,
So that I can regain access to my account securely.

**Acceptance Criteria:**

**Given** I click "Forgot Password" on the login page
**When** I enter my email and submit
**Then** a password reset email is sent with a time-limited token (1 hour expiration)

**And** the reset link directs me to a password reset form

**And** I can set a new password (minimum 8 characters)

**And** my old password is invalidated after successful reset

**And** I receive a confirmation email that my password was changed

**And** API endpoints exist: `POST /api/auth/reset-password`, `POST /api/auth/confirm-reset`

**Prerequisites:** Story 2.1, 2.3

**Technical Notes:** Use signed JWT tokens for reset links with 1-hour expiration. Hash new passwords with bcrypt. Reference NFR2.9, FR1.1.

---

### Story 2.5: Google OAuth 2.0 Integration

As a **business owner**,
I want to sign up and log in using my Google account,
So that I can access the platform without creating a new password.

**Acceptance Criteria:**

**Given** the login page displays a "Sign in with Google" button
**When** I click the button and authorize via Google
**Then** my Google account is linked to a new or existing user account

**And** user profile is populated with Google email and name

**And** if the email already exists, accounts are merged (OAuth linked to existing account)

**And** JWT tokens are generated and I am logged in

**And** API endpoints exist: `POST /api/auth/google` (OAuth callback)

**Prerequisites:** Story 2.1, 2.3

**Technical Notes:** Use Google OAuth 2.0 with client ID/secret stored in environment variables. Handle OAuth callback and exchange authorization code for user info. Reference FR1.1.

---

### Story 2.6: Role-Based Access Control (RBAC) Implementation

As a **company owner**,
I want to assign different roles to team members (Owner, Manager, Analyst, Viewer),
So that I can control who has access to sensitive features like billing and user management.

**Acceptance Criteria:**

**Given** the system supports 4 roles
**When** a user is created or invited
**Then** they are assigned one of: Owner, Manager, Analyst, Viewer

**And** permissions are enforced at the API level:
- **Owner**: Full access (billing, user management, all dashboards)
- **Manager**: All dashboards, reports (no billing access)
- **Analyst**: Read-only dashboards, export reports
- **Viewer**: Limited dashboard access, no exports

**And** role checks are implemented via FastAPI dependencies

**And** unauthorized actions return 403 Forbidden with clear error messages

**Prerequisites:** Story 2.3

**Technical Notes:** Store role in JWT token and `users.role` enum field. Create permission decorators: `@require_role(["owner", "manager"])`. Reference FR1.5-1.9.

---

### Story 2.6.1: RBAC Endpoint Security Audit Tool

As a **developer**,
I want an automated tool that scans all API endpoints for missing permission checks,
So that we prevent privilege escalation vulnerabilities.

**Acceptance Criteria:**

**Given** the API has role-based endpoints
**When** the RBAC audit tool runs
**Then** it scans all FastAPI routes and flags endpoints missing `@require_role` decorators

**And** audit report lists:
- Protected endpoints (with role requirements)
- Unprotected endpoints (missing decorators)
- Risk level for each unprotected endpoint

**And** tool runs in CI pipeline and warns on missing permissions (non-blocking initially)

**And** after Month 1, tool becomes blocking (fails CI if critical endpoints unprotected)

**And** audit exceptions can be documented for intentionally public endpoints

**Prerequisites:** Story 2.6

**Technical Notes:** Use AST parsing or FastAPI route inspection to detect `@require_role` usage. Generate markdown report. **FAILURE PREVENTION:** Prevents critical privilege escalation vulnerabilities from missing RBAC checks.

---

### Story 2.7: User Invitation System

As a **company owner**,
I want to invite team members to my company,
So that they can collaborate and access company dashboards.

**Acceptance Criteria:**

**Given** I am a company owner
**When** I invite a user via email
**Then** an invitation email is sent with a signup link (7-day expiration)

**And** the invited user can register and is automatically added to my company

**And** I can specify the role for the invited user (Manager, Analyst, Viewer)

**And** invitation status is tracked (pending, accepted, expired)

**And** I can resend or cancel pending invitations

**And** API endpoints exist: `POST /api/users/invite`, `GET /api/users/invitations`, `DELETE /api/users/invitations/{id}`

**Prerequisites:** Story 2.1, 2.6

**Technical Notes:** Store invitations in `user_invitations` table with token, email, role, company_id, expires_at. Reference FR1.4, FR2.4.

---

### Story 2.8: Frontend Auth UI Components

As a **user**,
I want intuitive authentication screens (login, register, forgot password),
So that I can easily access the platform with a professional user experience.

**Acceptance Criteria:**

**Given** the frontend authentication pages exist
**When** I navigate to login, register, or forgot password
**Then** clean, responsive forms are displayed with:
- Email and password inputs with validation
- "Sign in with Google" button
- "Forgot Password?" link
- "Don't have an account? Sign up" link

**And** form validation shows real-time error messages

**And** loading states are displayed during API requests

**And** success/error toast notifications appear for actions

**And** pages are accessible via keyboard navigation

**Prerequisites:** Story 2.1-2.5

**Technical Notes:** Use React Hook Form for form management. Use Tailwind CSS for styling. Store JWT tokens in memory + httpOnly cookies. Reference NFR4.1-4.2 (accessibility).

---

## Epic 3: Company & Multi-Location Setup

**Goal:** Enable users to create companies with progressive multi-location support (1→N model), experience playground demo with realistic data, and manage company/location settings. This delivers the first magical moment.

**Business Value:** Users see value within 60 seconds via playground demo, then seamlessly transition to creating their real company. Progressive disclosure keeps MVP simple for single-location users while supporting growth.

### Story 3.1: Company Creation Flow with First Location

As a **business owner**,
I want to create a company with my business details,
So that I can start tracking my business performance.

**Acceptance Criteria:**

**Given** I'm logged in and have no companies yet
**When** I complete the company creation form
**Then** a new company is created with the following fields:
- Company name (required)
- Unique identifier: RUT (Chile) with validation, or string (other countries)
- Country selection (Chile, Peru, Colombia, Mexico, Other)
- Industry dropdown (5 options: Retail, Food Service, Distribution, Professional Services, Other)
- Timezone (default: Santiago/Chile UTC-3)

**And** the first location is automatically created with fields:
- Location name (default: "Main Location")
- Address (for physical stores) OR Website URL (for web-based businesses) - one required
- Marked as `is_primary = true`

**And** I am redirected to the company dashboard

**And** API endpoints exist: `POST /api/companies`, `GET /api/companies`, `GET /api/companies/{id}`

**Prerequisites:** Story 2.1, 2.3, 1.2 (auth + database)

**Technical Notes:** Validate Chilean RUT format using Modulo 11 algorithm. Company and location are created in a single transaction. Reference FR2.1-2.8, FR2.13-2.17.

---

### Story 3.2: Playground Demo Company Auto-Creation

As a **new user**,
I want a playground company with realistic demo data created automatically,
So that I can explore the platform's features within 60 seconds without uploading my own data.

**Acceptance Criteria:**

**Given** I register and verify my email
**When** I first log in
**Then** a playground company is automatically created for me with:
- Company name: "Playground - [Selected Industry]"
- Demo data: 12 months of simulated transactions (current year)
- Industry selection prompt: Restaurant, Distributor, Clothing/Retail, Electronics, Medical Equipment

**And** I see 2 demo locations with realistic names per industry:
- Restaurant: "Downtown Location", "Mall Location"
- Distributor: "Warehouse North", "Warehouse South"
- Clothing: "Flagship Store", "Outlet Store"
- Electronics: "Tech Store Central", "Tech Store West"
- Medical: "Clinic A", "Clinic B"

**And** a persistent banner displays: "🎮 This is demo data. Create your real company → [Start Now]"

**And** transactions include realistic patterns (seasonal trends, location variation, growth)

**And** the demo company does NOT count against billing limits

**And** playground demo content is available in Spanish (hardcoded translations)

**Prerequisites:** Story 3.1, 1.7 (company creation + seeding)

**Technical Notes:** Use hardcoded seed data generation with industry-specific patterns. Store demo company flag in database (`companies.is_demo = true`). **SPANISH CONTENT:** Include hardcoded Spanish translations for demo company even if full i18n (Story 8.1) isn't complete - critical for Chilean user first impression. **DEPENDENCY NOTE:** Demo company needs pre-aggregated data for dashboards - either use hardcoded demo aggregations OR wait until Story 4.6 completes. Recommended: hardcoded demo aggregations for faster onboarding. Reference FR2.9-2.12.

---

### Story 3.3: Multi-Location Management (Progressive Enhancement)

As a **business owner with multiple locations**,
I want to add additional locations to my company,
So that I can track performance across all my stores/branches separately.

**Acceptance Criteria:**

**Given** I have created a company with the first location
**When** I navigate to Settings → Locations
**Then** I see my existing location(s) listed

**And** I see a "+ Add Location" button

**And** clicking the button opens a form with:
- Location name (required)
- Address OR Website URL (one required)
- Mark as primary location (checkbox)

**And** after adding a 2nd location, the dashboard automatically transforms to show:
- Location breakdown panel (metrics per location)
- Clickable location cards for drill-down

**And** I can edit or soft-delete locations (requires 2+ locations to delete)

**And** API endpoints exist: `POST /api/companies/{id}/locations`, `GET /api/locations/{id}`, `PUT /api/locations/{id}`, `DELETE /api/locations/{id}`

**Prerequisites:** Story 3.1

**Technical Notes:** Soft delete requires `deleted_at` timestamp field. Prevent deletion if only 1 location remains. Location changes trigger dashboard UI updates. Reference FR2.13-2.18.

---

### Story 3.4: Company Switcher for Multi-Company Users

As a **user who owns multiple companies**,
I want to easily switch between my companies,
So that I can manage multiple businesses from one account.

**Acceptance Criteria:**

**Given** I have access to multiple companies (owned or invited)
**When** I click the company switcher in the navigation
**Then** a dropdown displays all my companies with:
- Company name
- Industry icon
- "Demo" badge if playground company
- Current company highlighted

**And** selecting a company refreshes the dashboard with that company's data

**And** the selected company persists across sessions

**And** tenant_id in JWT is updated on company switch

**And** all subsequent API calls use the new company's tenant context

**Prerequisites:** Story 3.1, 2.3 (company + JWT tokens)

**Technical Notes:** Store selected company ID in user session. Update JWT claims on company switch. Use React Context for frontend company state. Reference FR2.6.

---

### Story 3.5: Company Settings Management

As a **company owner**,
I want to update my company settings,
So that I can keep business information current and configure preferences.

**Acceptance Criteria:**

**Given** I am a company owner
**When** I navigate to Settings → Company
**Then** I can edit:
- Company name
- Industry (dropdown)
- Timezone
- Country (read-only after creation)
- Identifier (read-only after creation)

**And** changes are saved with validation

**And** success/error messages display

**And** updated settings are reflected immediately in the dashboard

**And** API endpoint exists: `PUT /api/companies/{id}`

**Prerequisites:** Story 3.1, 2.6 (company + RBAC)

**Technical Notes:** Only Owner role can edit company settings. Prevent changing country/identifier to maintain data integrity. Reference FR2.8.

---

### Story 3.6: Chilean RUT Validation & Display

As a **Chilean business owner**,
I want my RUT (company tax ID) validated during company creation,
So that I can ensure my business is properly identified in the system.

**Acceptance Criteria:**

**Given** I select Chile as my country
**When** I enter a RUT in the identifier field
**Then** the system validates RUT format: XX.XXX.XXX-X (or XXXXXXXX-X)

**And** the system validates using Modulo 11 check digit algorithm

**And** invalid RUTs show clear error: "Invalid RUT format. Example: 12.345.678-9"

**And** valid RUTs are stored in normalized format (digits + dash + check digit)

**And** the platform prevents duplicate RUTs across all companies

**And** non-Chilean users see a simple text input for company identifier

**Prerequisites:** Story 3.1

**Technical Notes:** Implement Modulo 11 algorithm for RUT validation. Normalize RUT to XXXXXXXX-X format for storage. Reference FR2.2-2.5.

---

### Story 3.7: Frontend Company & Location UI

As a **user**,
I want clean, intuitive UI for company and location management,
So that I can easily set up and manage my business structure.

**Acceptance Criteria:**

**Given** the frontend company management pages exist
**When** I navigate to company creation, settings, or location management
**Then** forms are responsive and accessible with:
- Clear labels and validation messages
- Industry icons for visual distinction
- Chilean RUT input with proper formatting hints
- Address vs. Website toggle for location input
- Demo company banner styled prominently

**And** company switcher dropdown is accessible from main navigation

**And** playground demo industry selection uses card-based UI with illustrations

**And** location cards show quick stats (transaction count, revenue) if data exists

**Prerequisites:** Story 3.1-3.6

**Technical Notes:** Use Tailwind CSS for styling. Industry icons from Heroicons or similar. Implement responsive grid for location cards. Reference NFR4.5-4.8 (responsiveness).

---

## Epic 4: Data Pipeline & CSV Processing

**Goal:** Enable users to upload transaction data via CSV, map columns intelligently (with Chilean POS format detection), validate data, and execute multi-temporal aggregation pipelines. This is the technical moat that replaces data engineering teams.

**Business Value:** Automated aggregation pipelines transform raw transactions into queryable insights across 6 time dimensions (hour/day/week/month/quarter/year). PII removal ensures compliance. This is what makes Ayni valuable.

### Story 4.1: CSV Upload with Drag-and-Drop UI

As a **business owner**,
I want to upload transaction data via CSV file,
So that I can import my sales data into the platform.

**Acceptance Criteria:**

**Given** I am on the data upload page
**When** I drag and drop a CSV file or use the file picker
**Then** the file is uploaded to the server

**And** I see a progress indicator during upload

**And** the file is validated for basic format (CSV with headers)

**And** I am prompted to select the target location for this data

**And** I choose between two upload modes: Replace (overwrite existing) or Append (add new)

**And** files larger than 10MB are processed asynchronously via Celery

**And** API endpoint exists: `POST /api/data/upload`

**Prerequisites:** Story 3.1, 3.3, 1.4 (company, locations, Celery)

**Technical Notes:** Store uploaded files temporarily in cloud storage (S3 or Railway volumes). File size limit: 100MB. Use tus.io or similar for resumable uploads. Reference FR3.1-3.2.

---

### Story 4.2: Column Mapping Interface with Chilean POS Intelligence

As a **business owner**,
I want to map my CSV columns to the system's expected fields,
So that my data is correctly interpreted regardless of CSV format.

**Acceptance Criteria:**

**Given** my CSV file is uploaded
**When** I reach the column mapping step
**Then** I see my CSV headers listed alongside system fields

**And** the system auto-detects common Chilean POS column names:
- "Fecha" / "Date" / "fecha_venta" → `in_dt`
- "Total" / "Monto" / "total_venta" → `in_price_total`
- "Producto" / "producto_id" / "SKU" → `in_product_id`
- "Cantidad" / "quantity" / "cant" → `in_quantity`

**And** I see confidence scores for auto-detected mappings (High/Medium/Low)

**And** I can confirm or override auto-detected mappings via dropdown selectors

**And** REQUIRED fields are clearly marked: `in_dt`, `in_trans_id`, `in_product_id`, `in_quantity`, `in_price_total`

**And** OPTIONAL fields are available: `in_trans_type`, `in_customer_id`, `in_description`, `in_category`

**And** INFERABLE fields are noted: `in_cost_unit`, `in_price_unit`, `in_margin`

**And** I can save this mapping as a template for future uploads

**Prerequisites:** Story 4.1

**Technical Notes:** Use fuzzy string matching (Levenshtein distance) for column name detection. Store mapping templates in `csv_mapping_templates` table. Reference FR3.4-3.7, FR3.19-3.22.

---

### Story 4.3: Format Detection & Normalization (Chilean vs US)

As a **business owner**,
I want the system to detect my numeric and date formats automatically,
So that Chilean-format CSVs (1.234,56) are parsed correctly without manual configuration.

**Acceptance Criteria:**

**Given** my CSV uses Chilean numeric format (dot thousands, comma decimal)
**When** the system analyzes my data
**Then** it auto-detects numeric format: `1.234,56` (Chilean) vs `1,234.56` (US)

**And** it auto-detects date format: `DD/MM/YYYY`, `YYYY-MM-DD`, or `MM/DD/YYYY`

**And** I see a format preview: "We detected Chilean format (1.234,56) ✅"

**And** I can override if detection is incorrect

**And** format settings are saved in my mapping template

**And** all numbers are normalized to standard format (float) in the database

**And** all dates are stored as UTC timestamps

**Prerequisites:** Story 4.2

**Technical Notes:** Use sample rows (first 10) for format detection. Parse Chilean numbers: replace "." with "", replace "," with ".". Reference FR3.23-3.27.

---

### Story 4.4: CSV Validation Before Processing

As a **business owner**,
I want my CSV data validated before processing,
So that I catch errors early and fix issues before importing.

**Acceptance Criteria:**

**Given** my column mapping and format settings are configured
**When** I click "Validate Data"
**Then** the system validates:
- All required columns are mapped
- Data types match expected formats (dates are dates, numbers are numbers)
- Transaction IDs are unique
- No null values in required fields
- Date range is reasonable (not future dates >1 day ahead)

**And** validation errors are displayed clearly with row numbers: "Row 45: Invalid date format in 'fecha' column"

**And** I see a summary: "✅ 1,234 valid rows | ⚠️ 5 warnings | ❌ 2 errors"

**And** I can download an error report CSV

**And** I must fix errors before proceeding to import

**Prerequisites:** Story 4.2, 4.3

**Technical Notes:** Validate in batches of 1000 rows. Show first 100 errors max. Store validation results in Redis for 1 hour. Reference FR3.8-3.11.

---

### Story 4.5: Transactions Table & Data Import

As a **developer**,
I want uploaded CSV data imported into a transactions table,
So that raw transaction data is stored for aggregation processing.

**Acceptance Criteria:**

**Given** CSV validation passed
**When** import is triggered
**Then** data is inserted into `transactions` table with fields:
- `id`, `tenant_id`, `company_id`, `location_id`
- `transaction_datetime`, `transaction_id`, `product_id`
- `quantity`, `price_total`, `price_unit`
- `cost_total`, `cost_unit`, `margin`
- `transaction_type`, `customer_id`, `description`, `category`
- `uploaded_at`, `upload_batch_id`

**And** Replace mode deletes existing location data before insert

**And** Append mode adds new transactions with deduplication check on `transaction_id`

**And** PII fields (`customer_id`, `description`) are marked for removal after aggregation

**And** import progress is trackable via WebSocket or polling

**And** import completes within 30 seconds for 100K rows

**Prerequisites:** Story 4.4, 1.2 (validation, database)

**Technical Notes:** Use bulk insert with batching (10K rows per batch). Index on `transaction_datetime`, `location_id`. Partition table by tenant_id. Reference FR3.14-3.17, FR2.20-2.25.

---

### Story 4.6: Multi-Temporal Aggregation Pipeline (The Moat)

As a **developer**,
I want an automated aggregation pipeline that generates 6 time dimensions,
So that dashboards can query pre-aggregated data instead of raw transactions.

**Acceptance Criteria:**

**Given** transactions are imported
**When** the aggregation pipeline runs (triggered after import completion)
**Then** data is aggregated into 6 time dimension tables:
- `aggregations_hourly` (hour, location_id, revenue, transaction_count, avg_order_value, growth_rate)
- `aggregations_daily`
- `aggregations_weekly`
- `aggregations_monthly`
- `aggregations_quarterly`
- `aggregations_yearly`

**And** aggregations calculate: SUM (revenue), COUNT (transactions), AVG (order value), MIN/MAX (price ranges)

**And** growth rates are calculated: ((current - previous) / previous) × 100

**And** company-level aggregations SUM across all locations

**And** aggregation completes within 5 minutes for 1M transactions

**And** PII is removed: `customer_id` and `description` fields are not copied to aggregation tables

**And** `aggregation_metadata` table is created to support future incremental strategy (schema only, logic in Story 4.6.1)

**Prerequisites:** Story 4.5, 1.4 (transactions, Celery)

**Technical Notes:** Use PostgreSQL window functions for growth rate calculations. Implement as Celery task with progress tracking. Use upsert (ON CONFLICT UPDATE) for re-aggregation. Create `aggregation_metadata` table schema: (tenant_id, location_id, time_period_type, period_start, last_aggregated_at). **PERFORMANCE CRITICAL:** Initial implementation reaggregates all data. Story 4.6.1 adds incremental strategy for production scale. Reference FR3.14-3.17, NFR1.5-1.6.

---

### Story 4.6.1: Incremental Aggregation Strategy

As a **developer**,
I want aggregation to only process changed time periods,
So that 1M+ transaction datasets don't timeout on reaggregation.

**Acceptance Criteria:**

**Given** new transactions are uploaded for specific date ranges
**When** aggregation pipeline runs
**Then** only time periods containing new/changed data are reaggregated

**And** `aggregation_metadata` table tracks `last_aggregated_at` per location and time period

**And** pipeline identifies affected time periods from new transaction date ranges

**And** unchanged historical periods are skipped (no re-processing)

**And** incremental aggregation reduces 1M transaction processing from 5 min → <30 sec

**And** full reaggregation is still available as fallback/admin command

**Prerequisites:** Story 4.6 (base aggregation pipeline)

**Technical Notes:** Add `aggregation_metadata` table with (tenant_id, location_id, time_period_type, period_start, last_aggregated_at). Query min/max transaction_datetime from new uploads to identify affected periods. Use CTE to filter aggregation queries. **FAILURE PREVENTION:** Prevents catastrophic timeout failure on large datasets (Story 4.6's primary failure mode).

---

### Story 4.7: CSV File Deletion After Processing (15-Day Retention)

As a **system administrator**,
I want uploaded CSV files automatically deleted after 15 days,
So that we maintain "data processor" status under Chilean data protection law.

**Acceptance Criteria:**

**Given** a CSV file was uploaded and processed
**When** 15 days have passed since upload
**Then** the raw CSV file is deleted from storage

**And** a nightly Celery task identifies and deletes expired files

**And** deletion events are logged with file_id, upload_date, deletion_date

**And** processed transaction data and aggregations remain intact (not deleted)

**And** users receive email notification on Day 7: "Your uploaded CSV will be automatically deleted in 8 days for data protection compliance. Download a copy if needed."

**And** Settings page shows uploaded CSV files with deletion countdown timer

**And** users can manually download their uploaded CSVs before deletion

**And** users see a "Data Processing Timeline" in settings explaining the 15-day retention

**Prerequisites:** Story 4.1, 4.5

**Technical Notes:** Add `csv_file_url` and `csv_uploaded_at` to upload tracking table. Celery beat task runs daily at 2 AM UTC. Send email reminder on Day 7 using scheduled Celery task. **UX IMPROVEMENT:** Addresses user concern about losing access to original files without warning. Reference FR2.20-2.21, NFR2.19-2.23.

---

### Story 4.8: Upload Progress Tracking & Status UI

As a **business owner**,
I want to see real-time progress during CSV upload and processing,
So that I know when my data is ready to view in dashboards.

**Acceptance Criteria:**

**Given** my CSV is uploading and processing
**When** I view the upload status page
**Then** I see progress indicators for each stage:
1. ⏳ Uploading file (0-100% progress bar)
2. 🔄 Validating data (processing spinner)
3. ✅ Importing transactions (X of Y rows imported)
4. 📊 Aggregating data (X of 6 dimensions complete)
5. 🎉 Complete! View Dashboard →

**And** I can leave the page and return to check status

**And** I receive an email notification on completion or failure

**And** errors display with clear guidance: "5 rows failed validation. Download error report →"

**And** I can cancel the upload before import stage

**Prerequisites:** Story 4.1-4.6

**Technical Notes:** Use WebSockets (Socket.io) or polling (every 2 seconds) for real-time updates. Store progress in Redis. Reference NFR3.12-3.15.

---

### Story 4.9: Saved Mapping Templates

As a **business owner who uploads regularly**,
I want to save my column mappings as templates,
So that repeat uploads are faster without re-mapping columns.

**Acceptance Criteria:**

**Given** I have successfully mapped and imported a CSV
**When** I save the mapping as a template
**Then** the template stores: column mappings, format settings (Chilean vs US), field types

**And** I can name my templates: "Defontana Monthly Export", "Buk Payroll", etc.

**And** future uploads can auto-apply templates with matching CSV headers

**And** I see a list of my saved templates in the upload flow

**And** I can edit or delete templates from settings

**And** templates are company-specific (not shared across companies)

**Prerequisites:** Story 4.2, 4.3

**Technical Notes:** Store templates in `csv_mapping_templates` table with `company_id`, `name`, `mappings_json`, `format_settings_json`. Reference FR3.12.

---

### Story 4.10: Chilean POS Detection Badge

As a **Chilean business owner**,
I want to see confirmation that my POS format is recognized,
So that I have confidence the platform understands Chilean data formats.

**Acceptance Criteria:**

**Given** my CSV matches a known Chilean POS format
**When** the system analyzes my file
**Then** I see a badge: "Chilean POS Tested ✅ Defontana Format Detected"

**And** supported formats include: Defontana, Buk, Nubox, Generic Chilean CSV

**And** unsupported formats show: "Custom format - please map carefully ⚠️"

**And** the badge links to format-specific help documentation

**Prerequisites:** Story 4.2, 4.3

**Technical Notes:** Use header patterns to detect known POS systems. Store detection confidence score. Reference FR3.28-3.30.

---

## Epic 5: Core Dashboards & Navigation

**Goal:** Deliver the core product value - intuitive dashboards that display business performance across annual/monthly/daily views with multi-location support and hybrid time granularity navigation.

**Business Value:** This is the payoff - users see weeks of Excel work transformed into instant insights. The "first dashboard view" magical moment where aggregated data becomes actionable intelligence.

### Story 5.1: Annual Dashboard Backend API

As a **developer**,
I want API endpoints that return aggregated annual dashboard data,
So that the frontend can display 12 monthly performance cards.

**Acceptance Criteria:**

**Given** aggregation pipeline has completed
**When** frontend requests annual dashboard data
**Then** API endpoint `GET /api/analytics/dashboard/annual?year=2025` returns:
- 12 monthly data points (Jan-Dec)
- For each month: revenue, transaction_count, avg_order_value, growth_rate, performance_index
- Alert indicators (✅ good, ⚠️ warning, ❌ critical) based on growth thresholds

**And** if company has 2+ locations, response includes location breakdown

**And** current month is flagged in response

**And** data is queried from `aggregations_monthly` table

**And** response time <500ms for p95

**Prerequisites:** Story 4.6 (aggregation pipeline)

**Technical Notes:** Use Redis caching (5-minute TTL) for dashboard queries. Calculate alert thresholds: ✅ growth >5%, ⚠️ -5% to +5%, ❌ <-5%. Reference FR4.1-4.4, FR4.13-4.20.

---

### Story 5.2: Annual Dashboard Frontend UI

As a **business owner**,
I want to see my annual performance at a glance,
So that I can quickly understand my business trends over the past year.

**Acceptance Criteria:**

**Given** I'm viewing the annual dashboard
**When** the page loads
**Then** I see 12 monthly cards displayed in a 4x3 responsive grid

**And** each card shows: month name, revenue (formatted CLP), growth %, alert indicator

**And** current month is visually highlighted (border/glow)

**And** hovering a card shows tooltip with additional metrics

**And** clicking a card navigates to monthly detail view

**And** if my company has 2+ locations, I see a location breakdown panel below the grid

**And** year selector dropdown allows switching between available years

**Prerequisites:** Story 5.1, 3.3 (API + multi-location)

**Technical Notes:** Use Recharts 3.0 for sparklines. Implement responsive grid (1 column mobile, 2 tablet, 4 desktop). Reference FR4.1-4.4, FR4.13-4.17.

---

### Story 5.3: Monthly Dashboard Backend API

As a **developer**,
I want API endpoints for monthly dashboard detail,
So that users can drill down into specific month performance.

**Acceptance Criteria:**

**Given** user selects a specific month
**When** frontend requests monthly data
**Then** API endpoint `GET /api/analytics/dashboard/monthly?year=2025&month=11` returns:
- Daily performance data (all days in month)
- Product-level breakdown (top 10 products by revenue)
- Location comparison (if multiple locations)
- Time series data for trend charts

**And** response includes: revenue, transactions, avg_order_value per day

**And** data is queried from `aggregations_daily` table

**Prerequisites:** Story 4.6, 5.1

**Technical Notes:** Use Redis caching (5-minute TTL). Implement pagination for product breakdown (page size: 10). Reference FR4.5-4.8.

---

### Story 5.4: Monthly Dashboard Frontend UI with Drill-Down

As a **business owner**,
I want to see detailed monthly performance,
So that I can identify daily patterns and top-performing products.

**Acceptance Criteria:**

**Given** I click a monthly card from the annual dashboard
**When** the monthly view loads
**Then** I see:
- Breadcrumb trail: Annual > November 2025
- Daily performance chart (line chart showing revenue trend)
- Top products table with revenue, quantity sold, growth %
- Location comparison (if 2+ locations)

**And** pressing ESC key returns to annual dashboard

**And** I can navigate between months using prev/next buttons

**And** clicking a day opens daily detail view (future enhancement marker)

**Prerequisites:** Story 5.2, 5.3

**Technical Notes:** Use Recharts ResponsiveContainer for charts. Implement keyboard navigation (ESC, arrow keys). Reference FR4.5-4.12.

---

### Story 5.5: Location Breakdown Panel (Multi-Location Support)

As a **business owner with multiple locations**,
I want to see performance breakdown by location,
So that I can identify which stores are performing well or need attention.

**Acceptance Criteria:**

**Given** my company has 2+ locations
**When** I view the annual dashboard
**Then** I see a location breakdown panel below the monthly cards

**And** each location card shows: name, YTD revenue, transaction count, growth %

**And** location cards are clickable to filter dashboard to that location

**And** clicking a location navigates to location-specific annual view

**And** breadcrumb updates: Dashboard > Company > Location Name

**And** location view shows same 12-month layout filtered to that location

**Prerequisites:** Story 5.2, 3.3 (dashboard + locations)

**Technical Notes:** Location cards use same card component as monthly cards. Implement location filter state in React Context. **DEPENDENCY NOTE:** Requires Story 4.6 to have generated location-level aggregations (aggregations_monthly with location_id breakdown). Reference FR4.13-4.26.

---

### Story 5.6: Hybrid Time Granularity Navigation

As a **business owner**,
I want quick access to multiple time views without strict hierarchy,
So that I can jump directly to "today's performance" without drilling through multiple levels.

**Acceptance Criteria:**

**Given** I'm on any dashboard view
**When** I use the navigation
**Then** I see quick-access tabs: Annual | Monthly | Daily | Hourly (future)

**And** I see a "Last Month" performance card always visible in sidebar

**And** I see a "Last Day" performance card always visible in sidebar

**And** clicking "Today" button jumps directly to today's daily view

**And** breadcrumb shows current view but doesn't enforce strict navigation hierarchy

**And** I can access any time granularity from any other view

**Prerequisites:** Story 5.2, 5.4

**Technical Notes:** Use tab navigation for time granularities. Sidebar cards use mini-card component. Reference FR4.27-4.31.

---

### Story 5.7: Dashboard Empty States & Error Handling

As a **business owner without data yet**,
I want helpful empty states,
So that I know what to do next to see my dashboards.

**Acceptance Criteria:**

**Given** I haven't uploaded any transaction data
**When** I view the dashboard
**Then** I see an empty state with:
- Friendly illustration
- Message: "No data yet. Upload your first CSV to see insights!"
- "Upload Data" CTA button
- Link to sample CSV download

**And** if data upload is in progress, I see: "Processing your data... Dashboard will update automatically"

**And** if data upload failed, I see error with "Retry Upload" button

**And** if no data exists for selected time period, I see: "No data for November 2025. Try a different month"

**Prerequisites:** Story 5.2, 4.8 (dashboard + upload status)

**Technical Notes:** Use Tailwind CSS for empty state styling. Implement WebSocket listener for real-time data availability updates. Reference FR4.1-4.12.

---

### Story 5.8: Dashboard Performance Optimization & Caching

As a **developer**,
I want dashboard queries optimized with caching,
So that dashboards load in <2 seconds even with large datasets.

**Acceptance Criteria:**

**Given** the dashboard is queried
**When** data is fetched from API
**Then** Redis cache is checked first (5-minute TTL)

**And** cache keys include: company_id, view_type (annual/monthly), time_period, location_id

**And** cache is invalidated when new data is uploaded

**And** database queries use indexes on: (tenant_id, company_id, time_period)

**And** dashboard load time is <2 seconds on 4G connection (p95)

**And** API response time is <500ms (p95)

**Prerequisites:** Story 5.1, 5.3, 1.4 (APIs + Redis)

**Technical Notes:** Use Redis with `django-redis` or `fastapi-cache`. Monitor query performance with database slow query logs. Reference NFR1.1-1.4.

---

## Epic 6: Performance Index & Gamification

**Goal:** Add engagement layer with gamified performance scoring, color-coded rankings, and animated rank reveals that make analytics feel like "Warcraft Logs for Business".

**Business Value:** Gamification drives engagement - users check dashboards 2-3x per week to see their "parse score". Color-coded tiers create aspirational goals.

### Story 6.1: Performance Index Calculation Engine

As a **developer**,
I want automated performance index calculation,
So that users see their business "parse score" updated nightly.

**Acceptance Criteria:**

**Given** sector averages exist (from benchmarking epic or demo data)
**When** nightly aggregation completes
**Then** performance index is calculated: (Company Revenue / Sector Average) × 100

**And** index is calculated for each time period: monthly, quarterly, yearly

**And** historical index scores are stored in `performance_index_history` table

**And** calculation runs as Celery scheduled task at 3 AM UTC

**And** index is recalculated when new data is uploaded

**Prerequisites:** Story 4.6, 5.1 (aggregation + dashboard API)

**Technical Notes:** Store index in `aggregations_monthly` table as `performance_index` column. Use sector average from cross-tenant benchmarking (Epic 7) or hardcoded demo value (100) for MVP. Reference FR5.1-5.3.

---

### Story 6.2: Color-Coded Ranking Tiers

As a **business owner**,
I want my performance index displayed with color-coded tiers,
So that I can quickly see if I'm in the top tier (green) or need improvement (grey).

**Acceptance Criteria:**

**Given** my performance index is calculated
**When** I view the dashboard
**Then** my index is displayed with color tier:
- **Green** (90-100): Top performer
- **Blue** (75-89): Above average
- **Purple** (50-74): Average
- **Grey** (0-49): Below average

**And** color tiers are consistent across all dashboard views

**And** tier badge shows: color + index number (e.g., "Green 95")

**And** hovering tier badge shows tooltip: "You rank in the top 10% of Retail businesses"

**Prerequisites:** Story 6.1, 5.2

**Technical Notes:** Use Tailwind CSS color classes: green-500, blue-500, purple-500, gray-400. Implement badge component reusable across views. Reference FR5.4-5.6.

---

### Story 6.3: Animated Rank Reveal

As a **business owner**,
I want an animated rank reveal when I first view my performance index,
So that checking my score feels engaging and rewarding.

**Acceptance Criteria:**

**Given** I load a dashboard with performance index for the first time
**When** the page renders
**Then** the performance index animates:
1. Counter animates from 0 to actual value (1-second duration)
2. Color tier fades in smoothly
3. Confetti animation if index >90 (top tier)

**And** animation plays once per session

**And** animation can be skipped by clicking

**And** animation respects `prefers-reduced-motion` accessibility setting

**Prerequisites:** Story 6.2

**Technical Notes:** Use Framer Motion for animations. Store "animation_played" flag in sessionStorage. Use `react-confetti` for celebration effect. Reference FR5.5-5.6.

---

### Story 6.4: Performance Index Historical Trends

As a **business owner**,
I want to see how my performance index has changed over time,
So that I can track if I'm improving or declining compared to peers.

**Acceptance Criteria:**

**Given** I have multiple months of data
**When** I view performance index details
**Then** I see a trend chart showing my index over the past 12 months

**And** chart highlights: best month (peak), worst month (valley), average line

**And** I see month-over-month change: "+5 points vs last month ↑"

**And** I can toggle chart between absolute index vs rank percentile view

**Prerequisites:** Story 6.1, 6.2

**Technical Notes:** Query `performance_index_history` table. Use Recharts LineChart with custom styling. Reference FR5.3.

---

## Epic 7: Cross-Tenant Benchmarking

**Goal:** Deliver the unique differentiator - anonymized cross-tenant benchmarking with percentile rankings, sector consolidation (5 broad sectors), and opt-in/opt-out model with conversion funnel.

**Business Value:** This is the "percentile revelation" magical moment and network effect moat. Every new customer makes benchmarking more valuable. No competitor can replicate without our data.

### Story 7.1: k-Anonymity Aggregation Engine

As a **developer**,
I want automated sector average calculation with k-anonymity (k=10),
So that benchmarking data is anonymized and compliant with Chilean data protection law.

**Acceptance Criteria:**

**Given** 10+ companies exist in a sector with opt-in status
**When** nightly aggregation runs
**Then** sector averages are calculated:
- Average revenue per sector per time period (monthly/quarterly/yearly)
- Median, 25th percentile, 75th percentile
- Transaction count averages

**And** sectors with <11 companies show no benchmarks (k=11 anonymity threshold with safety buffer)

**And** sector aggregates are stored in `sector_benchmarks` table

**And** individual company data cannot be reverse-engineered from aggregates

**And** calculation runs as Celery scheduled task at 2 AM UTC

**And** outlier filtering removes top/bottom 5% before calculating sector averages (prevents 1 company skewing results)

**Prerequisites:** Story 4.6, 1.4, 7.2 (aggregation + Celery + opt-in flow)

**Technical Notes:** Only aggregate companies where `opt_in_benchmarking = true`. **USE MEDIAN instead of AVG** to reduce outlier impact. Use PostgreSQL aggregate functions (MEDIAN, PERCENTILE_CONT). Filter outliers: remove companies with revenue >95th percentile or <5th percentile before aggregation. **FAILURE PREVENTION:** k=11 (not k=10) provides safety buffer; outlier filtering prevents single company skewing sector averages. **DEPENDENCY NOTE:** Requires Story 7.2 to be completed first so opt_in_benchmarking field exists and users have made opt-in decisions. Reference FR6.1-6.8, FR6.45-6.48, NFR2.24-2.28.

---

### Story 7.2: Opt-In/Opt-Out Onboarding Flow

As a **new user**,
I want to understand the value of opting into benchmarking,
So that I can make an informed decision during onboarding.

**Acceptance Criteria:**

**Given** I'm completing onboarding after creating my first company
**When** I reach the benchmarking opt-in step
**Then** I see a clear value proposition:
- "Contribute anonymized data to sector benchmarks"
- "Unlock percentile rankings and full comparison insights"
- Side-by-side comparison: Opt-In (full features) vs Opt-Out (limited stats)

**And** I see a toggle: "Contribute my anonymized data to sector benchmarks and unlock full comparisons"

**And** default state is Opt-In (checked)

**And** I can change my decision later in settings

**And** opt-in status is stored in `companies.opt_in_benchmarking` boolean field

**Prerequisites:** Story 3.1 (company creation)

**Technical Notes:** Use modal or dedicated onboarding screen. Include privacy reassurance messaging and link to data processing policy. **DEPENDENCY NOTE:** This story MUST complete before Story 7.1 - the benchmarking engine needs to know who opted in. Correct implementation sequence: 7.2 → 7.1. Reference FR6.13-6.19.

---

### Story 7.3: Percentile Ranking Calculation & Display

As a **business owner who opted in**,
I want to see my percentile ranking compared to sector peers,
So that I know if I'm in the top 68th percentile or need improvement.

**Acceptance Criteria:**

**Given** I'm opted in and sector has ≥10 companies
**When** I view dashboard
**Then** I see percentile ranking: "You rank in the 68th percentile of Retail businesses"

**And** percentile is calculated using my revenue vs sector distribution

**And** percentile updates nightly after aggregation

**And** percentile is displayed with contextual help: "What does this mean?" tooltip

**And** if opt-out, I see greyed-out indicator: "Opt-in to unlock ⭐"

**Prerequisites:** Story 7.1, 7.2, 6.1

**Technical Notes:** Use PostgreSQL `PERCENT_RANK()` window function. Store percentile in `aggregations_monthly.percentile_rank`. Reference FR6.9-6.12, FR6.26-6.29.

---

### Story 7.4: Opt-Out User Experience & Conversion Funnel

As a **user who opted out**,
I want to see what I'm missing,
So that I'm motivated to opt back in to unlock full insights.

**Acceptance Criteria:**

**Given** I opted out of benchmarking
**When** I view dashboard
**Then** I see limited sector statistics (basic averages only)

**And** I do NOT see: percentile rankings, performance index comparisons, tier badges

**And** I see greyed-out comparison indicators with "Opt-in to unlock ⭐" tooltips

**And** I see a banner: "80% of Retail users have opted in - unlock comparisons →"

**And** clicking banner opens opt-in modal with value prop

**And** I receive Week 2 email: "See how other [Sector] businesses are performing"

**Prerequisites:** Story 7.2, 7.3

**Technical Notes:** Track opt-in conversion rate as key metric (target: 70% within 90 days). Use email campaign tool (SendGrid/Resend). Reference FR6.30-6.40.

---

### Story 7.5: Sector Consolidation Strategy (3 Initial Sectors)

As a **system administrator**,
I want the platform to launch with 3 broad sectors,
So that we reach k=11 threshold quickly with only 33 customers (3 × 11).

**Acceptance Criteria:**

**Given** the platform launches
**When** users select industry during company creation
**Then** industries are mapped to 3 broad sectors for MVP:
- **Retail**: Clothing, Electronics, General Retail stores
- **Food Service**: Restaurants, Cafes, Catering, Food delivery
- **Other**: Professional Services, Distribution, Healthcare, All others

**And** sector taxonomy requires only 33 total companies to activate benchmarking (3 × 11 minimum)

**And** users see sector selection during company creation mapped to these 3 categories

**And** after reaching 66 companies (6 per sector), can expand to 5 sectors:
  - Split "Other" into: **Distribution** and **Professional Services**

**And** future expansion to granular sectors (10+) only after 200+ total companies

**Prerequisites:** Story 3.1, 7.1

**Technical Notes:** Store sector mapping in `sector_taxonomy` config table. Monitor sector distribution in admin dashboard. **MARKET RISK REDUCTION:** 33 customers (vs 55 with 5 sectors) makes benchmarking viable sooner, reducing cold-start problem. Track time-to-k11 per sector. Reference FR6.41-6.44.

---

### Story 7.6: Cold Start with Demo Data

As a **new user exploring benchmarking**,
I want to see benchmarking features in action via demo data,
So that I understand the value before opting in with my real data.

**Acceptance Criteria:**

**Given** I'm using the playground demo company
**When** I view dashboards
**Then** I see full benchmarking features with hardcoded demo data:
- Sector averages (simulated for 5 sectors)
- Percentile rankings (randomized 50th-80th percentile)
- Performance index with color tiers

**And** demo data is NOT stored in production database (hardcoded JSON)

**And** real sector statistics are calculated continuously but hidden until ≥10 companies

**And** benchmarking features appear seamlessly when threshold reached (no "coming soon" messaging)

**Prerequisites:** Story 3.2, 7.1, 7.3

**Technical Notes:** Store demo benchmark data in `demo_sector_data.json`. Switch from demo to real data when `sector_benchmark_count >= 10`. Reference FR6.20-6.25.

---

## Epic 8: Localization, Billing & Essential Features

**Goal:** Complete MVP with Chilean market fit (language, currency, payments) and monetization infrastructure (MercadoPago/MercadoLibre, usage tracking, subscription tiers).

**Business Value:** Enables launch in Chilean market and revenue generation. Without this, we can't sell to customers or handle payments.

### Story 8.1: English/Spanish Language Toggle

As a **Chilean business owner**,
I want the entire interface in Spanish,
So that I can use the platform in my preferred language.

**Acceptance Criteria:**

**Given** the platform supports English and Spanish
**When** I click the language toggle in navigation
**Then** all UI text switches to selected language

**And** language preference persists across sessions

**And** language setting is stored in user profile

**And** all static text is properly translated (not machine-translated)

**And** numbers, dates, and currency respect selected locale

**Prerequisites:** Story 2.1, 5.2

**Technical Notes:** Use `react-i18next` for translations. Store translations in JSON files (`en.json`, `es.json`). Default language based on browser locale. Reference FR7.1-7.4.

---

### Story 8.2: Chilean Peso (CLP) Currency Formatting

As a **Chilean business owner**,
I want all monetary values displayed in Chilean Pesos,
So that I see familiar currency formatting.

**Acceptance Criteria:**

**Given** I'm viewing dashboard with revenue data
**When** monetary values are displayed
**Then** amounts are formatted as: $1.234.567 (Chilean format with dot thousands separator)

**And** currency symbol is $ (Chilean Peso)

**And** no decimal places are shown (CLP doesn't use cents)

**And** large numbers use K/M suffix: $1.5M instead of $1.500.000

**And** currency formatting respects selected language (Spanish uses Chilean format by default)

**Prerequisites:** Story 5.2, 8.1

**Technical Notes:** Use `Intl.NumberFormat` with `es-CL` locale. Create `formatCurrency()` utility function. Reference FR7.5-7.7.

---

### Story 8.3: Dark/Light Mode Toggle

As a **user**,
I want to switch between dark and light modes,
So that I can use the platform comfortably in any lighting condition.

**Acceptance Criteria:**

**Given** the platform supports dark and light themes
**When** I click the theme toggle
**Then** the entire interface switches themes smoothly (transition animation)

**And** theme preference persists across sessions

**And** theme respects system preference on first visit (`prefers-color-scheme`)

**And** charts and visualizations remain readable in both themes

**And** theme toggle is accessible via keyboard shortcut (CMD/CTRL + D)

**Prerequisites:** Story 5.2

**Technical Notes:** Use Tailwind CSS dark mode with `class` strategy. Store theme in localStorage. Reference FR7.8-7.10.

---

### Story 8.4: MercadoPago Integration & Subscription Setup

As a **developer**,
I want MercadoPago/MercadoLibre integrated for subscription payments,
So that users can upgrade to paid tiers using Chile's most popular payment method.

**Acceptance Criteria:**

**Given** MercadoPago is configured
**When** a user upgrades to a paid plan
**Then** MercadoPago Checkout session is created

**And** subscription tiers exist:
- **Free**: 1.000 transactions/month, 1 user, basic dashboards
- **Starter**: CLP 31.000/month (~$39 USD) - 3 users, 3.000 transactions, all dashboards - **30-day free trial (no credit card required)**
- **Professional**: CLP 63.000/month (~$79 USD) - 10 users, unlimited transactions, benchmarking - **30-day free trial**
- **Business**: CLP 119.000/month (~$149 USD) - unlimited users, API access, white-label - **30-day free trial**

**And** free trial implementation:
- Trial starts immediately without payment method
- On Day 23, send email: "Your trial ends in 7 days - add payment method to continue"
- On Day 30, account converts to Free tier if no payment added
- Users can add payment method anytime during trial

**And** payment methods include: credit/debit cards, Chilean debit cards, MercadoPago wallet

**And** subscription status is synced from MercadoPago webhooks

**And** API endpoints exist: `POST /api/billing/create-checkout`, `POST /api/billing/mercadopago-webhook`, `POST /api/billing/start-trial`

**Prerequisites:** Story 2.1, 1.3

**Technical Notes:** Use MercadoPago SDK for hosted payment page. Track trial status in `companies.trial_started_at`, `companies.trial_ends_at`. Handle webhooks: `subscription.created`, `subscription.updated`, `subscription.cancelled`. Store MercadoPago subscription_id and payer_id. **CONVERSION OPTIMIZATION:** 30-day trial reduces friction vs immediate CLP 31K payment, improving conversion for users hitting Free tier limits. **NOTE:** Stripe removed - doesn't operate in Chile. MercadoPago is primary (95% Chilean market share). Reference FR8.1-8.4.

---

### Story 8.5: Usage Tracking & Freemium Limits

As a **system**,
I want to track monthly transaction usage per company,
So that freemium limits are enforced and users are prompted to upgrade.

**Acceptance Criteria:**

**Given** a company is on the Free tier
**When** they upload transactions
**Then** system tracks cumulative transaction count for current billing month

**And** at 800 transactions (80% of 1.000 limit), user sees warning: "You've used 80% of your free limit"

**And** at 1.000 transactions, uploads are blocked with upgrade prompt

**And** usage resets on 1st of each month

**And** API endpoint exists: `GET /api/billing/usage` returns current usage and limit

**And** usage counter is displayed in dashboard sidebar

**Prerequisites:** Story 4.5, 8.4

**Technical Notes:** Store usage in `company_usage_tracking` table with `month`, `transaction_count`. Check limits before CSV import. **USE ATOMIC INCREMENTS:** `UPDATE company_usage_tracking SET transaction_count = transaction_count + :new_count WHERE company_id = :id AND month = :current_month`. Add idempotency key to import requests (upload_batch_id) to prevent double-counting on retries. **FAILURE PREVENTION:** Atomic operations prevent race conditions that would wrongly block users at limits. **DEPENDENCY NOTE:** Usage counter hook must be added during Story 4.5 transaction import to increment count atomically. Reference FR8.5-8.8.

---

### Story 8.6: Subscription Management UI

As a **business owner**,
I want to manage my subscription,
So that I can upgrade, downgrade, or cancel my plan.

**Acceptance Criteria:**

**Given** I'm on a paid plan
**When** I navigate to Settings → Billing
**Then** I see:
- Current plan and billing cycle
- Next billing date and amount
- Payment method on file
- Usage statistics (transactions this month)

**And** I can click "Upgrade Plan" to see available tiers

**And** I can click "Cancel Subscription" with confirmation modal

**And** I can update payment method (redirects to MercadoPago account settings)

**And** subscription changes take effect immediately (upgrades) or at end of billing period (downgrades)

**Prerequisites:** Story 8.4, 8.5, 2.6 (MercadoPago + usage + RBAC)

**Technical Notes:** Only Owner role can access billing. Use MercadoPago subscription management API for payment method updates. Reference FR8.1-8.4.

---

### Story 8.7: MercadoPago Webhook Monitoring & Retry

As a **system administrator**,
I want automated monitoring and retry for failed MercadoPago webhooks,
So that subscription activations never fail silently.

**Acceptance Criteria:**

**Given** MercadoPago sends webhook events
**When** a webhook fails to process (network error, server down, etc.)
**Then** the system logs the failure with full webhook payload

**And** automatic retry with exponential backoff: 1 min → 5 min → 15 min → 1 hour

**And** after 4 failed retries, alert is sent to admin via email/Slack

**And** admin dashboard shows webhook delivery status:
- Recent successful webhooks
- Failed webhooks requiring manual reconciliation
- Subscription status discrepancies

**And** manual reconciliation tool allows admins to replay webhooks

**Prerequisites:** Story 8.4 (MercadoPago integration)

**Technical Notes:** Store webhooks in `payment_webhooks` table with (id, provider, event_type, payload, status, retry_count, last_retry_at). Use Celery for retry scheduling. Implement webhook signature verification. **FAILURE PREVENTION:** Prevents critical subscription activation failures from silent webhook drops. Reference FR8.1-8.4.

---

### Story 8.8: Annual Billing Discount (20% Off)

As a **business owner**,
I want to choose annual billing and save 20%,
So that I get better value for committing long-term.

**Acceptance Criteria:**

**Given** I'm selecting a subscription plan
**When** I toggle between monthly and annual billing
**Then** I see prices update:
- Starter: $39/month or $375/year (save $93)
- Professional: $79/month or $758/year (save $190)
- Business: $149/month or $1,430/year (save $358)

**And** annual plans show "Save 20%" badge

**And** annual subscriptions are billed once per year

**And** annual plans cannot be downgraded mid-cycle (only at renewal)

**Prerequisites:** Story 8.4

**Technical Notes:** Create annual MercadoPago subscription plans. Calculate discount: monthly price × 12 × 0.8. Prices in CLP: Starter Annual CLP 298.000, Professional CLP 606.000, Business CLP 1.144.000. Reference FR8.4.

---

## Stakeholder Validation Summary

This epic breakdown was enhanced through advanced elicitation methods including Dependency Mapping, Failure Mode Analysis, and Stakeholder Round Table validation with Chilean business owners, developers, and multi-location operators.

### Key Enhancements Applied

**Dependency Mapping Results:**
- Added Critical Path visualization (1.1 → 1.2 → 1.4 → 4.5 → 4.6 → 5.1)
- Identified and fixed Epic 7 sequencing issue (7.2 must precede 7.1)
- Added 12-week phased implementation schedule
- Documented cross-epic dependencies and impact analysis

**Failure Mode Prevention (5 New Stories Added):**
- **Story 1.8:** Multi-Tenant Security Audit Suite (prevents tenant data leaks)
- **Story 2.6.1:** RBAC Endpoint Security Audit Tool (prevents privilege escalation)
- **Story 4.6.1:** Incremental Aggregation Strategy (prevents timeout on 1M+ transactions)
- **Story 8.7:** MercadoPago Webhook Monitoring & Retry (prevents silent payment failures)
- Enhanced Stories 2.3, 7.1, 8.5 with failure prevention notes

**Chilean Market Validation:**
- ✅ Replaced Stripe with MercadoPago (95% Chilean market share)
- ✅ Adjusted pricing: Free tier increased from 300 → 1.000 transactions/month
- ✅ Starter tier increased from 1.000 → 3.000 transactions/month
- ✅ Added Spanish demo content requirement to Story 3.2
- ✅ All pricing displayed in CLP (Chilean Pesos)

**Technical Architecture Improvements:**
- Story 4.6 now creates `aggregation_metadata` table schema for future incremental strategy
- Usage tracking (Story 8.5) uses atomic database increments with idempotency
- Benchmarking (Story 7.1) uses MEDIAN (not AVG) with k=11 threshold and outlier filtering
- JWT secrets require 64+ chars with quarterly rotation and CI secret scanning

### Post-MVP Backlog Items (Not Blocking Launch)
- **Story 3.3.1:** Location status management (active/paused/closed) with historical data preservation
- **UX Enhancement:** Quick location selector in sidebar for "Last Day" card (multi-location power users)
- **Hourly Drill-Down:** Location-level hourly performance analysis

**Devil's Advocate Challenges & Resolutions:**
- ✅ Timeline adjusted from 12→14 weeks with buffer for aggregation complexity
- ✅ Added Chilean market validation checkpoint after Phase 3 (10 user tests)
- ✅ CSV deletion (Story 4.7) enhanced with Day 7 email warning and download UI
- ✅ Sector count reduced from 5→3 (Story 7.5), lowering benchmarking activation threshold from 55→33 customers
- ✅ Added 30-day free trial to Starter tier (Story 8.4) to improve conversion funnel
- ✅ Added Story 1.9 for observability/monitoring to prevent silent failures
- 📋 Post-MVP: Microsoft OAuth (Story 2.5.1) for enterprise adoption

**5 Whys Deep Dive - Technical Decision Rationale:**

*Why PostgreSQL RLS for multi-tenancy?*
- **Root Cause:** Multi-tenant data leaks are catastrophic and irreversible
- **Decision:** Database-level enforcement (RLS) guarantees tenant isolation even if application code is buggy or compromised
- **Validation:** Story 1.8 automated security tests prevent RLS misconfigurations

*Why multi-temporal aggregation (6 time dimensions)?*
- **Root Cause:** Real-time dashboard performance on multi-dimensional data requires pre-computed aggregations
- **Decision:** 1M transactions × complex window functions = 10+ second queries; pre-aggregation delivers <500ms p95 response times
- **Why 6 dimensions:** Chilean users need hourly (lunch rush), daily, weekly, monthly, quarterly, and yearly views for different business questions
- **Validation:** Story 4.6.1 incremental aggregation ensures this scales beyond 1M transactions

*Why k-anonymity (k=11) for benchmarking?*
- **Root Cause:** Benchmarking must be legally compliant, useful, AND achievable
- **Decision:** k=11 balances anonymization (Chilean law), outlier resistance (MEDIAN not AVG), and launch viability (33 customers vs 55)
- **Why k=11 not k=10:** Safety buffer prevents benchmarking from breaking when 1 company opts out
- **Validation:** Story 7.5 uses 3 sectors (not 5) to reach k=11 faster with network effects

### Total Story Count
- **Original:** 62 stories across 8 epics
- **Added:** 5 new stories (1.8, 1.9, 2.6.1, 4.6.1, 8.7)
- **Final:** 67 stories across 8 epics
- **Timeline:** 14 weeks (7 phases + buffers)

---

_For implementation: Use the `create-story` workflow to generate individual story implementation plans from this epic breakdown._
