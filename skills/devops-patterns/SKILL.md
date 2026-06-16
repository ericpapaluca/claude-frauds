---
name: devops-patterns
description: Deployment and infrastructure patterns for rapid hackathon delivery. Use when setting up Vercel/Railway configs, Docker, environment variables, or monitoring. Covers one-command deploys, health checks, and free-tier optimization.
---

# DevOps Patterns for Rapid Deployment

## Railway Deployment (Backend - 2 min)

**railway.toml**:
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "on-failure"
restartPolicyMaxRetries = 3
```

**One-command deploy:**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

**Environment variables** (set via Railway dashboard or CLI):
```bash
railway variables set SUPABASE_URL=https://...
railway variables set SUPABASE_KEY=your-key
railway variables set ANTHROPIC_API_KEY=sk-ant-...
```

## Vercel Deployment (Frontend - 1 min)

**vercel.json**:
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "env": {
    "VITE_API_URL": "https://your-backend.railway.app"
  },
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        { "key": "Access-Control-Allow-Origin", "value": "*" }
      ]
    }
  ]
}
```

**One-command deploy:**
```bash
npm run build
npx vercel --prod
```

## Docker (If Platform-Agnostic Needed)

**Dockerfile (Backend)**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml** (Local development):
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - backend
```

**Run locally:**
```bash
docker-compose up --build
```

## Environment Variable Management

**.env.example** (Backend):
```bash
# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here

# APIs
ANTHROPIC_API_KEY=sk-ant-your-key-here
SENSOR_API_URL=https://api.greentech-hackathon.org/sensors

# App Config
ENVIRONMENT=production
PORT=8000
```

**.env.example** (Frontend):
```bash
VITE_API_URL=http://localhost:8000
VITE_ENABLE_ANALYTICS=false
```

**Never commit actual .env files!** Add to .gitignore:
```
.env
.env.local
.env.*.local
```

## Health Check Patterns

**Backend health endpoint** (already in main.py):
```python
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "demo-api",
        "timestamp": datetime.now().isoformat()
    }
```

**Test health check:**
```bash
curl http://localhost:8000/health
```

## Monitoring Setup (Sentry - Optional)

**Install:**
```bash
pip install sentry-sdk[fastapi]
```

**Initialize in main.py:**
```python
import sentry_sdk

if settings.environment == "production":
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=0.1,
        environment=settings.environment
    )
```

## One-Command Deploy Script

**deploy.sh**:
```bash
#!/bin/bash
set -e

echo "🚀 Deploying Hackathon Demo..."

# Backend
echo "📦 Deploying backend to Railway..."
cd backend
railway up
BACKEND_URL=$(railway status --json | jq -r '.url')
echo "✅ Backend deployed: $BACKEND_URL"

# Frontend  
echo "📦 Deploying frontend to Vercel..."
cd ../frontend
# Update API URL in vercel.json
jq --arg url "$BACKEND_URL" '.env.VITE_API_URL = $url' vercel.json > vercel.json.tmp
mv vercel.json.tmp vercel.json
npx vercel --prod
echo "✅ Frontend deployed"

echo "🎉 Deployment complete!"
```

**Make executable and run:**
```bash
chmod +x deploy.sh
./deploy.sh
```

## Deployment Checklist

### Pre-Deploy
- [ ] Environment variables documented in .env.example
- [ ] Health check endpoint working locally
- [ ] CORS configured for frontend domain
- [ ] Database migrations run (if any)
- [ ] API endpoints tested with curl

### Deploy
- [ ] Backend deployed and health check returns 200
- [ ] Frontend deployed and loads without errors
- [ ] Frontend can reach backend API
- [ ] Test one complete user flow (e.g., view anomalies)

### Post-Deploy
- [ ] Save deployment URLs (backend + frontend)
- [ ] Test on mobile device
- [ ] Check browser console for errors
- [ ] Verify data refreshes correctly

## Troubleshooting Common Issues

### CORS Error
**Symptom:** Frontend can't call backend  
**Fix:** Add frontend URL to CORS origins in main.py
```python
allow_origins=["https://your-frontend.vercel.app"]
```

### Environment Variables Not Loading
**Symptom:** KeyError or "environment variable not set"  
**Fix:** Verify Railway/Vercel env vars are set
```bash
railway variables list
```

### Health Check Failing
**Symptom:** Platform shows "unhealthy"  
**Fix:** Test locally first
```bash
curl http://localhost:8000/health
```

### Cold Start Issues
**Symptom:** First request takes 10+ seconds  
**Fix:** Railway free tier spins down after inactivity. Use Railway Pro ($5/month) or accept initial delay.

## DEPLOYMENT.md Template

```markdown
# Deployment Guide

## Backend (Railway)

1. Install Railway CLI:
   \`\`\`bash
   npm i -g @railway/cli
   \`\`\`

2. Login and create project:
   \`\`\`bash
   cd backend
   railway login
   railway init
   \`\`\`

3. Set environment variables:
   \`\`\`bash
   railway variables set SUPABASE_URL=your-url
   railway variables set SUPABASE_KEY=your-key
   railway variables set ANTHROPIC_API_KEY=your-key
   \`\`\`

4. Deploy:
   \`\`\`bash
   railway up
   \`\`\`

5. Get URL:
   \`\`\`bash
   railway status
   \`\`\`

## Frontend (Vercel)

1. Build:
   \`\`\`bash
   cd frontend
   npm run build
   \`\`\`

2. Deploy:
   \`\`\`bash
   npx vercel --prod
   \`\`\`

3. Set environment variable in Vercel dashboard:
   - VITE_API_URL = [your Railway backend URL]

## Verify

- Backend health: https://your-backend.railway.app/health
- Frontend: https://your-frontend.vercel.app
- API docs: https://your-backend.railway.app/docs
```

## Time Budget (5-10 minute implementation)

- **Minute 1-2:** Create railway.toml and vercel.json configs
- **Minute 3-4:** Set up environment variables in platforms
- **Minute 5-6:** Deploy backend to Railway
- **Minute 7-8:** Deploy frontend to Vercel (with backend URL)
- **Minute 9:** Test health check and API connectivity
- **Minute 10:** Verify end-to-end data flow

**Critical path:** Health check working → Deploy backend → Get backend URL → Deploy frontend with URL → Test integration