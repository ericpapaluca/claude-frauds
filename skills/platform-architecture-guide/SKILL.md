---
name: platform-architecture-guide
description: Platform and infrastructure patterns for hackathons. Use when evaluating hosting strategy, deployment complexity, observability, or operational feasibility. Covers rapid deployment (Vercel/Railway/Render), service selection (auth/DB/storage), demo-day reliability, and cost estimation for 48-hour builds.
---

# Platform Architecture Guide for Hackathons

## Hosting Decision Tree

```
START: What are you building?
  │
  ├─ Static site / React/Vue/Svelte
  │   └─→ Vercel/Netlify (10 min deploy) ──→ FREE
  │
  ├─ Next.js / Full-stack React
  │   └─→ Vercel (15 min deploy) ──→ FREE
  │
  ├─ Python API (Flask/FastAPI)
  │   └─→ Render/Railway (20 min deploy) ──→ FREE tier OK
  │
  ├─ Node API (Express)
  │   └─→ Render/Railway/fly.io (20 min) ──→ FREE tier OK
  │
  ├─ Database needed?
  │   ├─ Postgres ──→ Supabase/Neon (5 min) ──→ FREE
  │   └─ MongoDB ──→ MongoDB Atlas (10 min) ──→ FREE
  │
  ├─ Background jobs / Workers
  │   └─→ Railway + Redis (30 min) ──→ $5/month
  │
  ├─ Docker container
  │   └─→ fly.io/Railway (45 min) ──→ FREE tier usually OK
  │
  └─ Complex (multiple services, GPU)
      └─→ AWS/GCP with Docker Compose (4+ hours) ──→ $$
```

**Hackathon golden rule:** If setup takes > 1 hour, you're over-engineering.

## Rapid Deployment Patterns

### Pattern 1: Frontend on Vercel (Fastest)

**Use for:** React, Next.js, Vue, Svelte, static sites

**Time:** 10-15 minutes from code to URL

```bash
# One-time setup
npm install -g vercel
vercel login

# Deploy (run in your project root)
vercel

# That's it! You get: https://your-project-abc123.vercel.app
```

**GitHub integration (even better):**
1. Push code to GitHub
2. Connect repo in Vercel dashboard
3. Auto-deploys on every push to main

**Environment variables:**
```bash
# Add via CLI
vercel env add ANTHROPIC_API_KEY

# Or in dashboard: Settings → Environment Variables
```

**Cost:** FREE for unlimited projects

### Pattern 2: Python API on Render

**Use for:** Flask, FastAPI, Django APIs

**Time:** 20 minutes

```yaml
# render.yaml (in repo root)
services:
  - type: web
    name: hackathon-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: ANTHROPIC_API_KEY
        sync: false  # Set manually in dashboard
```

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CRITICAL: Allow your frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Hackathon mode - be permissive
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/generate")
def generate(data: dict):
    # Your AI logic here
    return {"result": "..."}
```

**Deploy:**
1. Push to GitHub
2. Create new Web Service in Render dashboard
3. Connect repo
4. It auto-detects Python and deploys

**Cost:** FREE tier (spins down after 15 min idle - OK for demos)

### Pattern 3: Full-Stack on Railway

**Use for:** Monolith with DB, background workers, multiple services

**Time:** 30 minutes

```toml
# railway.toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
restartPolicyType = "on-failure"
```

**Add Postgres:**
```bash
# In Railway dashboard: New → Database → PostgreSQL
# Automatically injects DATABASE_URL env var
```

**Add Redis (for caching/jobs):**
```bash
# In Railway dashboard: New → Database → Redis
# Injects REDIS_URL
```

**Cost:** $5/month (includes $5 credit - effectively free for hackathon)

### Pattern 4: Docker Anywhere

**Use when:** You have complex dependencies, need specific OS packages, or multi-service app

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Expose port
EXPOSE 8000

# Health check (critical for deployment platforms)
HEALTHCHECK --interval=30s --timeout=3s \\
  CMD curl -f http://localhost:8000/health || exit 1

# Run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Deploy to fly.io:**
```bash
# One-time setup
curl -L https://fly.io/install.sh | sh
fly auth login

