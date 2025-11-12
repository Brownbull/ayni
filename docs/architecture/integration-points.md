# Integration Points

## Backend ↔ Frontend

**Protocol:** REST API with JSON
**Base URL:** `https://api.ayni.cl/api/v1/` (production)
**Authentication:** JWT Bearer tokens in `Authorization` header

**Request Format:**
```json
POST /api/v1/companies
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "name": "Mi Empresa",
  "country": "Chile",
  "identifier": "12.345.678-9"
}
```

**Response Format (Success):**
```json
{
  "status": "success",
  "data": {
    "id": 123,
    "name": "Mi Empresa",
    "country": "Chile",
    "identifier": "12.345.678-9",
    "created_at": "2025-11-12T10:30:00-03:00"
  },
  "message": null
}
```

**Response Format (Error):**
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": [
    {
      "field": "identifier",
      "message": "RUT inválido para Chile"
    }
  ]
}
```

## Backend ↔ Database

**Connection:** SQLAlchemy async engine with asyncpg
**Tenant Isolation:** PostgreSQL Row-Level Security (RLS)
**Connection Pool:** Min 5, Max 20 connections

**RLS Context Setup (Every Request):**
```python
# Set tenant context from JWT token
await session.execute(
    text("SELECT set_config('app.current_tenant', :tenant_id, false)"),
    {"tenant_id": current_user.tenant_id}
)

# All subsequent queries automatically filtered by tenant_id
```

**Migration Strategy:**
```bash
# Create new migration
alembic revision --autogenerate -m "Add locations table"

# Apply migrations
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

## Backend ↔ Celery/Redis

**Message Broker:** Redis (same instance as cache)
**Task Routing:** Default queue for all tasks (MVP)
**Result Backend:** Redis

**Task Definition:**
```python
from app.workers.celery_app import celery_app

@celery_app.task(bind=True, max_retries=3)
def process_csv_task(self, file_path: str, company_id: int, mapping_id: int):
    try:
        # Use gabeda_core for processing
        from gabeda.core import process_data
        result = process_data(file_path, mapping_id)

        # Trigger aggregation after processing
        trigger_aggregation.delay(company_id)

        return {"status": "success", "rows": result.count}
    except Exception as exc:
        # Exponential backoff: 60s, 120s, 240s
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

**Task Invocation:**
```python
# From API endpoint
task = process_csv_task.delay(file_path, company_id, mapping_id)
return {"task_id": task.id, "status": "processing"}
```

## Backend ↔ gabeda_core

**Integration:** Python package import (gabeda-core)
**Logging:** Configure gabeda_core logger to use app logger
**Data Flow:** CSV file → Validation → gabeda_core processing → Database
**Validation Pattern:** From notebook `03_consolidated_all_models.ipynb`

**Complete Validation + Processing Flow:**
```python
from gabeda.preprocessing.loaders import DataLoader
from gabeda.preprocessing.validators import DataValidator
from gabeda.preprocessing.schema import SchemaProcessor
from gabeda.preprocessing.synthetic import SyntheticEnricher
from app.core.logging import logger

# Configure gabeda_core logger
import logging
gabeda_logger = logging.getLogger('gabeda')
gabeda_logger.addHandler(logger.handlers[0])

# ============================================================
# STEP 1: Load raw CSV
# ============================================================
loader = DataLoader()
raw_data = loader.load_csv(file_path)
logger.info(f"Loaded raw data: {raw_data.shape}", tenant_id=company_id)

# ============================================================
# STEP 2: Phase 1 Validation - Schema & Structure
# ============================================================
validator = DataValidator()
required_cols = [spec['source_column'] for spec in mapping_template.items()]

validation = validator.validate_all(
    df=raw_data,
    required_cols=required_cols,
    data_schema=mapping_template,
    default_formats=default_formats
)

if not validation.is_valid:
    logger.error("Validation failed", tenant_id=company_id, errors=validation.errors)
    return ValidationError(
        message="Validación fallida",
        errors=validation.errors,
        rejected_rows=len(raw_data),
        total_rows=len(raw_data)
    )

# Log warnings (non-blocking)
if validation.warnings:
    logger.warning(f"Validation warnings: {len(validation.warnings)}",
                   tenant_id=company_id, warnings=validation.warnings[:5])

# ============================================================
# STEP 3: Process schema (column mapping + type conversion)
# ============================================================
schema_processor = SchemaProcessor()
preprocessed_df = schema_processor.process_schema(raw_data, mapping_template).df
logger.info(f"Schema processed: {preprocessed_df.shape}", tenant_id=company_id)

# ============================================================
# STEP 4: Synthetic enrichment (optional)
# ============================================================
enricher = SyntheticEnricher(synthetic_model_name='synthetic')
preprocessed_df = enricher.enrich(data=preprocessed_df)

# ============================================================
# STEP 5: Phase 2 Validation - Row-level required fields
# ============================================================
validated_df, reject_result = validator.validate_row_level_required_fields(
    df=preprocessed_df,
    data_schema=mapping_template,
    save_to_file=False
)

# Log data quality metrics
logger.info(
    "Validation complete",
    tenant_id=company_id,
    total_rows=len(preprocessed_df),
    clean_rows=len(validated_df),
    rejected_rows=len(reject_result.rejected_rows) if reject_result.rejected_rows is not None else 0,
    rejection_rate=f"{(len(reject_result.rejected_rows) / len(preprocessed_df) * 100):.2f}%" if reject_result.rejected_rows is not None else "0.00%"
)

# ============================================================
# STEP 6: Process validated data with gabeda_core
# ============================================================
from gabeda.core import process_data

result = process_data(
    data=validated_df,
    mapping_template=mapping_template,
    company_id=company_id
)

# ============================================================
# STEP 7: Return results
# ============================================================
return ProcessingResult(
    validated_df=validated_df,
    rejected_rows=reject_result.rejected_rows,
    processing_result=result,
    metrics={
        "total_rows": len(preprocessed_df),
        "clean_rows": len(validated_df),
        "rejected_rows": len(reject_result.rejected_rows) if reject_result.rejected_rows is not None else 0
    }
)
```

**Validation Classes from gabeda_core:**
- `DataValidator.validate_all()`: Schema + structure validation
  - Checks: Column existence, data types, date formats, numeric formats, duplicate IDs
- `DataValidator.validate_row_level_required_fields()`: Row-level validation
  - Checks: Required fields not null, valid ranges, business logic constraints
- Returns: `ValidationResult` with `is_valid`, `errors`, `warnings`

## Frontend ↔ React Query

**Cache Strategy:**
- **Dashboard data:** 5-minute cache, auto-refetch
- **User profile:** 1-hour cache
- **Company list:** Cached until mutation

**Query Example:**
```typescript
import { useQuery } from '@tanstack/react-query';
import { fetchDashboardData } from '@/api/analytics';

function Dashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard', companyId, year],
    queryFn: () => fetchDashboardData(companyId, year),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: true,
  });

  if (isLoading) return <DashboardSkeleton />;
  if (error) return <ErrorToast message={error.message} />;

  return <DashboardView data={data.data} />;
}
```

**Mutation Example:**
```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { uploadCSV } from '@/api/data';

function UploadPage() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: uploadCSV,
    onSuccess: () => {
      // Invalidate dashboard cache
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      toast.success('CSV procesado exitosamente');
    },
  });

  return <UploadForm onSubmit={mutation.mutate} />;
}
```

---
