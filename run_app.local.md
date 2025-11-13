# Ayni - Local Development Setup

This guide covers running all services locally for development: PostgreSQL, Redis, Celery workers, Backend API, and Frontend.

---

## Quick Start (All Services)

### Option 1: Using Docker Compose (Recommended)

Start all infrastructure services at once:

```bash
# Start PostgreSQL, Redis, and optionally Celery worker
docker compose up -d redis db

# Start backend API (in one terminal)
cd backend && uv run uvicorn app.main:app --reload

# Start Celery worker (in another terminal)
cd backend && uv run celery -A app.workers.celery_app worker --loglevel=info --concurrency=4

# Start frontend (in another terminal)
cd frontend && npm run dev

# Start Flower (Celery monitoring) (in another terminal) - Optional
cd backend && uv run celery -A app.workers.celery_app flower --port=5555 --basic-auth=admin:admin
```

**Access the application:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/v1/health
- Flower UI: http://localhost:5555 (credentials: admin/admin)

---

## Individual Service Setup

### 1. PostgreSQL Database

#### Start PostgreSQL Container (WITHOUT Superuser)

**IMPORTANT**: We create the `ayni_user` role WITHOUT superuser privileges to enforce Row-Level Security (RLS) policies. Superuser roles bypass RLS even with `FORCE ROW LEVEL SECURITY` enabled.

```bash
docker run --name ayni-postgres \
  -e POSTGRES_USER=ayni_user \
  -e POSTGRES_PASSWORD=changethis \
  -e POSTGRES_DB=ayni_dev \
  -p 5432:5432 \
  -d postgres:17
```

#### Remove Superuser Privileges (Required for RLS)

After the container starts, the `ayni_user` role is created as a SUPERUSER by default. We need to remove these privileges:

```bash
# Connect to the database and remove superuser privileges
docker exec -it ayni-postgres psql -U ayni_user -d ayni_dev -c "ALTER ROLE ayni_user NOSUPERUSER NOBYPASSRLS;"

# Verify the role no longer has superuser privileges
docker exec -it ayni-postgres psql -U ayni_user -d ayni_dev -c "SELECT rolname, rolsuper, rolbypassrls FROM pg_roles WHERE rolname = 'ayni_user';"
```

Expected output:
```
  rolname   | rolsuper | rolbypassrls
------------+----------+--------------
 ayni_user  | f        | f
```

#### Run Database Migrations

```bash
cd backend
uv run alembic upgrade head
```

#### Managing PostgreSQL Container

```bash
# Stop the database
docker stop ayni-postgres

# Start it again
docker start ayni-postgres

# View logs
docker logs ayni-postgres

# Connect to database with psql
docker exec -it ayni-postgres psql -U ayni_user -d ayni_dev

# Remove container completely
docker stop ayni-postgres && docker rm ayni-postgres
```

---

### 2. Redis (Cache & Message Broker)

Redis is used for:
- Caching expensive database queries
- Celery message broker (task queue)
- Celery result backend (task results storage)

#### Start Redis Container

```bash
docker run --name ayni-redis \
  -p 6379:6379 \
  -d redis:7-alpine redis-server --appendonly yes
```

Or using Docker Compose:

```bash
docker compose up -d redis
```

#### Managing Redis Container

```bash
# Stop Redis
docker stop ayni-redis

# Start it again
docker start ayni-redis

# View logs
docker logs ayni-redis

# Connect to Redis CLI
docker exec -it ayni-redis redis-cli

# Test Redis connection
docker exec -it ayni-redis redis-cli ping
# Should return: PONG

# Remove container completely
docker stop ayni-redis && docker rm ayni-redis
```

#### Redis CLI Commands (For Debugging)

```bash
# Connect to Redis CLI
docker exec -it ayni-redis redis-cli

# View all keys
KEYS *

# View cache keys for a specific tenant
KEYS analytics:*:tenant_123:*

# Get a specific key
GET "analytics:get_monthly_sales:tenant_1:abc123"

# Delete all cache keys (use with caution!)
FLUSHDB

# View Redis info
INFO

# Monitor all commands in real-time
MONITOR
```

---

### 3. Backend API (FastAPI)

The backend API serves:
- REST API endpoints
- Health checks
- Task queue management
- Database queries with caching

#### Install Dependencies

```bash
cd backend
uv sync
```

#### Environment Configuration

Ensure `.env` file exists in the project root with:

```bash
# Database
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=ayni_user
POSTGRES_PASSWORD=changethis
POSTGRES_DB=ayni_dev

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=changethis-secret-key-for-local-dev-only
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=changethis

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:5173"]
FRONTEND_HOST=http://localhost:5173

# Environment
ENVIRONMENT=local
```

#### Start Backend API

```bash
cd backend
uv run uvicorn app.main:app --reload
```

**Options:**
- `--reload`: Auto-reload on code changes (development only)
- `--host 0.0.0.0`: Listen on all interfaces
- `--port 8001`: Change port (default: 8000)

