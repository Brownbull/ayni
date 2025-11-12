# Functional Requirements

## 1. User Management & Authentication

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

## 2. Company & Multi-Tenancy

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

## 3. Data Pipeline & Processing

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

## 4. Dashboard & Analytics

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

## 5. Performance Index & Gamification

**Performance Score Calculation:**
- FR5.1: System SHALL calculate: (Company Revenue / Sector Average) × 100
- FR5.2: Score SHALL update nightly after aggregation pipeline completes
- FR5.3: Historical scores SHALL be stored for trend analysis

**Visual Ranking System:**
- FR5.4: Scores SHALL map to color tiers: Green (90-100), Blue (75-89), Purple (50-74), Grey (0-49)
- FR5.5: Rank reveal SHALL animate on dashboard load
- FR5.6: Color transitions SHALL smoothly fade when tier changes

## 6. Cross-Tenant Benchmarking

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

## 7. Localization & Accessibility

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

## 8. Billing & Subscription

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

## 9. AI & Future Capabilities

**AI-Ready Dataset Architecture:**
- FR9.1: Multi-level aggregation pipeline SHALL generate AI-queryable datasets suitable for LLM/chatbot queries
- FR9.2: Future AI features (Year 2+) SHALL query pre-aggregated tables, not raw transactions, for privacy compliance
- FR9.3: System SHALL support natural language queries on aggregated data (e.g., "Which location grew fastest last quarter?")

## 10. Launch Validation & Risk Mitigation (CRITICAL)

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
