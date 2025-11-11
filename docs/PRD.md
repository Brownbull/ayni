# ayni - Product Requirements Document

**Author:** Gabe
**Date:** 2025-11-11
**Version:** 1.0

---

## Executive Summary

Ayni transforms how multi-location retail SMBs in Chile and Latin America understand their business performance. By replacing teams of data engineers, scientists, and analysts with automated analytics infrastructure, Ayni delivers enterprise-grade insights at SMB-friendly prices.

The platform solves a critical blind spot: retail business owners with 3-10 locations have transaction data scattered across multiple POS systems but lack the analytical infrastructure to turn this data into competitive intelligence. They spend 10+ hours weekly on manual Excel reporting, make $50-100K expansion decisions on gut feel, and operate without knowing how they compare to similar retailers.

Ayni provides the missing infrastructure through automated multi-temporal aggregation pipelines, pre-built retail dashboards, and most uniquely - anonymized cross-tenant benchmarking that shows percentile rankings against sector competitors. This is "Warcraft Logs for Business" - making performance analytics engaging through gamification while delivering serious business value.

### What Makes This Special

The magic of Ayni lies in three transformative moments:

1. **The First Dashboard View** - When Carolina sees all 5-8 stores aggregated in one view for the first time, weeks of Excel work becomes instant insight
2. **The Percentile Revelation** - Discovering "You rank in the 68th percentile" transforms gut feel into data-driven confidence
3. **The Time Liberation** - When Miguel realizes he just got 10 hours of his week back to focus on strategy, not spreadsheets

What makes this truly special is the network effect moat: every new customer makes the cross-tenant benchmarking more valuable, creating competitive intelligence that no competitor can replicate without our data. We're not just building dashboards - we're democratizing infrastructure that normally requires a full data team.

---

## Project Classification

**Technical Type:** SaaS B2B Platform
**Domain:** Retail Analytics
**Complexity:** Level 3 (Multi-tenant, cross-tenant aggregation, complex data pipelines)

This is a multi-tenant SaaS platform with sophisticated data infrastructure requirements. The project combines:
- Complex multi-temporal aggregation pipelines (hour/day/week/month/quarter/year dimensions)
- Multi-tenant isolation with PostgreSQL Row-Level Security
- Cross-tenant anonymized benchmarking (unique technical challenge)
- Real-time dashboard performance at scale
- Freemium to paid conversion funnel optimization

---

## Success Criteria

### Primary Success Metrics

**Year 1 - Product-Market Fit Validation:**
- ✅ 50 paying customers (Chilean retail SMBs with 3-10 locations)
- ✅ $40K ARR ($79 ARPU × 50 customers × 10 months average)
- ✅ NPS >30 (good for SaaS)
- ✅ Monthly churn <5% (industry benchmark)
- ✅ 80% of users logging in 2-3x per week
- ✅ 60% using cross-tenant benchmarking within 30 days

**Critical User Outcomes:**
- **Time Saved:** Users reduce reporting time from 10+ hours to <1 hour weekly
- **Decision Confidence:** 100% of expansion decisions backed by location performance data
- **Competitive Intelligence:** Users know their percentile ranking vs. sector
- **Problem Detection:** Underperforming stores identified within 48 hours (vs. weeks)
- **ROI Demonstration:** Users can quantify $5-20K saved from faster problem detection

**Platform Health Indicators:**
- **Time to First Value:** <1 hour (playground demo explored)
- **Time to Real Company Creation:** <7 days from signup
- **Data Upload Completion:** 80% upload real data within 14 days
- **Freemium → Paid Conversion:** 2-5% (industry standard)
- **LTV:CAC Ratio:** >3:1 (sustainable unit economics)

### Business Metrics

**Financial Targets:**
- **Year 1:** $40K ARR, 50 customers
- **Year 2:** $160K ARR, 200 customers
- **Year 3:** $475K ARR, 500 customers, break-even
- **Gross Margin:** 80%+ (typical SaaS)
- **Infrastructure Cost:** <1% of revenue

**Market Penetration:**
- **TAM:** $8.44B LATAM business analytics market
- **SAM:** $845M-$1.27B Chile + adjacent markets
- **SOM Target:** 1-3% market share within 3 years ($8.5M-$38.1M)

---

## Product Scope

### MVP - Minimum Viable Product

**Core Value Proposition:** Multi-location analytics with cross-tenant benchmarking in <1 hour setup

