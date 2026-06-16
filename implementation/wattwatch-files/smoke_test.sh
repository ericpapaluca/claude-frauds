#!/usr/bin/env bash
set -e

API_URL=${API_URL:-"http://localhost:8000"}
echo "🧪 Running smoke tests against $API_URL"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

test_passed=0
test_failed=0

# Helper: Run curl and check HTTP status code
check_status() {
    local name=$1
    local endpoint=$2
    local method=${3:-GET}
    local data=$4
    
    echo -n "Testing: $name... "
    
    if [ "$method" == "POST" ]; then
        http_code=$(curl -s -o /tmp/resp.json -w '%{http_code}' -X POST "$API_URL$endpoint" -H "Content-Type: application/json" -d "$data")
    else
        http_code=$(curl -s -o /tmp/resp.json -w '%{http_code}' "$API_URL$endpoint")
    fi
    
    if [ "$http_code" == "200" ] || [ "$http_code" == "201" ]; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((test_passed++))
        return 0
    else
        echo -e "${RED}✗ FAIL (HTTP $http_code)${NC}"
        ((test_failed++))
        return 1
    fi
}

# Helper: Check JSON field exists
has_field() {
    local field=$1
    if command -v jq &> /dev/null; then
        jq -e "$field" /tmp/resp.json > /dev/null 2>&1
        return $?
    else
        grep -q "$field" /tmp/resp.json
        return $?
    fi
}

# Test 1: Health check
echo "=== Core Endpoints ==="
check_status "GET /health" "/health" && has_field '.status' && echo -n "  ✓ Contains status field"

# Test 2: Facilities list
check_status "GET /facilities" "/facilities" && {
    if command -v jq &> /dev/null; then
        COUNT=$(jq 'length' /tmp/resp.json)
        if [ "$COUNT" -gt 0 ]; then
            echo -n "  ✓ Array with $COUNT items"
            FIRST_ID=$(jq -r '.[0].id' /tmp/resp.json)
        fi
    fi
}

# Test 3: Anomalies list
echo ""
check_status "GET /anomalies" "/anomalies" && {
    if command -v jq &> /dev/null; then
        COUNT=$(jq 'length' /tmp/resp.json)
        if [ "$COUNT" -gt 0 ]; then
            echo -n "  ✓ Array with $COUNT items"
            FIRST_ANOMALY_ID=$(jq -r '.[0].id' /tmp/resp.json)
        fi
    fi
}

# Test 4: Anomaly work_order fields
echo ""
echo "=== Work Order Contract ==="
check_status "Anomaly work_order check" "/anomalies" && {
    if command -v jq &> /dev/null; then
        HAS_WO=$(jq -e '.[0].work_order.title' /tmp/resp.json > /dev/null 2>&1 && echo "yes" || echo "no")
        if [ "$HAS_WO" == "yes" ]; then
            echo -n "  ✓ Contains work_order.title"
            HAS_CO2=$(jq -e '.[0].work_order.co2_impact_kg_per_day' /tmp/resp.json > /dev/null 2>&1 && echo "yes" || echo "no")
            HAS_COST=$(jq -e '.[0].work_order.cost_impact_gbp_per_day' /tmp/resp.json > /dev/null 2>&1 && echo "yes" || echo "no")
            if [ "$HAS_CO2" == "yes" ] && [ "$HAS_COST" == "yes" ]; then
                echo -n " + CO2 + Cost"
            fi
        fi
    fi
}

# Test 5: Stats endpoint
echo ""
echo "=== Analytics ==="
check_status "GET /stats" "/stats" && has_field '.facilities_total'

# Test 6: Impact projection
check_status "GET /impact/projection" "/impact/projection" && has_field '.projection_100_facilities'

# Test 7: Facility detail with readings
echo ""
echo "=== Facility Detail ==="
if [ ! -z "$FIRST_ID" ]; then
    check_status "GET /facilities/$FIRST_ID" "/facilities/$FIRST_ID" && {
        if command -v jq &> /dev/null; then
            jq -e '.readings' /tmp/resp.json > /dev/null && echo -n "  ✓ Contains readings array"
        fi
    }
else
    echo "⚠️  Skipping facility detail (no facility ID found)"
fi

# Test 8: Assign anomaly (POST)
echo ""
echo "=== Mutation ==="
if [ ! -z "$FIRST_ANOMALY_ID" ]; then
    check_status "POST /anomalies/$FIRST_ANOMALY_ID/assign" "/anomalies/$FIRST_ANOMALY_ID/assign" "POST" '{}' && {
        if command -v jq &> /dev/null; then
            jq -e '.assigned_at' /tmp/resp.json > /dev/null && echo -n "  ✓ Contains assigned_at"
        fi
    }
else
    echo "⚠️  Skipping assign (no anomaly ID found)"
fi

# Summary
echo ""
echo ""
echo "╔════════════════════════════════╗"
echo "║ Results: $test_passed passed, $test_failed failed ║"
echo "╚════════════════════════════════╝"

if [ $test_failed -gt 0 ]; then
    exit 1
fi

exit 0
