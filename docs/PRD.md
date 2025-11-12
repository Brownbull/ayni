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
- **Progressive Multi-Location Enhancement:**
  - Default: 1 company = 1 location (auto-created together)
  - Company creation form includes first location details (name + address/website)
  - "+ Add Location" button unlocks multi-location features
  - Dashboard transforms to show location breakdown when 2nd location added
  - This approach simplifies MVP for single-location users while supporting growth

**3. Core Dashboards**
- **Company Dashboard (Annual View):**
  - 12 monthly cards with revenue, growth %, performance index
  - Year selector dropdown (current year default)
  - Current month visually highlighted
  - If 2+ locations: Location breakdown panel showing metrics per location
  - Clickable location cards drill into location-specific view
- **Location Dashboard (Annual View):**
  - Only accessible when company has 2+ locations
  - Breadcrumb: Dashboard > Company > Location
  - 12 monthly cards filtered to that specific location
  - Year selector dropdown
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
- **Multi-Level Benchmarking:**
  - Company-to-company: Compare aggregated performance across all locations
  - Location-to-location: Compare individual locations within multi-location companies
  - Within-company: Compare your own locations against each other
  - Multi-company owners: Compare performance between your own companies

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

**Multi-Location Management:**
- FR2.13: Companies SHALL support 1 to N locations (minimum 1)
- FR2.14: Company creation form SHALL include first location details (name, address OR website)
- FR2.15: System SHALL auto-create primary location when company is created
- FR2.16: Users SHALL add additional locations via "+ Add Location" button in settings
- FR2.17: Location SHALL have name, address (for physical stores) OR website URL (for web-based businesses)
- FR2.18: CSV uploads SHALL be tagged to a specific location

**Playground Demo:**
- FR2.9: System SHALL auto-create demo company on first user login
- FR2.10: Demo SHALL include 12 months of realistic transaction data
- FR2.11: Users SHALL select from 5 industries: Restaurant, Distributor, Clothing/Retail, Electronics, Medical Equipment
- FR2.12: Demo SHALL display persistent banner: "This is demo data. Create your real company"

**Data Retention & Processing Model:**
- FR2.20: System SHALL delete uploaded CSV files within 15 days of upload
- FR2.21: System SHALL process and anonymize transaction data within 15-day window before file deletion
- FR2.22: System SHALL retain processed/anonymized transaction data indefinitely for trend analysis
- FR2.23: System SHALL remove all personally identifiable information (customer names, emails, phone numbers) during processing pipeline
- FR2.24: System SHALL maintain "data processor" classification (not "data store") per Chilean data protection regulations
- FR2.25: System SHALL document data lineage showing PII removal and transformation steps

**Franchise Operations Exclusion:**
- FR2.26: System SHALL NOT support franchise-specific features in MVP (out of scope)
- FR2.27: Target market SHALL be limited to SMBs with 3-10 directly-owned locations
- FR2.28: Future franchise support (different P&L ownership, royalty tracking) deferred to post-MVP

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

**Chilean POS Format Intelligence:**
- FR3.19: Column mapping SHALL recognize common Chilean POS column naming patterns
- FR3.20: System SHALL auto-detect Chilean POS naming conventions:
  - "Fecha" / "Date" / "fecha_venta" → `in_dt`
  - "Total" / "Monto" / "total_venta" → `in_price_total`
  - "Producto" / "producto_id" / "SKU" → `in_product_id`
  - "Cantidad" / "quantity" / "cant" → `in_quantity`
- FR3.21: System SHALL display confidence scores for auto-detected mappings
- FR3.22: Users SHALL confirm or override auto-detected mappings before processing

**Format Detection & Normalization:**
- FR3.23: System SHALL auto-detect numeric format:
  - Chilean standard: `1.234,56` (dot thousands, comma decimal)
  - US standard: `1,234.56` (comma thousands, dot decimal)
- FR3.24: System SHALL auto-detect date format:
  - `DD/MM/YYYY` (Chilean common)
  - `YYYY-MM-DD` (ISO standard)
  - `MM/DD/YYYY` (US format)
- FR3.25: System SHALL show format preview: "We detected Chilean format (1.234,56) ✅"
- FR3.26: Users SHALL override if auto-detection incorrect
- FR3.27: Format settings SHALL be saved in mapping template for reuse