**Access Points:**
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/api/v1/health

#### Run Tests

```bash
cd backend

# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/core/test_redis.py -v

# Run with coverage
uv run pytest --cov=app tests/
```

#### Monitoring Endpoints

The backend includes comprehensive monitoring endpoints for observability:

**System Health & Metrics:**
```bash
# Get comprehensive system metrics
curl http://localhost:8000/api/v1/monitoring/metrics

# Response includes:
# - Application status and uptime
# - Database connection status
# - Redis connection status
# - Celery worker status
# - Request/response statistics
```

**Celery Task Monitoring:**
```bash
# Get Celery worker and task information
curl http://localhost:8000/api/v1/monitoring/celery/tasks

# Response includes:
# - Active workers
# - Registered tasks
# - Task execution statistics
```

**Error Tracking:**
All backend errors are automatically captured and sent to Sentry when `SENTRY_DSN` is configured in the environment variables. This includes:
- Unhandled exceptions
- HTTP errors (4xx, 5xx)
- Database errors
- Redis connection issues
- Celery task failures

**Performance Monitoring:**
Every API request includes an `X-Response-Time` header showing the request processing time in milliseconds. This is useful for identifying slow endpoints during development.

**Configuration:**
Set these environment variables in `.env` to enable monitoring:
```bash
# Sentry Error Tracking (Optional for local dev)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=local
SENTRY_TRACES_SAMPLE_RATE=0.1
```

---

### 4. Celery Worker (Background Jobs)

Celery processes background tasks like:
- CSV file processing
- Data aggregation pipelines
- Email notifications (future)
- Report generation (future)

#### Start Celery Worker

```bash
cd backend
uv run celery -A app.workers.celery_app worker --loglevel=info --concurrency=4
```

**Options:**
- `--loglevel=info`: Show task execution logs (use `debug` for more detail)
- `--concurrency=4`: Number of worker processes (adjust based on CPU cores)
- `--pool=solo`: Use single-threaded execution (for debugging)

#### Monitor Celery

```bash
# View worker status
cd backend
uv run celery -A app.workers.celery_app inspect active

# View registered tasks
uv run celery -A app.workers.celery_app inspect registered

# View worker stats
uv run celery -A app.workers.celery_app inspect stats

# Purge all queued tasks (use with caution!)
uv run celery -A app.workers.celery_app purge
```

#### Flower UI (Celery Monitoring)

Start Flower to monitor Celery workers and tasks in a web interface:

```bash
cd backend
uv run celery -A app.workers.celery_app flower --port=5555 --basic-auth=admin:admin
```

**Access Flower:**
- URL: http://localhost:5555
- Username: `admin`
- Password: `admin`

**Flower Features:**
- Real-time worker monitoring
- Task history and status
- Task execution details
- Worker resource usage
- Task rate limiting controls

**Configuration:**
The `FLOWER_BASIC_AUTH` environment variable controls access credentials in the format `username:password`.

#### Test Background Tasks

Using the API:

```bash
# Queue a sample task
curl -X POST http://localhost:8000/api/v1/tasks/sample \
  -H "Content-Type: application/json" \
  -d '{"param1": "test", "param2": 42}'

# Response: {"task_id": "abc-123-def", "status": "queued"}

# Check task status
curl http://localhost:8000/api/v1/tasks/abc-123-def

# Response: {"task_id": "abc-123-def", "status": "success", "result": {...}}
```

---

### 5. Frontend (React + Vite)

**Status:** Placeholder - To be implemented

#### Install Dependencies

```bash
cd frontend
npm install
```

#### Start Development Server

```bash
cd frontend
npm run dev
```

**Access:** http://localhost:5173

#### Build for Production

```bash
cd frontend
npm run build
```

---

## Development Workflows

### Full Stack Development

Run all services in separate terminals:

```bash
# Terminal 1: Infrastructure services
docker compose up -d redis db

# Terminal 2: Backend API
cd backend && uv run uvicorn app.main:app --reload

# Terminal 3: Celery worker
cd backend && uv run celery -A app.workers.celery_app worker --loglevel=info

# Terminal 4: Frontend (when ready)
cd frontend && npm run dev
```

### Backend-Only Development

```bash
# Terminal 1: Start infrastructure
docker compose up -d redis db

# Terminal 2: Backend API
cd backend && uv run uvicorn app.main:app --reload

# Terminal 3 (optional): Celery worker
cd backend && uv run celery -A app.workers.celery_app worker --loglevel=info
```

### Testing Workflow

```bash
# Ensure Redis and PostgreSQL are running
docker compose up -d redis db

# Run tests
cd backend && uv run pytest -v

# Run tests with coverage
cd backend && uv run pytest --cov=app tests/

# Run specific test category
cd backend && uv run pytest tests/core/ -v
```

---

## Troubleshooting

### PostgreSQL Issues

**RLS tests failing (seeing all users):**
```bash
# Remove superuser privileges
docker exec -it ayni-postgres psql -U postgres -d ayni_dev -c "ALTER ROLE ayni_user NOSUPERUSER NOBYPASSRLS;"
```