# Deploy
fly launch  # Detects Dockerfile, asks a few questions
fly deploy  # Each subsequent deploy
```

**Cost:** FREE tier includes 3 small VMs

## Service Selection Guide

### Authentication

| Service | Setup Time | Free Tier | Best For | Code Example |
|---------|------------|-----------|----------|--------------|
| **Clerk** | 15 min | 10k MAU | React/Next.js | Drop-in components |
| Auth0 | 30 min | 7.5k MAU | Any stack | More config needed |
| Supabase Auth | 10 min | Unlimited | If already using Supabase | Built into Supabase |
| Roll your own | 2-4 hours | FREE | Learning experience | JWT + bcrypt |

**Hackathon recommendation:** Clerk for frontend apps, Supabase if you need Postgres anyway

**Clerk setup (Next.js):**
```bash
npm install @clerk/nextjs
```

```typescript
// app/layout.tsx
import { ClerkProvider } from '@clerk/nextjs'

export default function RootLayout({ children }) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body>{children}</body>
      </html>
    </ClerkProvider>
  )
}

// Any page - automatically shows sign-in if not logged in
import { auth } from '@clerk/nextjs/server'

export default async function DashboardPage() {
  const { userId } = await auth()
  if (!userId) return <div>Not authorized</div>
  return <div>Welcome, user {userId}</div>
}
```

### Database

| Service | Setup Time | Free Tier | Best For | Connection |
|---------|------------|-----------|----------|------------|
| **Supabase** | 5 min | 500MB | Postgres + realtime | `postgresql://...` |
| Neon | 5 min | 10GB | Serverless Postgres | `postgresql://...` |
| PlanetScale | 10 min | 10GB | MySQL, branching | `mysql://...` |
| MongoDB Atlas | 10 min | 512MB | Document DB | `mongodb+srv://...` |
| SQLite | 0 min | Unlimited | Local/small data | `sqlite:///local.db` |

**Hackathon recommendation:** Supabase (best free tier + realtime features)

**Supabase quickstart:**
1. Create project at supabase.com (2 min)
2. Get connection string from Settings → Database
3. Use in your app:

```python
import os
from supabase import create_client

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Insert data
supabase.table('events').insert({
    "user_id": "123",
    "event_type": "click",
    "timestamp": "2026-06-16T10:00:00"
}).execute()

# Query data
result = supabase.table('events').select("*").eq('user_id', '123').execute()
```

### File Storage

| Service | Setup Time | Free Tier | Best For | Note |
|---------|------------|-----------|----------|------|
| **Supabase Storage** | 5 min | 1GB | If using Supabase | Built-in |
| Cloudinary | 15 min | 25GB | Images/video | Auto-optimization |
| AWS S3 | 30 min | 5GB | Any files | Most flexible, more complex |
| Vercel Blob | 10 min | Varies | If on Vercel | Simple API |

**Cloudinary example (images):**
```python
import cloudinary.uploader

result = cloudinary.uploader.upload(
    file,
    folder="hackathon",
    transformation={"width": 800, "crop": "limit"}  # Auto-resize
)

url = result['secure_url']  # Use this in your app
```

### Caching / Session Storage

| Service | Setup Time | Use Case | Code |
|---------|------------|----------|------|
| **Redis (Upstash)** | 10 min | Session data, rate limiting | See below |
| In-memory (dict) | 0 min | Single-server only | `cache = {}` |
| Browser localStorage | 0 min | Client-side cache | `localStorage.setItem()` |

**Upstash Redis (serverless):**
```python
import redis

r = redis.from_url(
    os.getenv("UPSTASH_REDIS_URL"),
    decode_responses=True
)

# Cache expensive computation
def get_recommendations(user_id):
    cache_key = f"recs:{user_id}"
    
    # Check cache
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Compute
    recs = expensive_ai_call(user_id)
    
    # Cache for 1 hour
    r.setex(cache_key, 3600, json.dumps(recs))
    return recs
```

