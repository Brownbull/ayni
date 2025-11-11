# Product Brief: Ayni

**Date:** 2025-11-11
**Author:** Gabe
**Context:** Software Project (Level 3, BMM Method, Greenfield)

---

## Executive Summary

Ayni is a multi-tenant business analytics SaaS platform designed specifically for multi-location retail SMBs in Chile and Latin America. The platform transforms raw transactional data into actionable insights with cross-tenant benchmarking capabilities - essentially "Warcraft Logs for Business."

**The Core Insight:** Chilean retail SMBs (3-10 locations, 10-50 employees) lack affordable, retail-specific analytics that provide competitive intelligence. They're flying blind, unable to answer basic questions like "How do I compare to similar retailers?" or "Which location should I replicate for expansion?"

**The Unique Value:** Ayni democratizes Experian-level analytical infrastructure for SMBs - replacing teams of data engineers, scientists, and analysts with automated pipelines and cross-tenant insights that no competitor can replicate.

**Market Opportunity:** $845M-$1.27B SAM in Chile + adjacent LATAM markets, growing at 7-17% CAGR in an underserved segment where 83% of SMBs are actively investing in digital transformation.

---

## Core Vision

### Problem Statement

Multi-location retail business owners in Chile face a critical blind spot: they have transaction data scattered across multiple POS systems but lack the analytical infrastructure to turn this data into competitive intelligence.

**The Pain:**
- **3-4 hours weekly** spent manually compiling Excel reports from each POS system
- **$50-100K expansion decisions** made on gut feel without data on what makes successful locations successful
- **Complete competitive blindness** - no way to know if performance is good compared to similar retailers
- **$20-50K annual waste** in inventory mismanagement across locations
- **Weeks of delay** detecting underperforming stores, costing $5-20K in lost revenue

**The Deeper Issue:** The problem isn't dashboards - it's infrastructure. SMBs can't build the enterprise-grade data warehouses, dimensional modeling, and multi-temporal aggregation pipelines that would normally require:
- Team of data engineers
- Data scientist to design features
- Analyst to build models
- BI specialist to create reports

Without this infrastructure, sophisticated analysis is impossible. They're stuck with basic POS reports that work for single locations but break down at 3+ locations.

### Problem Impact

**Business Impact:**
- **Expansion Risk:** $50-100K investments in new locations made without data-driven confidence
- **Revenue Leakage:** Underperforming stores go undetected for weeks, costing $5-20K per incident
- **Inventory Waste:** $20-50K annually lost to overstock and stockouts across locations
- **Time Drain:** 10+ hours weekly spent on manual reporting by operations managers
- **Competitive Disadvantage:** Operating blind while competitors may have better insights

**Emotional Impact:**
- Anxiety about making wrong expansion decisions
- Frustration with reactive problem-solving instead of proactive management
- Feeling of lost control over multi-location operations
- Lack of confidence when presenting to banks, investors, or boards

**Market Validation:**
- 40% of LATAM SMBs cite "insufficient budget" as barrier to analytics adoption
- 83% of LATAM SMBs actively investing in digital transformation
- Chile: 94.1% internet penetration, 86% public services digitalized
- No competitor offers transaction→analytics→sector benchmarking combination in Chile

### Why Existing Solutions Fall Short

**Enterprise BI Tools (Power BI, Tableau):**
- Too expensive: $100-750/month for 10-person team vs. our $79/month
- Too complex: Requires weeks of setup and analyst training
- Horizontal: Not retail-specific, requires building everything from scratch
- Overkill: 80% of features unused by SMBs

**SMB Tools (Zoho Analytics):**
- Horizontal: No retail-specific dashboards or metrics
- Per-user pricing: Costs scale with team collaboration
- No benchmarking: Can't compare to other companies
- Generic: Slower time-to-value without pre-built templates

**POS Built-in Reports:**
- Single-POS only: Can't aggregate across multiple locations
- Basic metrics: Revenue totals without deeper analytics
- No benchmarking: Zero competitive intelligence
- Limited: Can't answer strategic questions about expansion or optimization

**Local Competitors (Elemetrica):**
- Limited features: Basic real-time POS analytics only
- No cross-tenant insights: Missing the unique differentiator
- Uncertain stability: Startup risk without proven track record

**Bottom Line:** There's a white space for a retail-specific, SMB-affordable, LATAM-optimized analytics platform with cross-tenant competitive intelligence.

