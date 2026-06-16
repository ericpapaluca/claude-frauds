# WattWatch Frontend

Energy anomaly detection dashboard for industrial facilities — "Waze for industrial energy waste."

## Setup

```bash
npm install
cp .env.example .env
# Edit .env: set VITE_API_URL to your backend
npm run dev
```

Open http://localhost:5173

## Stack

- **React 18** + **Vite 5** — fast dev server, instant HMR
- **Recharts** — power readings line chart with anomaly window highlight
- **Axios** — API client

## Features

- Live anomaly feed sorted by £ cost impact (refreshes every 15s)
- Urgency badges (HIGH / MED / LOW) with colour coding
- Work order panel with Claude-generated likely cause + action
- Power readings chart with baseline reference and anomaly window ReferenceArea
- One-click "Assign to Tech" with toast notification
- Stats bar: facilities monitored, active anomalies, daily CO₂ waste, daily £ waste
- Impact projection banner: year-1 CO₂ + cost savings across 100 facilities

## Build for Production

```bash
npm run build
npm run preview
```

## API

Expects backend at `VITE_API_URL` (default: http://localhost:8000).

Endpoints used:
- `GET /anomalies` — anomaly list (polled every 15s)
- `GET /anomalies/{id}` — full detail with readings for chart
- `GET /stats` — headline numbers
- `GET /impact/projection` — year-1 projection
- `POST /anomalies/{id}/assign` — assign technician
