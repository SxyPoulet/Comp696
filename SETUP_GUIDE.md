# Setup and Testing Guide

## Prerequisites Check

Before starting, ensure you have the following installed:

### Required Software
- [ ] **Docker Desktop** (version 20.10+)
  - Download: https://www.docker.com/products/docker-desktop
  - Verify: `docker --version` and `docker-compose --version`

- [ ] **Python 3.11+** (for local development)
  - Download: https://www.python.org/downloads/
  - Verify: `python --version` or `python3 --version`

- [ ] **Git** (optional, for version control)
  - Download: https://git-scm.com/downloads
  - Verify: `git --version`

### Required API Keys
- [ ] **Anthropic API Key** (Required)
  - Get yours at: https://console.anthropic.com/
  - Will be used for Claude AI agents

- [ ] **Clearbit API Key** (Optional for POC)
  - Get free tier at: https://clearbit.com/
  - 50 requests/month free

- [ ] **Hunter.io API Key** (Optional for POC)
  - Get free tier at: https://hunter.io/
  - 25 requests/month free

## Setup Steps

### Step 1: Configure Environment Variables

Edit the `.env` file in the `backend` directory:

```bash
cd sales-intelligence-agent/backend
# Edit .env file with your favorite editor
notepad .env  # Windows
nano .env     # Linux/Mac
```

**Required Configuration:**
```bash
# REQUIRED: Add your Anthropic API key
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here

# Optional for now (can add later)
CLEARBIT_API_KEY=your-clearbit-key-here
HUNTER_API_KEY=your-hunter-key-here
```

Keep the rest of the configuration as-is for now.

### Step 2: Start with Docker (Recommended)

**Option A: Using Make (Linux/Mac/WSL)**

```bash
cd sales-intelligence-agent

# Build all containers
make build

# Start all services
make up

# View logs
make logs
```

**Option B: Using Docker Compose Directly (Windows/All)**

```bash
cd sales-intelligence-agent

# Build containers
docker-compose build

# Start services in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Step 3: Verify Services are Running

After starting services, verify each component:

#### 1. Check Container Status
```bash
docker-compose ps
```

Expected output:
```
NAME                         STATUS    PORTS
sales-intel-backend         Up        0.0.0.0:8000->8000/tcp
sales-intel-celery-worker   Up
sales-intel-flower          Up        0.0.0.0:5555->5555/tcp
sales-intel-postgres        Up        0.0.0.0:5432->5432/tcp
sales-intel-redis           Up        0.0.0.0:6379->6379/tcp
```

#### 2. Test API Health Check
```bash
# Using curl
curl http://localhost:8000/health

# Using PowerShell (Windows)
Invoke-WebRequest -Uri http://localhost:8000/health

# Or open in browser:
# http://localhost:8000
```

Expected response:
```json
{"status": "healthy"}
```

#### 3. Access API Documentation
Open in browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

#### 4. Check Celery Monitoring (Flower)
Open in browser:
- **Flower Dashboard**: http://localhost:5555

#### 5. Test Database Connection
```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U sales_intel_user -d sales_intel_db

# Inside psql, run:
\dt  # List tables (should see companies, contacts, intelligence, search_history)
\q   # Quit
```

#### 6. Test Redis Connection
```bash
# Connect to Redis CLI
docker-compose exec redis redis-cli

# Inside redis-cli, run:
ping  # Should return PONG
exit
```

### Step 4: Test the Example Agent

Access the backend container and test the example agent:

```bash
# Enter backend container
docker-compose exec backend /bin/bash

# Inside container, run the example agent
python -m app.agents.example_agent

# Exit container
exit
```

## Alternative: Local Development (Without Docker)

If you prefer to run services locally without Docker:

### 1. Install PostgreSQL and Redis Locally
- **PostgreSQL**: https://www.postgresql.org/download/
- **Redis**: https://redis.io/download (or use Redis Cloud free tier)

### 2. Create Database
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE sales_intel_db;
CREATE USER sales_intel_user WITH PASSWORD 'sales_intel_pass';
GRANT ALL PRIVILEGES ON DATABASE sales_intel_db TO sales_intel_user;
\q
```