## Demo-Day Reliability Checklist

### Critical: Must-Haves for Live Demo

**1. Health Check Endpoint**
```python
@app.get("/health")
def health():
    """Platform uses this to verify app is running"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
```

**2. Graceful Error Handling**
```python
from fastapi import HTTPException

@app.post("/api/generate")
async def generate(data: dict):
    try:
        result = ai_api_call(data)
        return {"result": result}
    except Exception as e:
        # Log error but don't crash
        print(f"ERROR: {e}")
        # Return fallback
        return {"result": "Sorry, AI service temporarily unavailable"}
```

**3. Fallback / Demo Mode**
```python
# Always have cached demo data
DEMO_RESPONSES = {
    "sample input 1": {"result": "precomputed output 1"},
    "sample input 2": {"result": "precomputed output 2"}
}

def safe_generate(input_text):
    # If network fails during demo, use cache
    try:
        return live_ai_call(input_text)
    except:
        # Fallback to closest demo example
        if input_text in DEMO_RESPONSES:
            return DEMO_RESPONSES[input_text]
        else:
            return DEMO_RESPONSES["sample input 1"]  # Default fallback
```

**4. Rate Limiting (Prevent Abuse)**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/generate")
@limiter.limit("10/minute")  # Max 10 requests per minute per IP
async def generate(request: Request, data: dict):
    return {"result": ai_call(data)}
```

**5. Request Timeout**
```python
import asyncio

async def generate_with_timeout(prompt):
    try:
        return await asyncio.wait_for(
            ai_api_call(prompt),
            timeout=10.0  # 10 second max
        )
    except asyncio.TimeoutError:
        return "Request timed out - please try again"
```

### Nice-to-Haves

**Loading States:**
```typescript
// Frontend - show progress during API calls
const [loading, setLoading] = useState(false);

async function generate() {
  setLoading(true);
  try {
    const response = await fetch('/api/generate', {...});
    const data = await response.json();
    setResult(data.result);
  } finally {
    setLoading(false);
  }
}

return (
  <div>
    {loading ? <Spinner text="Generating..." /> : <Result />}
  </div>
);
```

**Logging:**
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/api/generate")
async def generate(data: dict):
    logger.info(f"Generate request: {data}")
    result = ai_call(data)
    logger.info(f"Generate success: {result[:50]}...")
    return {"result": result}
```

## Cost Estimation

### Typical Hackathon Project Budget

| Service | Cost | What You Get |
|---------|------|--------------|
| **Hosting** | $0 | Vercel/Render free tier |
| **Database** | $0 | Supabase free tier (500MB) |
| **Auth** | $0 | Clerk free tier (10k users) |
| **AI API** | $10-30 | ~500-1500 Claude Sonnet requests |
| **File Storage** | $0 | Cloudinary free tier (25GB) |
| **Monitoring** | $0 | Sentry free tier |
| **Domain** (optional) | $0 | Use platform subdomain |
| **Total** | **$10-30** | Just AI API costs |

### Cloud Provider Comparison (if you need more than free tiers)

| Provider | Good For | Easy To Use | Hackathon Advice |
|----------|----------|-------------|------------------|
| **Vercel** | Frontend, Next.js, serverless functions | ⭐⭐⭐⭐⭐ | DEFAULT CHOICE |
| **Railway** | Full-stack, multiple services, databases | ⭐⭐⭐⭐ | If you need DB + backend |
| **Render** | APIs, background workers | ⭐⭐⭐⭐ | Good alternative to Railway |
| **fly.io** | Docker, global edge deployment | ⭐⭐⭐ | If you know Docker |
| **AWS** | Everything, complex systems | ⭐⭐ | Only if required by hackathon |
| **GCP** | ML workloads, Google services | ⭐⭐ | Has $300 credit but complex |
| **Azure** | Enterprise, Microsoft stack | ⭐⭐ | Avoid unless required |

