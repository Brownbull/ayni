# Development Environment Setup

## Prerequisites

**Required:**
- Python ≥3.9
- Node.js ≥18
- PostgreSQL 17.5 (via Docker)
- Redis 7.x (via Docker)
- Git

**Optional:**
- Docker Desktop (for local development)
- Railway CLI (for deployment)
- Playwright browsers (for E2E testing)

## Setup Commands

**Clone and Initialize:**
```bash
# Clone repository
git clone <repository-url>
cd ayni

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install gabeda-core  # Add if not in requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your settings

# Run migrations
alembic upgrade head

# Frontend setup
cd ../frontend
npm install

# Start development servers
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Celery worker
cd backend
celery -A app.workers.celery_app worker --loglevel=info

# Terminal 3: Frontend
cd frontend
npm run dev
```

**Docker Development:**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

## IDE Configuration

**VSCode (Recommended):**
```json
// .vscode/settings.json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

**Extensions:**
- Python
- Pylance
- ESLint
- Prettier
- Tailwind CSS IntelliSense

---
