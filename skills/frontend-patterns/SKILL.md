---
name: frontend-patterns
description: React frontend patterns for rapid hackathon implementation. Use when building UI components, API integration, or deployment configs. Covers Vite setup, component patterns, state management, chart libraries, and one-command deployment.
---

# Frontend Patterns for Rapid Implementation

## Vite React Project Scaffold (5 min setup)

```bash
npm create vite@latest my-app -- --template react
cd my-app
npm install
```

**Folder structure:**
```
src/
├── App.jsx              # Main app component
├── main.jsx             # Entry point
├── components/          # Reusable UI components
│   ├── Dashboard.jsx
│   ├── Chart.jsx
│   └── Card.jsx
├── hooks/               # Custom React hooks
│   └── useApi.js        # API fetching hook
├── services/            # API clients
│   └── api.js           # Backend API wrapper
└── styles/              # CSS files
    └── App.css
```

## package.json Template

```json
{
  "name": "hackathon-demo",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "recharts": "^2.10.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.0.8"
  }
}
```

## API Integration Pattern

**services/api.js** - Reusable API client with error handling:

```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function fetchWithErrorHandling(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    throw error;
  }
}

// Usage examples:
export const getAnomalies = () => fetchWithErrorHandling('/api/anomalies');
export const getWorkOrders = () => fetchWithErrorHandling('/api/work-orders');
export const getFacilities = () => fetchWithErrorHandling('/api/facilities');
```

## Custom Hook for API Calls

**hooks/useApi.js**:

```javascript
import { useState, useEffect } from 'react';

export function useApi(fetchFn, dependencies = []) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;
    
    async function loadData() {
      try {
        setLoading(true);
        const result = await fetchFn();
        if (mounted) {
          setData(result);
          setError(null);
        }
      } catch (err) {
        if (mounted) {
          setError(err.message);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }
    
    loadData();
    return () => { mounted = false; };
  }, dependencies);

  return { data, loading, error };
}

// Usage in component:
// const { data: anomalies, loading, error } = useApi(getAnomalies, []);
```

## Recharts Integration

**Simple line chart component:**

```javascript
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export function PowerChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="timestamp" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="power_kw" stroke="#8884d8" />
      </LineChart>
    </ResponsiveContainer>
  );
}

// Usage:
// <PowerChart data={[{timestamp: '10:00', power_kw: 150}, ...]} />
```

## Simple Dashboard Layout

```javascript
import { useState, useEffect } from 'react';
import { useApi } from './hooks/useApi';
import { getAnomalies, getFacilities } from './services/api';

function App() {
  const { data: anomalies, loading, error } = useApi(getAnomalies);
  
  if (loading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">Error: {error}</div>;
  
  return (
    <div className="app">
      <header>
        <h1>WattWatch Dashboard</h1>
      </header>
      
      <main className="dashboard">
        <section className="anomalies">
          <h2>Active Anomalies</h2>
          {anomalies?.map(anomaly => (
            <div key={anomaly.id} className="card">
              <h3>{anomaly.title}</h3>
              <p>{anomaly.description}</p>
              <span className="impact">${anomaly.cost_impact}/day</span>
            </div>
          ))}
        </section>
      </main>
    </div>
  );
}

export default App;
```

## Environment Variables

**.env.example**:
```
VITE_API_URL=http://localhost:8000
VITE_ANTHROPIC_API_KEY=your-key-here
```

**Access in code:**
```javascript
const apiUrl = import.meta.env.VITE_API_URL;
```

## Basic Styling (App.css)

```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: system-ui, -apple-system, sans-serif;
  background: #f5f5f5;
}

.app {
  min-height: 100vh;
}

header {
  background: #2c3e50;
  color: white;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.dashboard {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 1rem;
}

.card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.loading, .error {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
}

.error {
  color: #e74c3c;
}

/* Responsive */
@media (max-width: 768px) {
  .dashboard {
    padding: 0 0.5rem;
  }
}
```

## Deployment to Vercel

**One command:**
```bash
npm run build
npx vercel --prod
```

**vercel.json** (optional config):
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "env": {
    "VITE_API_URL": "@api_url"
  }
}
```

## Quick Wins for Demos

1. **Loading states** - Always show "Loading..." while fetching
2. **Error boundaries** - Catch errors gracefully
3. **Responsive design** - Works on mobile (judges test this)
4. **Fast load** - Vite's HMR makes development instant
5. **Real data** - Connect to backend API early

## README.md Template

```markdown
# Project Name

Demo dashboard for [hackathon name].

## Setup

\`\`\`bash
npm install
cp .env.example .env
# Edit .env with your API keys
npm run dev
\`\`\`

Open http://localhost:5173

## Build for Production

\`\`\`bash
npm run build
npm run preview
\`\`\`

## Deploy

\`\`\`bash
npx vercel --prod
\`\`\`
```

## Time Budget (5-10 minute implementation)

- **Minute 1-2:** Scaffold with Vite, install dependencies
- **Minute 3-5:** Create main components (Dashboard, Chart, Card)
- **Minute 6-7:** API integration (services/api.js, hooks/useApi.js)
- **Minute 8-9:** Basic styling, test with mock data
- **Minute 10:** Connect to backend, verify data flow

**Critical path:** API integration → Main dashboard → One chart/visualization → Deploy config