---

## Proposed Solution

### The Ayni Platform

Ayni is a purpose-built analytics infrastructure platform that transforms raw retail transaction data into multi-dimensional insights with competitive benchmarking - all without requiring data engineering expertise.

**How It Works:**
1. **Easy Data Upload:** SMBs upload transaction CSVs (daily/weekly/monthly batches) via simple interface
2. **Automated Aggregation:** Platform automatically generates hour/day/week/month/quarter/year dimensional aggregations
3. **Instant Dashboards:** Pre-built retail dashboards show insights immediately - no configuration needed
4. **Cross-Tenant Intelligence:** Anonymized sector benchmarking shows "You rank in the 68th percentile"
5. **Multi-Location View:** All stores aggregated in one dashboard with drill-down capability

**The "Playground" Onboarding Experience:**
- First login: User selects industry (Restaurant, Distributor, Tech, Medical Equipment)
- Auto-created demo company with full year of realistic simulated data
- User explores fully functional dashboards before creating real company
- **Principle:** "Don't ask users to imagine value - immerse them in it"
- Persistent banner: "This is demo data. Create your real company → [Start Now]"
- Conversion trigger when user sees the value and wants their own data

**Core Platform Features (MVP):**

**1. Multi-Temporal Aggregation Pipeline** (The Infrastructure Moat)
- Automated calculation of metrics across 6 time dimensions: hour, day, week, month, quarter, year
- Each temporal level unlocks different analytical questions
- Pre-computing creates performance advantage competitors can't easily replicate

**2. Annual Dashboard** (Primary Landing View)
- 12 monthly cards showing 3 key metrics per month: revenue, growth %, performance index
- Alert indicators (✅✅⚠️ format) for quick health assessment
- Clickable drill-down to monthly detail views
- Buff/debuff indicators (holidays, seasonal patterns, economic factors)

**3. Performance Index System** ("Parse Score" for Business)
- Default model: (Your Revenue / Sector Average Revenue) × 100
- Color-coded rankings: Green (90-100), Blue (75-89), Purple (50-74), Grey (0-49)
- Multiple model options: Revenue-focused, Growth-focused, Efficiency, Diversification
- Users select scoring model that fits their business goals

**4. Cross-Tenant Sector Benchmarking** (The Unique Differentiator)
- Anonymized aggregation of sector data: "Restaurant sector average: $150K monthly revenue"
- Percentile ranking: "You rank in the 68th percentile among similar retailers"
- Performance comparison without exposing individual company data
- **This is impossible for competitors to replicate without our tenant data**

**5. Multi-Location Aggregation**
- All locations visible in single dashboard
- Compare performance across stores
- Identify top performers and underperformers
- Location-specific drill-downs

**6. CSV Upload with Smart Modes**
- Replace mode: Overwrite existing data
- Append mode: Add new transactions without deleting
- User controls data management strategy

**7. Multilingual & Theme Support**
- English / Spanish (Latin American)
- Light mode / Dark mode
- Chilean Peso (CLP) pricing display
- Local payment integration (Chilean credit cards, Mercado Pago)

### Key Differentiators

**What Makes Ayni Unique:**

**1. Retail Vertical Specialization**
- Only platform purpose-built for retail SMB metrics
- Pre-configured dashboards for revenue, inventory, product performance, location comparison
- Works out-of-the-box in hours, not weeks
- **vs. Horizontal tools** (Power BI, Zoho): They're swiss-army knives, we're a scalpel for retail

**2. Cross-Tenant Benchmarking (The Network Effect Moat)**
- Unique feature impossible for competitors to replicate without tenant data
- Anonymized sector aggregates provide competitive intelligence
- Value increases with every new customer (network effects)
- **vs. All competitors:** None offer this - it's our defensible moat

**3. LATAM-First Optimization**
- Chilean Peso pricing with purchasing power parity adjustment ($39-79/month vs. $50-100 US equivalent)
- Local payment methods (Chilean credit cards, Mercado Pago, digital wallets)
- Spanish language as first-class citizen, not translation
- Chilean business hours support
- **vs. Global tools:** They're translated from US, we're built for LATAM

**4. Infrastructure-as-a-Service Philosophy**
- Not just dashboards - we're replacing data engineering teams
- Multi-temporal aggregation pipeline automates what would take months to build
- Experian-level analytical infrastructure democratized for SMBs
- **vs. POS reports:** Basic totals vs. enterprise-grade data warehouse

