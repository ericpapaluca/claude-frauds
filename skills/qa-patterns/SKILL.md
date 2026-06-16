---
name: qa-patterns
description: QA and integration testing patterns for rapid validation. Use when verifying API contracts, creating smoke tests, or validating demo flows. Covers curl-based testing, integration checklists, and common failure modes.
---

# QA Patterns for Rapid Validation

## Smoke Test Script

**smoke_test.sh**:
```bash
#!/bin/bash
set -e

API_URL=${API_URL:-"http://localhost:8000"}
echo "🧪 Running smoke tests against $API_URL"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

test_passed=0
test_failed=0

run_test() {
    local name=$1
    local command=$2
    
    echo -n "Testing: $name... "
    if eval $command > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((test_passed++))
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((test_failed++))
    fi
}

# Test 1: Health check
run_test "Health check" "curl -f $API_URL/health"

# Test 2: List anomalies
run_test "GET /api/anomalies" "curl -f $API_URL/api/anomalies"

# Test 3: List facilities
run_test "GET /api/facilities" "curl -f $API_URL/api/facilities"

# Test 4: API docs accessible
run_test "API docs" "curl -f $API_URL/docs"

# Test 5: CORS headers present
run_test "CORS headers" "curl -I $API_URL/api/anomalies | grep -i 'access-control'"

echo ""
echo "Results: ${test_passed} passed, ${test_failed} failed"

if [ $test_failed -gt 0 ]; then
    exit 1
fi

echo -e "${GREEN}✅ All smoke tests passed!${NC}"
```

**Run:**
```bash
chmod +x smoke_test.sh
API_URL=https://your-backend.railway.app ./smoke_test.sh
```

## API Contract Validation

**test_api_contract.sh**:
```bash
#!/bin/bash

API_URL=${1:-"http://localhost:8000"}

echo "📋 Validating API contracts..."

# Test anomalies endpoint returns expected fields
response=$(curl -s $API_URL/api/anomalies)
echo "$response" | jq '.[0] | has("id", "facility_id", "sensor_id", "severity")' || {
    echo "❌ Anomaly response missing required fields"
    exit 1
}

echo "✅ API contract validated"
```

## QA Checklist Template

**QA_CHECKLIST.md**:
```markdown
# QA Checklist

## Pre-Demo Validation

### Backend API
- [ ] Health check returns 200: \`curl https://backend.railway.app/health\`
- [ ] GET /api/anomalies returns data (not empty array)
- [ ] GET /api/facilities returns data
- [ ] API docs accessible at /docs
- [ ] CORS headers allow frontend origin
- [ ] No 500 errors in logs

### Frontend
- [ ] Site loads without errors (check browser console)
- [ ] Dashboard shows data (not "Loading..." forever)
- [ ] Charts render correctly
- [ ] Mobile responsive (test on phone or DevTools)
- [ ] API calls succeed (check Network tab)
- [ ] No CORS errors in console

### Integration
- [ ] Frontend successfully calls backend API
- [ ] Data flows end-to-end (sensor → backend → frontend)
- [ ] Real-time updates work (if applicable)
- [ ] Error states handled gracefully (try with backend offline)

### Demo Flow
- [ ] Main dashboard loads in < 3 seconds
- [ ] Key visualization (chart/map) displays correctly
- [ ] Can navigate between sections without errors
- [ ] Demo data is realistic and makes sense
- [ ] Pitch narrative matches what's shown on screen

## Common Failure Modes Checked

- [ ] CORS: Frontend on different domain can call API
- [ ] Env vars: All required variables set in Railway/Vercel
- [ ] Cold start: First request after idle completes (may take 10s)
- [ ] Database: Supabase connection string correct
- [ ] API keys: Claude API key valid and has credits
- [ ] Rate limits: Not hitting API rate limits during demo
```

## Integration Test Examples

**Test frontend-backend integration with curl + jq:**

