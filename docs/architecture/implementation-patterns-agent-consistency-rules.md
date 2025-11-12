# Implementation Patterns (Agent Consistency Rules)

## NAMING PATTERNS

**Backend (Python):**
- Files: `snake_case.py` (e.g., `csv_processor.py`)
- Classes: `PascalCase` (e.g., `CompanyService`)
- Functions: `snake_case` (e.g., `process_csv_file`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_FILE_SIZE`)
- Database Tables: `snake_case` plural (e.g., `companies`, `transactions`)
- Database Columns: `snake_case` (e.g., `company_id`, `created_at`)

**Frontend (TypeScript):**
- Component Files: `PascalCase.tsx` (e.g., `Dashboard.tsx`)
- Utility Files: `camelCase.ts` (e.g., `formatCurrency.ts`)
- Components: `PascalCase` (e.g., `UploadCSV`)
- Functions: `camelCase` (e.g., `fetchDashboardData`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `API_BASE_URL`)
- Interfaces: `PascalCase` with `I` prefix (e.g., `IUser`)
- Types: `PascalCase` (e.g., `CompanyData`)

**API Endpoints:**
- Format: `/api/v1/resource` (plural nouns)
- Parameters: `{id}` not `:id`
- Query params: `snake_case` (e.g., `?company_id=123`)
- Examples:
  - ✅ `/api/v1/companies/{id}/locations`
  - ❌ `/api/v1/company/:id/location`

## STRUCTURE PATTERNS

**Backend:**
- Tests co-located in `tests/` directory, mirror source structure
- One service per file, each handles one domain
- Models in separate files: one model per file in `models/`

**Frontend:**
- Components organized by feature, not by type
  - ✅ `components/dashboard/MonthlyCard.tsx`
  - ❌ `components/cards/MonthlyCard.tsx`
- Tests co-located with components
  - `components/dashboard/MonthlyCard.tsx`
  - `components/dashboard/MonthlyCard.test.tsx`
- One component per file

## FORMAT PATTERNS

**API Response Wrapper (MANDATORY):**
```json
{
  "status": "success",
  "data": {...},
  "message": null
}
```

**Error Response (MANDATORY):**
```json
{
  "status": "error",
  "message": "User-friendly message in Spanish",
  "errors": [
    {"field": "email", "message": "Invalid format"}
  ]
}
```

**Date Format in API:**
- Send: ISO 8601 with timezone: `"2025-11-12T10:30:00-03:00"`
- Receive: ISO 8601 UTC: `"2025-11-12T13:30:00Z"`
- Display: DD/MM/YYYY (Chilean format)

**Numbers in JSON:**
- Currency: Raw numbers (no formatting): `1234567`
- Percentages: Decimals: `0.685` (not `68.5`)
- Frontend formats for display

**Chilean Formatting:**
```typescript
// Currency
const formatCurrency = (amount: number) =>
  new Intl.NumberFormat('es-CL', {
    style: 'currency',
    currency: 'CLP',
    minimumFractionDigits: 0
  }).format(amount);
// Output: $1.234.567

// Numbers
const formatNumber = (num: number) =>
  new Intl.NumberFormat('es-CL').format(num);
// Output: 1.234.567,89
```

## COMMUNICATION PATTERNS

**Database Queries (MANDATORY):**
```python
# ALWAYS use async
result = await session.execute(select(Company).where(...))

# ALWAYS filter by tenant (RLS handles this, but for clarity)
await session.execute(
    text("SELECT set_config('app.current_tenant', :tenant_id, false)"),
    {"tenant_id": current_user.tenant_id}
)

# ALWAYS use transactions for writes
async with session.begin():
    session.add(new_company)
    await session.commit()
```

**API Calls (Frontend - MANDATORY):**
```typescript
// ALWAYS use React Query
const { data, isLoading } = useQuery({
  queryKey: ['companies'],
  queryFn: fetchCompanies,
});

// NEVER use bare axios/fetch in components
// ❌ Bad: axios.get('/api/companies')
// ✅ Good: useQuery with React Query
```

## LIFECYCLE PATTERNS

**Loading States:**
- Backend: Return 202 Accepted for async operations
- Frontend: Skeleton screens (not spinners)

**Error Recovery:**
- Backend: Celery tasks retry 3 times, exponential backoff
- Frontend: React Query retries 3 times for failed requests

**State Management:**
- Server State: React Query (auto-refetch every 5 minutes)
- UI State: Zustand (persisted to localStorage)

## CONSISTENCY PATTERNS

**Dates Everywhere:**
- Backend: Store UTC, convert to Santiago timezone for display
- Frontend: Use `date-fns` for all date operations
- Display: DD/MM/YYYY (Chilean format)

**Currency Everywhere:**
- Backend: Store as DECIMAL(12, 2)
- Frontend: Format with `Intl.NumberFormat('es-CL')`
- Display: $1.234.567 CLP

**Error Messages:**
- Primary: Spanish (Chilean Spanish)
- Include: English translation in `message_en` field
- User-facing: Never show stack traces

**Logging Everywhere:**
- Include: `tenant_id`, `user_id`, `request_id` in all logs
- Format: Structured JSON
- Level: INFO (operations), ERROR (failures), WARNING (security)

## SECURITY PATTERNS (CRITICAL)

**Tenant Isolation:**
```python
# MANDATORY: Set RLS context on every request
await session.execute(
    text("SELECT set_config('app.current_tenant', :tenant_id, false)"),
    {"tenant_id": current_user.tenant_id}
)
```

**Authentication:**
```python
# MANDATORY: Use dependency injection
from app.api.deps import get_current_active_user

@router.get("/companies")
async def get_companies(
    current_user: User = Depends(get_current_active_user)
):
    # tenant_id from current_user, NEVER from request
    pass
```

**Frontend:**
```typescript
// MANDATORY: Always include auth token
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
```

---
