# Quick Start Guide

Get the Sales Intelligence Agent running in 5 minutes!

## Prerequisites

1. **Docker Desktop** installed and running
   - Download: https://www.docker.com/products/docker-desktop

2. **Anthropic API Key**
   - Sign up at: https://console.anthropic.com/
   - Get your API key from the dashboard

## Quick Setup (Windows)

### Option 1: Automated Setup (Recommended)

1. **Run the setup script:**
   ```cmd
   cd sales-intelligence-agent
   setup.bat
   ```

2. **When prompted, add your API key to `.env` file:**
   ```bash
   ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
   ```

3. **Done!** The script will:
   - Build containers
   - Start all services
   - Open API documentation in your browser

### Option 2: Manual Setup

1. **Configure environment:**
   ```cmd
   cd sales-intelligence-agent\backend
   copy .env.example .env
   notepad .env
   ```
   Add your `ANTHROPIC_API_KEY`

2. **Start services:**
   ```cmd
   cd ..
   docker-compose up -d
   ```

3. **Verify:**
   ```cmd
   docker-compose ps
   ```

## Quick Setup (Linux/Mac)

1. **Configure environment:**
   ```bash
   cd sales-intelligence-agent/backend
   cp .env.example .env
   nano .env  # or your preferred editor
   ```
   Add your `ANTHROPIC_API_KEY`

2. **Start services:**
   ```bash
   cd ..
   docker-compose up -d
   ```

3. **Verify:**
   ```bash
   docker-compose ps
   ```

## Access Your Application

Once running, access:

- **API**: http://localhost:8000
- **Interactive API Docs**: http://localhost:8000/docs
- **Celery Monitoring (Flower)**: http://localhost:5555

## Test the API

### Using Browser
Open: http://localhost:8000/docs

Try the health check endpoint:
1. Click on `GET /health`
2. Click "Try it out"
3. Click "Execute"

### Using curl
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy"}
```

### Using PowerShell (Windows)
```powershell
Invoke-RestMethod -Uri http://localhost:8000/health
```

## Verify Setup

Run the verification script:

```bash
# If Python is installed:
python verify_setup.py

# Or check manually:
docker-compose ps
curl http://localhost:8000/health
```

## Common Commands

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Rebuild and restart
docker-compose up -d --build

# Access backend shell
docker-compose exec backend /bin/bash

# Access database
docker-compose exec postgres psql -U sales_intel_user -d sales_intel_db
```

## Test the Example Agent

1. **Access the backend container:**
   ```bash
   docker-compose exec backend /bin/bash
   ```

2. **Run the example agent:**
   ```bash
   python -m app.agents.example_agent
   ```

3. **Exit container:**
   ```bash
   exit
   ```

## Troubleshooting

### Services won't start?

**Check Docker is running:**
```bash
docker info
```

**Check logs:**
```bash
docker-compose logs
```

**Rebuild:**
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Can't access API?

**Check if backend is running:**
```bash
docker-compose ps backend
```

**Check backend logs:**
```bash
docker-compose logs backend
```

**Verify port 8000 is not in use:**
```bash
# Windows
netstat -ano | findstr "8000"

# Linux/Mac
lsof -i :8000
```

### Database errors?

**Check PostgreSQL logs:**
```bash
docker-compose logs postgres
```

**Restart database:**
```bash
docker-compose restart postgres
```

## What's Next?

Now that your system is running, you can:

1. **Explore the API Documentation**
   - Visit: http://localhost:8000/docs
   - Test the available endpoints

2. **Review the Project Structure**
   - Check `README.md` for full documentation
   - Explore `backend/app/` directory

3. **Continue Development**
   - Phase 2: Build data collection services
   - Phase 3: Implement AI agents
   - Phase 4: Create REST endpoints
   - Phase 5: Build frontend

4. **Read Full Setup Guide**
   - See `SETUP_GUIDE.md` for detailed instructions
   - Includes local development setup (no Docker)

## Need Help?

- **Setup Guide**: See `SETUP_GUIDE.md`
- **README**: See `README.md` for architecture details
- **Requirements Spec**: See `agent_requirements_spec.md`

## Stop Services

When you're done:

```bash
# Stop services (keeps data)
docker-compose down

# Stop and remove all data
docker-compose down -v
```

---

**You're all set!** 🚀 The foundation is ready for building the AI agents.