**5. SMB-Friendly Pricing & Packaging**
- Flat $79/month (Professional tier) regardless of team size
- Freemium entry ($0) to try before buying
- No per-user fees that penalize collaboration
- 4-9x cheaper than enterprise tools (Power BI: $100-200, Tableau: $330-750)
- **vs. Enterprise tools:** Built for collaboration, not license counting

**6. Playground-First Onboarding**
- Immersive value demonstration with realistic demo data
- Users explore full platform capabilities before committing
- Zero friction - no data upload required to see value
- **vs. Empty state competitors:** Show value immediately, not eventually

**7. "Warcraft Logs for Business" Gamification**
- Performance Index (parse score equivalent) makes metrics engaging
- Color-coded rankings create aspiration to improve
- Sector comparison without privacy violations
- **vs. Traditional BI:** Makes analytics exciting, not boring

---

## Target Users

### Primary Users: "Carolina the Expanding Retailer" 👔

**Who She Is:**
- **Role:** Business Owner / CEO of regional retail chain
- **Company Size:** 5-8 stores across Santiago and Valparaíso
- **Employees:** 30-45 (5-7 per store)
- **Revenue:** $3-8M annually
- **Age:** 38-48 years old
- **Tech Comfort:** Moderate (uses smartphones, cloud tools, but not technical)

**Her Critical Pain Points:**
1. "I don't know which location to replicate for expansion" ($50-100K decision, make or break)
2. "I can't quickly see which stores are underperforming" (3-4 hours weekly, weeks of delay detecting problems)
3. "I don't know if my performance is good compared to similar retailers" (competitive blindness)
4. "Inventory decisions are guesswork" ($20-50K annual waste)

**Her Jobs-to-be-Done:**
- **Functional:** "See all stores' performance in one dashboard", "Make confident expansion decisions"
- **Emotional:** "Feel in control of my business", "Sleep well knowing I'm not missing problems"
- **Social:** "Be seen as a professional, data-driven operator" (to investors, lenders, peers)

**Her Purchase Triggers:**
- Planning to open new location in 3-6 months (HIGH urgency)
- One store consistently underperforming for 2+ months (STRONG urgency)
- Competitor opened nearby affecting sales (MODERATE urgency)

**Her Decision Criteria:**
1. Ease of setup: Must work within 1 day, not weeks
2. Retail-specific: Pre-built dashboards, not blank canvas
3. Affordable: <$100/month budget
4. Trustworthy: Chilean case studies and testimonials
5. Support: Spanish email support included

**Why She Chooses Ayni:**
- Gets insights in hours that would take weeks with Power BI
- Sees immediately how she compares to sector (unique feature)
- Affordable flat pricing vs. expensive per-user tools
- Built for retailers like her, not retrofitted from enterprise

### Secondary Users: "Miguel the Operations Manager" 📊

**Who He Is:**
- **Role:** Operations Manager / COO (reports to owner)
- **Age:** 28-40 years old
- **Responsibility:** Day-to-day operations, reporting performance to owner
- **Tech Comfort:** Moderate-high (more technical than owner)

**His Critical Pain Points:**
1. "I spend 10 hours/week manually compiling reports" (Excel hell)
2. "The owner asks questions I can't answer quickly" (makes him look unprepared)
3. "I'm stuck as report-compiler, not strategic advisor" (career frustration)

**His Jobs-to-be-Done:**
- **Functional:** "Automate weekly reports", "Answer owner's questions instantly"
- **Emotional:** "Look competent and prepared", "Be seen as valuable strategic advisor"
- **Career:** "Spend time on strategy, not manual work"

**His Influence:** HIGH - Recommends tools to owner, becomes daily user and champion

**Why He Champions Ayni:**
- Saves him 10 hours weekly (immediate ROI)
- Makes him look good to owner with instant answers
- Simple enough he can set up without IT help
- Frees him to do strategic work he actually enjoys

### Future Target: "Sofia the Aspiring Retailer" 🌱

**Who She Is:**
- **Role:** Owner of 1-2 location boutique/specialty store
- **Age:** 25-35 years old
- **Aspiration:** Grow to 3-5 locations like Carolina
- **Budget:** Very limited ($0-30/month)
- **Tech Comfort:** High (digital native)

