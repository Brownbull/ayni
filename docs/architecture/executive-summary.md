# Executive Summary

Ayni is a multi-tenant SaaS platform that transforms retail analytics for Chilean and Latin American SMBs. This architecture document defines the technical foundation for building a scalable, secure system that handles multi-location analytics, cross-tenant benchmarking, and real-time dashboard performance.

**Key Architectural Principles:**
- **Multi-tenant isolation** via PostgreSQL Row-Level Security
- **Async-first** design for performance (FastAPI + asyncpg + React Query)
- **Early deployment** strategy to catch integration issues early
- **AI agent consistency** through strict implementation patterns
- **Mobile-first reality** with desktop-first development
- **Chilean-specific** localization throughout

**Technology Stack:** FastAPI + PostgreSQL + React 19 + Tailwind CSS + Celery + Redis + gabeda_core

---
