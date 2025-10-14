# Sales Intelligence Agent - Testing Checklist

Use this checklist to verify all functionality before deployment or demos.

---

## ✅ Pre-Flight Checks

### Environment Setup
- [ ] Docker Desktop is running
- [ ] Services are started: `docker-compose up -d`
- [ ] All 5 containers are running: `docker-compose ps`
- [ ] Environment variables configured in `backend/.env`
- [ ] `ANTHROPIC_API_KEY` is set and valid

### Service Health
- [ ] API responds: `curl http://localhost:8000/health`
- [ ] API docs load: http://localhost:8000/docs
- [ ] Flower dashboard loads: http://localhost:5555
- [ ] PostgreSQL is accessible
- [ ] Redis is accessible

---

## 🔍 Manual API Testing

### Companies API

#### Create Company
```bash
curl -X POST http://localhost:8000/api/v1/companies \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Company",
    "domain": "test.com",
    "industry": "Technology"
  }'
```
- [ ] Returns 201 status
- [ ] Returns company with ID
- [ ] Company saved in database

#### List Companies
```bash
curl http://localhost:8000/api/v1/companies
```
- [ ] Returns 200 status
- [ ] Returns paginated list
- [ ] Shows total count

#### Get Company
```bash
curl http://localhost:8000/api/v1/companies/1
```
- [ ] Returns 200 status
- [ ] Returns full company details
- [ ] Includes contacts array

#### Update Company
```bash
curl -X PUT http://localhost:8000/api/v1/companies/1 \
  -H "Content-Type: application/json" \
  -d '{"lead_score": 85.0}'
```
- [ ] Returns 200 status
- [ ] Company updated successfully
- [ ] Changes persisted

#### Delete Company
```bash
curl -X DELETE http://localhost:8000/api/v1/companies/999
```
- [ ] Returns 204 or 404
- [ ] Company removed from database

---

### Discovery API

#### Discover Companies (Sync)
```bash
curl -X POST http://localhost:8000/api/v1/discover/sync \
  -H "Content-Type: application/json" \
  -d '{
    "criteria": {
      "industry": "AI",
      "location": "San Francisco",
      "max_results": 3
    },
    "include_scoring": true
  }'
```
- [ ] Returns 200 status
- [ ] Returns list of companies
- [ ] Companies have lead scores

#### Discover Companies (Async)
```bash
curl -X POST http://localhost:8000/api/v1/discover \
  -H "Content-Type: application/json" \
  -d '{
    "criteria": {
      "industry": "Technology",
      "max_results": 5
    }
  }'
```
- [ ] Returns 200 status
- [ ] Returns task_id
- [ ] Can check task status

---

### Profiles API

#### Build Profile (Sync)
```bash
curl -X POST http://localhost:8000/api/v1/profiles/sync \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": 1,
    "include_contacts": true,
    "use_cache": true
  }'
```
- [ ] Returns 200 status
- [ ] Returns lead score
- [ ] Returns contacts found/saved
- [ ] Updates company status
- [ ] Data persisted to database

#### Build Profile (Async)
```bash
curl -X POST http://localhost:8000/api/v1/profiles \
  -H "Content-Type: application/json" \
  -d '{"company_id": 1, "include_contacts": true}'
```
- [ ] Returns 200 status
- [ ] Returns task_id
- [ ] Task appears in Celery/Flower

---

### Intelligence API

#### Analyze Company (Sync)
```bash
curl -X POST http://localhost:8000/api/v1/intelligence/sync \
  -H "Content-Type: application/json" \
  -d '{"company_id": 1}'
```
- [ ] Returns 200 status
- [ ] Returns intelligence data
- [ ] Includes pain points
- [ ] Includes priorities
- [ ] Includes approach strategy
- [ ] Intelligence saved to database

#### Get Existing Intelligence
```bash
curl http://localhost:8000/api/v1/companies/1/intelligence
```
- [ ] Returns 200 status
- [ ] Returns cached intelligence
- [ ] Includes generated_at timestamp

---

### Content API