**Her Role in Strategy:**
- **Freemium user** initially (free tier proves value)
- **Conversion target** when opens 3rd location (upgrade trigger)
- **Future Carolina** in 3-5 years if successful

**Why She Matters:**
- Early adopter who grows with platform
- Will need our product when she scales
- Champions to other aspiring entrepreneurs

---

## Success Metrics

### Business Objectives

**Year 1 Goals:**
- 50 paying customers (Chilean retail SMBs, 3-10 locations)
- $40K ARR ($79 ARPU × 50 customers × 10 months)
- Product-market fit validated (NPS >30, <5% monthly churn)
- 2-3 Chilean POS integrations live

**Year 2 Goals:**
- 200 paying customers
- $160K ARR
- Cross-tenant benchmarking launched with critical mass (50+ companies per sector)
- 5-7 POS integrations
- Expand to secondary Chilean cities (Valparaíso, Concepción)

**Year 3 Goals:**
- 500 paying customers
- $475K ARR
- Geographic expansion (Peru, Colombia)
- Break-even or profitable
- Established brand: "The retail analytics platform for LATAM"

### Key Performance Indicators

**Acquisition Metrics:**
- **Freemium Signups:** 100/month by end of Year 1
- **Freemium → Paid Conversion:** 2-5% (industry standard)
- **CAC (Customer Acquisition Cost):** <$400 blended
- **Traffic Sources:** 30% organic search, 20% paid search, 15% referrals, 10% partnerships

**Activation Metrics:**
- **Time to First Value:** <1 hour (playground demo explored)
- **Time to Real Company Creation:** <7 days from signup
- **Data Upload Completion:** 80% of signups upload data within 14 days
- **Dashboard Views:** 3+ different dashboards viewed in first week

**Engagement Metrics:**
- **Login Frequency:** 2-3x per week (active users)
- **Feature Adoption:** 60% using cross-tenant benchmarking within 30 days
- **Dashboard Shares:** 40% share reports with team members

**Retention Metrics:**
- **Monthly Churn:** <5% (SaaS benchmark)
- **Annual Retention:** >70%
- **Net Revenue Retention:** >100% (upsells offset churn)

**Financial Metrics:**
- **ARPU (Average Revenue Per User):** $79/month (Professional tier)
- **LTV (Lifetime Value):** $1,264 (20-month avg lifecycle × $79 × 80% margin)
- **LTV:CAC Ratio:** 3.16:1 (healthy SaaS metric, target >3:1)
- **Payback Period:** 6.3 months
- **Gross Margin:** 80%+ (typical SaaS)

**Customer Satisfaction:**
- **NPS (Net Promoter Score):** >30 (good for SaaS)
- **CSAT (Customer Satisfaction):** >80%
- **Support Response Time:** <24 hours (Spanish email support)

---

## MVP Scope

### Core Features (Must-Have for Launch)

**MVP Philosophy:** Focus on proving the core value proposition - multi-location analytics with cross-tenant benchmarking. Everything else is future enhancement.

**1. Google OAuth Authentication**
- Frictionless login with Google account
- Persistent user identity across sessions
- JWT-based session management

**2. Playground Company with Demo Data**
- Auto-created demo company on first login
- 4 industry options: Restaurant, Distributor, Tech, Medical Equipment
- Full year of realistic simulated transaction data
- Pre-loaded with calculated statistics
- Persistent demo banner: "This is demo data. Create your real company → [Start Now]"

**3. Multi-Temporal Aggregation Pipeline**
- CSV upload → automated aggregations (hourly/daily/weekly/monthly/quarterly/yearly)
- Transform raw transactions into queryable analytical tables
- Proper dimensional modeling by company, product, location, time
- **This is the infrastructure moat**

**4. Annual Dashboard (Owner Role Only)**
- 12 monthly cards showing: revenue, growth %, performance index
- Alert indicators (✅✅⚠️ format)
- Clickable drill-down to monthly detail view
- Year-at-a-glance performance summary

**5. Monthly Dashboard (Deep Dive)**
- Single month detailed breakdown
- Product-level performance
- Location-level performance
- Trend charts and comparisons

**6. Basic Performance Index (Revenue-Based)**
- Formula: (Your Revenue / Sector Average) × 100
- Color-coded: Green (90-100), Blue (75-89), Purple (50-74), Grey (0-49)
- Proves "Warcraft Logs for business" concept