## Quick Observability

### Logging (Free)

**Simple: Print to stdout (all platforms collect this)**
```python
import sys
import json
from datetime import datetime

def log(level, message, **kwargs):
    """Structured logging for platform dashboards"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "message": message,
        **kwargs
    }
    print(json.dumps(log_entry), file=sys.stdout, flush=True)

# Usage
log("INFO", "User generated content", user_id="123", tokens=450)
log("ERROR", "AI API failed", error=str(e))
```

### Error Tracking (Free Tier)

**Sentry (catch exceptions automatically):**
```python
import sentry_sdk

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    traces_sample_rate=0.1,  # 10% of requests (free tier limit)
)

# That's it - now all exceptions auto-reported with context
```

### Uptime Monitoring (Free)

**UptimeRobot:** Ping your `/health` endpoint every 5 minutes, email if down

1. Add endpoint: `https://your-app.vercel.app/health`
2. Set check interval: 5 minutes
3. Add notification email
4. Cost: FREE

## Architecture Patterns

### Monolith (Fastest to Build)

```
[React Frontend] ─HTTP─> [FastAPI Backend + SQLite]
                              │
                              ├─ /api/auth
                              ├─ /api/generate (calls AI API)
                              └─ /api/data (queries SQLite)
```

**Time to deploy:** 1-2 hours  
**Best for:** Most hackathons  
**Trade-off:** Not "scalable" (but judges rarely care)

### Frontend + Backend Split (Most Common)

```
[React on Vercel] ─CORS→ [Python API on Render] ─→ [Supabase Postgres]
                              │
                              └─→ [AI APIs]
```

**Time to deploy:** 2-3 hours  
**Best for:** Team with frontend/backend specialists  
**Trade-off:** More deployment complexity

### Serverless (Minimal Ops)

```
[Next.js on Vercel]
    ├─ /app/* (React pages)
    └─ /api/* (Serverless functions)
           │
           ├─→ [Supabase] (DB)
           └─→ [AI APIs]
```

**Time to deploy:** 1 hour  
**Best for:** Solo dev, tight timeline  
**Trade-off:** Cold starts (first request slow)

## Deployment Checklist

| Task | Time | When |
|------|------|------|
| ✅ Choose hosting platform | 15 min | Hour 0-2 |
| ✅ Get one endpoint deployed | 30 min | Hour 2-4 |
| ✅ Add database (if needed) | 30 min | Hour 4-8 |
| ✅ Configure env vars | 15 min | Hour 4-8 |
| ✅ Add health check endpoint | 10 min | Hour 8-12 |
| ✅ Test from public URL | 15 min | Hour 12+ |
| ✅ Add error handling | 1 hour | Hour 12-16 |
| ✅ Add rate limiting | 30 min | Hour 16-20 |
| ✅ Setup logging | 30 min | Hour 20-24 |
| ✅ Test demo paths 10x | 1 hour | Hour 40-44 |
| ✅ Prepare fallback data | 30 min | Hour 44-46 |

## Demo Day Checklist

**Morning of Demo:**
- [ ] Verify app is up (check health endpoint)
- [ ] Test critical user flows 3x
- [ ] Prepare demo account (if auth required)
- [ ] Screenshot working state (backup if live demo fails)
- [ ] Have fallback video ready
- [ ] Charge laptop fully
- [ ] Test on demo WiFi (often slow/blocked)

**5 Minutes Before:**
- [ ] Open app in browser tab
- [ ] Open logs dashboard in another tab
- [ ] Close unrelated tabs
- [ ] Disable notifications
- [ ] Use incognito/private mode (clean state)

**Backup Plan:**
- [ ] "Sorry, network issue - here's a video of it working"
- [ ] Have 30-second video pre-recorded showing happy path
- [ ] Alternatively: run locally if platform is down