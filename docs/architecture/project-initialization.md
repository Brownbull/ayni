# Project Initialization

## First Implementation Story: Setup Foundation

**Backend Setup:**
```bash
# 1. Generate FastAPI cookiecutter
cookiecutter https://github.com/tiangolo/full-stack-fastapi-postgresql

# 2. Commit to preserve reference
cd ayni
git init && git add . && git commit -m "Original FastAPI template"
git tag v0.1-cookiecutter

# 3. Install additional dependencies
cd backend
pip install celery[redis]==5.5.3 redis fastapi-users[sqlalchemy]==15.0.1 gabeda-core
```

**Frontend Setup (Delete Chakra, Build Fresh Tailwind):**
```bash
# 1. Delete entire frontend from cookiecutter
rm -rf frontend/

# 2. Create fresh React + TypeScript + Vite
npm create vite@latest frontend -- --template react-ts
cd frontend

# 3. Install Tailwind CSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# 4. Install core dependencies
npm install axios react-router-dom @tanstack/react-query@5.90.7 zustand@5.0.8
npm install recharts@3.4.1 react-i18next date-fns

# 5. Configure Tailwind (tailwind.config.js)
# Add content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"]

# 6. Add Tailwind directives to src/index.css
# @tailwind base;
# @tailwind components;
# @tailwind utilities;
```

**Early Deployment (Railway + Render):**
```bash
# After basic setup works locally:

# 1. Deploy backend to Railway
railway login
railway init
railway add postgresql
railway up

# 2. Deploy frontend to Render
# Create render.yaml in root:
# - Build command: cd frontend && npm install && npm run build
# - Publish directory: frontend/dist
# Push to GitHub, connect Render to repository

# 3. Test deployed version IMMEDIATELY
# Fix any deployment issues before continuing development
```

This establishes the base architecture with these decisions already made:
- FastAPI backend with async PostgreSQL
- React 19 + TypeScript + Tailwind CSS frontend
- Deployment infrastructure tested early
- No Chakra/Tailwind conflicts (fresh build)

---
