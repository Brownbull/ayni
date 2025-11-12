# Executive Summary

## Project Vision

**Ayni** transforms how multi-location retail SMBs in Chile and Latin America understand their business performance. By replacing teams of data engineers, scientists, and analysts with automated analytics infrastructure, Ayni delivers enterprise-grade insights at SMB-friendly prices.

The platform solves a critical blind spot: retail business owners with 3-10 locations have transaction data scattered across multiple POS systems but lack the analytical infrastructure to turn this data into competitive intelligence. We're essentially building "Warcraft Logs for Business" - making performance analytics engaging through gamification while delivering serious business value.

## Technical Approach

Based on pragmatic development considerations:
- **Initial UI:** Chakra UI (FastAPI cookiecutter default) - migration to Tailwind post-MVP
- **Deployment:** Early and continuous deployment to Railway (backend) + Render (frontend)
- **Testing:** Playwright/Chrome DevTools verification of actual UI functionality
- **Architecture:** Keep FastAPI backend, eventually rebuild frontend fresh with React + Tailwind

## Target Users

Chilean retail SMBs with 3-10 locations, 10-50 employees - operations managers and business owners who currently spend 10+ hours weekly on manual Excel reporting, making $50-100K expansion decisions without data-driven insights.

---