**Chilean POS Validation Badge:**
- FR3.28: System SHALL display "Chilean POS Tested ✅" badge when recognizing common formats
- FR3.29: Supported systems SHALL include detection for:
  - Defontana exports (common Chilean ERP)
  - Buk exports (Chilean HR/payroll system)
  - Nubox exports (Chilean accounting software)
  - Generic POS CSV formats
- FR3.30: Unsupported formats SHALL show "Custom format - please map carefully" warning

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

**Multi-Location Dashboard (Company View):**
- FR4.13: Company dashboard SHALL display year-to-date metrics (current year default)
- FR4.14: Company dashboard SHALL include year selector dropdown to change years
- FR4.15: Company dashboard SHALL display 12 monthly cards for the selected year
- FR4.16: Current month card SHALL be visually highlighted
- FR4.17: If company has 2+ locations, dashboard SHALL show location breakdown panel
- FR4.18: Location breakdown panel SHALL display aggregated metrics per location for selected time period
- FR4.19: Location cards SHALL be clickable to navigate to location-specific view
- FR4.20: Company-level metrics SHALL aggregate (SUM) across all locations

**Multi-Location Dashboard (Location View):**
- FR4.21: Location view SHALL only be accessible when company has 2+ locations
- FR4.22: Location dashboard SHALL display breadcrumb: Dashboard > Company > Location
- FR4.23: Location dashboard SHALL display year-to-date metrics for that specific location
- FR4.24: Location dashboard SHALL include year selector dropdown
- FR4.25: Location dashboard SHALL display 12 monthly cards for selected year
- FR4.26: Location view SHALL filter all metrics to that location only

**Hybrid Time Granularity Navigation:**
- FR4.27: Dashboard SHALL provide parallel access to multiple time granularities (not pure hierarchical drill-down)
- FR4.28: Company dashboard SHALL display both:
  - Last month performance card (monthly aggregation)
  - Last day performance card (daily aggregation)
  - Both visible simultaneously without drilling
- FR4.29: Users SHALL navigate between annual/monthly/daily/hourly views via tabs or quick-switch controls
- FR4.30: Breadcrumb navigation SHALL indicate current view but not enforce strict hierarchy
- FR4.31: Users SHALL access "today's performance" directly from any screen via quick action button

**Opinionated Analytics Philosophy:**
- FR4.32: System SHALL provide fixed, curated analytics (NOT customizable dashboards or drag-and-drop builders)
- FR4.33: Users SHALL NOT create custom visualizations or dashboard layouts
- FR4.34: Users SHALL rank/favorite pre-built views for personalized ordering
- FR4.35: System SHALL provide 10-15 core views designed for non-technical business owners
- FR4.36: All views SHALL include contextual help tooltips explaining metrics and why they matter
- FR4.37: System SHALL NOT provide:
  - Custom date range pickers (beyond preset granularities: hour/day/week/month/quarter/year)
  - Drag-and-drop dashboard builders
  - SQL/query interfaces
  - "Analyst mode" or advanced customization tools

**View Personalization (Limited Scope):**
- FR4.38: Users SHALL mark views as "Favorite" to appear at top of navigation
- FR4.39: Users SHALL hide views they don't use (minimum 3 views must remain visible)
- FR4.40: Users SHALL provide feedback: "Useful" / "Not Useful" on each view (for product improvement)
- FR4.41: System SHALL suggest views based on industry and usage patterns
- FR4.42: Personalization SHALL NOT extend to layout customization, color schemes, or data manipulation

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
- FR6.5: Aggregations SHALL use k-anonymity model (minimum k=10 companies per sector)
- FR6.6: No reverse engineering of individual data SHALL be possible through simple aggregates (sum, average, percentiles)
- FR6.7: Users SHALL opt-in to contribute data to benchmarks
- FR6.8: System SHALL use simulated data until critical mass reached

**Multi-Level Benchmarking:**
- FR6.9: System SHALL support company-to-company benchmarking (aggregate across all locations)
- FR6.10: System SHALL support location-to-location benchmarking (for multi-location companies)
- FR6.11: Users owning multiple companies SHALL compare performance between their own companies
- FR6.12: Users SHALL compare performance between their own locations within same company