**Connection refused:**
```bash
# Check if container is running
docker ps | grep postgres

# Check logs
docker logs ayni-postgres

# Restart container
docker restart ayni-postgres
```

### Redis Issues

**Connection refused:**
```bash
# Check if Redis is running
docker ps | grep redis

# Test connection
docker exec -it ayni-redis redis-cli ping

# Restart Redis
docker restart ayni-redis
```

**Cache not working:**
```bash
# Check Redis logs
docker logs ayni-redis

# Verify cache keys exist
docker exec -it ayni-redis redis-cli KEYS "*"

# Clear cache if needed
docker exec -it ayni-redis redis-cli FLUSHDB
```

### Celery Issues

**Tasks not executing:**
```bash
# Check worker is running
uv run celery -A app.workers.celery_app inspect active

# Check worker logs for errors
# (View terminal where worker is running)

# Verify Redis connection
docker exec -it ayni-redis redis-cli ping

# Restart worker
# Ctrl+C in worker terminal, then restart command
```

**Task stuck in pending:**
- Verify Celery worker is running
- Check Redis connection
- Check worker logs for errors

### Backend API Issues

**Import errors:**
```bash
# Ensure dependencies are installed
cd backend && uv sync

# Check Python version
python --version  # Should be 3.12+
```

**Port already in use:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uv run uvicorn app.main:app --reload --port 8001
```

---

## Docker Compose Commands

### Start All Services

```bash
# Start in background
docker compose up -d

# Start and view logs
docker compose up

# Start specific services
docker compose up -d redis db
```

### Stop Services

```bash
# Stop all services
docker compose stop

# Stop specific service
docker compose stop redis

# Stop and remove containers
docker compose down
```

### View Logs

```bash
# All services
docker compose logs

# Specific service
docker compose logs redis

# Follow logs
docker compose logs -f redis
```

### Manage Containers

```bash
# List running containers
docker compose ps

# Restart service
docker compose restart redis

# Remove all containers and volumes
docker compose down -v
```

---

## Environment Variables Reference

Create a `.env` file in the project root with these variables:

```bash
# Project
PROJECT_NAME=Ayni

# Database Configuration
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=ayni_user
POSTGRES_PASSWORD=changethis
POSTGRES_DB=ayni_dev

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=changethis-secret-key-for-local-dev-only
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=changethis

# Backend CORS
BACKEND_CORS_ORIGINS=["http://localhost:5173"]

# Frontend
FRONTEND_HOST=http://localhost:5173

# Environment
ENVIRONMENT=local

# Docker Compose Configuration
STACK_NAME=ayni-stack
DOMAIN=localhost
DOCKER_IMAGE_BACKEND=ayni-backend
DOCKER_IMAGE_FRONTEND=ayni-frontend

# Optional: Email Configuration (not required for local dev)
# SMTP_HOST=
# SMTP_USER=
# SMTP_PASSWORD=
# EMAILS_FROM_EMAIL=

# Optional: Monitoring & Observability
# Sentry error tracking and performance monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=local
SENTRY_TRACES_SAMPLE_RATE=0.1

# Flower UI for Celery monitoring (username:password)
# Access at http://localhost:5555
FLOWER_BASIC_AUTH=admin:admin
```

---

## Port Reference

| Service             | Port | URL                                    |
|---------------------|------|----------------------------------------|
| Frontend            | 5173 | http://localhost:5173                  |
| Backend             | 8000 | http://localhost:8000                  |
| API Docs            | 8000 | http://localhost:8000/docs             |
| Monitoring Metrics  | 8000 | http://localhost:8000/api/v1/monitoring/metrics |
| Celery Task Monitor | 8000 | http://localhost:8000/api/v1/monitoring/celery/tasks |
| Flower UI           | 5555 | http://localhost:5555                  |
| PostgreSQL          | 5432 | postgresql://localhost:5432/ayni_dev   |
| Redis               | 6379 | redis://localhost:6379/0               |

---

## Additional Resources

- **Backend API Docs:** Once running, visit http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/v1/health
- **Project Documentation:** `/docs` folder
- **Story Files:** `.bmad-ephemeral/stories/`

---

## Tips for Productive Development

1. **Use tmux or terminal tabs** to run multiple services simultaneously
2. **Enable auto-reload** for backend (`--reload` flag) and frontend (`vite` does this automatically)
3. **Monitor logs** from all services to catch errors early
4. **Use Redis CLI** to debug caching issues
5. **Check health endpoint** regularly to ensure all services are healthy
6. **Run tests frequently** to catch regressions early

---

## Next Steps

After setting up local environment:

1. Run migrations: `cd backend && uv run alembic upgrade head`
2. Create test user: Use `/api/v1/utils/test-user` endpoint (local environment only)
3. Start development: Begin implementing features following the stories in `.bmad-ephemeral/stories/`
4. Run tests: Ensure all tests pass before committing changes