#### Generate Content (Sync)
```bash
curl -X POST http://localhost:8000/api/v1/content/sync \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": 1,
    "contact_name": "John Doe",
    "contact_title": "CTO",
    "product_description": "AI infrastructure platform",
    "include_variants": true
  }'
```
- [ ] Returns 200 status
- [ ] Returns email with subject/body/cta
- [ ] Returns conversation starters
- [ ] Returns A/B variants
- [ ] Content is personalized

#### Generate Email Only
```bash
curl -X POST http://localhost:8000/api/v1/content/email-only \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": 1,
    "contact_name": "Jane Smith",
    "product_description": "Cloud platform"
  }'
```
- [ ] Returns 200 status
- [ ] Returns email content
- [ ] Response is faster than full generation

---

### Tasks API

#### Get Task Status
```bash
# First create an async task, then check status
TASK_ID="<task_id_from_async_request>"
curl http://localhost:8000/api/v1/tasks/$TASK_ID
```
- [ ] Returns 200 status
- [ ] Shows current task status
- [ ] Updates as task progresses
- [ ] Shows result when complete

#### Cancel Task
```bash
curl -X DELETE http://localhost:8000/api/v1/tasks/$TASK_ID
```
- [ ] Returns 204 status
- [ ] Task is revoked in Celery

---

## 🤖 Agent Testing

### Discovery Agent
```bash
docker-compose exec backend python -m app.agents.discovery
```
- [ ] Agent initializes without errors
- [ ] Can search for companies
- [ ] Can score leads
- [ ] Returns structured output

### Profile Builder Agent
```bash
docker-compose exec backend python -m app.agents.profiler
```
- [ ] Agent initializes without errors
- [ ] Can build profiles
- [ ] Can find decision makers
- [ ] Integrates with data services

### Intelligence Analyst Agent
```bash
docker-compose exec backend python -m app.agents.analyst
```
- [ ] Agent initializes without errors
- [ ] Can analyze pain points
- [ ] Can identify priorities
- [ ] Uses Claude API successfully

### Content Generator Agent
```bash
docker-compose exec backend python -m app.agents.generator
```
- [ ] Agent initializes without errors
- [ ] Can generate emails
- [ ] Can create conversation starters
- [ ] Content is personalized

---

## 🔄 Data Services Testing

### Cache Service
```bash
docker-compose exec backend python -c "
from app.services.cache_service import cache_service
cache_service.set('test', 'key1', {'data': 'value'})
print(cache_service.get('test', 'key1'))
print('Cache test:', 'PASSED' if cache_service.get('test', 'key1') else 'FAILED')
"
```
- [ ] Can set values
- [ ] Can get values
- [ ] Can delete values
- [ ] TTL works correctly

### Data Collector
```bash
docker-compose exec backend python -c "
import asyncio
from app.services.data_collector import data_collector
result = asyncio.run(data_collector.collect_company_data('Test', 'test.com'))
print('Data collector test:', 'PASSED' if result else 'FAILED')
"
```
- [ ] Can collect company data
- [ ] Merges data from sources
- [ ] Calculates lead score
- [ ] Returns structured data

---

## 📊 Database Testing

### Check Tables Exist
```bash
docker-compose exec postgres psql -U sales_intel_user -d sales_intel_db -c "\dt"
```
- [ ] `companies` table exists
- [ ] `contacts` table exists
- [ ] `intelligence` table exists
- [ ] `search_history` table exists

### Query Data
```bash
docker-compose exec postgres psql -U sales_intel_user -d sales_intel_db -c "SELECT COUNT(*) FROM companies;"
```
- [ ] Can query companies
- [ ] Can query contacts
- [ ] Can query intelligence
- [ ] Foreign keys work

---

## ⚡ Performance Testing

### API Response Times
- [ ] Health check: < 100ms
- [ ] List companies: < 500ms
- [ ] Create company: < 200ms
- [ ] Build profile (sync): < 60s
- [ ] Analyze intelligence (sync): < 120s
- [ ] Generate content (sync): < 90s

### Background Job Processing
- [ ] Tasks appear in Flower immediately
- [ ] Worker picks up tasks within 5s
- [ ] Tasks complete successfully
- [ ] Results are retrievable