**Opt-in Incentive Model:**
- FR6.13: Users SHALL explicitly opt-in to contribute anonymized data to sector benchmarking pools during onboarding
- FR6.14: Opt-out users SHALL view limited sector statistics (basic averages) without personalized comparison indicators on dashboards
- FR6.15: Opt-out users SHALL NOT see percentile rankings or performance index comparisons
- FR6.16: Opt-in users SHALL see full comparison indicators across all dashboards (company/location/monthly/yearly views)
- FR6.17: Opt-in users SHALL access complete sector statistics, percentile rankings, and performance index
- FR6.18: System SHALL clearly communicate value difference between opt-in and opt-out during onboarding flow
- FR6.19: Onboarding SHALL include toggle: "Contribute my anonymized data to sector benchmarks and unlock full comparisons"

**Benchmarking Cold Start Strategy:**
- FR6.20: System SHALL include hardcoded demo dataset with 12+ months of simulated sector data (not in production database)
- FR6.21: Demo data SHALL be used in playground companies to demonstrate benchmarking value
- FR6.22: Live sector statistics SHALL be calculated continuously but hidden from UI until minimum threshold met
- FR6.23: Benchmarking features SHALL only appear in UI when sector has ≥10 opt-in companies
- FR6.24: No "coming soon" messaging SHALL be shown - features appear seamlessly when threshold reached
- FR6.25: Users SHALL see message "Sector benchmarking will be available when 10+ companies join your sector" if <10 companies

**Percentile Ranking Educational Context:**
- FR6.26: System SHALL provide contextual help explaining what percentile rankings mean
- FR6.27: Dashboard SHALL include "What does this mean?" tooltip for percentile indicators
- FR6.28: System SHALL suggest actionable insights based on percentile tier:
  - Top 25% (75th+ percentile): "You're outperforming peers - what's working?"
  - Middle 50% (25th-75th): "You're on track - explore optimization opportunities"
  - Bottom 25% (<25th): "Investigate: Are there seasonal factors or operational issues?"
- FR6.29: Users SHALL access "Understanding Your Performance Index" help article from dashboard

**Opt-in Conversion Funnel:**
- FR6.30: Opt-out users SHALL see greyed-out comparison indicators with "Opt-in to unlock ⭐" tooltips
- FR6.31: System SHALL provide "View demo companies" link from limited benchmarking view
- FR6.32: Demo companies SHALL display full benchmarking experience to show value
- FR6.33: Modal SHALL appear when opt-out users view sector statistics: "Want to see how YOU compare? Opt-in →"
- FR6.34: Email campaigns SHALL re-engage opt-out users with social proof and network effects messaging
- FR6.35: System SHALL track opt-in conversion rate as key metric (target: 70% opt-in within 90 days)

**Opt-in Re-engagement Campaigns:**
- FR6.36: Week 2 email: "See how other [Sector] businesses are performing - opt-in to compare"
- FR6.37: Week 4 email: "You're missing personalized insights - join [X] other companies"
- FR6.38: In-app notifications: "80% of [Sector] users have opted in - unlock comparisons"
- FR6.39: Social proof messaging: "[120] businesses contributing to [Retail] sector benchmarks"
- FR6.40: Early adopter incentive: "Be one of the first 50 companies - shape your sector's insights"

**Sector Consolidation Strategy:**
- FR6.41: MVP SHALL launch with 5 broad sectors (not 20): Retail, Food Service, Distribution, Professional Services, Other
- FR6.42: Sector taxonomy SHALL require <50 companies to cover all active sectors (5 sectors × 10 companies minimum)
- FR6.43: System SHALL consolidate sectors if any sector <5 companies by Month 6
- FR6.44: Future expansion to granular sectors (e.g., "Clothing Retail", "Electronics") only after hitting 200+ total companies

**Privacy Model Specification:**
- FR6.45: System SHALL implement k-anonymity with k=10 (minimum 10 companies per sector)
- FR6.46: Benchmarks SHALL use simple aggregates: sum, average, median, percentiles (no noise injection required)
- FR6.47: Current approach meets Chilean Data Protection Law 19.628 requirements through aggregation-based anonymization
- FR6.48: True differential privacy (epsilon/delta parameters) deferred to Year 2+ if needed for advanced AI features

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
- FR8.6: Free tier SHALL enforce 300 transaction limit (updated from 100)
- FR8.7: System SHALL send warning at 80% of limit (240 transactions)
- FR8.8: Exceeding limits SHALL prompt upgrade, not data loss

### 9. AI & Future Capabilities