**1. Authentication & Onboarding**
- Email/password registration with verification
- Google OAuth login (optional)
- Playground company with demo data (Restaurant, Distributor, Tech, Medical Equipment)
- Full year of simulated transactions pre-loaded
- Persistent banner: "This is demo data. Create your real company → [Start Now]"

**2. Data Infrastructure (The Moat)**
- CSV upload with Replace/Append modes
- Column mapping interface for flexible CSV formats
- Validation before processing (required columns, data types)
- Saved mapping templates for repeat uploads
- Automated multi-temporal aggregation pipeline (hour/day/week/month/quarter/year)
- Multi-tenant isolation with PostgreSQL RLS
- Company creation with RUT validation (Chile) or string identifier (other countries)
- Company switcher for multiple businesses

**3. Core Dashboards**
- **Annual Dashboard:** 12 monthly cards with revenue, growth %, performance index
- **Monthly Dashboard:** Deep dive into single month performance
- **Alert Indicators:** ✅✅⚠️ format for quick health assessment
- **Drill-down Navigation:** Click any metric to explore deeper

**4. Performance Index (Gamification)**
- Formula: (Your Revenue / Sector Average) × 100
- Color-coded rankings: Green (90-100), Blue (75-89), Purple (50-74), Grey (0-49)
- "Parse score for business" engagement model

**5. Cross-Tenant Benchmarking (Unique Differentiator)**
- Anonymized sector averages
- Percentile ranking: "You rank in the 68th percentile"
- Start with simulated data, transition to real aggregates at 50+ companies/sector

**6. Essential Features**
- Multi-language support (English/Spanish)
- Dark/Light mode toggle
- Chilean Peso (CLP) pricing display
- Landing page with clear value proposition

### Growth Features (Post-MVP)

**Months 3-6 Post-Launch:**

**Enhanced Analytics:**
- AI-powered forecasting (predict next month/quarter)
- Multiple Performance Index models (growth-focused, efficiency, diversification)
- Hourly Dashboard (intraday patterns)
- Product-level performance analytics
- Location comparison matrix

**External Context:**
- Buffs & Debuffs calendar (holidays, events, economic factors)
- Weather impact correlation
- Competitive event tracking

**AI & Automation:**
- Natural language Q&A ("How did my best store perform last quarter?")
- Automated insights generation
- Anomaly detection alerts

**Reporting:**
- PDF export for banks/investors
- Scheduled email reports
- Custom dashboard builder

### Vision (Future)

**Year 2+ Moonshot Features:**

**Platform Evolution:**
- Real-time POS integrations (Chilean ERPs/CRMs)
- Mobile app (iOS/Android native)
- API for third-party integrations
- Webhook notifications

**Advanced Analytics:**
- Predictive models (churn, credit risk, demand forecasting)
- Multi-variate optimization (pricing, inventory, staffing)
- Supply chain analytics
- Customer lifetime value modeling

**Collaboration:**
- Multi-role dashboards (Operations Manager, Sales Lead, CFO views)
- Private benchmarking groups (franchise networks)
- Cross-owner benchmarking groups
- Team annotations and insights sharing

**Market Expansion:**
- Industry-specific models marketplace
- White-label offering for POS providers
- Enterprise tier with custom integrations
- Regional expansion (Peru, Colombia, Mexico)

---

---

## SaaS B2B Specific Requirements

### Multi-Tenancy Architecture

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

### Subscription & Billing Model

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

### Permission & Access Control

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

### API Specification

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
- `POST /api/companies` - Create new company
- `GET /api/companies/{id}` - Get company details
- `PUT /api/companies/{id}` - Update company settings
- `DELETE /api/companies/{id}` - Soft delete company

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

### Authentication & Authorization

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

## User Experience Principles

### Design Philosophy

**"Professional Gaming Aesthetic"** - Combine the engagement of gaming interfaces with the trust of professional tools:
- Clean, modern interface inspired by esports analytics platforms
- Color-coded performance metrics (green/blue/purple/grey rankings)
- Instant visual feedback and smooth transitions
- Dark mode as first-class citizen (not an afterthought)

### Core UX Principles

1. **Zero to Insight in 60 Seconds**
   - Playground demo loads immediately on first visit
   - No empty states - always show meaningful data
   - Progressive disclosure - complexity revealed as needed

2. **Dashboard Hierarchy**
   - Annual view as default (strategic overview)
   - Click to drill down (month → day → hour)
   - Breadcrumb navigation for context
   - Escape key returns to previous level

