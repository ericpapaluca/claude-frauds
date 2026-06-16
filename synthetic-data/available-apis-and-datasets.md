# Available APIs & Datasets for Hackathon

## AI / LLM APIs

### Anthropic Claude
- **Models:** Claude Opus 4, Claude Sonnet 4, Claude Haiku 4
- **Credit:** $25 provided per team
- **Best for:** Data analysis, natural language insights, structured data extraction, conversational interfaces
- **Docs:** https://docs.anthropic.com
- **Cost:** Sonnet ~$3 per 1M input tokens (recommended for hackathons)
- **Key features:** 1M context window, tool use, structured output

### OpenAI
- **Models:** GPT-4, GPT-3.5 Turbo, DALL-E 3, Whisper, Embeddings
- **Credit:** $25 provided per team
- **Best for:** Text generation, image generation, speech-to-text, embeddings
- **Docs:** https://platform.openai.com/docs
- **Cost:** GPT-4 Turbo ~$10 per 1M input tokens
- **Key features:** Function calling, JSON mode, vision capabilities

### HuggingFace Inference API
- **Models:** 100K+ open-source models
- **Cost:** FREE (rate-limited) or $9/month Pro
- **Best for:** Pre-trained models (sentiment analysis, NER, image classification, time-series)
- **Docs:** https://huggingface.co/docs/api-inference
- **Popular models:**
  - `facebook/bart-large-mnli` (zero-shot classification)
  - `distilbert-base-uncased` (text embeddings)
  - `facebook/prophet` (time-series forecasting)

---

## Climate & Environmental Data

### Carbon Intensity API
- **Endpoint:** `https://api.carbonintensity.org.uk/`
- **Data:** Real-time grid carbon intensity (UK)
- **Cost:** FREE, no API key required
- **Use case:** Calculate actual CO2 emissions from electricity use
- **Rate limit:** 100 requests/hour
- **Example:** `GET /intensity` returns current g CO2/kWh

### OpenWeatherMap
- **Endpoint:** `https://api.openweathermap.org/data/2.5/`
- **Data:** Current weather, 5-day forecast, historical data
- **Cost:** FREE tier (1K calls/day)
- **API key:** Sign up at openweathermap.org
- **Use case:** Correlate energy use with temperature
- **Example:** `GET /weather?q=London&appid=YOUR_KEY`

### EPA Air Quality API
- **Endpoint:** `https://aqs.epa.gov/data/api`
- **Data:** Air quality measurements (PM2.5, ozone, etc.) from 10K+ monitors
- **Cost:** FREE, API key required
- **Docs:** https://aqs.epa.gov/aqsweb/documents/data_api.html
- **Use case:** Air quality monitoring and health alerts

### World Bank Climate Data
- **Endpoint:** `https://climateknowledgeportal.worldbank.org/api`
- **Data:** Historical climate data, future projections
- **Cost:** FREE, no key
- **Use case:** Long-term climate trends, baseline comparisons

---

## IoT & Sensor Data (Simulated)

### GreenTech Simulated Sensor API
**Provided by hackathon organizers**

- **Endpoint:** `https://api.greentech-hackathon.org/sensors`
- **Auth:** Bearer token (provided at kickoff)
- **Data format:**
  ```json
  {
    "facility_id": "FAC-001",
    "timestamp": "2026-06-16T10:30:00Z",
    "sensors": {
      "temperature_c": 22.5,
      "humidity_percent": 45,
      "power_kw": 150.2,
      "co2_ppm": 420
    },
    "location": {
      "lat": 37.7749,
      "lon": -122.4194,
      "region": "US-CA"
    }
  }
  ```
- **Coverage:** 50 simulated facilities
- **Update frequency:** Every 5 seconds
- **Historical data:** Last 30 days available via `/sensors/historical?facility_id=...`

---

## Data Storage & Databases

### Supabase (Postgres)
- **Free tier:** 500MB database, 2GB bandwidth, 50K monthly active users
- **Features:** Auth, real-time subscriptions, storage, REST API auto-generated
- **Setup time:** 5 minutes
- **Best for:** Relational data, real-time apps
- **Hosting:** Cloud (no local setup needed)

### MongoDB Atlas
- **Free tier:** 512MB storage, shared cluster
- **Features:** Document database, aggregation pipelines, Atlas Search
- **Setup time:** 10 minutes
- **Best for:** Flexible schemas, JSON-heavy data
- **Hosting:** Cloud

### PlanetScale (MySQL)
- **Free tier:** 10GB storage, 1 billion row reads/month
- **Features:** Branching (like Git for databases), online schema changes
- **Setup time:** 10 minutes
- **Best for:** MySQL users, teams needing DB branches for testing

### Redis (Upstash)
- **Free tier:** 10K commands/day, 256MB
- **Features:** In-memory cache, pub/sub, rate limiting
- **Setup time:** 5 minutes
- **Best for:** Caching, session storage, real-time leaderboards
- **Serverless:** Pay-per-request beyond free tier

---

## Hosting & Deployment

### Vercel
- **Free tier:** Unlimited projects, 100GB bandwidth/month
- **Best for:** Next.js, React, Vue, Svelte, static sites
- **Deploy time:** 2 minutes (connect GitHub repo)
- **Features:** Auto-HTTPS, preview deployments, edge functions

### Railway
- **Free tier:** $5 credit/month (usually enough for hackathon + 30 days)
- **Best for:** Full-stack apps, background workers, Docker containers
- **Features:** Postgres, Redis, cron jobs all built-in
- **Deploy time:** 5 minutes

