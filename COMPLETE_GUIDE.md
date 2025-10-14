# Sales Intelligence Agent - Complete Guide

**Everything you need to know in one place**

---

## 🎯 What Is This?

The **Sales Intelligence Agent** is an AI-powered system that automates sales research and outreach. It uses multiple specialized AI agents to discover companies, build profiles, analyze intelligence, and generate personalized content.

**Built with:**
- FastAPI (backend)
- Claude AI (LangChain agents)
- PostgreSQL (database)
- Redis (caching)
- Celery (background jobs)
- Docker (deployment)

---

## 🚀 Quick Start (5 Minutes)

### 1. Start Services

```bash
cd sales-intelligence-agent
docker-compose up -d
```

### 2. Configure API Key

```bash
cd backend
cp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 3. Test It

```bash
# Check health
curl http://localhost:8000/health

# View docs
open http://localhost:8000/docs
```

### 4. Run Demo

```bash
python demo_script.py
```

**That's it!** You're ready to use the system.

---

## 📚 All Documentation

| Document | When to Use It |
|----------|---------------|
| `README.md` | Overview and architecture |
| `QUICKSTART.md` | First-time setup |
| `SETUP_GUIDE.md` | Detailed installation |
| `API_USAGE_GUIDE.md` | API reference with examples |
| `NEXT_STEPS.md` | What to build next |
| `TESTING_CHECKLIST.md` | Verify everything works |
| `FINAL_PROJECT_SUMMARY.md` | Complete system overview |
| `COMPLETE_GUIDE.md` | This file - everything in one place |

---

## 🔧 System Architecture

```
User
  ↓
REST API (FastAPI)
  ↓
AI Agents (Claude + LangChain)
  ├─ Discovery Agent
  ├─ Profile Builder Agent
  ├─ Intelligence Analyst Agent
  └─ Content Generator Agent
  ↓
Data Services
  ├─ LinkedIn Scraper (mock)
  ├─ Clearbit API
  ├─ Hunter.io API
  └─ Data Collector
  ↓
Storage
  ├─ PostgreSQL (persistent data)
  └─ Redis (cache + queue)
  ↓
Background Jobs (Celery)
  └─ Async task processing
```

---

## 🎯 Core Workflows

### Workflow 1: Discover New Prospects

```bash
# 1. Search for companies
POST /api/v1/discover/sync
{
  "criteria": {
    "industry": "AI",
    "location": "San Francisco",
    "size": "50-200"
  }
}

# 2. Results include lead scores
Response: [
  {"name": "Company A", "lead_score": 85},
  {"name": "Company B", "lead_score": 72}
]
```

### Workflow 2: Research a Company

```bash
# 1. Create company record
POST /api/v1/companies
{"name": "Anthropic", "domain": "anthropic.com"}

# 2. Build comprehensive profile
POST /api/v1/profiles/sync
{"company_id": 1, "include_contacts": true}

# 3. Results include contacts, tech stack, lead score
Response: {
  "lead_score": 82.5,
  "contacts_found": 10,
  "tech_stack": ["Python", "React", "AWS"]
}
```

### Workflow 3: Generate Outreach

```bash
# 1. Analyze company (AI)
POST /api/v1/intelligence/sync
{"company_id": 1}

# 2. Get pain points and priorities
Response: {
  "pain_points": [...],
  "priorities": [...]
}

# 3. Generate personalized content (AI)
POST /api/v1/content/sync
{
  "company_id": 1,
  "contact_name": "John Doe",
  "product_description": "Your product"
}

# 4. Get ready-to-send email
Response: {
  "email": {
    "subject": "...",
    "body": "...",
    "cta": "..."
  }
}
```

---

## 🤖 AI Agents Explained

### 1. Discovery Agent
**Purpose**: Find companies matching criteria

**What it does:**
- Searches web for companies
- Extracts basic information
- Calculates lead scores
- Returns ranked list

**Tools:**
- Web search (DuckDuckGo)
- Company data collector
- Lead scorer

**Example:**
```python
from app.agents.discovery import DiscoveryAgent

agent = DiscoveryAgent()
result = agent.discover_companies({
    "industry": "AI",
    "size": "50-200"
}, max_results=10)
```

### 2. Profile Builder Agent
**Purpose**: Build detailed company profiles

**What it does:**
- Collects data from multiple sources
- Finds key decision makers
- Identifies tech stack
- Analyzes company fit

**Tools:**
- Build profile (orchestrates data collection)
- Find decision makers
- Analyze profile data

**Example:**
```python
from app.agents.profiler import ProfileBuilderAgent

agent = ProfileBuilderAgent()
result = agent.build_profile("Anthropic", "anthropic.com")
```

### 3. Intelligence Analyst Agent
**Purpose**: AI-powered strategic analysis

**What it does:**
- Identifies pain points (Claude AI)
- Determines priorities (Claude AI)
- Recommends approach (Claude AI)
- Generates summaries (Claude AI)

**Tools:**
- Analyze pain points
- Identify priorities
- Determine approach
- Generate summary

**Example:**
```python
from app.agents.analyst import IntelligenceAnalystAgent