### 3. Update .env File
```bash
# Update these lines to point to local services
DATABASE_URL=postgresql://sales_intel_user:sales_intel_pass@localhost:5432/sales_intel_db
REDIS_URL=redis://localhost:6379/0
```

### 4. Install Python Dependencies

**Using Poetry (Recommended):**
```bash
cd backend

# Install Poetry if you don't have it
pip install poetry

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

**Using pip:**
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Run Services Locally

**Terminal 1 - Run FastAPI:**
```bash
cd backend
poetry shell  # or activate venv
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Run Celery Worker:**
```bash
cd backend
poetry shell  # or activate venv
celery -A app.tasks.celery_app worker --loglevel=info
```

**Terminal 3 - Run Flower (Optional):**
```bash
cd backend
poetry shell  # or activate venv
celery -A app.tasks.celery_app flower --port=5555
```

## Troubleshooting

### Issue: Docker containers won't start

**Solution 1: Check Docker is running**
```bash
docker info
```

**Solution 2: Check ports are available**
Make sure ports 5432, 6379, 8000, and 5555 are not in use:
```bash
# Windows
netstat -ano | findstr "8000"
netstat -ano | findstr "5432"

# Linux/Mac
lsof -i :8000
lsof -i :5432
```

**Solution 3: Rebuild containers**
```bash
docker-compose down -v  # Remove volumes
docker-compose build --no-cache
docker-compose up
```

### Issue: Database connection errors

**Check PostgreSQL is running:**
```bash
docker-compose ps postgres
docker-compose logs postgres
```

**Manually connect to verify:**
```bash
docker-compose exec postgres psql -U sales_intel_user -d sales_intel_db
```

### Issue: Celery worker errors

**Check Celery logs:**
```bash
docker-compose logs celery_worker
```

**Common fix - restart worker:**
```bash
docker-compose restart celery_worker
```

### Issue: "Module not found" errors

**Rebuild backend container:**
```bash
docker-compose build backend
docker-compose up -d backend
```

### Issue: Permission denied errors (Linux/Mac)

**Fix Docker permissions:**
```bash
sudo usermod -aG docker $USER
# Log out and log back in
```

## Success Checklist

Once everything is working, you should be able to:

- [ ] Access API at http://localhost:8000
- [ ] View API docs at http://localhost:8000/docs
- [ ] Get healthy response from http://localhost:8000/health
- [ ] Access Flower at http://localhost:5555
- [ ] Connect to PostgreSQL database
- [ ] Connect to Redis
- [ ] See database tables created (companies, contacts, intelligence, search_history)
- [ ] Run the example agent successfully

## Next Steps

Once your setup is verified and working:

1. **Phase 2**: Build data collection services (Playwright, Clearbit, Hunter.io)
2. **Phase 3**: Implement the 5 AI agents
3. **Phase 4**: Create REST API endpoints
4. **Phase 5**: Build React frontend

## Useful Commands Reference

```bash
# Docker Compose
docker-compose up -d              # Start services
docker-compose down               # Stop services
docker-compose ps                 # Check status
docker-compose logs -f [service]  # View logs
docker-compose restart [service]  # Restart a service
docker-compose exec [service] sh  # Access container shell

# Make shortcuts (if available)
make build    # Build containers
make up       # Start services
make down     # Stop services
make logs     # View logs
make test     # Run tests
make clean    # Clean everything

# Database
docker-compose exec postgres psql -U sales_intel_user -d sales_intel_db
docker-compose exec backend alembic upgrade head  # Run migrations

# Redis
docker-compose exec redis redis-cli

# Backend shell
docker-compose exec backend /bin/bash
```

## Getting Help

If you encounter issues:
1. Check the logs: `docker-compose logs -f`
2. Verify environment variables in `.env`
3. Ensure all required ports are available
4. Try rebuilding: `docker-compose build --no-cache`
5. Check Docker Desktop is running and has enough resources
