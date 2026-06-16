---
name: data-engineering-patterns
description: Hackathon data engineering patterns and architecture guide. Use when evaluating data pipeline feasibility, storage architecture, data source integration, or scalability for hackathon projects. Covers tool selection (Spark/Pandas/DuckDB), pipeline patterns (batch/streaming), storage strategies, and 48-hour implementation heuristics.
---

# Data Engineering Patterns for Hackathons

## Tool Selection Matrix

### When to Use What

| Data Volume | Latency Need | Recommended Stack | Setup Time | Code Example |
|-------------|--------------|-------------------|------------|--------------|
| < 1GB | Any | Pandas + SQLite | 15 min | `df = pd.read_csv(); df.to_sql()` |
| 1-50GB | Batch OK | DuckDB | 30 min | `duckdb.sql("SELECT * FROM 'data.parquet'")` |
| 50GB+ | Batch OK | Spark (Databricks Community) | 2 hours | `spark.read.parquet().groupBy().agg()` |
| Any | < 1s | Redis + Postgres | 1 hour | Cache hot paths, batch writes |
| Streaming | Real-time | Python + Kafka/Redis Streams | 3 hours | Complex - only if required |

**Hackathon heuristic:** If you can fit it in memory, use Pandas. If not, use DuckDB. Spark only if judges care about "enterprise scale."

### Quick Setup Examples

**Pandas (90% of hackathon use cases):**
```python
import pandas as pd
import sqlite3

# Read from CSV/JSON/API
df = pd.read_csv('data.csv')
# or: df = pd.read_json('api_response.json')

# Transform
df['normalized'] = (df['value'] - df['value'].mean()) / df['value'].std()

# Store for querying
conn = sqlite3.connect('hackathon.db')
df.to_sql('events', conn, if_exists='replace', index=False)

# Query
result = pd.read_sql("SELECT * FROM events WHERE normalized > 2", conn)
```

**DuckDB (for larger datasets, still simple):**
```python
import duckdb

# Read directly from files (no loading to memory!)
result = duckdb.sql("""
    SELECT sensor_id, AVG(temperature) as avg_temp
    FROM 'sensors/*.parquet'
    WHERE timestamp > '2026-01-01'
    GROUP BY sensor_id
    ORDER BY avg_temp DESC
""").df()  # Returns pandas DataFrame
```

## Data Pipeline Architectures

### Pattern 1: Simple Batch (0-6 hours to build)

```
[Data Source] → [Ingest Script] → [SQLite/Postgres] → [API/Viz]
```

**When to use:** 
- Data doesn't change during demo
- < 10GB total
- No real-time requirements

**Implementation:**
```python
# ingest.py - Run once before demo
import requests
import pandas as pd
import sqlite3

# Fetch from API
response = requests.get('https://api.example.com/data')
df = pd.DataFrame(response.json())

# Clean and transform
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.dropna(subset=['critical_field'])

# Store
conn = sqlite3.connect('demo.db')
df.to_sql('data', conn, if_exists='replace')
print(f"Loaded {len(df)} records")
```

### Pattern 2: Streaming Lite (6-12 hours to build)

```
[API/Webhook] → [Python Service] → [Redis/SQLite] → [WebSocket to Frontend]
```

**When to use:**
- Demo requires "live updates"
- Can simulate streaming with polling
- < 100 events/sec

**Implementation:**
```python
# stream_processor.py
import time
import redis
import json
from collections import deque

r = redis.Redis(host='localhost', decode_responses=True)
window = deque(maxlen=100)  # Keep last 100 events in memory

while True:
    # Poll data source (or receive webhook)
    new_data = fetch_latest_data()
    
    for event in new_data:
        # Store in Redis with TTL
        r.setex(f"event:{event['id']}", 3600, json.dumps(event))
        
        # Update windowed aggregate
        window.append(event['value'])
        avg = sum(window) / len(window)
        
        # Publish to frontend via Redis pubsub
        r.publish('updates', json.dumps({'avg': avg, 'event': event}))
    
    time.sleep(5)  # Poll every 5 seconds (simulates real-time)
```