3. **Visual Information Density**
   - High data-to-ink ratio
   - Minimal chrome, maximum content
   - Sparklines and micro-charts for trends
   - Hover for details, click for action

4. **Mobile-First Responsive**
   - Touch-friendly targets (44px minimum)
   - Swipe gestures for time navigation
   - Responsive grid that reflows intelligently
   - Native-feeling interactions on mobile

### Key Interactions

**Dashboard Navigation:**
- **Click monthly card** → Opens monthly detailed view
- **Hover over metric** → Shows tooltip with context
- **Drag time slider** → Updates all charts in real-time
- **Press spacebar** → Toggle play/pause for time animation

**Data Upload Flow:**
- **Drag & drop zone** → Visual feedback on hover
- **Progress indicator** → Real-time processing status
- **Success animation** → Celebration moment when complete
- **Error recovery** → Clear guidance on fixing issues

**Performance Index:**
- **Animated rank reveal** → Build anticipation
- **Color transition** → Smooth fade between ranking tiers
- **Percentile counter** → Animated count-up to final number
- **Share button** → One-click social proof generation

**Quick Actions:**
- **CMD/CTRL + K** → Universal search/command palette
- **CMD/CTRL + D** → Toggle dark/light mode
- **CMD/CTRL + L** → Switch language
- **CMD/CTRL + ,** → Open settings

---

## Functional Requirements

### 1. User Management & Authentication

**Account Creation & Access:**
- FR1.1: Users SHALL register and authenticate via email/password OR Google OAuth 2.0
- FR1.2: System SHALL create user profile on registration with email verification
- FR1.3: Users SHALL remain logged in for 30 days via refresh tokens
- FR1.4: System SHALL support multiple users per company with role-based permissions

**User Roles & Permissions:**
- FR1.5: System SHALL implement 4 roles: Owner, Manager, Analyst, Viewer
- FR1.6: Owners SHALL manage billing, users, and all company settings
- FR1.7: Managers SHALL access all dashboards without billing permissions
- FR1.8: Analysts SHALL have read-only dashboard access with export capabilities
- FR1.9: Viewers SHALL have limited dashboard access without exports

### 2. Company & Multi-Tenancy

**Company Management:**
- FR2.1: Users SHALL create multiple companies under one account
- FR2.2: Companies SHALL be created with a unique identifier (RUT for Chile, string for others)
- FR2.3: System SHALL validate Chilean RUT format when Chile is selected as country
- FR2.4: System SHALL accept any string as unique identifier for non-Chilean companies
- FR2.5: System SHALL prevent duplicate company identifiers within the platform
- FR2.6: System SHALL provide company switcher in main navigation
- FR2.7: Each company SHALL have isolated data with no cross-contamination
- FR2.8: Companies SHALL have configurable settings (name, industry, timezone, country)

**Playground Demo:**
- FR2.9: System SHALL auto-create demo company on first user login
- FR2.10: Demo SHALL include 12 months of realistic transaction data
- FR2.11: Users SHALL select from 4 industries: Restaurant, Distributor, Tech, Medical
- FR2.12: Demo SHALL display persistent banner: "This is demo data. Create your real company"

### 3. Data Pipeline & Processing

**Data Upload & Validation:**
- FR3.1: System SHALL accept CSV files via drag-and-drop or file selector
- FR3.2: Upload SHALL support two modes: Replace (overwrite) and Append (add)
- FR3.3: System SHALL require column mapping configuration before processing

**CSV Column Mapping:**
- FR3.4: Users SHALL map their CSV columns to expected system columns
- FR3.5: REQUIRED columns that must be mapped:
  - `in_dt` - Transaction datetime
  - `in_trans_id` - Unique transaction ID
  - `in_product_id` - Product identifier
  - `in_quantity` - Quantity sold
  - `in_price_total` - Total price/revenue of transaction
- FR3.6: OPTIONAL columns that may be mapped:
  - `in_trans_type` - Transaction type
  - `in_customer_id` - Customer identifier
  - `in_description` - Product description
  - `in_category` - Product category
  - `in_unit_type` - Unit of measure
  - `in_stock` - Stock level
- FR3.7: INFERABLE columns (system can calculate if not provided):
  - `in_cost_unit` - Unit cost
  - `in_cost_total` - Total cost
  - `in_price_unit` - Unit price
  - `in_discount_total` - Total discount
  - `in_commission_total` - Total commission
  - `in_margin` - Profit margin

