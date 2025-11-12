# Epic to Architecture Mapping

| Epic | Backend Components | Frontend Components | Database Tables | External Services |
|------|-------------------|---------------------|-----------------|-------------------|
| **Authentication & User Management** | `api/v1/endpoints/auth.py`, fastapi-users | `pages/Login.tsx`, `hooks/useAuth.ts` | `users` | Google OAuth |
| **Company Management** | `api/v1/endpoints/companies.py`, RLS policies | `components/companies/`, `hooks/useCompany.ts` | `companies` | - |
| **Multi-Location Support** | `api/v1/endpoints/locations.py` | `pages/LocationView.tsx`, `components/locations/` | `locations` | - |
| **CSV Upload & Column Mapping** | `api/v1/endpoints/data.py`, `services/csv_processor.py` | `pages/Upload.tsx`, `components/upload/ColumnMapper.tsx` | `transactions`, `mapping_templates` | gabeda_core |
| **Multi-Temporal Aggregation** | `workers/tasks.py`, `services/aggregation.py` | N/A (background processing) | `aggregates_hourly`, `aggregates_daily`, `aggregates_weekly`, `aggregates_monthly`, `aggregates_quarterly`, `aggregates_yearly` | Celery + Redis |
| **Dashboard Analytics** | `api/v1/endpoints/analytics.py` | `pages/Dashboard.tsx`, `components/dashboard/` | `aggregates_*`, `companies`, `locations` | - |
| **Cross-Tenant Benchmarking** | `api/v1/endpoints/benchmarks.py`, `services/benchmarking.py` | `components/dashboard/PercentileCard.tsx` | `benchmarks`, `sector_averages` | - |
| **Internationalization** | API responses with i18n | react-i18next, `utils/i18n.ts` | - | - |
| **Billing & Subscriptions** (Post-MVP) | Stripe integration endpoints | `pages/Billing.tsx` | `subscriptions`, `payments` | Stripe |

---
