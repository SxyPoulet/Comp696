# Sales Intelligence Agent

AI Agent-Driven System for Automated Sales Research

## Generated using Claude Code by Anthropic

## Overview

The Sales Intelligence Agent is a multi-agent system that automates the process of discovering, researching, and analyzing target companies for sales outreach. It leverages Claude AI and LangChain to orchestrate intelligent agents that gather data from multiple sources and generate actionable insights.

## Architecture

### 5 Specialized AI Agents

1. **Discovery Agent** - Find and qualify target companies
2. **Profile Builder Agent** - Build detailed company profiles
3. **Intelligence Analyst Agent** - Generate AI-powered insights
4. **Content Generator Agent** - Create personalized outreach
5. **Monitor Agent** - Track changes and send alerts

### Technology Stack

**Backend:**
- Python 3.11+
- FastAPI (REST API)
- LangChain (Agent Framework)
- SQLAlchemy (ORM)
- PostgreSQL (Database)
- Redis (Cache/Queue)
- Celery (Background Jobs)

**AI/ML:**
- Claude API (Anthropic)
- spaCy (NLP)
- sentence-transformers (Embeddings)
- FAISS (Vector Store)

**Data Sources:**
- LinkedIn (Playwright scraping)
- Clearbit API (Company enrichment)
- Hunter.io (Email discovery)
- News APIs

## Project Structure

```
sales-intelligence-agent/
├── backend/
│   ├── app/
│   │   ├── agents/           # LangChain agents
│   │   │   ├── base.py
│   │   │   └── example_agent.py
│   │   ├── api/              # FastAPI routes (to be added)
│   │   ├── db/               # Database models
│   │   │   ├── database.py
│   │   │   └── models.py
│   │   ├── services/         # Business logic (to be added)
│   │   ├── tasks/            # Celery tasks
│   │   │   ├── celery_app.py
│   │   │   └── agent_tasks.py
│   │   ├── core/             # Config
│   │   │   └── config.py
│   │   └── main.py
│   ├── tests/
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/                  # (to be added)
├── docker-compose.yml
├── Makefile
└── README.md
```

## Setup Instructions

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- Poetry (Python package manager)
- Anthropic API Key

### 1. Clone and Setup

```bash
# Navigate to project directory
cd sales-intelligence-agent

# Copy environment file
cp backend/.env.example backend/.env
```

### 2. Configure Environment Variables

Edit `backend/.env` and add your API keys:

```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
CLEARBIT_API_KEY=your-clearbit-key
HUNTER_API_KEY=your-hunter-key
```

### 3. Start Services with Docker

```bash
# Build containers
make build

# Start all services
make up
```

This will start:
- PostgreSQL (port 5432)
- Redis (port 6379)
- FastAPI Backend (port 8000)
- Celery Worker
- Flower (Celery monitoring, port 5555)

### 4. Access the Application

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Flower**: http://localhost:5555

### 5. Verify Installation

```bash
# Check API health
curl http://localhost:8000/health

# View logs
make logs

# Run tests
make test
```

## Development

### Local Development (Without Docker)

```bash
cd backend

# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Set environment variables
export ANTHROPIC_API_KEY=sk-ant-...
export DATABASE_URL=postgresql://user:pass@localhost/sales_intel_db
export REDIS_URL=redis://localhost:6379/0

# Run FastAPI
uvicorn app.main:app --reload

# In another terminal, run Celery worker
celery -A app.tasks.celery_app worker --loglevel=info
```

### Database Management

```bash
# Create a new migration
make db-migrate msg="description of changes"

# Apply migrations
make db-upgrade

# Access PostgreSQL shell
make psql
```

### Useful Commands

```bash
make help          # Show all available commands
make logs          # View service logs
make shell         # Access backend container shell
make redis-cli     # Access Redis CLI
make down          # Stop all services
make clean         # Remove all containers and volumes
```

## Testing the Example Agent

The project includes an example agent demonstrating the LangChain setup:

```bash
# Access backend shell
make shell

# Run example agent
python -m app.agents.example_agent
```

## API Endpoints

### Current Endpoints

- `GET /` - Root endpoint with API info
- `GET /health` - Health check

### Coming Soon (Phase 2-4)

- `POST /api/v1/discover` - Search for companies
- `GET /api/v1/companies/{id}` - Get company profile
- `POST /api/v1/companies/{id}/analyze` - Run analysis
- `POST /api/v1/companies/{id}/generate-outreach` - Generate content

## Database Models

### Company
- Basic info (name, domain, industry, size, location)
- Lead scoring
- Technology stack
- Status tracking

### Contact
- Personnel information
- Decision maker classification
- Contact details

### Intelligence
- AI-generated insights
- Pain points and priorities
- Recommended approaches
- Outreach content

### SearchHistory
- Query tracking
- Performance metrics

## Next Steps

### Phase 2: Data Collection
- Implement Playwright scraper for LinkedIn
- Integrate Clearbit API
- Integrate Hunter.io API
- Add caching layer with Redis

### Phase 3: AI Agents
- Build Discovery Agent
- Build Profile Builder Agent
- Build Intelligence Analyst Agent
- Build Content Generator Agent

### Phase 4: API & Background Jobs
- Create REST API endpoints
- Implement Celery task workflows
- Add progress tracking

### Phase 5: Frontend
- React application with TailwindCSS
- Search and discovery page
- Company profile page
- Campaign dashboard

## Contributing

This is a POC project. For production use:
1. Add proper authentication/authorization
2. Implement rate limiting
3. Add comprehensive error handling
4. Set up monitoring and logging
5. Configure production database backups
6. Add CI/CD pipelines

## License

MIT License

## Support

For issues and questions, please refer to the project documentation.
