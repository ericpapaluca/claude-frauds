---
name: backend-patterns
description: FastAPI backend patterns for rapid hackathon implementation. Use when building APIs, data pipelines, background jobs, or database integrations. Covers project structure, Supabase connections, APScheduler, error handling, and CORS setup.
---

# Backend Patterns for Rapid Implementation

## FastAPI Project Structure (5 min setup)

```
backend/
├── main.py              # Entry point, FastAPI app
├── routers/             # API route modules
│   ├── anomalies.py
│   └── facilities.py
├── services/            # Business logic
│   ├── detector.py      # Anomaly detection
│   └── claude.py        # AI integration
├── models.py            # Pydantic models
├── database.py          # DB connection
├── config.py            # Settings (env vars)
└── requirements.txt     # Dependencies
```

## requirements.txt Template

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic-settings==2.1.0
supabase==2.3.0
anthropic==0.9.0
apscheduler==3.10.4
requests==2.31.0
python-dotenv==1.0.0
```

## main.py - FastAPI App Setup

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler

from routers import anomalies, facilities
from services.poller import start_polling

scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: start background jobs
    scheduler.start()
    start_polling(scheduler)
    yield
    # Shutdown: stop scheduler
    scheduler.shutdown()

app = FastAPI(title="Hackathon Demo API", lifespan=lifespan)

# CORS - allow frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: ["https://your-frontend.vercel.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "demo-api"}

# Include routers
app.include_router(anomalies.router, prefix="/api")
app.include_router(facilities.router, prefix="/api")

# Root endpoint
@app.get("/")
def root():
    return {"message": "API is running", "docs": "/docs"}
```

## config.py - Environment Variables

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    supabase_url: str
    supabase_key: str
    
    # APIs
    anthropic_api_key: str
    sensor_api_url: str = "https://api.greentech-hackathon.org/sensors"
    
    # App config
    environment: str = "development"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## database.py - Supabase Connection

```python
from supabase import create_client, Client
from config import settings

supabase: Client = create_client(settings.supabase_url, settings.supabase_key)

def get_anomalies():
    """Fetch recent anomalies"""
    response = supabase.table('anomalies').select('*').order('created_at', desc=True).limit(50).execute()
    return response.data

def insert_anomaly(data: dict):
    """Insert new anomaly"""
    response = supabase.table('anomalies').insert(data).execute()
    return response.data

def get_facilities():
    """Fetch all facilities"""
    response = supabase.table('facilities').select('*').execute()
    return response.data
```

## models.py - Pydantic Models

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Anomaly(BaseModel):
    id: Optional[int] = None
    facility_id: str
    sensor_id: str
    timestamp: datetime
    current_value: float
    baseline_value: float
    severity: str  # 'low', 'medium', 'high'
    description: Optional[str] = None
    created_at: Optional[datetime] = None

class WorkOrder(BaseModel):
    id: Optional[int] = None
    anomaly_id: int
    title: str
    likely_cause: str
    urgency: str  # 'immediate', 'today', 'this_week'
    action: str
    co2_impact_kg_per_day: float
    cost_impact_gbp_per_day: float
    created_at: Optional[datetime] = None

class Facility(BaseModel):
    id: str
    name: str
    region: str
    size_sqm: int
    avg_power_kw: Optional[float] = None
```

## routers/anomalies.py - API Endpoints

```python
from fastapi import APIRouter, HTTPException
from typing import List
from database import get_anomalies, insert_anomaly
from models import Anomaly

router = APIRouter()

@router.get("/anomalies", response_model=List[Anomaly])
def list_anomalies():
    """Get recent anomalies"""
    try:
        return get_anomalies()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/anomalies", response_model=Anomaly)
