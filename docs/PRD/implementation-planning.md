# Implementation Planning

## Epic Breakdown Required

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

## Technology Stack

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