**AI-Ready Dataset Architecture:**
- FR9.1: Multi-level aggregation pipeline SHALL generate AI-queryable datasets suitable for LLM/chatbot queries
- FR9.2: Future AI features (Year 2+) SHALL query pre-aggregated tables, not raw transactions, for privacy compliance
- FR9.3: System SHALL support natural language queries on aggregated data (e.g., "Which location grew fastest last quarter?")

### 10. Launch Validation & Risk Mitigation (CRITICAL)

**Acquisition Validation Gate (BLOCKING FOR LAUNCH):**
- FR10.1: System SHALL NOT launch publicly until CAC validated <$300 in at least 2 acquisition channels
- FR10.2: Beta phase SHALL test 3 channels: content marketing, partnerships (Defontana/Buk/Nubox), paid ads
- FR10.3: Month 3 kill criteria: If CAC >$500 across all channels, trigger strategy pivot
- FR10.4: Partnership outreach SHALL begin Month 1 (Defontana, Buk, Nubox, business consultants)

**Engagement Threshold Monitoring:**
- FR10.5: System SHALL track weekly login rate per cohort (target: 50%+ by Month 3)
- FR10.6: System SHALL track feature usage across 15 dashboard views (if <3 views used by 80% of users, simplify UI)
- FR10.7: System SHALL trigger product review if monthly churn >5% for 2 consecutive months
- FR10.8: If mobile traffic >30%, mobile-first redesign SHALL be triggered within 4 weeks

**Aha Moment Optimization:**
- FR10.9: Time-to-first-insight SHALL be <15 minutes from signup to actionable dashboard
- FR10.10: Onboarding SHALL include guided "first upload" with sample CSV download provided
- FR10.11: Dashboard SHALL highlight "Top 3 Insights" on first login (not show all 15 views immediately)
- FR10.12: System SHALL show "Next Action" suggestions alongside metrics, not just raw numbers

**Competitive Monitoring & Response:**
- FR10.13: Team SHALL monitor competitor launches (Defontana Analytics, Buk partnerships, Power BI templates) monthly
- FR10.14: Competitive response plan SHALL be triggered if major competitor launches analytics product
- FR10.15: Pivot options SHALL include: white-label strategy, API business model, partnership/acquisition
- FR10.16: White-label offering SHALL be designed by Month 6 as partnership enabler for POS providers

**Partnership Strategy (Month 1 Priority):**
- FR10.17: Outreach SHALL begin Month 1 to: Defontana, Buk, Nubox, Chilean business consulting firms
- FR10.18: Goal: Integration partnership OR reseller agreement within 6 months of launch
- FR10.19: If direct integration not achievable, pursue referral partnership program (commission-based)
- FR10.20: Partnership deck SHALL be prepared in pre-launch phase with case studies, ROI calculator

**Hyper-Growth Contingency Plan:**
- FR10.21: If 150+ customers acquired by Month 6 (3x target), trigger contingency plan:
  - Immediately hire: Support Lead + Senior Backend Engineer
  - Launch self-service content sprint (10 video tutorials, chatbot, knowledge base)
  - Validate database scaling strategy (test sharding at 100 companies)
  - Increase infrastructure budget by 50%
- FR10.22: Hyper-growth monitoring SHALL track customer acquisition velocity monthly
- FR10.23: If growth rate >25 customers/month sustained for 2 months, trigger pre-emptive scaling

**Multi-POS Positioning Strategy:**
- FR10.24: If major POS provider (Defontana, Buk) becomes direct competitor:
  - Pivot messaging to "Works with ANY POS system" (universal compatibility)
  - Target multi-location businesses using 2+ different POS systems
  - Emphasize CSV compatibility as strength, not limitation
- FR10.25: Competitive intelligence SHALL monitor POS provider product announcements monthly
- FR10.26: White-label offering SHALL be market-ready by Month 6 as defensive strategy

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

**Performance Scalability Monitoring:**
- NFR1.13: System SHALL monitor query performance for PostgreSQL RLS policies from Day 1
- NFR1.14: System SHALL establish performance baseline at 100 companies / 10M transactions
- NFR1.15: System SHALL trigger architectural review if:
  - Dashboard load times exceed 3 seconds (p95)
  - Database query times exceed 1 second (p95)
  - Concurrent user capacity drops below 500
  - Aggregation job duration exceeds 1 hour
