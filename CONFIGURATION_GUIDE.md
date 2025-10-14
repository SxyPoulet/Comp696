# Configuration Guide

## Required Configuration

### 1. Backend API Keys (REQUIRED)

#### Anthropic API Key (REQUIRED ⚠️)

This is the **ONLY REQUIRED** API key to run the system. Without it, the AI agents won't work.

**Get your key:**
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new key
5. Copy the key (starts with `sk-ant-`)

**Configure:**
```bash
# Edit backend/.env
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
```

---

### 2. Optional API Keys (Enhance Data Quality)

#### Clearbit API (Optional)
Enriches company data with additional information.

**Get your key:**
1. Go to https://clearbit.com/
2. Sign up for free tier (50 requests/month)
3. Get API key from dashboard

**Configure:**
```bash
CLEARBIT_API_KEY=your-clearbit-key-here
```

**If you don't configure:**
- System will use mock data for company enrichment
- Will still work, but with less detailed company information

#### Hunter.io API (Optional)
Discovers email addresses for contacts.

**Get your key:**
1. Go to https://hunter.io/
2. Sign up for free tier (25 requests/month)
3. Get API key from dashboard

**Configure:**
```bash
HUNTER_API_KEY=your-hunter-key-here
```

**If you don't configure:**
- System will use mock data for email discovery
- Will still work, but with placeholder emails

---

## Configuration Files

### Backend Configuration

**File:** `backend/.env`

```bash
# ===========================================
# REQUIRED - System won't work without this!
# ===========================================
ANTHROPIC_API_KEY=sk-ant-your-key-here

# ===========================================
# OPTIONAL - Enhance data quality
# ===========================================
CLEARBIT_API_KEY=your-clearbit-key-here  # Optional
HUNTER_API_KEY=your-hunter-key-here      # Optional

# ===========================================
# AUTO-CONFIGURED - Don't change for Docker
# ===========================================
DATABASE_URL=postgresql://sales_intel_user:sales_intel_pass@postgres:5432/sales_intel_db
REDIS_URL=redis://redis:6379/0

# ===========================================
# SETTINGS - Can customize if needed
# ===========================================
SCRAPING_DELAY=2                    # Delay between scrapes (seconds)
CACHE_TTL=604800                    # Cache expiration (7 days)
MAX_COMPANIES_PER_SEARCH=50         # Max results per search

# ===========================================
# ENVIRONMENT
# ===========================================
ENVIRONMENT=development
DEBUG=True
```

### Frontend Configuration

**File:** `frontend/.env`

```bash
# Backend API URL
VITE_API_URL=http://localhost:8000/api/v1
```

**Default is fine for local development!** Only change if:
- Running backend on different port
- Deploying to production
- Using custom domain

---

## Quick Setup Steps

### Step 1: Get Anthropic API Key (REQUIRED)

```bash
1. Visit: https://console.anthropic.com/
2. Sign up/login
3. Create API key
4. Copy key (starts with sk-ant-)
```

### Step 2: Configure Backend

```bash
# Navigate to backend
cd backend

# Edit .env file
notepad .env  # Windows
nano .env     # Linux/Mac

# Replace this line:
ANTHROPIC_API_KEY=sk-ant-your-key-here

# With your actual key:
ANTHROPIC_API_KEY=sk-ant-api03-xyz123...
```

### Step 3: (Optional) Configure Additional APIs

If you want enhanced data:
```bash
# Add Clearbit key
CLEARBIT_API_KEY=sk_abc123...

# Add Hunter.io key
HUNTER_API_KEY=xyz789...
```

### Step 4: Verify Configuration

```bash
# Check backend .env exists
ls backend/.env

# Check frontend .env exists
ls frontend/.env

# Start the system
start-dev.bat  # Windows
docker-compose up -d  # Linux/Mac
```

---

## Configuration Checklist