agent = IntelligenceAnalystAgent()
result = agent.analyze_company({
    "name": "TechCorp",
    "industry": "Software"
})
```

### 4. Content Generator Agent
**Purpose**: Create personalized outreach

**What it does:**
- Generates cold emails (Claude AI)
- Creates conversation starters (Claude AI)
- Produces A/B variants (Claude AI)
- Optimizes messaging (Claude AI)

**Tools:**
- Generate email
- Generate conversation starters
- Generate variants
- Optimize messaging

**Example:**
```python
from app.agents.generator import ContentGeneratorAgent

agent = ContentGeneratorAgent()
result = agent.generate_outreach_campaign(
    company_name="Anthropic",
    contact_name="John Doe",
    contact_title="CEO",
    industry="AI",
    pain_points=["Scaling challenges"],
    product_description="AI platform"
)
```

---

## 🔌 Complete API Reference

### Companies

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/companies` | Create company |
| GET | `/api/v1/companies` | List companies (paginated) |
| GET | `/api/v1/companies/{id}` | Get company details |
| PUT | `/api/v1/companies/{id}` | Update company |
| DELETE | `/api/v1/companies/{id}` | Delete company |
| GET | `/api/v1/companies/{id}/contacts` | Get company contacts |
| GET | `/api/v1/companies/{id}/intelligence` | Get company intelligence |

### Discovery

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/discover` | Discover companies (async) |
| POST | `/api/v1/discover/sync` | Discover companies (sync) |

### Profiles

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/profiles` | Build profile (async) |
| POST | `/api/v1/profiles/sync` | Build profile (sync) |

### Intelligence

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/intelligence` | Analyze company (async) |
| POST | `/api/v1/intelligence/sync` | Analyze company (sync) |

### Content

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/content` | Generate content (async) |
| POST | `/api/v1/content/sync` | Generate content (sync) |
| POST | `/api/v1/content/email-only` | Generate email only |

### Tasks

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v1/tasks/{task_id}` | Get task status |
| DELETE | `/api/v1/tasks/{task_id}` | Cancel task |

---

## 💾 Database Schema

### companies
- id, name, domain, industry, size, employee_count
- location, description, website, linkedin_url
- lead_score, status, tech_stack
- created_at, updated_at, last_analyzed_at

### contacts
- id, company_id (FK), name, title, email, phone
- is_decision_maker, department, seniority_level
- linkedin_url, source, verified
- created_at, updated_at

### intelligence
- id, company_id (FK), summary
- pain_points (JSON), priorities (JSON)
- decision_makers (JSON), communication_style
- approach_strategy, recommended_messaging
- email_templates (JSON), confidence_score
- generated_at, updated_at

### search_history
- id, query, industry, company_size, location
- keywords (JSON), total_results
- companies_discovered (JSON), execution_time
- created_at

---

## ⚙️ Configuration

### Environment Variables

**Required:**
```bash
ANTHROPIC_API_KEY=sk-ant-...  # Get from console.anthropic.com
```

**Optional (enhances data):**
```bash
CLEARBIT_API_KEY=...  # Company enrichment
HUNTER_API_KEY=...    # Email discovery
```

**Auto-configured in Docker:**
```bash
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

**Settings:**
```bash
SCRAPING_DELAY=2        # Delay between requests
CACHE_TTL=604800        # 7 days
MAX_COMPANIES_PER_SEARCH=50
```

---

## 🧪 Testing

### Run All Tests
```bash
docker-compose exec backend pytest -v
```

### Test Individual Components
```bash
# Test agents
docker-compose exec backend python -m app.agents.discovery
docker-compose exec backend python -m app.agents.profiler
docker-compose exec backend python -m app.agents.analyst
docker-compose exec backend python -m app.agents.generator

# Test data collection
docker-compose exec backend python -c "
import asyncio
from app.services.data_collector import data_collector
asyncio.run(data_collector.collect_full_profile('Test', 'test.com'))
"
```

### Run Demo
```bash
python demo_script.py
```

### Use Testing Checklist
See `TESTING_CHECKLIST.md` for comprehensive testing guide.

---

## 🐛 Troubleshooting

### Services Won't Start

**Check Docker:**
```bash
docker info
```

**Rebuild:**
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### API Errors

**Check logs:**
```bash
docker-compose logs backend
```

**Common issues:**
- Missing ANTHROPIC_API_KEY
- Database not ready (wait 10s and retry)
- Port 8000 in use (stop other services)

### Celery Not Working

**Check worker:**
```bash
docker-compose logs celery_worker
```

**Restart:**
```bash
docker-compose restart celery_worker
```

### Database Issues

**Check connection:**
```bash
docker-compose exec postgres psql -U sales_intel_user -d sales_intel_db
```

**Reset database:**
```bash
docker-compose down -v
docker-compose up -d
```

---

## 💡 Tips & Best Practices

### Performance

1. **Use caching**: Set `use_cache: true` in requests
2. **Async for long ops**: Use async endpoints for multi-step workflows
3. **Pagination**: Always paginate large result sets
4. **Batch processing**: Process multiple companies in parallel

### API Usage