```bash
# Test 1: Backend returns valid JSON
curl -s http://localhost:8000/api/anomalies | jq '.' > /dev/null && echo "✓ Valid JSON"

# Test 2: Required fields present
curl -s http://localhost:8000/api/anomalies | jq '.[0] | keys' | grep -q "severity" && echo "✓ Has severity field"

# Test 3: Response time acceptable
time curl -s http://localhost:8000/api/anomalies > /dev/null
# Should complete in < 2 seconds

# Test 4: Error handling works
curl -s -w "%{http_code}" http://localhost:8000/api/nonexistent | grep -q "404" && echo "✓ 404 handled"
```

## Frontend Validation Script

**test_frontend.js** (run in browser console):
```javascript
// Test 1: API call succeeds
fetch('/api/anomalies')
  .then(r => r.json())
  .then(data => console.log('✓ API call succeeded:', data.length, 'anomalies'))
  .catch(e => console.error('✗ API call failed:', e));

// Test 2: No console errors
const errorCount = performance.getEntriesByType('navigation')[0]?.domContentLoadedEventEnd;
console.log('Page load time:', errorCount, 'ms');

// Test 3: Key elements present
const checks = [
  document.querySelector('h1') ? '✓ Header' : '✗ Header missing',
  document.querySelector('.dashboard') ? '✓ Dashboard' : '✗ Dashboard missing',
  document.querySelector('svg') ? '✓ Chart' : '✗ Chart missing'
];
console.log('Element checks:', checks);
```

## Performance Checks

```bash
# Test page load time (should be < 3s)
curl -w "@curl-format.txt" -o /dev/null -s "https://your-frontend.vercel.app"

# curl-format.txt:
#     time_namelookup:  %{time_namelookup}s\n
#        time_connect:  %{time_connect}s\n
#     time_appconnect:  %{time_appconnect}s\n
#    time_pretransfer:  %{time_pretransfer}s\n
#       time_redirect:  %{time_redirect}s\n
#  time_starttransfer:  %{time_starttransfer}s\n
#                     ----------\n
#          time_total:  %{time_total}s\n
```

## Common Issues & Fixes

### Issue: API returns 500
**Debug:**
```bash
# Check Railway logs
railway logs

# Test locally
curl -v http://localhost:8000/api/anomalies
```
**Common causes:**
- Missing environment variable
- Database connection failed
- Unhandled exception in code

### Issue: CORS error in browser
**Debug:**
```bash
# Check response headers
curl -I https://backend.railway.app/api/anomalies

# Should see:
# access-control-allow-origin: *
```
**Fix:** Add CORS middleware in main.py

### Issue: Frontend shows "Loading..." forever
**Debug:** Open browser DevTools → Network tab
**Common causes:**
- API URL wrong in .env
- Backend is down
- API endpoint path mismatch

### Issue: Data is empty
**Debug:**
```bash
# Check if database has data
curl https://backend.railway.app/api/anomalies
```
**Fix:** Seed database with test data

## Demo Day Validation (5 min before pitch)

```bash
# Quick validation script
echo "🎯 Pre-demo check..."

# 1. Backend health
curl -f https://your-backend.railway.app/health || echo "❌ Backend down!"

# 2. Frontend loads
curl -f https://your-frontend.vercel.app || echo "❌ Frontend down!"

# 3. API has data
ANOMALY_COUNT=$(curl -s https://your-backend.railway.app/api/anomalies | jq 'length')
if [ "$ANOMALY_COUNT" -gt 0 ]; then
    echo "✅ Backend has $ANOMALY_COUNT anomalies"
else
    echo "⚠️  Backend has no data!"
fi

# 4. Test from mobile
echo "📱 Test on mobile: https://your-frontend.vercel.app"
```

## Time Budget (5-10 minute implementation)

- **Minute 1-2:** Create smoke_test.sh with key endpoint checks
- **Minute 3-4:** Create QA_CHECKLIST.md from proposal's demo strategy
- **Minute 5-6:** Test API contracts (required fields present)
- **Minute 7-8:** Validate frontend-backend integration
- **Minute 9:** Check for common failure modes (CORS, env vars, cold start)
- **Minute 10:** Document any blockers found

**Critical path:** Health check → API endpoints return data → Frontend can call API → Demo flow works → Document issues