### Render
- **Free tier:** Static sites, web services (with spin-down after 15 min idle)
- **Best for:** Python/Node APIs, Docker apps
- **Features:** Auto-deploy from GitHub, managed Postgres/Redis
- **Deploy time:** 10 minutes

### fly.io
- **Free tier:** 3 small VMs, 160GB bandwidth
- **Best for:** Docker apps, global edge deployment
- **Deploy time:** 15 minutes
- **Features:** Multi-region, persistent volumes

---

## Additional Services

### Twilio (SMS/Voice)
- **Free trial:** $15 credit
- **Use case:** SMS alerts, phone notifications
- **Docs:** https://www.twilio.com/docs
- **Example:** Send SMS when CO2 levels spike

### SendGrid (Email)
- **Free tier:** 100 emails/day
- **Use case:** Email alerts, reports, notifications
- **Setup:** 10 minutes
- **Docs:** https://docs.sendgrid.com

### Cloudinary (Image/Video)
- **Free tier:** 25GB storage, 25GB bandwidth/month
- **Use case:** Image optimization, transformations, video processing
- **Features:** Auto-format, responsive images, AI-powered tagging

### Sentry (Error Tracking)
- **Free tier:** 5K errors/month
- **Use case:** Catch and debug production errors
- **Setup:** 5 minutes (one line of code)
- **Features:** Stack traces, breadcrumbs, performance monitoring

---

## Pre-built Components & Libraries

### Recharts (React charts)
- **Free:** MIT licensed
- **Use case:** Beautiful charts with minimal code
- **Example:** Line charts, bar charts, area charts for sensor data
- **Docs:** https://recharts.org

### Chart.js (Vanilla JS charts)
- **Free:** MIT licensed
- **Use case:** Charts for any JS framework
- **Lightweight:** 11KB gzipped
- **Docs:** https://www.chartjs.org

### Plotly (Python visualizations)
- **Free:** MIT licensed
- **Use case:** Interactive charts in Streamlit, Flask apps
- **Features:** 3D plots, heatmaps, time-series
- **Docs:** https://plotly.com/python

### Leaflet.js (Maps)
- **Free:** BSD licensed
- **Use case:** Interactive maps, geolocation, facility markers
- **Lightweight:** 42KB
- **Docs:** https://leafletjs.com

---

## Time-Series & ML Libraries

### Prophet (Facebook)
- **Free:** MIT licensed
- **Use case:** Time-series forecasting (energy demand prediction)
- **Setup:** `pip install prophet`
- **Strength:** Handles seasonality, holidays, missing data automatically
- **Docs:** https://facebook.github.io/prophet

### scikit-learn
- **Free:** BSD licensed
- **Use case:** Anomaly detection, clustering, classification
- **Setup:** `pip install scikit-learn`
- **Popular models:**
  - `IsolationForest` (anomaly detection)
  - `KMeans` (clustering facilities by usage patterns)
  - `RandomForestClassifier` (predict equipment failures)

### Pandas
- **Free:** BSD licensed
- **Use case:** Data manipulation, time-series analysis
- **Setup:** `pip install pandas`
- **Features:** DataFrames, rolling windows, resampling

### DuckDB
- **Free:** MIT licensed
- **Use case:** Fast SQL queries on large datasets (Parquet, CSV)
- **Setup:** `pip install duckdb`
- **Strength:** 100x faster than Pandas for aggregations
- **Docs:** https://duckdb.org

---

## Quick-Start Stacks (Copy-Paste Ready)

### Stack 1: Simple Dashboard
- **Frontend:** React + Recharts
- **Backend:** FastAPI (Python)
- **Database:** Supabase (Postgres)
- **Hosting:** Vercel (frontend) + Render (backend)
- **Time to working prototype:** 2-3 hours

### Stack 2: ML-Powered Insights
- **Full-stack:** Streamlit (Python)
- **ML:** Prophet + scikit-learn
- **Data:** Pandas DataFrames
- **Hosting:** Streamlit Cloud
- **Time to working prototype:** 1-2 hours

### Stack 3: Real-Time Alerts
- **Frontend:** Next.js
- **Backend:** Vercel serverless functions
- **Database:** Firebase Realtime Database
- **Notifications:** Twilio (SMS)
- **AI:** Claude API (natural language alerts)
- **Time to working prototype:** 3-4 hours

### Stack 4: IoT Data Pipeline
- **Ingestion:** Python script polling sensor API
- **Storage:** PostgreSQL (Railway)
- **Processing:** DuckDB for aggregations
- **Visualization:** Plotly + Streamlit
- **Time to working prototype:** 4-5 hours

---

## Cost Guardrails

**Total budget per team:** ~$100 in credits + free tiers

| Service | Free Tier | Paid Threshold | Hackathon Risk |
|---------|-----------|----------------|----------------|
| Claude API | $25 credit | ~1500 Sonnet calls | LOW (monitor usage) |
| OpenAI API | $25 credit | ~2500 GPT-3.5 calls | MEDIUM (GPT-4 expensive) |
| Vercel | Unlimited | NA | ZERO |
| Railway | $5/month | Auto-shuts off at $5 | LOW |
| Supabase | 500MB | NA | ZERO |
| Twilio | $15 trial | ~500 SMS | LOW |

**Pro tip:** Set billing alerts at $20 for any paid service!

---

## Support Channels

- **Technical questions:** Slack #tech-support
- **API issues:** Slack #api-help
- **Billing/credits:** Slack #admin
- **Mentors:** Request 1:1 via /mentor command in Slack

---

**Remember:** The best stack is the one you can ship in 48 hours. Don't try to learn 5 new technologies at once!