### Pattern 3: ETL with Scheduled Refresh (8-16 hours to build)

```
[External API] → [Airflow/Cron] → [Transform] → [Postgres] → [API/Dashboard]
```

**When to use:**
- Data updates hourly/daily
- Need historical trends
- Multiple data sources to combine

**Minimal Airflow-lite with cron:**
```python
# etl_job.py - Schedule with: crontab -e → 0 * * * * python etl_job.py
import pandas as pd
import psycopg2
from datetime import datetime

def extract():
    """Pull from multiple sources"""
    df1 = pd.read_csv('https://data.gov/api/sensor_data')
    df2 = pd.read_json('https://weather-api.com/forecast')
    return df1, df2

def transform(df1, df2):
    """Join and aggregate"""
    df1['timestamp'] = pd.to_datetime(df1['timestamp'])
    df2['timestamp'] = pd.to_datetime(df2['timestamp'])
    
    merged = pd.merge(df1, df2, on='timestamp', how='inner')
    merged['score'] = merged['sensor_value'] * merged['temperature_factor']
    return merged

def load(df):
    """Append to Postgres"""
    conn = psycopg2.connect("postgresql://user:pass@localhost/hackathon")
    df.to_sql('enriched_data', conn, if_exists='append', index=False)
    print(f"{datetime.now()}: Loaded {len(df)} rows")

if __name__ == "__main__":
    df1, df2 = extract()
    merged = transform(df1, df2)
    load(merged)
```

## Data Source Patterns

### APIs (Most Common)

```python
import requests
import pandas as pd
from time import sleep

def fetch_paginated_api(base_url, pages=10):
    """Handle pagination - common in real APIs"""
    all_data = []
    for page in range(1, pages + 1):
        response = requests.get(f"{base_url}?page={page}")
        if response.status_code != 200:
            break
        data = response.json()
        all_data.extend(data['results'])
        sleep(0.5)  # Be nice to free APIs
    return pd.DataFrame(all_data)

# Example: GitHub API
df = fetch_paginated_api('https://api.github.com/users/anthropics/repos')
```

### Synthetic Data Generation (When Real Data Unavailable)

```python
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_iot_sensor_data(num_sensors=50, days=30):
    """Generate realistic-looking sensor data for demo"""
    np.random.seed(42)  # Reproducible for demo
    
    timestamps = pd.date_range(
        end=datetime.now(), 
        periods=days * 24 * 60,  # Minute-level data
        freq='1min'
    )
    
    data = []
    for sensor_id in range(num_sensors):
        # Each sensor has baseline + noise + daily pattern
        baseline = np.random.uniform(20, 30)
        daily_pattern = 5 * np.sin(np.arange(len(timestamps)) * 2 * np.pi / (24 * 60))
        noise = np.random.normal(0, 1, len(timestamps))
        
        values = baseline + daily_pattern + noise
        
        # Add occasional anomalies (makes demo interesting)
        anomaly_indices = np.random.choice(len(timestamps), size=10, replace=False)
        values[anomaly_indices] += np.random.uniform(10, 20, 10)
        
        sensor_df = pd.DataFrame({
            'sensor_id': f'sensor_{sensor_id:03d}',
            'timestamp': timestamps,
            'temperature': values,
            'status': np.random.choice(['ok', 'warning'], len(timestamps), p=[0.95, 0.05])
        })
        data.append(sensor_df)
    
    return pd.concat(data, ignore_index=True)

# Generate and save
df = generate_iot_sensor_data()
df.to_parquet('synthetic_sensors.parquet')  # Efficient storage
```

## Storage Patterns

### SQLite (Best for < 50GB, single-server)

```python
import sqlite3

conn = sqlite3.connect('demo.db')

# Create indexed table
conn.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY,
        timestamp DATETIME,
        sensor_id TEXT,
        value REAL
    )
""")

# CRITICAL: Add indexes for demo queries
conn.execute("CREATE INDEX idx_timestamp ON events(timestamp)")
conn.execute("CREATE INDEX idx_sensor ON events(sensor_id)")

# Bulk insert (much faster than row-by-row)
data = [(ts, sid, val) for ts, sid, val in zip(timestamps, sensor_ids, values)]
conn.executemany("INSERT INTO events VALUES (NULL, ?, ?, ?)", data)
conn.commit()
```