- NFR1.16: System SHALL implement query optimization (materialized views, indexes) before considering RLS alternatives
- NFR1.17: Architecture decision: PostgreSQL RLS sufficient for MVP, revisit at 1000+ tenants

**Load Testing Requirement (BLOCKING FOR LAUNCH):**
- NFR1.18: System SHALL complete load testing before public launch:
  - Simulate 1000 concurrent users
  - Simulate 1000 companies / 100M total transactions
  - Validate dashboard load time <2s (p95)
  - Validate aggregation pipeline completes in <30 minutes
- NFR1.19: Performance budgets SHALL be enforced via automated CI/CD checks
- NFR1.20: Load test SHALL identify bottlenecks and trigger optimization sprint if needed

**Performance Monitoring & Alerting:**
- NFR1.21: System SHALL implement Datadog or NewRelic monitoring from Day 1
- NFR1.22: Alerts SHALL trigger for:
  - Dashboard p95 >3 seconds
  - API p95 >500ms
  - Database CPU >70%
  - Aggregation job duration >1 hour
  - CSV upload failures >5%
- NFR1.23: Monthly performance review SHALL analyze trends and trigger optimization if degrading
- NFR1.24: On-call rotation SHALL respond to performance alerts within 15 minutes

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

**Data Processor Compliance:**
- NFR2.19: System SHALL maintain "data processor" classification under Chilean data protection law
- NFR2.20: System SHALL NOT retain raw uploaded CSV files beyond 15 days
- NFR2.21: System SHALL complete all data processing, transformation, anonymization, and aggregation within 15-day retention window
- NFR2.22: System SHALL document and audit data lineage showing PII removal compliance
- NFR2.23: System SHALL provide users with "Data Processing Timeline" documentation showing file deletion schedule

**Privacy Model Clarification:**
- NFR2.24: System SHALL implement k-anonymity with k=10 (minimum 10 companies per sector)
- NFR2.25: Benchmarks SHALL use simple aggregates: sum, average, median, percentiles
- NFR2.26: No noise injection required (aggregation-based anonymization sufficient for Chilean law)
- NFR2.27: True differential privacy (epsilon/delta parameters) deferred to Year 2+ if needed for advanced AI features
- NFR2.28: Current approach meets Chilean Data Protection Law 19.628 requirements

**Data Sovereignty Readiness:**
- NFR2.29: Architecture SHALL support multi-region deployment without code changes
- NFR2.30: Chilean data localization compliance plan SHALL be documented
- NFR2.31: If Chilean law requires data localization, migration playbook SHALL enable seamless transition
- NFR2.32: System SHALL support datacenter selection per company (Chilean companies → Chilean DC, others → global DC)

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

**Background Job Processing:**
- NFR3.12: CSV uploads >10K transactions SHALL process asynchronously via Celery
- NFR3.13: Users SHALL see real-time progress updates via WebSocket or polling
- NFR3.14: Failed jobs SHALL retry 3x with exponential backoff
- NFR3.15: System SHALL email user on completion/failure with clear next steps
- NFR3.16: Background jobs SHALL have monitoring dashboards showing queue depth, processing time, failure rate

**Zero-Downtime Migration Capability:**
- NFR3.17: Database replication strategy SHALL enable seamless datacenter migrations
- NFR3.18: Gradual cutover process SHALL maintain <100ms latency increase during migration
- NFR3.19: System SHALL support blue-green deployment for major infrastructure changes
- NFR3.20: Migration playbook SHALL be tested annually with simulated datacenter move

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

**Technical Debt Register:**
- NFR5.13: System SHALL maintain technical debt log documenting known performance limitations
- NFR5.14: RLS scalability SHALL be tracked as "Monitor & Optimize" debt item
- NFR5.15: Each debt item SHALL include:
  - Risk level (low/medium/high)
  - Trigger conditions for addressing
  - Estimated effort to resolve
  - Mitigation strategies
- NFR5.16: Technical debt review SHALL occur quarterly with prioritization decisions

---

## Risk Management & Failure Prevention

### Pre-mortem Analysis: Critical Failure Paths Identified

**Scenario: December 2026 - What if Ayni fails?**

To prevent failure, we've identified 5 critical risk paths and built mitigation strategies into requirements:

#### 🔴 Failure Path 1: Customer Acquisition Collapse
**Risk:** CAC >$500, couldn't validate sustainable unit economics, burned through runway.
**Mitigation:** FR10.1 - Acquisition validation gate (BLOCKING for launch)

