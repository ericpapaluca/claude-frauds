# WattWatch API Contract Reference

Quick validation: Frontend calls must match Backend response shapes exactly.

## Endpoints

| **Endpoint** | **Method** | **Auth** | **Response Schema** | **Notes** |
|---|---|---|---|---|
| `/health` | GET | None | `{status: "ok", service: "wattwatch-api", version: "0.1.0"}` | Liveness check; always 200 |
| `/facilities` | GET | API Key | `[{id, name, region, lat, lng, status, current_power_kw}]` | List of all facilities; array must be non-empty for demo |
| `/facilities/{id}` | GET | API Key | `{id, name, region, lat, lng, status, current_power_kw, readings: [{timestamp, power_kw}]}` | Detail view; readings array powers chart |
| `/anomalies` | GET | API Key | `[{id, facility_id, severity, created_at, work_order: {title, likely_cause, action, urgency, co2_impact_kg_per_day, cost_impact_gbp_per_day}}]` | **CRITICAL:** work_order must be embedded; contains demo numbers |
| `/anomalies/{id}` | GET | API Key | `{id, facility_id, severity, created_at, work_order: {...}}` | Single anomaly detail |
| `/anomalies/{id}/assign` | POST | API Key | `{status: "assigned", assigned_at: <ISO 8601>}` | Mutation: confirm assignment with toast |
| `/stats` | GET | API Key | `{facilities_total, anomalies_total, resolved_count}` | Dashboard counters |
| `/impact/projection` | GET | API Key | `{total_co2_kg, total_cost_gbp, projection_100_facilities: {co2_kg, cost_gbp}}` | Impact slide numbers; **must be > 0** |

---

## Critical Checks (Frontend ↔ Backend)

### work_order Object (Most Important)
```json
{
  "title": "string (5-15 words, actionable)",
  "likely_cause": "string (1-2 sentences)",
  "action": "string (imperative: 'Replace...', 'Schedule...')",
  "urgency": "enum [high|medium|low]",
  "co2_impact_kg_per_day": "number (5-200)",
  "cost_impact_gbp_per_day": "number (50-5000)"
}
```
**Frontend must display all 6 fields in work order panel.**

### readings Array (For Charts)
```json
[
  {"timestamp": "2024-01-15T14:30:00Z", "power_kw": 450.2},
  {"timestamp": "2024-01-15T14:31:00Z", "power_kw": 451.8}
]
```
**Frontend passes to LineChart; ensure timestamps are ordered ascending.**

### projection_100_facilities (For Impact Slide)
```json
{
  "co2_kg": 12500000,
  "cost_gbp": 180000
}
```
**Must scale sensibly from current totals; used in pitch deck.**

---

## Integration Test (1-Minute Validation)

```bash
#!/bin/bash
API_URL=${1:-"http://localhost:8000"}

echo "Checking API contract..."

# 1. Health
curl -s $API_URL/health | grep -q "ok" && echo "✓ Health"

# 2. Facilities (non-empty)
FACILITIES=$(curl -s $API_URL/facilities | jq 'length')
[ $FACILITIES -gt 0 ] && echo "✓ Facilities ($FACILITIES)"

# 3. Anomalies + work_order
curl -s $API_URL/anomalies | jq '.[0].work_order | keys' | grep -q "title" && \
curl -s $API_URL/anomalies | jq '.[0].work_order | keys' | grep -q "co2_impact_kg_per_day" && \
echo "✓ work_order contract"

# 4. Impact projection
curl -s $API_URL/impact/projection | jq '.projection_100_facilities' | grep -q "co2_kg" && echo "✓ Impact projection"

echo "Contract check complete"
```

---

## Common Integration Issues

| **Issue** | **Symptom** | **Fix** |
|---|---|---|
| Missing `work_order` field | Panel shows "undefined title" | Verify `/anomalies` response includes embedded object |
| Null `co2_impact_kg_per_day` | Impact slide blank | Ensure all work orders have numeric impact values |
| Empty `readings` array | Chart is flat line | Seed facility with historical power data |
| `projection_100_facilities` is `null` | Crash on impact slide | Implement calculation: `(current × 10)` minimum |
| CORS blocked | Browser console error | Backend CORS header must allow frontend origin |
| API URL mismatch | 404 on all calls | `VITE_API_URL` env var must point to Railway backend |

---

## Seeding (For Consistent Demo)

**Backend should seed these on startup:**
- ≥1 facility with `id = "fac-001"`
- ≥8 anomalies with realistic work_order data
- ≥24 readings per facility (for 24-hour chart)

**Example seed:**
```python
# main.py or seed script
anomalies = [
    {
        "id": "anom-001",
        "facility_id": "fac-001",
        "severity": "high",
        "work_order": {
            "title": "Replace faulty compressor valve",
            "likely_cause": "Pressure relief leaking air continuously",
            "action": "Schedule maintenance visit; estimated 4 hours",
            "urgency": "high",
            "co2_impact_kg_per_day": 125,
            "cost_impact_gbp_per_day": 850
        }
    },
    # ... more anomalies
]
```

---

**Last Updated:** Pitch day -0  
**Tested:** smoke_test.sh ✓  
**Frontend Integration:** ✓ (confirmed via Network tab)