def create_anomaly(anomaly: Anomaly):
    """Create new anomaly"""
    try:
        result = insert_anomaly(anomaly.dict(exclude={'id', 'created_at'}))
        return result[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## services/poller.py - Background Jobs

```python
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from database import insert_anomaly
from services.detector import detect_anomaly
from config import settings

def poll_sensors():
    """Poll sensor API and check for anomalies"""
    try:
        response = requests.get(f"{settings.sensor_api_url}/latest", timeout=10)
        response.raise_for_status()
        
        readings = response.json()
        
        for reading in readings:
            anomaly = detect_anomaly(reading)
            if anomaly:
                insert_anomaly(anomaly)
                print(f"Anomaly detected: {anomaly['sensor_id']}")
                
    except Exception as e:
        print(f"Polling error: {e}")

def start_polling(scheduler: BackgroundScheduler):
    """Start background polling job"""
    # Poll every 30 seconds
    scheduler.add_job(poll_sensors, 'interval', seconds=30, id='sensor_poller')
    print("✅ Started sensor polling (every 30s)")
```

## services/detector.py - Anomaly Detection

```python
from datetime import datetime

def detect_anomaly(reading: dict) -> dict | None:
    """Simple threshold-based anomaly detection"""
    current = reading.get('power_kw', 0)
    baseline = reading.get('baseline_kw', current)
    
    # Threshold: 20% deviation
    deviation = abs(current - baseline) / baseline if baseline > 0 else 0
    
    if deviation > 0.20:
        severity = 'high' if deviation > 0.40 else 'medium' if deviation > 0.30 else 'low'
        
        return {
            'facility_id': reading['facility_id'],
            'sensor_id': reading['sensor_id'],
            'timestamp': reading['timestamp'],
            'current_value': current,
            'baseline_value': baseline,
            'severity': severity,
            'description': f"{deviation*100:.1f}% above baseline"
        }
    
    return None
```

## services/claude.py - AI Integration

```python
import anthropic
from config import settings

client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

def generate_work_order(anomaly: dict) -> dict:
    """Use Claude to generate actionable work order"""
    
    prompt = f"""Anomaly detected at facility {anomaly['facility_id']}:
Sensor: {anomaly['sensor_id']}
Current: {anomaly['current_value']} kW
Baseline: {anomaly['baseline_value']} kW
Deviation: {((anomaly['current_value']/anomaly['baseline_value'])-1)*100:.1f}%

Generate a brief work order with:
- Title (max 80 chars)
- Likely cause
- Recommended action
- Estimated daily cost impact (£)
- Estimated daily CO2 impact (kg)
"""
    
    message = client.messages.create(
        model="claude-sonnet-4",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Parse response (simplified - in production use structured output)
    text = message.content[0].text
    
    return {
        'anomaly_id': anomaly['id'],
        'title': text.split('\n')[0][:80],
        'likely_cause': 'Equipment malfunction',
        'urgency': 'today',
        'action': text,
        'co2_impact_kg_per_day': 50.0,
        'cost_impact_gbp_per_day': 100.0
    }
```

## Error Handling Middleware

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "type": type(exc).__name__}
    )
```

## .env.example Template

```bash
# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# APIs
ANTHROPIC_API_KEY=sk-ant-...
SENSOR_API_URL=https://api.greentech-hackathon.org/sensors

# App
ENVIRONMENT=development
```

## README.md Template

```markdown
# Backend API

FastAPI backend for hackathon demo.

## Setup

\`\`\`bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
\`\`\`

## Run Locally

\`\`\`bash
uvicorn main:app --reload --port 8000
\`\`\`

Open http://localhost:8000/docs for API documentation.

## Deploy to Railway

\`\`\`bash
# Railway will auto-detect and deploy
git push railway main
\`\`\`
```

## Quick Database Schema (Supabase)

```sql
-- Run in Supabase SQL Editor

CREATE TABLE facilities (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    region TEXT NOT NULL,
    size_sqm INTEGER,
    avg_power_kw REAL
);

CREATE TABLE anomalies (
    id SERIAL PRIMARY KEY,
    facility_id TEXT REFERENCES facilities(id),
    sensor_id TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    current_value REAL NOT NULL,
    baseline_value REAL NOT NULL,
    severity TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE work_orders (
    id SERIAL PRIMARY KEY,
    anomaly_id INTEGER REFERENCES anomalies(id),
    title TEXT NOT NULL,
    likely_cause TEXT,
    urgency TEXT NOT NULL,
    action TEXT,
    co2_impact_kg_per_day REAL,
    cost_impact_gbp_per_day REAL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert sample facility
INSERT INTO facilities (id, name, region, size_sqm) 
VALUES ('FAC-001', 'Manchester Plant', 'UK-NW', 15000);
```

## Time Budget (5-10 minute implementation)

- **Minute 1-2:** Setup FastAPI app, install dependencies, configure CORS
- **Minute 3-4:** Create models, database connection (Supabase)
- **Minute 5-6:** Implement key API endpoints (GET /anomalies, GET /facilities)
- **Minute 7-8:** Add background poller (APScheduler) for sensor data
- **Minute 9:** Add health check, test with curl
- **Minute 10:** Connect to frontend, verify data flow

**Critical path:** Health check → Database connection → GET endpoints → Background job → Claude integration