### Concurrent Requests
```bash
# Test 5 concurrent requests
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/v1/companies \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"Company $i\", \"domain\": \"company$i.com\"}" &
done
wait
```
- [ ] All requests succeed
- [ ] No database locks
- [ ] Reasonable response times

---

## 🎯 Complete Workflow Testing

### End-to-End Test
```bash
python demo_script.py
```
- [ ] All steps complete successfully
- [ ] No errors in output
- [ ] Data persisted correctly
- [ ] Results are sensible

### Manual Workflow
1. [ ] Create company via API
2. [ ] Build profile for company
3. [ ] View profile data
4. [ ] Analyze intelligence
5. [ ] View intelligence insights
6. [ ] Generate outreach content
7. [ ] Review generated content
8. [ ] List all companies
9. [ ] Delete test company

---

## 🐛 Error Handling Testing

### Invalid Requests
- [ ] Invalid company ID returns 404
- [ ] Missing required fields returns 400
- [ ] Invalid JSON returns 422
- [ ] Large requests handled gracefully

### Edge Cases
- [ ] Empty company name rejected
- [ ] Duplicate domain handled
- [ ] Non-existent company handled
- [ ] Missing API key handled gracefully

### Resource Limits
- [ ] Large result sets paginated
- [ ] Long-running tasks timeout appropriately
- [ ] Memory usage reasonable
- [ ] Database connections pooled

---

## 📱 Cross-Platform Testing

### Windows
- [ ] Docker Compose works
- [ ] setup.bat runs successfully
- [ ] demo_script.py runs
- [ ] All commands work in CMD
- [ ] All commands work in PowerShell

### Linux/Mac
- [ ] Docker Compose works
- [ ] Makefile commands work
- [ ] Shell scripts executable
- [ ] Permissions correct

---

## 📚 Documentation Testing

### Documentation Accuracy
- [ ] README instructions work
- [ ] QUICKSTART guide accurate
- [ ] API_USAGE_GUIDE examples work
- [ ] All curl commands work
- [ ] Python examples run
- [ ] Environment variables documented correctly

### API Documentation
- [ ] Swagger UI loads correctly
- [ ] All endpoints documented
- [ ] Request schemas correct
- [ ] Response schemas correct
- [ ] Try-it-out feature works

---

## 🔐 Security Testing (Basic)

### Input Validation
- [ ] SQL injection attempts blocked
- [ ] XSS attempts sanitized
- [ ] Large payloads rejected
- [ ] Invalid types rejected

### Access Control
- [ ] CORS configured correctly
- [ ] No sensitive data in responses
- [ ] Error messages don't leak info

---

## ✅ Deployment Readiness

### Configuration
- [ ] Environment variables documented
- [ ] Secrets not in code
- [ ] Database URL configurable
- [ ] Redis URL configurable

### Monitoring
- [ ] Health check endpoint works
- [ ] Celery workers monitored (Flower)
- [ ] Logs are structured
- [ ] Error tracking ready

### Backup & Recovery
- [ ] Database backup strategy planned
- [ ] Data migration tested
- [ ] Rollback procedure documented

---

## 📊 Test Results Summary

**Date**: ___________
**Tester**: ___________

| Category | Tests Passed | Tests Failed | Notes |
|----------|-------------|--------------|-------|
| API Endpoints | ___/40 | ___ | |
| Agents | ___/4 | ___ | |
| Data Services | ___/2 | ___ | |
| Database | ___/4 | ___ | |
| Performance | ___/8 | ___ | |
| Workflow | ___/9 | ___ | |
| Error Handling | ___/7 | ___ | |
| Documentation | ___/10 | ___ | |

**Overall Status**: ⬜ PASS / ⬜ FAIL

**Issues Found**:
1. ___________________________________________
2. ___________________________________________
3. ___________________________________________

**Recommendations**:
1. ___________________________________________
2. ___________________________________________
3. ___________________________________________

---

## 🚀 Quick Test Commands

```bash
# Start services
docker-compose up -d

# Run demo
python demo_script.py

# Run unit tests
docker-compose exec backend pytest -v

# Check health
curl http://localhost:8000/health

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

---

**Testing completed!** 🎉

For deployment checklist, see `NEXT_STEPS.md` section on Production Readiness.
