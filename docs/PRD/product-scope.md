# Product Scope

## MVP - Minimum Viable Product

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

## Growth Features (Post-MVP)

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

## Vision (Future)

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