### Minimum (Required)
- [x] `backend/.env` file exists
- [x] `ANTHROPIC_API_KEY` is set with valid key
- [x] `frontend/.env` file exists

### Recommended
- [ ] `CLEARBIT_API_KEY` configured (optional)
- [ ] `HUNTER_API_KEY` configured (optional)

### Advanced
- [ ] Custom `DATABASE_URL` (if not using Docker)
- [ ] Custom `REDIS_URL` (if not using Docker)
- [ ] Adjusted `MAX_COMPANIES_PER_SEARCH`
- [ ] Custom `CACHE_TTL`

---

## Environment-Specific Configuration

### Development (Default)

Uses Docker Compose defaults - **no changes needed** except API keys!

```bash
DATABASE_URL=postgresql://sales_intel_user:sales_intel_pass@postgres:5432/sales_intel_db
REDIS_URL=redis://redis:6379/0
VITE_API_URL=http://localhost:8000/api/v1
```

### Production

Update these for production deployment:

**Backend:**
```bash
ANTHROPIC_API_KEY=sk-ant-your-production-key
CLEARBIT_API_KEY=your-production-clearbit-key
HUNTER_API_KEY=your-production-hunter-key

# Production database
DATABASE_URL=postgresql://user:pass@prod-db-host:5432/sales_intel_db

# Production Redis
REDIS_URL=redis://prod-redis-host:6379/0

# Production settings
ENVIRONMENT=production
DEBUG=False
```

**Frontend:**
```bash
# Production API URL
VITE_API_URL=https://api.yourdomain.com/api/v1
```

---

## Troubleshooting Configuration

### Issue: "ANTHROPIC_API_KEY not configured"

**Cause:** API key not set or invalid

**Fix:**
```bash
# Check if .env exists
ls backend/.env

# Check if key is set
cat backend/.env | grep ANTHROPIC_API_KEY

# Make sure key starts with sk-ant-
# Make sure no extra spaces
# Make sure no quotes around key
```

### Issue: "Connection refused" to database

**Cause:** Docker not running or services not started

**Fix:**
```bash
# Check Docker is running
docker ps

# Restart services
docker-compose down
docker-compose up -d

# Check service health
docker-compose ps
```

### Issue: "Cannot connect to API"

**Cause:** Frontend can't reach backend

**Fix:**
```bash
# Check backend is running
curl http://localhost:8000/health

# Check VITE_API_URL in frontend/.env
cat frontend/.env

# Should be: http://localhost:8000/api/v1

# Restart frontend
docker-compose restart frontend
```

### Issue: "Rate limit exceeded"

**Cause:** Too many API calls to external services

**Fix:**
```bash
# Free tier limits:
# - Clearbit: 50 requests/month
# - Hunter.io: 25 requests/month

# Options:
# 1. Upgrade to paid tier
# 2. Reduce MAX_COMPANIES_PER_SEARCH
# 3. Use cache more (increase CACHE_TTL)
```

---

## Configuration Best Practices

### Security
- ❌ **Never** commit `.env` files to git
- ✅ Use `.env.example` as template
- ✅ Keep API keys secure
- ✅ Use different keys for dev/prod
- ✅ Rotate keys regularly

### Performance
- ✅ Enable caching with reasonable TTL
- ✅ Adjust `MAX_COMPANIES_PER_SEARCH` based on needs
- ✅ Monitor API usage
- ✅ Use Redis for session management

### Development
- ✅ Use development keys for testing
- ✅ Keep DEBUG=True in development
- ✅ Use localhost URLs
- ✅ Check `.gitignore` includes `.env`

### Production
- ✅ Use production API keys
- ✅ Set DEBUG=False
- ✅ Use environment variables (not .env files)
- ✅ Enable HTTPS
- ✅ Set up monitoring
- ✅ Configure backups

---

## Environment Variables Reference

### Required

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | ✅ Yes | - | Claude API key from Anthropic |