**Validation Process:**
- FR3.8: System SHALL validate mapped columns exist in uploaded file
- FR3.9: System SHALL validate data types match expected formats
- FR3.10: System SHALL validate required columns are present and mapped
- FR3.11: System SHALL provide clear error messages for validation failures
- FR3.12: System SHALL allow users to save column mapping templates for reuse
- FR3.13: Upload progress SHALL display in real-time with estimated completion

**Multi-Temporal Aggregation:**
- FR3.14: System SHALL automatically aggregate data into 6 time dimensions
- FR3.15: Aggregations SHALL include: hourly, daily, weekly, monthly, quarterly, yearly
- FR3.16: Pipeline SHALL calculate sum, average, min, max, count for each dimension
- FR3.17: Aggregations SHALL complete within 5 minutes for 1M transactions

**Data Storage:**
- FR3.18: System SHALL store raw transactions and aggregated metrics separately
- FR3.19: Data SHALL be partitioned by tenant_id for isolation
- FR3.20: System SHALL maintain data lineage for audit trail
- FR3.21: Historical data SHALL be retained for minimum 3 years

### 4. Dashboard & Analytics

**Annual Dashboard (Default View):**
- FR4.1: Dashboard SHALL display 12 monthly cards in 4x3 grid
- FR4.2: Each card SHALL show: revenue, growth %, performance index
- FR4.3: Cards SHALL use alert indicators: ✅ (good), ⚠️ (warning), ❌ (critical)
- FR4.4: Clicking a month card SHALL navigate to monthly detail view

**Monthly Dashboard:**
- FR4.5: Dashboard SHALL show detailed metrics for selected month
- FR4.6: View SHALL include product-level performance breakdown
- FR4.7: Location comparison SHALL display if multiple locations exist
- FR4.8: Time series chart SHALL show daily trends within month

**Dashboard Navigation:**
- FR4.9: Breadcrumb trail SHALL show: Annual > Month > Day hierarchy
- FR4.10: ESC key SHALL return to previous dashboard level
- FR4.11: Time slider SHALL allow quick navigation between periods
- FR4.12: Dashboard URLs SHALL be shareable with proper authentication

### 5. Performance Index & Gamification

**Performance Score Calculation:**
- FR5.1: System SHALL calculate: (Company Revenue / Sector Average) × 100
- FR5.2: Score SHALL update nightly after aggregation pipeline completes
- FR5.3: Historical scores SHALL be stored for trend analysis

**Visual Ranking System:**
- FR5.4: Scores SHALL map to color tiers: Green (90-100), Blue (75-89), Purple (50-74), Grey (0-49)
- FR5.5: Rank reveal SHALL animate on dashboard load
- FR5.6: Color transitions SHALL smoothly fade when tier changes

### 6. Cross-Tenant Benchmarking

**Sector Comparison:**
- FR6.1: System SHALL calculate anonymized sector averages nightly
- FR6.2: Benchmarks SHALL require minimum 10 companies per sector
- FR6.3: Individual company data SHALL never be exposed
- FR6.4: Percentile ranking SHALL show: "You rank in the Xth percentile"

**Data Privacy:**
- FR6.5: Aggregations SHALL use differential privacy techniques
- FR6.6: No reverse engineering of individual data SHALL be possible
- FR6.7: Users SHALL opt-in to contribute data to benchmarks
- FR6.8: System SHALL use simulated data until critical mass reached

### 7. Localization & Accessibility

**Multi-Language Support:**
- FR7.1: Interface SHALL support English and Latin American Spanish
- FR7.2: Language toggle SHALL be accessible from main navigation
- FR7.3: All text SHALL be properly localized, not machine translated
- FR7.4: Numbers SHALL format according to selected locale

**Currency & Regional:**
- FR7.5: System SHALL display Chilean Peso (CLP) with proper formatting
- FR7.6: Dates SHALL use DD/MM/YYYY format for LATAM users
- FR7.7: Timezone SHALL default to Santiago/Chile (UTC-3)

**Theme Support:**
- FR7.8: System SHALL provide dark and light mode options
- FR7.9: Theme preference SHALL persist across sessions
- FR7.10: Charts SHALL maintain readability in both themes

### 8. Billing & Subscription

**Subscription Management:**
- FR8.1: System SHALL integrate with Stripe for payment processing
- FR8.2: Chilean credit cards and Mercado Pago SHALL be supported
- FR8.3: Users SHALL upgrade/downgrade plans without data loss
- FR8.4: Annual plans SHALL receive 20% discount automatically