1. **Check health first**: Always verify API is running
2. **Handle errors**: Check status codes and error messages
3. **Poll tasks**: For async operations, poll every 3-5 seconds
4. **Use sync for testing**: Faster feedback during development

### Data Collection

1. **Start with mock data**: Test without external APIs
2. **Add API keys gradually**: Clearbit → Hunter.io → etc.
3. **Monitor quotas**: Free tiers have limits
4. **Cache aggressively**: Saves API calls and money

### AI Agents

1. **Provide context**: Better input = better output
2. **Review output**: Always check AI-generated content
3. **Iterate prompts**: Adjust prompts for better results
4. **Monitor costs**: Claude API is pay-per-token

---

## 📊 Costs

### Development
- **Infrastructure**: Free (Docker local)
- **APIs**: Free tiers sufficient for development

### Production (Monthly)

**Option 1: Minimal (Railway)**
- Hosting: $15
- Claude API: ~$10
- **Total: ~$25/month**

**Option 2: Azure**
- Hosting: $65-90
- Claude API: ~$15
- **Total: ~$80-105/month**

**Option 3: AWS**
- Hosting: $70-95
- Claude API: ~$15
- **Total: ~$85-110/month**

---

## 🎯 Use Cases

### 1. Sales Development
- Automated prospect research
- Lead qualification
- Personalized outreach at scale

### 2. Account-Based Marketing
- Target account research
- Stakeholder mapping
- Personalized campaigns

### 3. Market Research
- Competitor analysis
- Industry trends
- Company profiling

### 4. Recruiting
- Company research for candidates
- Hiring manager identification
- Personalized outreach

---

## 🚀 Deployment Options

### Local (Development)
```bash
docker-compose up -d
```
**Best for**: Development, testing, demos

### Railway.app (Simplest)
1. Push to GitHub
2. Connect Railway
3. Add PostgreSQL + Redis
4. Deploy

**Best for**: POC, small teams, quick demos

### Azure (Enterprise)
1. Build Docker images
2. Push to Azure Container Registry
3. Create Azure Database + Redis
4. Deploy containers

**Best for**: Production, scalability, enterprise

### AWS (Flexible)
1. Build Docker images
2. Push to ECR
3. Deploy on ECS Fargate
4. RDS + ElastiCache

**Best for**: High traffic, AWS ecosystem

---

## 📈 Roadmap

### Current: Backend Complete (80%)
- ✅ Foundation
- ✅ Data collection
- ✅ AI agents
- ✅ REST API

### Next: Frontend (20%)
- ⏳ React application
- ⏳ Search interface
- ⏳ Profile viewer
- ⏳ Content generator UI

### Future: Enhancements
- Authentication
- CRM integration
- Campaign tracking
- Advanced analytics
- ML-based lead scoring

---

## 🎓 Learning Resources

### Technologies Used
- **FastAPI**: https://fastapi.tiangolo.com/
- **LangChain**: https://python.langchain.com/
- **Claude**: https://docs.anthropic.com/
- **PostgreSQL**: https://postgresql.org/docs/
- **Redis**: https://redis.io/docs/
- **Celery**: https://docs.celeryproject.org/

### Tutorials
- FastAPI Tutorial: https://fastapi.tiangolo.com/tutorial/
- LangChain Agents: https://python.langchain.com/docs/modules/agents/
- Docker Compose: https://docs.docker.com/compose/

---

## 🤝 Support

### Documentation
1. Check relevant .md file for your question
2. Review API docs at `/docs`
3. See troubleshooting section

### Debugging
1. Check Docker logs: `docker-compose logs`
2. Verify environment variables
3. Test individual components
4. Run demo script

### Common Questions

**Q: Do I need all API keys?**
A: Only ANTHROPIC_API_KEY is required. Others enhance data quality.

**Q: How much does Claude API cost?**
A: ~$5-20/month for typical usage. Pay-per-token pricing.

**Q: Can I use without Docker?**
A: Yes, see SETUP_GUIDE.md for local setup instructions.

**Q: Is this production-ready?**
A: Backend yes! Add authentication and monitoring for production.

**Q: How do I add more data sources?**
A: Create new service in `app/services/` and add as tool to agents.

---

## ✅ Quick Commands Reference

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f backend

# Test
python demo_script.py

# Shell
docker-compose exec backend /bin/bash

# Database
docker-compose exec postgres psql -U sales_intel_user -d sales_intel_db

# Redis
docker-compose exec redis redis-cli

# Health
curl http://localhost:8000/health

# Docs
open http://localhost:8000/docs
```

---

## 🎉 You're Ready!

You now have:
- ✅ Complete backend system
- ✅ AI-powered agents
- ✅ REST API
- ✅ Background jobs
- ✅ Comprehensive docs
- ✅ Demo script
- ✅ Testing guide

**Next steps:**
1. Run `python demo_script.py` to see it in action
2. Read `NEXT_STEPS.md` for frontend guide
3. Check `API_USAGE_GUIDE.md` for API details

**Questions?** All answers are in the documentation files!

**Ready to build?** Let's go! 🚀

---

**Project Status**: Backend Complete (80%)
**Version**: 1.0 POC
**Last Updated**: October 13, 2024