### Optional API Keys

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CLEARBIT_API_KEY` | ❌ No | - | Company enrichment API |
| `HUNTER_API_KEY` | ❌ No | - | Email discovery API |

### Database

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ✅ Yes | Docker default | PostgreSQL connection URL |
| `REDIS_URL` | ✅ Yes | Docker default | Redis connection URL |

### Settings

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SCRAPING_DELAY` | ❌ No | 2 | Delay between scrapes (seconds) |
| `CACHE_TTL` | ❌ No | 604800 | Cache expiration (seconds) |
| `MAX_COMPANIES_PER_SEARCH` | ❌ No | 50 | Max results per search |
| `ENVIRONMENT` | ❌ No | development | Environment name |
| `DEBUG` | ❌ No | True | Debug mode |

### Frontend

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_URL` | ✅ Yes | localhost:8000 | Backend API URL |

---

## Getting API Keys

### Anthropic (Claude AI) - REQUIRED

**Free Tier:**
- $5 free credits
- Pay-as-you-go after
- ~$0.003 per request

**Steps:**
1. Go to https://console.anthropic.com/
2. Sign up with email
3. Verify email
4. Go to "API Keys"
5. Click "Create Key"
6. Copy key (starts with `sk-ant-`)
7. Add to `backend/.env`

### Clearbit - Optional

**Free Tier:**
- 50 requests/month free
- $99/month for more

**Steps:**
1. Go to https://clearbit.com/
2. Sign up
3. Go to Dashboard → API
4. Copy API key
5. Add to `backend/.env`

### Hunter.io - Optional

**Free Tier:**
- 25 requests/month free
- $49/month for 500

**Steps:**
1. Go to https://hunter.io/
2. Sign up
3. Go to API → API Keys
4. Copy API key
5. Add to `backend/.env`

---

## Testing Configuration

### Test Backend Configuration

```bash
# Start services
docker-compose up -d

# Wait 30 seconds for startup
timeout /t 30  # Windows
sleep 30       # Linux/Mac

# Test health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy"}

# Test API docs
# Open: http://localhost:8000/docs
```

### Test Frontend Configuration

```bash
# Open frontend
# Open: http://localhost:5173

# Check browser console for errors
# Open DevTools → Console

# Should see:
# [API] GET /companies
# No CORS errors
```

### Test API Keys

```bash
# Create a test company
curl -X POST http://localhost:8000/api/v1/companies \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Corp","domain":"test.com"}'

# Analyze intelligence (tests Claude API)
curl -X POST http://localhost:8000/api/v1/intelligence/sync \
  -H "Content-Type: application/json" \
  -d '{"company_id":1}'

# Should return intelligence analysis
# If error about API key, check ANTHROPIC_API_KEY
```

---

## Summary

### What You MUST Configure:
1. ✅ `ANTHROPIC_API_KEY` in `backend/.env`

### What's Already Configured:
- ✅ Database connection (Docker)
- ✅ Redis connection (Docker)
- ✅ Frontend API URL
- ✅ All default settings

### What's Optional:
- `CLEARBIT_API_KEY` - Better company data
- `HUNTER_API_KEY` - Real email discovery

**That's it! Just add your Anthropic API key and you're ready to go! 🚀**

---

## Quick Reference Card

```
┌─────────────────────────────────────────┐
│     REQUIRED CONFIGURATION              │
├─────────────────────────────────────────┤
│ 1. Get Anthropic key                    │
│    https://console.anthropic.com/       │
│                                         │
│ 2. Edit backend/.env                    │
│    ANTHROPIC_API_KEY=sk-ant-...        │
│                                         │
│ 3. Start system                         │
│    start-dev.bat                        │
│                                         │
│ 4. Open browser                         │
│    http://localhost:5173                │
└─────────────────────────────────────────┘
```

---

**Need help?** Check `COMPLETE_SYSTEM_GUIDE.md` for more details!
