# Sales Intelligence Agent - API Usage Guide

**Version**: 1.0
**Base URL**: `http://localhost:8000/api/v1`

## Table of Contents

- [Authentication](#authentication)
- [Quick Start](#quick-start)
- [Complete Workflows](#complete-workflows)
- [API Endpoints Reference](#api-endpoints-reference)
- [Error Handling](#error-handling)
- [Examples](#examples)

---

## Authentication

Currently, the API does not require authentication. For production deployment, add authentication middleware.

---

## Quick Start

### 1. Check API Health

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy"
}
```

### 2. View API Documentation

Open in browser:
- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc

---

## Complete Workflows

### Workflow 1: Discover → Profile → Analyze → Generate Content

This is the complete end-to-end workflow for researching a company and creating outreach.

#### Step 1: Discover Companies

```bash
curl -X POST http://localhost:8000/api/v1/discover/sync \
  -H "Content-Type: application/json" \
  -d '{
    "criteria": {
      "industry": "AI/ML",
      "location": "San Francisco",
      "size": "50-200",
      "keywords": "machine learning",
      "max_results": 5
    },
    "include_scoring": true
  }'
```

**Response:**
```json
{
  "total_found": 5,
  "companies": [
    {
      "name": "Company 1",
      "domain": "company1.com",
      "industry": "AI/ML",
      "employee_count": 100,
      "location": "San Francisco",
      "lead_score": 75.0
    }
  ],
  "search_criteria": {...}
}
```

#### Step 2: Create Company Record

```bash
curl -X POST http://localhost:8000/api/v1/companies \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Anthropic",
    "domain": "anthropic.com",
    "industry": "Artificial Intelligence",
    "size": "50-200",
    "employee_count": 150,
    "location": "San Francisco, CA",
    "description": "AI safety and research company",
    "website": "https://anthropic.com",
    "linkedin_url": "https://linkedin.com/company/anthropic"
  }'
```

**Response:**
```json
{
  "id": 1,
  "name": "Anthropic",
  "domain": "anthropic.com",
  "lead_score": 0.0,
  "status": "discovered",
  "created_at": "2024-10-13T18:00:00Z",
  "contacts": []
}
```

#### Step 3: Build Company Profile

```bash
curl -X POST http://localhost:8000/api/v1/profiles/sync \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": 1,
    "include_contacts": true,
    "use_cache": true
  }'
```

**Response:**
```json
{
  "company_id": 1,
  "status": "completed",
  "lead_score": 82.5,
  "contacts_found": 10,
  "contacts_saved": 8,
  "sources_used": ["linkedin", "clearbit", "hunter"],
  "profile": {
    "name": "Anthropic",
    "domain": "anthropic.com",
    "industry": "Artificial Intelligence",
    "employee_count": 150,
    "description": "AI safety and research company",
    "tech_stack": {
      "technologies": ["Python", "React", "AWS"]
    }
  }
}
```

#### Step 4: Analyze Company Intelligence

```bash
curl -X POST http://localhost:8000/api/v1/intelligence/sync \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": 1,
    "force_refresh": false
  }'
```

**Response:**
```json
{
  "company_id": 1,
  "status": "completed",
  "intelligence": {
    "summary": "Anthropic is a high-quality prospect...",
    "pain_points": [
      {
        "pain_point": "Scaling AI infrastructure",
        "reasoning": "Fast-growing AI company",
        "impact": "Performance bottlenecks"
      }
    ],
    "priorities": [
      {
        "priority": "AI safety research",
        "reasoning": "Core mission",
        "urgency_level": "high"
      }
    ],
    "approach_strategy": "Focus on technical credibility...",
    "confidence_score": 0.85
  }
}
```

#### Step 5: Generate Outreach Content

```bash
curl -X POST http://localhost:8000/api/v1/content/sync \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": 1,
    "contact_name": "John Doe",
    "contact_title": "VP Engineering",
    "product_description": "AI infrastructure platform that reduces deployment time by 70%",
    "tone": "professional",
    "include_variants": true
  }'
