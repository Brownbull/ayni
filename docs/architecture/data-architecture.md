# Data Architecture

## Database Schema

**Core Tables:**

```sql
-- Users (managed by fastapi-users)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(320) UNIQUE NOT NULL,
    hashed_password VARCHAR(1024) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Companies (multi-tenant)
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    owner_id UUID NOT NULL REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    country VARCHAR(2) NOT NULL, -- ISO 3166-1 alpha-2
    identifier VARCHAR(50) NOT NULL, -- RUT for Chile, other for non-Chile
    industry VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(identifier)
);

-- Row-Level Security Policy
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON companies
    USING (id = current_setting('app.current_tenant', TRUE)::INTEGER);

-- Locations (1-N per company)
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    address TEXT, -- For physical stores
    website VARCHAR(500), -- For web-based businesses
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- RLS for locations
ALTER TABLE locations ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON locations
    USING (company_id = current_setting('app.current_tenant', TRUE)::INTEGER);

-- Raw Transactions
CREATE TABLE transactions (
    id BIGSERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    location_id INTEGER NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
    transaction_datetime TIMESTAMP NOT NULL,
    transaction_id VARCHAR(100) NOT NULL,
    product_id VARCHAR(100) NOT NULL,
    quantity DECIMAL(10, 2) NOT NULL,
    price_total DECIMAL(12, 2) NOT NULL,
    cost_total DECIMAL(12, 2),
    margin DECIMAL(12, 2),
    customer_id VARCHAR(100),
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(company_id, transaction_id)
);

-- Partitioned by company_id for scale
CREATE INDEX idx_transactions_company_datetime
    ON transactions(company_id, transaction_datetime DESC);

-- RLS for transactions
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON transactions
    USING (company_id = current_setting('app.current_tenant', TRUE)::INTEGER);

-- CSV Mapping Templates
CREATE TABLE mapping_templates (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    mapping JSONB NOT NULL, -- Column mappings
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Aggregates (Multi-Temporal)
CREATE TABLE aggregates_daily (
    id BIGSERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    location_id INTEGER NOT NULL REFERENCES locations(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    revenue DECIMAL(12, 2) NOT NULL,
    transactions_count INTEGER NOT NULL,
    avg_transaction DECIMAL(12, 2),
    growth_pct DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(company_id, location_id, date)
);

-- Similar tables: aggregates_hourly, aggregates_weekly,
-- aggregates_monthly, aggregates_quarterly, aggregates_yearly

-- Benchmarks (Cross-Tenant)
CREATE TABLE sector_averages (
    id SERIAL PRIMARY KEY,
    industry VARCHAR(100) NOT NULL,
    country VARCHAR(2) NOT NULL,
    period_type VARCHAR(20) NOT NULL, -- monthly, yearly
    period_date DATE NOT NULL,
    avg_revenue DECIMAL(12, 2) NOT NULL,
    company_count INTEGER NOT NULL, -- For transparency
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(industry, country, period_type, period_date)
);

-- No RLS on sector_averages (aggregated, anonymous data)
```

## Data Flow

**CSV Upload Flow (with gabeda_core Validation):**

**Step 1: File Upload → Preview (Frontend)**
1. User selects CSV file
2. Frontend reads first 10 rows client-side
3. Display preview table to user
4. Show detected columns

**Step 2: Column Mapping UI (Frontend)**
1. Display column mapping interface:
   - CSV columns (from file header) → System columns (in_dt, in_trans_id, etc.)
   - Dropdown to map each CSV column to system column
   - Format selector per column:
     - Date format: DD/MM/YYYY, YYYY-MM-DD, MM/DD/YYYY HH:MM, etc.
     - Number format: Integer, Decimal (with thousands/decimal separators)
     - Text format: String
2. Allow saving mapping as template for future uploads
3. Pre-validation (client-side):
   - Required columns mapped (in_dt, in_trans_id, in_product_id, in_quantity, in_price_total)
   - No duplicate mappings
   - File size < MAX_SIZE (10MB)

