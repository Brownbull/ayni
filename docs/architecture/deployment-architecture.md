# Deployment Architecture

## Development Environment

**Local Setup:**
```bash
# Backend (FastAPI + PostgreSQL + Redis)
docker-compose up -d

# Frontend (Vite dev server)
cd frontend
npm run dev
```

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:17.5
    environment:
      POSTGRES_DB: ayni_dev
      POSTGRES_USER: ayni
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    command: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    environment:
      DATABASE_URL: postgresql+asyncpg://ayni:dev_password@postgres/ayni_dev
      REDIS_URL: redis://redis:6379

  celery:
    build: ./backend
    command: celery -A app.workers.celery_app worker --loglevel=info
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:
```

## Production Deployment

**Backend (Railway):**
```yaml
# railway.toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"

[[services]]
name = "backend"
replicas = 2  # For high availability

[[services]]
name = "celery-worker"
command = "celery -A app.workers.celery_app worker --loglevel=info"
replicas = 1

[[services]]
name = "postgres"
type = "postgres"

[[services]]
name = "redis"
type = "redis"
```

**Environment Variables (Railway):**
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/ayni
REDIS_URL=redis://host:6379
SECRET_KEY=<random-secret>
GOOGLE_OAUTH_CLIENT_ID=<google-client-id>
GOOGLE_OAUTH_CLIENT_SECRET=<google-secret>
ENVIRONMENT=production
```

**Frontend (Render):**
```yaml
# render.yaml
services:
  - type: web
    name: ayni-frontend
    env: static
    buildCommand: cd frontend && npm install && npm run build
    staticPublishPath: frontend/dist
    headers:
      - path: /*
        name: X-Frame-Options
        value: DENY
      - path: /*
        name: X-Content-Type-Options
        value: nosniff
    routes:
      - type: rewrite
        source: /*
        destination: /index.html
```

**Environment Variables (Render):**
```bash
VITE_API_URL=https://api.ayni.cl
VITE_ENVIRONMENT=production
```

## Database Migrations

**Alembic Commands:**
```bash
# Create migration
alembic revision --autogenerate -m "Add locations table"

# Review migration file
# Edit if needed (e.g., add RLS policies manually)

# Apply to local
alembic upgrade head

# Apply to production (Railway)
railway run alembic upgrade head
```

**Manual RLS Setup (in migration):**
```python
# alembic/versions/xxx_add_rls.py
from alembic import op

def upgrade():
    # Enable RLS
    op.execute("ALTER TABLE companies ENABLE ROW LEVEL SECURITY;")

    # Create policy
    op.execute("""
        CREATE POLICY tenant_isolation_policy ON companies
        USING (id = current_setting('app.current_tenant', TRUE)::INTEGER);
    """)

def downgrade():
    op.execute("DROP POLICY tenant_isolation_policy ON companies;")
    op.execute("ALTER TABLE companies DISABLE ROW LEVEL SECURITY;")
```

## Backup & Recovery

**Automated Backups (Railway):**
- Daily automatic backups (included)
- 30-day retention
- Point-in-time recovery within 24 hours

**Manual Backup:**
```bash
# Download backup from Railway
railway db:backup download

# Restore to local
psql -U ayni ayni_dev < backup.sql
```

## Monitoring & Alerts

**Railway Logs:**
- Real-time logs in Railway dashboard
- Filter by service (backend, celery, postgres)
- Search by tenant_id, user_id, error level

**Future Monitoring (Post-MVP):**
- Sentry for error tracking
- Datadog for performance monitoring
- Uptime monitoring (UptimeRobot)

---