```

**Response:**
```json
{
  "company_id": 1,
  "email": {
    "subject": "Helping Anthropic with Scaling AI infrastructure",
    "body": "Hi John,\n\nI noticed Anthropic is...",
    "cta": "Would you be open to a 15-minute call to discuss?"
  },
  "conversation_starters": {
    "linkedin_message": "Hi John, I noticed Anthropic is working on...",
    "email_subject": "Helping Anthropic with Scaling AI infrastructure",
    "phone_opener": "Hi John, I'm reaching out because...",
    "connection_request": "Hi John, I'd love to connect...",
    "followup_subject": "Following up: Anthropic + scaling solutions"
  },
  "variants": {
    "version_a": {...},
    "version_b": {...}
  },
  "generated_at": "2024-10-13T18:05:00Z"
}
```

---

## API Endpoints Reference

### Companies API

#### Create Company

**Endpoint:** `POST /api/v1/companies`

**Request Body:**
```json
{
  "name": "string (required)",
  "domain": "string (required)",
  "industry": "string (optional)",
  "size": "string (optional)",
  "employee_count": "integer (optional)",
  "location": "string (optional)",
  "description": "string (optional)",
  "website": "string (optional)",
  "linkedin_url": "string (optional)"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "name": "...",
  "domain": "...",
  "lead_score": 0.0,
  "status": "discovered",
  "created_at": "2024-10-13T18:00:00Z",
  "contacts": []
}
```

#### List Companies

**Endpoint:** `GET /api/v1/companies`

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)
- `status`: Filter by status (discovered, profiling, analyzed, contacted)
- `industry`: Filter by industry
- `min_score`: Minimum lead score (0-100)

**Example:**
```bash
curl "http://localhost:8000/api/v1/companies?page=1&page_size=10&min_score=70"
```

**Response:** `200 OK`
```json
{
  "total": 50,
  "page": 1,
  "page_size": 10,
  "companies": [
    {
      "id": 1,
      "name": "...",
      "lead_score": 82.5,
      ...
    }
  ]
}
```

#### Get Company Details

**Endpoint:** `GET /api/v1/companies/{company_id}`

**Example:**
```bash
curl http://localhost:8000/api/v1/companies/1
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "Anthropic",
  "domain": "anthropic.com",
  "industry": "AI",
  "employee_count": 150,
  "lead_score": 82.5,
  "status": "analyzed",
  "tech_stack": {...},
  "contacts": [...]
}
```

#### Update Company

**Endpoint:** `PUT /api/v1/companies/{company_id}`

**Request Body:**
```json
{
  "name": "string (optional)",
  "industry": "string (optional)",
  "status": "string (optional)",
  "lead_score": "float (optional)"
}
```

#### Delete Company

**Endpoint:** `DELETE /api/v1/companies/{company_id}`

**Response:** `204 No Content`

#### Get Company Contacts

**Endpoint:** `GET /api/v1/companies/{company_id}/contacts`

**Query Parameters:**
- `decision_makers_only`: boolean (default: false)

**Example:**
```bash
curl "http://localhost:8000/api/v1/companies/1/contacts?decision_makers_only=true"
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "title": "VP Engineering",
    "email": "john@anthropic.com",
    "is_decision_maker": true,
    "department": "Engineering",
    "seniority_level": "VP"
  }
]
```

#### Get Company Intelligence

**Endpoint:** `GET /api/v1/companies/{company_id}/intelligence`

**Example:**
```bash
curl http://localhost:8000/api/v1/companies/1/intelligence
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "company_id": 1,
  "summary": "...",
  "pain_points": [...],
  "priorities": [...],
  "approach_strategy": "...",
  "confidence_score": 0.85,
  "generated_at": "2024-10-13T18:00:00Z"
}
```

---

### Discovery API

#### Discover Companies (Async)

**Endpoint:** `POST /api/v1/discover`

**Request Body:**
```json
{
  "criteria": {
    "industry": "string (optional)",
    "location": "string (optional)",
    "size": "string (optional)",
    "keywords": "string (optional)",
    "max_results": "integer (1-50, default: 10)"
  },
  "include_scoring": "boolean (default: true)"
}
```

**Response:** `200 OK`
```json
{
  "message": "Company discovery started",
  "task_id": "abc123...",
  "status": "PENDING",
  "note": "Use GET /api/v1/tasks/{task_id} to check status"
}
```

#### Discover Companies (Sync)

**Endpoint:** `POST /api/v1/discover/sync`

Same request body as async version.

**Response:** `200 OK`
```json
{
  "total_found": 5,
  "companies": [...],
  "search_criteria": {...}
}
```

---

### Profiles API

#### Build Profile (Async)

**Endpoint:** `POST /api/v1/profiles`

**Request Body:**
```json
{
  "company_id": "integer (required)",
  "include_contacts": "boolean (default: true)",
  "use_cache": "boolean (default: true)"
}
```

**Response:** `200 OK`
```json
{
  "company_id": 1,
  "status": "started",
  "task_id": "xyz789...",
  "message": "Profile building started for Anthropic"
}
```

#### Build Profile (Sync)

**Endpoint:** `POST /api/v1/profiles/sync`

Same request body as async version.

**Response:** `200 OK`
```json
{
  "company_id": 1,
  "status": "completed",
  "lead_score": 82.5,
  "contacts_found": 10,
  "contacts_saved": 8,
  "sources_used": ["linkedin", "clearbit"],
  "profile": {...}
}
```

---

### Intelligence API

#### Analyze Company (Async)

**Endpoint:** `POST /api/v1/intelligence`

**Request Body:**
```json
{
  "company_id": "integer (required)",
  "force_refresh": "boolean (default: false)"
}
```

**Response:** `200 OK`
```json
{
  "company_id": 1,
  "status": "started",
  "task_id": "def456...",
  "message": "Intelligence analysis started for Anthropic"
}
```

#### Analyze Company (Sync)

**Endpoint:** `POST /api/v1/intelligence/sync`

Same request body as async version.

**Response:** `200 OK`
```json
{
  "company_id": 1,
  "status": "completed",
  "intelligence": {
    "summary": "...",
    "pain_points": [...],
    "priorities": [...],
    "approach_strategy": "...",
    "confidence_score": 0.85
  }
}
```

---

### Content API

#### Generate Content (Async)

**Endpoint:** `POST /api/v1/content`

**Request Body:**
```json
{
  "company_id": "integer (required)",
  "contact_id": "integer (optional)",
  "contact_name": "string (optional)",
  "contact_title": "string (optional)",
  "product_description": "string (required)",
  "tone": "string (optional, default: professional)",
  "include_variants": "boolean (default: true)"
}
```

**Response:** `200 OK`
```json
{
  "message": "Content generation started",
  "company_id": 1,
  "task_id": "ghi789...",
  "status": "PENDING"
}
```

#### Generate Content (Sync)

**Endpoint:** `POST /api/v1/content/sync`

Same request body as async version.

**Response:** `200 OK`
```json
{
  "company_id": 1,
  "email": {
    "subject": "...",
    "body": "...",
    "cta": "..."
  },
  "conversation_starters": {...},
  "variants": {...},
  "generated_at": "2024-10-13T18:05:00Z"
}
```

#### Generate Email Only

**Endpoint:** `POST /api/v1/content/email-only`

Same request body as sync version.

**Response:** `200 OK`
```json
{
  "subject": "...",
  "body": "...",
  "cta": "..."
}
```

---

### Tasks API

#### Get Task Status

**Endpoint:** `GET /api/v1/tasks/{task_id}`

**Example:**
```bash
curl http://localhost:8000/api/v1/tasks/abc123...
```

**Response:** `200 OK`
```json
{
  "task_id": "abc123...",
  "status": "SUCCESS",
  "result": {...},
  "error": null,
  "progress": 100
}
```

**Status Values:**
- `PENDING` - Task is waiting to start
- `STARTED` - Task is running
- `SUCCESS` - Task completed successfully
- `FAILURE` - Task failed
- `PROGRESS` - Task in progress with updates

#### Cancel Task

**Endpoint:** `DELETE /api/v1/tasks/{task_id}`

**Response:** `204 No Content`

---

## Error Handling

### Error Response Format

All errors return a consistent format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Request successful, no content to return |
| 400 | Bad Request | Invalid request data |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server error occurred |

### Common Errors

**Company Not Found:**
```json
{
  "detail": "Company not found"
}
```

**Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**API Key Not Configured:**
```json
{
  "detail": "ANTHROPIC_API_KEY not configured"
}
```

---

## Examples

### Example 1: Quick Email Generation

```bash
# 1. Create company
COMPANY_ID=$(curl -s -X POST http://localhost:8000/api/v1/companies \
  -H "Content-Type: application/json" \
  -d '{
    "name": "TechCorp",
    "domain": "techcorp.com",
    "industry": "Software"
  }' | jq -r '.id')