**Usage Tracking:**
- FR8.5: System SHALL track monthly transaction count per company
- FR8.6: Free tier SHALL enforce 100 transaction limit
- FR8.7: System SHALL send warning at 80% of limit
- FR8.8: Exceeding limits SHALL prompt upgrade, not data loss

---

## Non-Functional Requirements

### Performance

**Dashboard Load Times:**
- NFR1.1: Annual dashboard SHALL load in <2 seconds on 4G connection
- NFR1.2: Monthly dashboard SHALL load in <1.5 seconds
- NFR1.3: Dashboard interactions SHALL respond in <100ms
- NFR1.4: Charts SHALL render smoothly at 60fps

**Data Processing:**
- NFR1.5: CSV upload SHALL process 100K transactions in <30 seconds
- NFR1.6: Multi-temporal aggregation SHALL complete within 5 minutes for 1M transactions
- NFR1.7: Cross-tenant benchmarks SHALL calculate in <10 seconds nightly
- NFR1.8: API responses SHALL return in <500ms for p95

**Scalability:**
- NFR1.9: System SHALL support 1000+ concurrent users
- NFR1.10: Platform SHALL handle 10K companies without performance degradation
- NFR1.11: Database SHALL scale to 100M+ transactions per company

### Security

**Data Protection:**
- NFR2.1: All data in transit SHALL use TLS 1.3
- NFR2.2: Passwords SHALL be hashed with bcrypt (cost factor 12)
- NFR2.3: PostgreSQL RLS SHALL enforce tenant isolation at database level
- NFR2.4: System SHALL prevent SQL injection via parameterized queries
- NFR2.5: File uploads SHALL be scanned for malware

**Authentication & Authorization:**
- NFR2.6: JWT tokens SHALL expire after 24 hours
- NFR2.7: Refresh tokens SHALL be rotated on each use
- NFR2.8: Failed login attempts SHALL be rate-limited (5 attempts per 15 minutes)
- NFR2.9: Password reset tokens SHALL expire after 1 hour
- NFR2.10: Email verification SHALL be required before account activation

**Tenant Isolation:**
- NFR2.11: Cross-tenant data access SHALL be impossible at code and database level
- NFR2.12: Tenant ID SHALL never be accepted from client requests
- NFR2.13: All database queries SHALL automatically filter by authenticated tenant
- NFR2.14: System SHALL log all cross-tenant access attempts

**Compliance:**
- NFR2.15: System SHALL comply with Chilean Data Protection Law 19.628
- NFR2.16: Users SHALL have right to data deletion
- NFR2.17: System SHALL maintain audit logs for 1 year
- NFR2.18: Data exports SHALL be encrypted

### Reliability & Availability

**Uptime:**
- NFR3.1: Platform SHALL maintain 99.5% uptime (22 hours downtime/year)
- NFR3.2: Planned maintenance SHALL occur during low-traffic windows
- NFR3.3: System SHALL notify users 48 hours before maintenance

**Backup & Recovery:**
- NFR3.4: Database SHALL be backed up daily
- NFR3.5: Backups SHALL be retained for 30 days
- NFR3.6: System SHALL support point-in-time recovery within 24 hours
- NFR3.7: Critical data SHALL be replicated across availability zones

**Error Handling:**
- NFR3.8: System SHALL gracefully handle API failures
- NFR3.9: User-facing errors SHALL provide clear guidance
- NFR3.10: System errors SHALL be logged with full context
- NFR3.11: Critical errors SHALL trigger alerts to operations team

### Usability

**Accessibility:**
- NFR4.1: Interface SHALL be keyboard navigable
- NFR4.2: Color contrast SHALL meet WCAG 2.1 AA standards
- NFR4.3: Screen readers SHALL properly announce all UI elements
- NFR4.4: Touch targets SHALL be minimum 44x44px

**Responsiveness:**
- NFR4.5: Interface SHALL work on desktop (1920x1080 to 1366x768)
- NFR4.6: Interface SHALL work on tablet (768x1024)
- NFR4.7: Interface SHALL work on mobile (375x667 minimum)
- NFR4.8: Layout SHALL reflow intelligently at all breakpoints

**Browser Support:**
- NFR4.9: Platform SHALL support Chrome/Edge (last 2 versions)
- NFR4.10: Platform SHALL support Firefox (last 2 versions)
- NFR4.11: Platform SHALL support Safari (last 2 versions)
- NFR4.12: Unsupported browsers SHALL show upgrade notice

### Maintainability