**Step 3: Upload → Backend Validation (gabeda_core pattern)**
1. POST to `/api/v1/data/upload` with file + mapping
2. Backend saves to `/tmp/uploads/{uuid}.csv`
3. **Phase 1: Schema & Structure Validation** (before processing):
   ```python
   validator = DataValidator()
   validation = validator.validate_all(
       df=raw_data,
       required_cols=required_cols,
       data_schema=mapping_template,
       default_formats=default_formats
   )
   ```

   Checks:
   - ✓ File can be read as CSV
   - ✓ Mapped columns exist in CSV
   - ✓ Required columns present (in_dt, in_trans_id, in_product_id, in_quantity, in_price_total)
   - ✓ Column data types match expected types
   - ✓ Date format can parse dates
   - ✓ Numeric columns contain valid numbers
   - ✓ No duplicate transaction IDs

   If validation fails:
   - Return error response with specific validation messages
   - User sees errors in UI (Spanish)
   - User can fix mapping or CSV and retry

**Step 4: If Valid → Process Schema (Backend)**
1. Apply column mapping (CSV columns → system columns)
2. Convert data types (dates, numbers, strings)
3. Apply number format parsing (Chilean formats: 1.234.567,89)
4. Enrich with synthetic columns (if needed by gabeda_core)

**Step 5: Row-Level Validation (Backend)**
1. **Phase 2: Row-Level Required Fields Validation**:
   ```python
   validated_df, reject_result = validator.validate_row_level_required_fields(
       df=preprocessed_df,
       data_schema=mapping_template
   )
   ```

   Checks per row:
   - ✓ Required fields not null
   - ✓ Dates within reasonable range
   - ✓ Quantities > 0
   - ✓ Prices > 0
   - ✓ Transaction IDs unique

   Result:
   - `validated_df`: Clean rows ready for processing
   - `reject_result`: Rejected rows with reasons

   Data quality report:
   - Total rows: X
   - Clean rows: Y
   - Rejected rows: Z (with reasons)

**Step 6: Queue Processing (Backend)**
1. If validation passed:
   - Create Celery task with validated data
   - Return task_id to user
   - Status: "processing"
2. If validation failed:
   - Return error response with rejected rows
   - User can download rejected rows CSV
   - User fixes data and re-uploads

**Step 7: Celery Worker Processing**
1. Use gabeda_core to process validated CSV:
   ```python
   result = gabeda_core.process_data(file_path, mapping_template)
   ```
2. Insert into `transactions` table in batches (1000 rows/batch)
3. Trigger multi-temporal aggregation pipeline
4. Delete temp file
5. Update task status: "completed"
6. Log data quality metrics:
   - Rows processed
   - Processing time
   - Any warnings

**Step 8: User Notification (Frontend)**
1. Poll `/api/v1/data/status/{task_id}` every 2 seconds
2. Show progress:
   - "Validando archivo..." (validating)
   - "Procesando 3.421 transacciones..." (processing)
   - "¡Datos actualizados!" (complete)
3. If errors:
   - Display validation errors
   - Option to download rejected rows
   - Retry button

**Validation Error Response Format:**
```json
{
  "status": "error",
  "message": "Validación fallida",
  "errors": [
    {
      "type": "missing_column",
      "column": "in_dt",
      "message": "Columna requerida 'in_dt' no encontrada en CSV"
    },
    {
      "type": "invalid_format",
      "column": "in_dt",
      "row": 15,
      "value": "invalid-date",
      "message": "Formato de fecha inválido en fila 15: 'invalid-date'"
    },
    {
      "type": "duplicate_transaction",
      "column": "in_trans_id",
      "rows": [23, 45],
      "value": "TXN-12345",
      "message": "ID de transacción duplicado: 'TXN-12345' en filas 23, 45"
    }
  ],
  "rejected_rows": 3,
  "total_rows": 100,
  "rejection_rate": 3.0
}
```

**Aggregation Pipeline Flow:**
1. Triggered by Celery task (scheduled nightly + on-demand after upload)
2. For each company/location:
   - Calculate hourly aggregates from transactions
   - Roll up to daily aggregates
   - Roll up to weekly, monthly, quarterly, yearly
3. Store in respective `aggregates_*` tables
4. Invalidate Redis cache for affected dashboards
5. Log completion with row counts

**Benchmarking Flow:**
1. Scheduled Celery task runs nightly
2. For each industry + country:
   - Aggregate monthly revenue across all companies (anonymized)
   - Calculate percentiles (25th, 50th, 75th, 90th)
   - Store in `sector_averages` table
3. API endpoint calculates user's percentile on-demand
4. Cache results in Redis (24h TTL)

---