# 2. Generate email
curl -X POST http://localhost:8000/api/v1/content/email-only \
  -H "Content-Type: application/json" \
  -d "{
    \"company_id\": $COMPANY_ID,
    \"contact_name\": \"Jane Smith\",
    \"contact_title\": \"CTO\",
    \"product_description\": \"Cloud infrastructure platform\"
  }"
```

### Example 2: Background Job Workflow

```bash
# 1. Start profile building (async)
TASK_ID=$(curl -s -X POST http://localhost:8000/api/v1/profiles \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": 1,
    "include_contacts": true
  }' | jq -r '.task_id')

# 2. Check task status
curl http://localhost:8000/api/v1/tasks/$TASK_ID

# 3. Wait for completion (poll every 5 seconds)
while true; do
  STATUS=$(curl -s http://localhost:8000/api/v1/tasks/$TASK_ID | jq -r '.status')
  echo "Status: $STATUS"
  if [ "$STATUS" = "SUCCESS" ] || [ "$STATUS" = "FAILURE" ]; then
    break
  fi
  sleep 5
done

# 4. Get results
curl http://localhost:8000/api/v1/tasks/$TASK_ID
```

### Example 3: Batch Company Processing

```bash
# Process multiple companies
for DOMAIN in "company1.com" "company2.com" "company3.com"; do
  # Create company
  COMPANY_ID=$(curl -s -X POST http://localhost:8000/api/v1/companies \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"Company\", \"domain\": \"$DOMAIN\"}" \
    | jq -r '.id')

  # Build profile (async)
  curl -X POST http://localhost:8000/api/v1/profiles \
    -H "Content-Type: application/json" \
    -d "{\"company_id\": $COMPANY_ID}"
done
```

### Example 4: Python Client

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Create company
response = requests.post(
    f"{BASE_URL}/companies",
    json={
        "name": "Anthropic",
        "domain": "anthropic.com",
        "industry": "AI"
    }
)
company = response.json()
company_id = company["id"]

# Build profile
response = requests.post(
    f"{BASE_URL}/profiles/sync",
    json={
        "company_id": company_id,
        "include_contacts": True
    }
)
profile = response.json()
print(f"Lead Score: {profile['lead_score']}")

# Analyze intelligence
response = requests.post(
    f"{BASE_URL}/intelligence/sync",
    json={"company_id": company_id}
)
intelligence = response.json()
print(f"Pain Points: {intelligence['intelligence']['pain_points']}")

# Generate content
response = requests.post(
    f"{BASE_URL}/content/sync",
    json={
        "company_id": company_id,
        "contact_name": "John Doe",
        "contact_title": "CEO",
        "product_description": "AI infrastructure platform"
    }
)
content = response.json()
print(f"Email Subject: {content['email']['subject']}")
```

### Example 5: JavaScript/Node.js Client

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000/api/v1';

async function main() {
  // Create company
  const { data: company } = await axios.post(`${BASE_URL}/companies`, {
    name: 'Anthropic',
    domain: 'anthropic.com',
    industry: 'AI'
  });

  const companyId = company.id;

  // Build profile
  const { data: profile } = await axios.post(`${BASE_URL}/profiles/sync`, {
    company_id: companyId,
    include_contacts: true
  });

  console.log(`Lead Score: ${profile.lead_score}`);

  // Generate content
  const { data: content } = await axios.post(`${BASE_URL}/content/sync`, {
    company_id: companyId,
    contact_name: 'John Doe',
    contact_title: 'CEO',
    product_description: 'AI infrastructure platform'
  });

  console.log(`Email Subject: ${content.email.subject}`);
}

main();
```

---

## Best Practices

### 1. Use Async Endpoints for Long Operations

For operations that take more than a few seconds, use async endpoints:
- Discovery (searches web)
- Profile building (multiple data sources)
- Intelligence analysis (Claude AI processing)
- Content generation (AI generation)

### 2. Poll Task Status Appropriately

When using async endpoints, poll task status every 3-5 seconds:

```bash
# Good
sleep 5 && check_status

# Bad (too frequent)
sleep 0.5 && check_status
```

### 3. Cache Aggressively

Use `use_cache: true` to avoid redundant API calls:

```json
{
  "company_id": 1,
  "use_cache": true
}
```

### 4. Handle Errors Gracefully

Always check response status and handle errors:

```python
response = requests.post(url, json=data)
if response.status_code != 200:
    print(f"Error: {response.json()['detail']}")
    return
```

### 5. Use Pagination

When listing companies, use pagination to avoid large responses:

```bash
curl "http://localhost:8000/api/v1/companies?page=1&page_size=20"
```

### 6. Filter Results

Use query parameters to filter results:

```bash
# High-quality leads only
curl "http://localhost:8000/api/v1/companies?min_score=70&status=analyzed"
```

---

## Rate Limits & Costs

### API Rate Limits

The Sales Intelligence Agent API itself has no rate limits, but be aware of:

- **Clearbit**: 50 requests/month (free tier)
- **Hunter.io**: 25 requests/month (free tier)
- **Claude API**: Pay-per-token (see Anthropic pricing)

### Cost Optimization

1. **Enable caching** - Reduces API calls
2. **Batch operations** - Process multiple companies together
3. **Use sync endpoints** for testing - Faster feedback
4. **Monitor Celery** - Check Flower dashboard for task status

---

## Troubleshooting

### Issue: API Returns 500 Error

**Cause**: Missing API key or service error

**Solution**:
1. Check `backend/.env` has `ANTHROPIC_API_KEY`
2. Check logs: `docker-compose logs backend`
3. Verify services are running: `docker-compose ps`

### Issue: Task Stays in PENDING Status

**Cause**: Celery worker not running

**Solution**:
```bash
# Check Celery worker
docker-compose ps celery_worker

# Restart worker
docker-compose restart celery_worker

# View worker logs
docker-compose logs celery_worker
```

### Issue: No Contacts Found

**Cause**: Using mock LinkedIn scraper

**Solution**: This is expected behavior with the mock scraper. To get real contacts:
1. Add `CLEARBIT_API_KEY` for company data
2. Add `HUNTER_API_KEY` for email discovery
3. Configure real LinkedIn scraping (not recommended for POC)

### Issue: Intelligence Analysis Returns Generic Results

**Cause**: Limited company data available

**Solution**:
1. Build profile first to gather more data
2. Add company description manually
3. Ensure ANTHROPIC_API_KEY is configured

---

## Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **Project README**: See `README.md`
- **Setup Guide**: See `SETUP_GUIDE.md`
- **Phase Summaries**: See `PHASE*_SUMMARY.md` files

---

## Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review the setup guide
3. Check Docker logs: `docker-compose logs`
4. Verify environment variables in `backend/.env`

---

**Happy Building!** 🚀