**7. Sector Benchmark Comparison (MVP Version)**
- Show company metrics vs. sector aggregates
- Percentile ranking: "You rank in the 68th percentile"
- Start with simulated sector data (until real aggregates exist)
- Disclosure about data source

**8. CSV Upload with Smart Modes**
- Replace mode: Overwrite existing data
- Append mode: Add new records
- User controls data accumulation strategy

**9. Multi-lingual Support (EN/ES)**
- English and Latin American Spanish
- Language toggle in navigation

**10. Dark/Light Mode**
- Theme toggle for user preference
- Modern UX expectation

**11. Company Switcher**
- Dropdown to navigate between companies
- "Create New Company" option always available

**12. Landing Page with Clear Value Proposition**
- "From Amateur to Professional: You can't improve what you don't measure"
- Sports/gaming analogy resonates with target market
- Clear CTA: "Start Free"

### Out of Scope for MVP (Post-Launch)

**Features Deferred to Phase 2 (Months 3-6):**
- AI-Powered Forecasting (predict next month/quarter performance)
- Multiple Performance Index Models (growth-focused, efficiency, diversification)
- Hourly Dashboard (intraday transaction patterns)
- Buffs & Debuffs Calendar (external event tracking)
- AI Insights Q&A (LLM-powered natural language queries)
- PDF Export Functionality (generate reports for banks/investors)

**Features Deferred to Phase 3 (Months 6-12):**
- Private Benchmarking Groups (same-owner multi-company comparison)
- Sector Aggregates Dashboard ("All Players" view)
- Primary Alert Zone (intelligent alert system)
- Settings & Profile Management (customization)

**Moonshot Features (Year 2+):**
- Real-Time Data Integration (API integrations with Chilean ERP/CRM)
- Multi-Role Dashboards (Operations Manager, Sales Lead, Analyst views)
- Advanced Statistical Modeling (credit risk scoring, churn prediction)
- Cross-Owner Benchmarking Groups (different business owners)
- Mobile App (native iOS/Android)
- API for Third-Party Integrations (webhooks, Zapier)
- Marketplace for Industry-Specific Models

### MVP Success Criteria

**The MVP is successful if:**
1. ✅ SMB owner can upload transaction data and see dashboard within 1 hour
2. ✅ Multi-location aggregation works (all stores visible in one view)
3. ✅ Basic sector benchmarking provides percentile ranking
4. ✅ Monthly/annual time-based views prove multi-temporal analysis works
5. ✅ 10 beta customers using product weekly and providing feedback
6. ✅ First paying customer within 3 months of launch

**Core Question the MVP Must Answer:**
"Can an SME owner upload transaction data and immediately answer questions that previously required hiring an analyst?"

If yes → Product-market fit validated, proceed to scale.
If no → Iterate on UX, onboarding, or core features.

---

## Market Context

### Market Opportunity

**Total Addressable Market (TAM):**
- LATAM Business Analytics: $8.44B (2025) → $12.21B (2030), 7.67% CAGR
- LATAM Smart Retail (analytics-driven): $32.18B (2025) → $82.64B (2031), 16.9% CAGR

**Serviceable Addressable Market (SAM):**
- Chile + adjacent markets: $845M - $1.27B annually
- 10% of TAM focused on SMB retail segment

**Serviceable Obtainable Market (SOM):**
- Conservative (1% share): $8.5M - $12.7M annually
- Realistic (3% share): $25.4M - $38.1M annually
- Optimistic (5% share): $42.3M - $63.5M annually

### Competitive Landscape

**Primary Competitors:**
1. **Status Quo (POS Basic Reports):** Free, basic, single-location only - **Biggest threat**
2. **Zoho Analytics:** $115/month, horizontal SMB tool - **Direct competitor**
3. **Microsoft Power BI:** $100-200/month, enterprise complexity - **Indirect competitor**
4. **Elemetrica (Chile):** Local player, basic features - **Geographic competitor**
5. **Metabase:** Free (self-hosted), requires DevOps - **Budget alternative**

**Our Competitive Advantage:**
- Retail vertical specialization (only player)
- Cross-tenant benchmarking (impossible to replicate)
- LATAM-first optimization (local payments, CLP pricing)
- SMB-friendly pricing ($79 flat vs. per-user)
- Faster time-to-value (hours vs. weeks)

