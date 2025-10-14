# Phase 2: Data Collection Services - Complete!

**Completed**: October 13, 2024

## Overview

Phase 2 implemented the complete data collection layer for the Sales Intelligence Agent. This layer orchestrates data gathering from multiple sources including web scraping, API enrichment, and email discovery.

## ✅ What Was Built

### 1. Cache Service (`app/services/cache_service.py`)

**Purpose**: Redis-based caching with TTL management

**Features**:
- Namespaced cache keys for organization
- Configurable TTL (default: 7 days)
- get/set/delete operations
- Cache existence checking
- TTL inspection
- Namespace invalidation
- get_or_set pattern for lazy loading
- Health check functionality

**Usage Example**:
```python
from app.services.cache_service import cache_service

# Cache data
cache_service.set("company", "anthropic.com", data, ttl=604800)

# Retrieve cached data
cached = cache_service.get("company", "anthropic.com")

# Get or fetch pattern
data = cache_service.get_or_set(
    "company",
    "anthropic.com",
    lambda: fetch_company_data()
)
```

### 2. Clearbit Service (`app/services/enrichers/clearbit_service.py`)

**Purpose**: Company enrichment via Clearbit API

**Features**:
- Company data enrichment by domain
- Automatic caching with Redis
- Rate limit handling (free tier: 50 req/month)
- Data extraction and normalization
- Technology stack detection
- Funding and revenue information
- Social media handles
- Error handling for API limits

**Key Methods**:
- `enrich_company(domain)` - Get enriched company data
- `extract_company_info(data)` - Normalize Clearbit response
- `get_tech_stack(domain)` - Get technologies used
- `is_available()` - Check if API key is configured

**Data Extracted**:
- Company name, domain, description
- Industry and sector
- Employee count and range
- Location (city, state, country)
- Founded year
- Logo URL
- Social media profiles
- Technology stack
- Funding information
- Annual revenue

### 3. Hunter.io Service (`app/services/enrichers/hunter_service.py`)

**Purpose**: Email discovery and verification

**Features**:
- Domain search for email patterns
- Email finder for specific people
- Email verification
- Contact discovery
- Automatic caching
- Rate limit handling (free tier: 25 req/month)

**Key Methods**:
- `domain_search(domain)` - Find emails for domain
- `email_finder(domain, first_name, last_name)` - Find specific email
- `email_verifier(email)` - Verify email validity
- `get_email_pattern(domain)` - Get company email pattern
- `get_contacts(domain, limit)` - Get list of contacts
- `generate_email(first_name, last_name, domain)` - Generate email from pattern

**Data Extracted**:
- Email pattern (e.g., `{first}.{last}@company.com`)
- Contact emails with confidence scores
- Contact names and titles
- Department and seniority
- Social media profiles
- Phone numbers

### 4. LinkedIn Scraper (`app/services/scrapers/linkedin_scraper.py`)

**Purpose**: Web scraping for company and employee data

**Implementation Notes**:
- ⚠️ Includes both real Playwright implementation and mock version
- Mock version used by default for POC (no LinkedIn credentials needed)
- Real implementation requires LinkedIn authentication
- Respects rate limiting (2-second delay between requests)

**Features**:
- Company search and data extraction
- Company page scraping
- Employee discovery
- Caching of scraped data
- Mock implementation for testing

**Mock Data Includes**:
- Company name, description, industry
- Employee count and size range
- Headquarters location
- Founded year
- Key personnel with titles
- Decision maker identification

### 5. Data Collector Orchestrator (`app/services/data_collector.py`)

**Purpose**: Unified interface for all data collection

**Features**:
- Coordinates multiple data sources
- Intelligent data merging from different sources
- Lead scoring algorithm (0-100)
- Contact deduplication
- Full profile assembly
- Source availability tracking

