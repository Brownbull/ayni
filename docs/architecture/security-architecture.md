# Security Architecture

## Authentication & Authorization

**JWT Token Structure:**
```json
{
  "sub": "user_uuid",
  "tenant_id": 123,
  "role": "owner",
  "permissions": ["read", "write", "manage_users"],
  "exp": 1731441000,
  "iat": 1731354600
}
```

**Token Lifecycle:**
- **Access Token:** 24-hour expiration
- **Refresh Token:** 30-day expiration, rotated on use
- **Storage:** Frontend stores in memory + httpOnly cookie (refresh token)

**Password Security:**
- **Hashing:** bcrypt with cost factor 12
- **Validation:** Minimum 8 characters, uppercase, lowercase, number
- **Reset:** Time-limited token (1 hour), email verification required

## Multi-Tenant Isolation

**Database Level (PostgreSQL RLS):**
```sql
-- Enable RLS on all tenant tables
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE locations ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE aggregates_daily ENABLE ROW LEVEL SECURITY;

-- Isolation policy
CREATE POLICY tenant_isolation_policy ON {table_name}
    USING (company_id = current_setting('app.current_tenant', TRUE)::INTEGER);

-- Set context on every request
SELECT set_config('app.current_tenant', '123', false);
```

**Application Level:**
```python
# Middleware sets tenant context from JWT
@app.middleware("http")
async def set_tenant_context(request: Request, call_next):
    # Extract tenant_id from JWT token
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = jwt.decode(token, SECRET_KEY)
    tenant_id = payload.get("tenant_id")

    # Set PostgreSQL RLS context
    async with get_db() as session:
        await session.execute(
            text("SELECT set_config('app.current_tenant', :tenant_id, false)"),
            {"tenant_id": tenant_id}
        )

    response = await call_next(request)
    return response
```

**Validation:**
- ❌ NEVER accept tenant_id from client requests
- ✅ ALWAYS derive tenant_id from authenticated JWT token
- ✅ ALWAYS set RLS context before any database query
- ✅ Log all cross-tenant access attempts as security incidents

## Data Protection

**Encryption:**
- **In Transit:** TLS 1.3 for all connections
- **At Rest:** PostgreSQL encryption (Railway managed)
- **Passwords:** bcrypt hashed, never stored plain

**Input Validation:**
- **API Level:** Pydantic schemas validate all inputs
- **SQL Injection:** Prevented by SQLAlchemy parameterized queries
- **XSS:** React escapes all user input by default
- **CSRF:** SameSite cookies + custom headers

**Rate Limiting:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/data/upload")
@limiter.limit("10/hour")  # 10 uploads per hour per IP
async def upload_csv(...):
    pass
```

## Compliance

**Chilean Data Protection Law 19.628:**
- Users can request data deletion (GDPR-like right)
- Audit logs retained for 1 year
- Data exports available in machine-readable format

**Security Headers:**
```python
@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response
```

---