#### 🔴 Failure Path 2: Product-Market Fit Illusion
**Risk:** Built for wrong persona, users didn't engage, 8% monthly churn.
**Mitigation:** FR10.2, FR10.3 - Engagement monitoring, aha moment <15 min

#### 🔴 Failure Path 3: Benchmarking Network Effects Failed
**Risk:** Never hit critical mass, 60% opt-out rate, no viral growth.
**Mitigation:** FR6.19, FR6.20 - Sector consolidation (5 not 20), opt-in incentives

#### 🔴 Failure Path 4: Technical Debt Explosion
**Risk:** PostgreSQL RLS hit performance wall, 40% dev time on firefighting.
**Mitigation:** NFR1.14, NFR1.15 - Load testing (BLOCKING), performance monitoring

#### 🔴 Failure Path 5: Competitive Response Overwhelmed
**Risk:** Defontana/Buk launched competing products, features copied, pricing pressure.
**Mitigation:** FR10.5 - Partnership strategy (Month 1), white-label pivot readiness

---

## Implementation Planning

### Epic Breakdown Required

This PRD contains **107 functional requirements** and **65 non-functional requirements** that must be decomposed into implementable epics and bite-sized stories optimized for AI-assisted development (200k context limit).

**Requirements Added (Advanced Elicitation + Pre-mortem Analysis):**
- FR2.20-FR2.21: Data retention & franchise scope (2 requirements)
- FR3.19-FR3.21: Chilean POS format intelligence (3 requirements)
- FR4.27-FR4.29: Hybrid navigation & opinionated analytics (3 requirements)
- FR6.13-FR6.20: Benchmarking strategy & opt-in conversion (8 requirements)
- FR8.9: Freemium limit updated to 300 transactions/month
- FR9.1: AI-ready dataset architecture (1 requirement)
- FR10.1-FR10.5: Launch gates & risk mitigation (5 requirements - CRITICAL)
- NFR1.13-NFR1.15, NFR2.19-NFR2.20, NFR3.12, NFR5.13: Technical debt, monitoring, privacy (7 requirements)

**BLOCKING Requirements for Public Launch:**
- ⚠️ **FR10.1:** CAC validation <$300 in 2+ channels
- ⚠️ **NFR1.14:** Load testing (1000 users, 100M transactions, <2s dashboard load)

**Progressive Enhancement Strategy:** The multi-location architecture uses progressive disclosure - single-location companies get a simple experience, and multi-location features unlock when a second location is added. This keeps the MVP clean for the majority of users while supporting growth.

**Next Step:** Run `workflow create-epics-and-stories` to create the implementation breakdown.

### Technology Stack

**Backend:**
- FastAPI (Python) - Modern async framework
- PostgreSQL with Row-Level Security - Multi-tenant isolation
  - **Database Schema:** `locations` table with `company_id` foreign key
  - **Aggregation Strategy:** Location-level first, then company roll-ups (SUM across locations)
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

This PRD captures the complete requirements for Ayni - from authentication to analytics, from MVP to moonshot features - including comprehensive multi-location support with progressive enhancement.

**Requirements Summary:**
- **154 Functional Requirements** (FR1-FR10)
  - 90 original requirements
  - 64 added through Advanced Elicitation, Pre-mortem Analysis, What If Scenarios & Dependency Mapping
- **89 Non-Functional Requirements** (NFR1-NFR5)
  - 60 original requirements
  - 29 added for performance monitoring, privacy model, technical debt management, data sovereignty, zero-downtime migrations

**Critical Additions:**
- ✅ Launch validation gates (CAC <$300, load testing - BLOCKING)
- ✅ Failure prevention strategies (5 critical paths identified & mitigated)
- ✅ Chilean POS format intelligence (Defontana, Buk, Nubox tested)
- ✅ Opinionated analytics philosophy (fixed views, not customizable)
- ✅ Opt-in conversion funnel (70% target, re-engagement campaigns)
- ✅ Data processor compliance (15-day retention, k-anonymity)
- ✅ Performance monitoring from Day 1 (Datadog, automated alerts)
- ✅ Partnership strategy (Month 1 outreach to POS providers)

---

_Created through collaborative discovery between Gabe and BMM Product Manager agent._
_Date: 2025-11-11_
_Enhanced: 2025-11-12 (Advanced Elicitation + Pre-mortem Analysis)_