**Market Gap Validated:**
No competitor in Chile offers transaction→analytics→sector benchmarking combination for SMB retail. **First-mover advantage in defined market.**

### Financial Considerations

**Pricing Strategy (Purchasing Power Parity Adjusted):**
- **Free Tier:** 1 user, 100 transactions/month, basic dashboards
- **Starter:** ~39,000 CLP/month ($39 USD) - 3 users, 1000 transactions
- **Professional:** ~79,000 CLP/month ($79 USD) - 10 users, unlimited transactions, cross-tenant analytics
- **Business:** ~149,000 CLP/month ($149 USD) - unlimited users, API access, white-label

**Revenue Model:**
- Freemium → Paid conversion (2-5% industry standard)
- Primary revenue: Professional tier ($79/month)
- Upsell: Business tier as companies grow

**Unit Economics (Year 1):**
- **ARPU:** $79/month
- **LTV:** $1,264 (20-month lifecycle, 5% churn, 80% margin)
- **CAC:** $400 (blended)
- **LTV:CAC:** 3.16:1 (healthy, target >3:1)
- **Payback Period:** 6.3 months
- **Gross Margin:** 80%+

**Infrastructure Costs:**
- Year 1: $10-20/month (Railway + Render)
- Year 2: $50-100/month
- Year 3: $100-200/month
- **Infrastructure <1% of revenue** (excellent SaaS margin)

**Break-Even Projection:**
- 142 paying customers at $79/month ARPU
- Estimated timeline: ~42 months (bootstrap scenario)
- With funding: Can accelerate significantly

### Market Validation

**Evidence of Demand:**
- 83% of LATAM SMBs actively investing in digital transformation
- Chile: 94.1% internet penetration, 86% public services digitalized
- 40% of SMBs cite "insufficient budget" for analytics (our freemium addresses this)
- Experts/PMEs/consultants confirm no such platform exists in Chilean market

**Willingness to Pay:**
- Chilean SMBs spend $100-300/employee/month on SaaS tools
- Budget constraints: "Sweet spot" is $30-75/month for SMBs
- Our $79 Professional tier aligns with market expectations
- Must demonstrate ROI within 30 days for adoption

---

## Technical Preferences

### Technology Stack (Validated)

**Backend:**
- **Framework:** FastAPI (Python) - Modern, fast, excellent for data/analytics
- **Database:** PostgreSQL with Row-Level Security (multi-tenant isolation)
- **Caching:** Redis (cross-tenant benchmarks, frequently accessed data)
- **Background Jobs:** Celery + Redis (nightly aggregations, report generation)
- **Deployment:** Railway (zero-config, managed PostgreSQL, affordable scaling)

**Frontend:**
- **Framework:** React 19 + TypeScript (modern, component-based)
- **Build Tool:** Vite (fast builds, replaces Create React App)
- **Charting:** Recharts 3.0 (SVG-based, accessible, React-idiomatic)
- **Styling:** Tailwind CSS (rapid UI development)
- **State Management:** React Query (API data) + Zustand (UI state)
- **Deployment:** Render (static site hosting, free tier, global CDN)

**Why This Stack:**
- ✅ Production-ready and battle-tested
- ✅ Cost-effective ($10-20/month Year 1 infrastructure)
- ✅ Scalable to 1000+ customers
- ✅ Fast development velocity (2.5-3 months MVP)
- ✅ Python ecosystem perfect for analytics (pandas, numpy for future ML)
- ✅ Modern best practices (TypeScript, async/await, REST API)

**Multi-Tenancy Approach:**
- Shared database, shared schema (most cost-effective)
- `tenant_id` column in every table
- PostgreSQL Row-Level Security (RLS) for automatic isolation
- JWT-based tenant identification
- **Best for MVP through 10,000 tenants**

**Security & Compliance:**
- HTTPS everywhere (Railway/Render provide free TLS)
- JWT authentication with secure token management
- PostgreSQL RLS (defense in depth against data leakage)
- Input validation (Pydantic models)
- SQL injection prevention (SQLAlchemy ORM)
- Chilean Data Protection Law 19.628 compliance (user consent, right to deletion)

**Development Timeline:**
- **MVP:** 10-12 weeks (2.5-3 months)
  - Backend: 6 weeks (auth, APIs, aggregation pipeline, multi-tenancy)
  - Frontend: 6 weeks (dashboards, charts, responsive design)
  - Parallel development possible
