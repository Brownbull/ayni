# API Contracts

## Authentication Endpoints

**Register:**
```
POST /api/v1/auth/register
Body: {"email": "user@example.com", "password": "SecurePass123!"}
Response: {"status": "success", "data": {"id": "uuid", "email": "user@example.com"}}
```

**Login:**
```
POST /api/v1/auth/login
Body: {"username": "user@example.com", "password": "SecurePass123!"}
Response: {
  "status": "success",
  "data": {
    "access_token": "jwt_token",
    "token_type": "bearer",
    "expires_in": 86400
  }
}
```

**Google OAuth:**
```
GET /api/v1/auth/google/authorize
Response: {"authorization_url": "https://accounts.google.com/..."}

GET /api/v1/auth/google/callback?code=...
Response: {"status": "success", "data": {"access_token": "...", "token_type": "bearer"}}
```

## Company Endpoints

**List Companies:**
```
GET /api/v1/companies
Headers: Authorization: Bearer {token}
Response: {
  "status": "success",
  "data": [
    {"id": 1, "name": "Mi Empresa", "country": "CL"}
  ]
}
```

**Create Company:**
```
POST /api/v1/companies
Headers: Authorization: Bearer {token}
Body: {
  "name": "Mi Empresa",
  "country": "CL",
  "identifier": "12.345.678-9",
  "first_location": {
    "name": "Casa Matriz",
    "address": "Av. Providencia 123, Santiago"
  }
}
Response: {
  "status": "success",
  "data": {
    "id": 1,
    "name": "Mi Empresa",
    "locations": [{"id": 1, "name": "Casa Matriz", "is_primary": true}]
  }
}
```

## Location Endpoints

**List Locations:**
```
GET /api/v1/companies/{company_id}/locations
Response: {
  "status": "success",
  "data": [
    {"id": 1, "name": "Casa Matriz", "address": "...", "is_primary": true},
    {"id": 2, "name": "Sucursal Las Condes", "address": "...", "is_primary": false}
  ]
}
```

**Add Location:**
```
POST /api/v1/companies/{company_id}/locations
Body: {"name": "Nueva Sucursal", "address": "..."}
Response: {"status": "success", "data": {"id": 3, "name": "Nueva Sucursal"}}
```

## Data Endpoints

**Preview CSV (Before Upload):**
```
POST /api/v1/data/preview
Headers: Content-Type: multipart/form-data
Body: file={csv_file}
Response: {
  "status": "success",
  "data": {
    "columns": ["in_dt", "in_trans_id", "in_product_id", "in_quantity", "in_price_total"],
    "preview": [
      {"in_dt": "01/10/2025 10:30", "in_trans_id": "TXN-001", "in_product_id": "PROD1", "in_quantity": "5", "in_price_total": "1.234,56"},
      // ... 9 more rows
    ],
    "row_count": 3421,
    "file_size_mb": 2.5
  }
}
```

**Upload CSV (with Mapping):**
```
POST /api/v1/data/upload
Headers: Content-Type: multipart/form-data
Body: {
  file={csv_file},
  location_id={id},
  mapping={
    "in_dt": {"source_column": "Fecha", "dtype": "date", "format": "%d/%m/%Y %H:%M"},
    "in_trans_id": {"source_column": "ID Transacción", "dtype": "str"},
    "in_product_id": {"source_column": "Producto", "dtype": "str"},
    "in_quantity": {"source_column": "Cantidad", "dtype": "float"},
    "in_price_total": {"source_column": "Total", "dtype": "float"}
  }
}

Response (Success - Validation Passed):
{
  "status": "success",
  "data": {
    "task_id": "uuid",
    "status": "processing",
    "estimated_time": "30 seconds",
    "rows_to_process": 3421
  }
}

Response (Error - Validation Failed):
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
      "message": "Formato de fecha inválido en fila 15"
    }
  ],
  "rejected_rows": 3,
  "total_rows": 100,
  "rejection_rate": 3.0,
  "rejected_rows_download_url": "/api/v1/data/rejected/{task_id}.csv"
}
```

**Check Upload Status:**
```
GET /api/v1/data/status/{task_id}
Response: {
  "status": "success",
  "data": {
    "task_id": "uuid",
    "status": "completed",
    "rows_processed": 3421,
    "errors": []
  }
}
```

## Analytics Endpoints

**Get Dashboard Data:**
```
GET /api/v1/analytics/dashboard?company_id=1&year=2025&view=annual
Response: {
  "status": "success",
  "data": {
    "company": {"id": 1, "name": "Mi Empresa"},
    "year": 2025,
    "months": [
      {
        "month": 1,
        "revenue": 1234567,
        "growth_pct": 12.5,
        "performance_index": 85,
        "alert_level": "success"
      },
      // ... 11 more months
    ],
    "locations": [
      {
        "location_id": 1,
        "name": "Casa Matriz",
        "revenue": 5000000,
        "performance": "high"
      }
    ]
  }
}
```

**Get Benchmark Data:**
```
GET /api/v1/analytics/benchmarks?company_id=1&period=monthly&date=2025-11
Response: {
  "status": "success",
  "data": {
    "your_revenue": 1234567,
    "sector_average": 980000,
    "percentile": 68,
    "rank_tier": "blue",
    "sector_info": {
      "industry": "Retail",
      "country": "CL",
      "company_count": 150
    }
  }
}
```

---