**Code Quality:**
- NFR5.1: Backend SHALL use type hints (Python)
- NFR5.2: Frontend SHALL use TypeScript strict mode
- NFR5.3: Code coverage SHALL exceed 70%
- NFR5.4: Critical paths SHALL have 90%+ coverage

**Documentation:**
- NFR5.5: API SHALL be documented with OpenAPI 3.0
- NFR5.6: All public functions SHALL have docstrings
- NFR5.7: Architecture decisions SHALL be documented
- NFR5.8: Deployment process SHALL be documented

**Monitoring:**
- NFR5.9: System SHALL log all errors with stack traces
- NFR5.10: Performance metrics SHALL be tracked (Datadog/similar)
- NFR5.11: User analytics SHALL be captured (PostHog/similar)
- NFR5.12: Database query performance SHALL be monitored

---

## Implementation Planning

### Epic Breakdown Required

This PRD contains 74 functional requirements and 60 non-functional requirements that must be decomposed into implementable epics and bite-sized stories optimized for AI-assisted development (200k context limit).

**Next Step:** Run `workflow create-epics-and-stories` to create the implementation breakdown.

### Technology Stack

**Backend:**
- FastAPI (Python) - Modern async framework
- PostgreSQL with Row-Level Security - Multi-tenant isolation
- Redis - Caching and background jobs
- Celery - Async task processing
- Railway - Deployment platform

**Frontend:**
- React 19 + TypeScript - Component framework
- Vite - Build tooling
- Tailwind CSS - Styling
- Recharts 3.0 - Data visualization
- React Query + Zustand - State management
- Render - Static hosting with CDN

**Development Timeline:**
- MVP: 10-12 weeks (2.5-3 months)
- Backend: 6 weeks (auth, APIs, aggregation, multi-tenancy)
- Frontend: 6 weeks (dashboards, charts, responsive design)

---

## References

### Source Documentation

- **Product Brief:** [docs/product-brief-ayni-2025-11-11.md](docs/product-brief-ayni-2025-11-11.md)
- **Market Research:** [docs/bmm-research-market-2025-11-10.md](docs/bmm-research-market-2025-11-10.md)
- **User Research:** [docs/bmm-research-user-2025-11-10.md](docs/bmm-research-user-2025-11-10.md)
- **Competitive Analysis:** [docs/bmm-research-competitive-2025-11-10.md](docs/bmm-research-competitive-2025-11-10.md)
- **Technical Research:** [docs/bmm-research-technical-2025-11-10.md](docs/bmm-research-technical-2025-11-10.md)
- **Brainstorming Session:** [docs/brainstorming-session-results-2025-11-10.md](docs/brainstorming-session-results-2025-11-10.md)

### Market Context

- **TAM:** $8.44B LATAM business analytics (2025) → $12.21B (2030)
- **SAM:** $845M-$1.27B Chile + adjacent markets
- **Target:** 50 customers Year 1, $40K ARR

---

## Next Steps

### Immediate (Week 1-2)

1. ✅ **PRD Complete** - This document
2. **Epic & Story Breakdown** - Run: `/bmad:bmm:workflows:create-epics-and-stories`
3. **Validate PRD** - Run: `/bmad:bmm:workflows:validate-prd`

### Phase 2: Solutioning (Week 3-4)

1. **UX Design** - Run: `/bmad:bmm:workflows:create-ux-design` (Critical for UI-heavy platform)
2. **Architecture** - Run: `/bmad:bmm:workflows:architecture` (Technical decisions)
3. **Solutioning Gate Check** - Run: `/bmad:bmm:workflows:solutioning-gate-check`

### Phase 3: Implementation (Week 5-16)

1. **Sprint Planning** - Run: `/bmad:bmm:workflows:sprint-planning`
2. **Story Development** - Execute stories sequentially
3. **Beta Launch** - 10-15 Chilean retail SMBs

---

## Summary

**Ayni democratizes enterprise-grade analytics for LATAM retail SMBs through three transformative moments:**

1. **The First Dashboard View** - Weeks of Excel work becomes instant insight
2. **The Percentile Revelation** - "You rank in the 68th percentile" transforms gut feel into confidence
3. **The Time Liberation** - 10 hours weekly saved for strategic work

**The network effect moat:** Every new customer makes cross-tenant benchmarking more valuable, creating competitive intelligence no competitor can replicate without our data.

This PRD captures the complete requirements for Ayni - from authentication to analytics, from MVP to moonshot features - providing the foundation for epic breakdown and implementation.

---

_Created through collaborative discovery between Gabe and BMM Product Manager agent._
_Date: 2025-11-11_