- **Post-MVP Features:** Rolling releases every 2-4 weeks

---

## Risks and Assumptions

### Key Assumptions

**Market Assumptions:**
1. Chilean retail SMBs will pay $79/month for analytics that save time and improve decisions
2. Freemium → paid conversion rate of 2-5% is achievable
3. Cross-tenant benchmarking is valued enough to drive adoption and retention
4. SMBs prefer flat pricing over per-user pricing
5. Chilean market is large enough to support initial growth (50-200 customers Year 1-2)

**Product Assumptions:**
1. CSV upload is acceptable MVP (don't need real-time API integrations initially)
2. Owner dashboard is sufficient for MVP (other roles deferred)
3. Playground demo effectively demonstrates value without real data
4. Multi-temporal aggregation pipeline can be built in 3-4 weeks
5. PostgreSQL with RLS provides sufficient tenant isolation security

**Technical Assumptions:**
1. FastAPI + React stack can scale to 1000+ customers without major refactoring
2. Railway + Render remain cost-effective as we scale
3. Recharts 3.0 can handle dashboard complexity and data volumes
4. Multi-tenant shared database doesn't create performance issues with proper indexing

### Primary Risks

**Risk 1: Budget Constraints Limit SMB Adoption**
- **Probability:** MEDIUM (40% of SMBs cite insufficient budget)
- **Impact:** HIGH (affects customer acquisition velocity)
- **Mitigation:**
  - Freemium tier reduces entry barrier
  - Clear ROI demonstration (time saved, decisions improved)
  - Month-to-month contracts (low commitment)
  - Chilean Peso pricing with PPP adjustment

**Risk 2: Status Quo Bias ("POS Reports Are Good Enough")**
- **Probability:** HIGH (biggest competitor is inertia)
- **Impact:** HIGH (slows customer acquisition)
- **Mitigation:**
  - Playground demo shows immediate value
  - Target pain point moments (expansion decisions, underperformance)
  - Freemium trial eliminates switching cost
  - Case studies showing "before/after" impact

**Risk 3: Multi-Tenant Data Leakage (Security Breach)**
- **Probability:** LOW (if implemented correctly)
- **Impact:** CRITICAL (business-ending)
- **Mitigation:**
  - PostgreSQL Row-Level Security (defense in depth)
  - Comprehensive integration tests for tenant isolation
  - Never trust frontend to send tenant_id
  - Security audit before launch
  - Bug bounty program

**Risk 4: Cross-Tenant Benchmarking Requires Critical Mass**
- **Probability:** MEDIUM (chicken-and-egg problem)
- **Impact:** MEDIUM-HIGH (unique feature won't shine initially)
- **Mitigation:**
  - Start with simulated sector data (industry benchmarks)
  - Transparent disclosure about data source
  - Switch to real aggregates at 50+ companies per sector
  - Emphasize other features until benchmarking reaches critical mass

**Risk 5: Competitor Launches Similar Product**
- **Probability:** MEDIUM (Zoho could add retail templates, Microsoft could target SMBs)
- **Impact:** MEDIUM-HIGH (commoditizes our differentiation)
- **Mitigation:**
  - Move fast to establish Chilean market before big players notice
  - Build cross-tenant data moat (network effects, switching costs)
  - Deep customer relationships (competitor can't easily steal)
  - Vertical specialization depth (harder to replicate than it looks)

**Risk 6: POS Providers Add Advanced Analytics**
- **Probability:** MEDIUM-HIGH (Square, Shopify constantly improving)
- **Impact:** MEDIUM (could make standalone analytics unnecessary)
- **Mitigation:**
  - Multi-POS aggregation (they can't aggregate across their competitors)
  - Cross-tenant insights (they can't/won't share data across customers)
  - Partnership strategy (integrate vs. compete)
  - Focus on multi-location complexity (single POS can't solve)

**Risk 7: Economic Recession in LATAM**
- **Probability:** MEDIUM (economic volatility)
- **Impact:** HIGH (SMB budgets cut, churn increases)
- **Mitigation:**
  - Position as cost-saving tool (replaces manual labor)
  - Month-to-month contracts (flexibility for customers)
  - Diversify geography (Chile, Peru, Colombia)
  - Maintain low burn rate (can survive downturn)

**Risk 8: Customer Acquisition Cost Too High**
- **Probability:** MEDIUM-HIGH (customer acquisition is hard)
- **Impact:** HIGH (unit economics break down)
- **Mitigation:**
  - Freemium PLG reduces CAC
  - Content marketing (organic traffic)
  - Referral program (leverage satisfied customers)
  - POS partnerships (channel distribution)
  - Target: Keep CAC <$400 (LTV:CAC >3:1)

---

## Supporting Materials

### Research Foundation

This Product Brief synthesizes insights from comprehensive discovery research:

**1. Brainstorming Session (2025-11-10)**
- 49 ideas generated across 4 techniques (First Principles, Mind Mapping, What If Scenarios, Five Whys)
- Key insight: Platform's core value is analytical infrastructure, not dashboards
- Validated: "Warcraft Logs for Business" concept with Performance Index gamification
- Validated: Playground solves cold-start problem
- Document: `brainstorming-session-results-2025-11-10.md`

**2. Market Research (2025-11-10)**
- TAM: $8.44B LATAM business analytics market
- SAM: $845M-$1.27B Chile + adjacent markets
- Pricing validation: $39-79/month sweet spot for Chilean SMBs
- Competitive landscape: 6 competitors analyzed, white space identified
- Payment methods: Local integration critical (80% use local cards)
- Document: `bmm-research-market-2025-11-10.md`

**3. User Research (2025-11-10)**
- 3 personas developed: Carolina (Primary), Miguel (Secondary), Sofia (Future)
- Jobs-to-be-Done: "See all locations in one dashboard", "Make confident expansion decisions"
- Pain point validation: $50-100K expansion decisions, 10 hours/week manual reporting
- Purchase triggers: Expansion planning, underperformance, competitor pressure
- Document: `bmm-research-user-2025-11-10.md`

**4. Competitive Intelligence (2025-11-10)**
- 6 competitors analyzed: Power BI, Tableau, Zoho, Metabase, POS reports, Elemetrica
- Threat assessment: POS reports (status quo) and Zoho (direct) are highest threats
- Positioning validated: Retail-specific + LATAM-optimized + cross-tenant = white space
- Document: `bmm-research-competitive-2025-11-10.md`

**5. Technical Research (2025-11-10)**
- Tech stack validated: FastAPI + React on Railway/Render
- Multi-tenancy pattern: Shared DB with Row-Level Security (best for MVP)
- Cost analysis: $10-20/month Year 1 infrastructure (<1% revenue)
- Development timeline: 10-12 weeks MVP
- Document: `bmm-research-technical-2025-11-10.md`

---

## Next Steps

**Immediate (Next 2 Weeks):**
1. ✅ Product Brief complete - this document
2. Validate Product Brief with 5-10 potential customers (user interviews)
3. Refine pricing based on customer feedback
4. Begin technical architecture specification

**Phase 1: Planning (Weeks 3-4)**
1. Create detailed Product Requirements Document (PRD) from this brief
2. Design database schema (multi-tenant, multi-temporal aggregation)
3. Wireframe core dashboards (annual, monthly, benchmarking)
4. Define API endpoints specification

**Phase 2: Development (Weeks 5-16)**
1. Backend development: Auth, APIs, aggregation pipeline, multi-tenancy (6 weeks)
2. Frontend development: Dashboards, charts, responsive design (6 weeks)
3. Integration: Connect frontend ↔ backend (2 weeks)
4. Testing: Security, performance, UX (2 weeks)

**Phase 3: Beta Launch (Weeks 17-20)**
1. Recruit 10-15 beta customers (Chilean retail SMBs)
2. Onboard beta customers with hands-on support
3. Gather feedback, iterate on UX/features
4. Validate pricing and value proposition

**Phase 4: Public Launch (Week 21+)**
1. Launch freemium tier publicly
2. Content marketing (blog posts, SEO)
3. Paid acquisition (Google Ads)
4. POS partnerships outreach
5. Monitor metrics: signups, conversions, churn, NPS

---

_This Product Brief captures the vision and requirements for Ayni, a multi-tenant retail analytics SaaS platform for Chilean SMBs. It was created through collaborative discovery, synthesizing extensive market, user, competitive, and technical research. The brief reflects the unique needs of this software project and provides the foundation for detailed planning and development._

**Next Workflow:** PRD (Product Requirements Document) will transform this brief into detailed specifications, epic breakdowns, and user stories ready for implementation.