### Postgres (Better for concurrent access, GIS, JSON)

```python
import psycopg2
from psycopg2.extras import execute_values

conn = psycopg2.connect("postgresql://user:pass@localhost/hackathon")
cur = conn.cursor()

# JSON support (great for flexible schemas in hackathons)
cur.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id SERIAL PRIMARY KEY,
        timestamp TIMESTAMPTZ,
        metadata JSONB,
        location GEOGRAPHY(POINT)  -- If you need geo queries
    )
""")

# JSONB index for fast queries on nested data
cur.execute("CREATE INDEX idx_metadata ON events USING GIN(metadata)")

# Bulk insert
data = [(ts, json.dumps(meta), f'POINT({lon} {lat})') 
        for ts, meta, lon, lat in data_tuples]
execute_values(cur, 
    "INSERT INTO events (timestamp, metadata, location) VALUES %s", 
    data)
conn.commit()
```

## Scalability Red Flags

### ❌ Bad: N+1 Query Pattern

```python
# DON'T DO THIS - 1000 sensors = 1000 queries!
for sensor_id in sensor_ids:
    df = pd.read_sql(f"SELECT * FROM events WHERE sensor_id = '{sensor_id}'", conn)
    process(df)
```

### ✅ Good: Single Query with Group By

```python
# Do this - 1 query total
df = pd.read_sql("""
    SELECT sensor_id, AVG(value) as avg_value, COUNT(*) as count
    FROM events
    GROUP BY sensor_id
""", conn)
```

### ❌ Bad: Loading Entire Dataset to Filter

```python
# DON'T - Loads 10GB into memory to get 100 rows
df = pd.read_csv('huge_file.csv')
filtered = df[df['date'] > '2026-01-01']
```

### ✅ Good: Filter at Source

```python
# Do this - Let DuckDB/database handle filtering
df = duckdb.sql("""
    SELECT * FROM 'huge_file.csv' 
    WHERE date > '2026-01-01'
""").df()
```

## 48-Hour Implementation Heuristics

| Task | Time Estimate | Notes |
|------|---------------|-------|
| Setup SQLite + basic CRUD | 30 min | Fastest path to working storage |
| Setup Postgres (local) | 1 hour | Use Docker: `docker run postgres` |
| Setup Postgres (cloud) | 15 min | Supabase/Render free tier |
| Write basic ETL script | 2-4 hours | Depends on data source complexity |
| Add error handling & retry logic | 1-2 hours | Critical for API ingestion |
| Build data validation | 1 hour | Prevent bad data from breaking demo |
| Setup scheduled jobs (cron) | 30 min | On Unix: `crontab -e` |
| Implement caching layer (Redis) | 2 hours | For frequently accessed data |
| Create data visualization API | 2-4 hours | Flask/FastAPI + SQL queries |

**Critical path for most hackathons:** 
1. Hours 0-4: Get ANY data flowing end-to-end
2. Hours 4-8: Make it clean and validated
3. Hours 8-12: Add indexes and optimize slow queries
4. Hours 12+: Nice-to-haves (caching, monitoring)

## Architecture Decision Flowchart

```
START: How much data?
  │
  ├─ < 1GB ──→ Use Pandas + SQLite ──→ DONE (fastest path)
  │
  ├─ 1-50GB
  │   └─ Need SQL? 
  │       ├─ Yes ──→ DuckDB or Postgres
  │       └─ No ──→ Parquet files + Pandas chunks
  │
  └─ 50GB+
      └─ Is this a real requirement or demo theater?
          ├─ Real ──→ Spark (budget 8+ hours setup)
          └─ Theater ──→ Use 10GB sample + mention "scales to petabytes"
```

**Pro tip:** Judges rarely verify scale claims. A well-designed 1GB demo beats a broken "big data" system.