**Key Methods**:
- `collect_company_data(name, domain)` - Collect from all sources
- `collect_contacts(name, domain, limit)` - Find contacts
- `calculate_lead_score(data)` - Score leads
- `collect_full_profile(name, domain)` - Complete profile

**Lead Scoring Algorithm**:
- Data completeness: 30 points
- Company size (sweet spot 50-500): 20 points
- Funding/revenue data: 20 points
- Technology stack: 15 points
- Contact availability: 15 points
- **Total**: 0-100 scale

## 📁 File Structure

```
backend/app/services/
├── __init__.py
├── cache_service.py           # Redis caching layer
├── data_collector.py           # Orchestration layer
├── enrichers/
│   ├── __init__.py
│   ├── clearbit_service.py    # Clearbit API integration
│   └── hunter_service.py      # Hunter.io API integration
└── scrapers/
    ├── __init__.py
    └── linkedin_scraper.py     # Playwright scraping + mock
```

## 🧪 Testing

Created comprehensive test suite: `tests/test_data_collection.py`

**Test Coverage**:
- ✅ Cache service CRUD operations
- ✅ Cache TTL and expiration
- ✅ LinkedIn mock scraper
- ✅ Data collector orchestration
- ✅ Lead scoring algorithm
- ✅ Full profile collection

**Run Tests**:
```bash
# Inside container
docker-compose exec backend pytest tests/test_data_collection.py -v

# Or locally
cd backend
poetry run pytest tests/test_data_collection.py -v
```

## 🔧 Configuration

All services respect the configuration in `backend/.env`:

```bash
# API Keys (optional for Phase 2 POC)
CLEARBIT_API_KEY=your-key-here      # Optional
HUNTER_API_KEY=your-key-here        # Optional

# Cache settings
CACHE_TTL=604800                    # 7 days in seconds
SCRAPING_DELAY=2                    # Delay between scrapes

# Redis (already configured)
REDIS_URL=redis://redis:6379/0
```

## 💡 Usage Examples

### Example 1: Collect Company Data

```python
from app.services.data_collector import data_collector

# Collect company data
profile = await data_collector.collect_full_profile(
    company_name="Anthropic",
    domain="anthropic.com",
    include_contacts=True
)

print(f"Lead Score: {profile['lead_score']}")
print(f"Employees: {profile['data']['employee_count']}")
print(f"Contacts Found: {len(profile['contacts'])}")
```

### Example 2: Use Individual Services

```python
from app.services.enrichers.clearbit_service import clearbit_service
from app.services.enrichers.hunter_service import hunter_service

# Enrich company
company_data = clearbit_service.enrich_company("anthropic.com")
print(company_data)

# Find emails
emails = hunter_service.get_contacts("anthropic.com", limit=10)
for contact in emails:
    print(f"{contact['email']} - {contact['position']}")
```

### Example 3: Caching

```python
from app.services.cache_service import cache_service

# Cache data with 1 hour TTL
cache_service.set("my_namespace", "my_key", {"data": "value"}, ttl=3600)

# Retrieve cached data
data = cache_service.get("my_namespace", "my_key")

# Get or fetch pattern
data = cache_service.get_or_set(
    "my_namespace",
    "my_key",
    fetch_function,
    ttl=3600
)
```

## 🎯 Key Capabilities

After Phase 2, the system can:

1. ✅ **Scrape** company data from LinkedIn (mock for POC)
2. ✅ **Enrich** companies using Clearbit API (if key provided)
3. ✅ **Discover** emails using Hunter.io (if key provided)
4. ✅ **Cache** all data in Redis with TTL
5. ✅ **Merge** data from multiple sources intelligently
6. ✅ **Score** leads algorithmically (0-100 scale)
7. ✅ **Deduplicate** contacts from different sources
8. ✅ **Orchestrate** data collection with single interface

## 🚦 Service Availability

The system works in multiple configurations:

### Configuration 1: Mock Only (No API Keys)
- ✅ LinkedIn mock scraper provides sample data
- ✅ Full profile collection works
- ✅ Lead scoring works
- ✅ Contact discovery works
- Perfect for **development and testing**

