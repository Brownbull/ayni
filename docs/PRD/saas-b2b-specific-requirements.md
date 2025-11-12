# SaaS B2B Specific Requirements

## Multi-Tenancy Architecture

**Tenant Isolation Strategy:**
- Shared database, shared schema with `tenant_id` column
- PostgreSQL Row-Level Security (RLS) for automatic isolation
- JWT tokens include tenant_id claim
- All queries automatically filtered by tenant context
- No cross-tenant data access possible at database level

**Scalability Approach:**
- Start with single database (supports 1000+ tenants)
- Ready for horizontal sharding by tenant_id if needed
- Redis caching for cross-tenant aggregates
- CDN for static assets and dashboard components

## Subscription & Billing Model

**Pricing Tiers:**
- **Free:** 1 user, 100 transactions/month, basic dashboards
- **Starter:** $39/month - 3 users, 1000 transactions, all dashboards
- **Professional:** $79/month - 10 users, unlimited transactions, benchmarking
- **Business:** $149/month - unlimited users, API access, white-label

**Billing Infrastructure:**
- Stripe integration for payments
- Chilean credit cards and Mercado Pago support
- Monthly and annual billing options (20% discount annual)
- Auto-retry failed payments with dunning emails
- Grace period before account suspension

## Permission & Access Control

**Role-Based Access Control (RBAC):**
- **Owner:** Full access, billing, user management, all dashboards
- **Manager:** All dashboards, reports, no billing access
- **Analyst:** Read-only dashboard access, export reports
- **Viewer:** Limited dashboard access, no exports

**Company Management:**
- Users can belong to multiple companies
- Company switcher in navigation
- Separate permission sets per company
- Invitation system with email verification

## API Specification

**Core API Endpoints (REST):**

**Authentication:**
- `POST /api/auth/register` - Register with email/password
- `POST /api/auth/login` - Login with email/password
- `POST /api/auth/google` - Google OAuth callback
- `POST /api/auth/verify-email` - Verify email address
- `POST /api/auth/reset-password` - Request password reset
- `POST /api/auth/refresh` - Refresh JWT token
- `POST /api/auth/logout` - Invalidate session

**Company Management:**
- `GET /api/companies` - List user's companies
- `POST /api/companies` - Create new company (auto-creates first location)
- `GET /api/companies/{id}` - Get company details
- `PUT /api/companies/{id}` - Update company settings
- `DELETE /api/companies/{id}` - Soft delete company

**Location Management:**
- `GET /api/companies/{id}/locations` - List all locations for company
- `POST /api/companies/{id}/locations` - Add new location to company
- `GET /api/locations/{id}` - Get location details
- `PUT /api/locations/{id}` - Update location settings
- `DELETE /api/locations/{id}` - Soft delete location (requires 2+ locations)

**Data Operations:**
- `POST /api/data/upload` - CSV upload endpoint
- `GET /api/data/transactions` - Query transactions
- `POST /api/data/aggregate` - Trigger aggregation pipeline
- `GET /api/data/status` - Check processing status

**Analytics:**
- `GET /api/analytics/dashboard/{type}` - Get dashboard data (annual/monthly/hourly)
- `GET /api/analytics/performance-index` - Calculate performance score
- `GET /api/analytics/benchmarks` - Get sector comparisons
- `GET /api/analytics/trends` - Time series analysis

**User Management:**
- `GET /api/users/me` - Current user profile
- `POST /api/users/invite` - Invite team member
- `PUT /api/users/{id}/role` - Update user role
- `DELETE /api/users/{id}` - Remove user access

## Authentication & Authorization

**JWT-Based Authentication:**
- Email/password registration with email verification
- Google OAuth 2.0 as optional login method
- JWT tokens with 24-hour expiration
- Refresh tokens with 30-day expiration
- Token includes: user_id, tenant_id, role, permissions
- Password reset via email with time-limited tokens

**Security Headers:**
- `Authorization: Bearer {jwt_token}`
- `X-Tenant-ID: {tenant_id}` (redundant safety)
- `X-Request-ID: {uuid}` (tracing)

**Rate Limiting:**
- 100 requests/minute per user (general)
- 10 uploads/hour per company (data operations)
- 1000 requests/hour per company (analytics)

---
