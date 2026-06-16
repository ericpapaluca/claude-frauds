"""
WattWatch Backend API - Minimal demo implementation
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import random

app = FastAPI(title="WattWatch API", version="0.1.0")

# CORS - allow all origins for demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seed data
FACILITIES = [
    {"id": "fac-001", "name": "Manchester Plant", "region": "UK-NW", "lat": 53.4808, "lng": -2.2426, "status": "online", "current_power_kw": 450.2},
    {"id": "fac-002", "name": "Birmingham Warehouse", "region": "UK-MW", "lat": 52.4862, "lng": -1.8904, "status": "online", "current_power_kw": 320.5},
    {"id": "fac-003", "name": "Leeds Factory", "region": "UK-NE", "lat": 53.8008, "lng": -1.5491, "status": "online", "current_power_kw": 580.1},
]

ANOMALIES = [
    {
        "id": 1,
        "facility_id": "fac-001",
        "severity": "high",
        "created_at": "2026-06-16T10:30:00Z",
        "work_order": {
            "title": "Compressor #7 drawing 28% above baseline",
            "likely_cause": "Likely refrigerant leak or mechanical wear in compressor",
            "action": "Schedule immediate inspection of compressor #7. Check refrigerant levels and belt tension.",
            "urgency": "high",
            "co2_impact_kg_per_day": 47.2,
            "cost_impact_gbp_per_day": 1400.0
        }
    },
    {
        "id": 2,
        "facility_id": "fac-002",
        "severity": "medium",
        "created_at": "2026-06-16T09:15:00Z",
        "work_order": {
            "title": "HVAC running outside business hours",
            "likely_cause": "Thermostat schedule not configured or override left active",
            "action": "Reset HVAC schedule to match business hours (Mon-Fri 7AM-7PM)",
            "urgency": "medium",
            "co2_impact_kg_per_day": 22.5,
            "cost_impact_gbp_per_day": 680.0
        }
    },
    {
        "id": 3,
        "facility_id": "fac-003",
        "severity": "high",
        "created_at": "2026-06-16T08:00:00Z",
        "work_order": {
            "title": "Conveyor motor stuck at full power",
            "likely_cause": "Variable frequency drive malfunction or control signal loss",
            "action": "Inspect VFD for error codes. Replace control board if faulty.",
            "urgency": "high",
            "co2_impact_kg_per_day": 65.8,
            "cost_impact_gbp_per_day": 1950.0
        }
    },
]

# Generate historical readings
def generate_readings(facility_id: str, hours: int = 24):
    base = 450 if facility_id == "fac-001" else 320 if facility_id == "fac-002" else 580
    readings = []
    now = datetime.now()

    for i in range(hours * 6):  # 6 readings per hour (every 10 min)
        ts = now - timedelta(minutes=i * 10)
        # Add some variation
        value = base + random.uniform(-30, 30)
        readings.append({
            "timestamp": ts.isoformat() + "Z",
            "power_kw": round(value, 1)
        })

    return list(reversed(readings))


@app.get("/health")
def health():
    return {"status": "ok", "service": "wattwatch-api", "version": "0.1.0"}


@app.get("/facilities")
def get_facilities():
    return FACILITIES


@app.get("/facilities/{fac_id}")
def get_facility(fac_id: str):
    facility = next((f for f in FACILITIES if f["id"] == fac_id), None)
    if not facility:
        return {"error": "Not found"}, 404

    return {
        **facility,
        "readings": generate_readings(fac_id)
    }


@app.get("/anomalies")
def get_anomalies():
    return ANOMALIES


@app.get("/anomalies/{anomaly_id}")
def get_anomaly(anomaly_id: int):
    anomaly = next((a for a in ANOMALIES if a["id"] == anomaly_id), None)
    if not anomaly:
        return {"error": "Not found"}, 404
    return anomaly


@app.post("/anomalies/{anomaly_id}/assign")
def assign_anomaly(anomaly_id: int):
    return {
        "status": "assigned",
        "assigned_at": datetime.now().isoformat() + "Z"
    }


@app.get("/stats")
def get_stats():
    return {
        "facilities_total": len(FACILITIES),
        "anomalies_total": len(ANOMALIES),
        "resolved_count": 15
    }


@app.get("/impact/projection")
def get_impact_projection():
    total_co2 = sum(a["work_order"]["co2_impact_kg_per_day"] for a in ANOMALIES)
    total_cost = sum(a["work_order"]["cost_impact_gbp_per_day"] for a in ANOMALIES)

    return {
        "total_co2_kg": round(total_co2 * 30, 1),  # Monthly
        "total_cost_gbp": round(total_cost * 30, 1),
        "projection_100_facilities": {
            "co2_kg": round(total_co2 * 365 * 33, 1),  # 100 facilities / 3 current
            "cost_gbp": round(total_cost * 365 * 33, 1)
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