### Configuration 2: With Clearbit
- ✅ Real company enrichment data
- ✅ Technology stack detection
- ✅ Funding and revenue data
- ✅ More accurate lead scoring

### Configuration 3: With Hunter.io
- ✅ Real email discovery
- ✅ Email pattern detection
- ✅ Contact verification
- ✅ Better contact quality

### Configuration 4: Full (All APIs)
- ✅ Maximum data quality
- ✅ Best lead scoring
- ✅ Most comprehensive profiles

## 📊 Data Flow

```
User Request
    ↓
Data Collector
    ↓
    ├─→ Check Cache ────→ Return if found
    │
    ├─→ LinkedIn Scraper (Mock) ──┐
    │                               │
    ├─→ Clearbit API (if available)├─→ Merge Data
    │                               │
    └─→ Hunter.io API (if available)┘
                ↓
            Cache Result
                ↓
        Calculate Lead Score
                ↓
          Return Profile
```

## 🔄 Caching Strategy

- **TTL**: 7 days default (configurable)
- **Namespaces**: Organized by service (linkedin, clearbit, hunter)
- **Keys**: Based on domain or company name
- **Invalidation**: Manual via namespace invalidation
- **Benefits**:
  - Reduces API calls (important for free tiers)
  - Faster response times
  - Cost savings
  - Offline development

## ⚠️ Important Notes

### LinkedIn Scraping
- Real LinkedIn scraping may violate their Terms of Service
- Mock implementation provided for POC
- For production, use LinkedIn's official API
- Authentication required for real scraping

### API Rate Limits
- **Clearbit Free**: 50 requests/month
- **Hunter.io Free**: 25 requests/month
- Caching helps conserve API quota
- Consider paid tiers for production

### Error Handling
- All services gracefully handle missing API keys
- Network errors are caught and logged
- Failed sources don't block other sources
- Partial data is still useful

## 🎉 Phase 2 Success Criteria

- [x] Cache service with Redis integration
- [x] Clearbit API integration with caching
- [x] Hunter.io API integration with caching
- [x] LinkedIn scraper (mock for POC)
- [x] Data collection orchestrator
- [x] Lead scoring algorithm
- [x] Contact deduplication
- [x] Comprehensive test suite
- [x] Works without API keys (mock data)
- [x] Handles API failures gracefully

## 🚀 Next Steps

**Phase 3: AI Agents** (Ready to start!)

Now that we have data collection, we can implement the intelligent agents:

1. **Discovery Agent** - Search and qualify companies
2. **Profile Builder Agent** - Orchestrate data collection
3. **Intelligence Analyst Agent** - AI-powered analysis with Claude
4. **Content Generator Agent** - Personalized outreach

These agents will use the data collection services we just built!

## 📝 Testing the Implementation

### Quick Test Script

Create `test_services.py`:

```python
import asyncio
from app.services.data_collector import data_collector

async def test():
    # Test full profile collection
    profile = await data_collector.collect_full_profile(
        company_name="Anthropic",
        domain="anthropic.com",
        include_contacts=True,
        use_cache=False
    )

    print(f"Company: {profile['company_name']}")
    print(f"Lead Score: {profile['lead_score']}/100")
    print(f"Employee Count: {profile['data'].get('employee_count', 'N/A')}")
    print(f"Contacts: {len(profile['contacts'])}")
    print(f"Sources: {profile['data'].get('sources_used', [])}")

    # Print top 5 contacts
    print("\nTop Contacts:")
    for contact in profile['contacts'][:5]:
        name = contact.get('name', 'N/A')
        title = contact.get('title', 'N/A')
        print(f"  - {name}: {title}")

asyncio.run(test())
```

Run it:
```bash
docker-compose exec backend python test_services.py
```

---

**Phase 2 Complete!** Ready for Phase 3: AI Agents 🤖
