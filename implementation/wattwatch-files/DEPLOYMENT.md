# WattWatch — Deployment Guide

> Backend → Railway | Frontend → Vercel (both free tier)

---

## Prerequisites

- [ ] Code pushed to a **GitHub repository**
- [ ] [Railway](https://railway.app) account (free tier OK)
- [ ] [Vercel](https://vercel.com) account (free tier OK)

---

## Local Development

### 1. Start the backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # fill in any required values
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Backend runs at **http://localhost:8000** — API docs at http://localhost:8000/docs.

### 2. Start the frontend

```bash
cd frontend
npm install
cp .env.example .env.local    # VITE_API_URL=http://localhost:8000 (default)
npm run dev
```

Frontend runs at **http://localhost:5173**.

---

## Deploy Backend to Railway

### Step 1 — Push code to GitHub

```bash
git add .
git commit -m "feat: wattwatch initial commit"
git push origin main
```

### Step 2 — Create a new Railway project

1. Log in at https://railway.app
2. Click **New Project → Deploy from GitHub repo**
3. Select your repository

### Step 3 — Set root directory

In the Railway project settings → **Source** → set **Root Directory** to `backend`.

Railway will use `railway.toml` (already in the repo root) for build and deploy config.

### Step 4 — Railway auto-detects Python via nixpacks

`backend/nixpacks.toml` pins Python 3.11 and runs `pip install -r requirements.txt` automatically. No manual build command needed.

### Step 5 — Add environment variables

In the Railway service → **Variables** tab, add:

| Variable | Value |
|---|---|
| `ENVIRONMENT` | `production` |
| `CORS_ORIGINS` | *(your Vercel URL — add after frontend deploy)* |
| `SENSOR_API_KEY` | *(if applicable)* |
| `ANTHROPIC_API_KEY` | *(if applicable)* |

See `backend/.env.example` for the full list.

### Step 6 — Deploy

Railway triggers a deploy automatically on each push. You can also click **Deploy Now** in the dashboard.

Once the deploy turns green, click **Settings → Networking → Generate Domain** to get your public URL.

### Step 7 — Verify the health check

```bash
curl https://YOUR-APP.railway.app/health
# Expected: {"status": "ok", ...}
```

---

## Deploy Frontend to Vercel

### Step 1 — Create a new Vercel project

1. Log in at https://vercel.com
2. Click **Add New → Project**
3. Import the same GitHub repository

### Step 2 — Set root directory

In the Vercel project wizard → **Root Directory** → type `frontend` → confirm.

### Step 3 — Framework preset

Vercel should auto-detect **Vite**. If not, select **Vite** from the framework dropdown.

- Build Command: `npm run build`
- Output Directory: `dist`
- Install Command: `npm install`

(`vercel.json` in the repo encodes these settings, so they may already be populated.)

### Step 4 — Add environment variable

| Variable | Value |
|---|---|
| `VITE_API_URL` | `https://YOUR-APP.railway.app` |

> **Important:** Use the Railway URL from Step 6 above. Do **not** include a trailing slash.

### Step 5 — Deploy

Click **Deploy**. Vercel builds the Vite app and serves it globally via its CDN.

### Step 6 — Verify

Open your Vercel URL in a browser. The dashboard should load and display data fetched from the Railway backend.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Browser shows CORS error | Backend `CORS_ORIGINS` doesn't include Vercel URL | Update `CORS_ORIGINS` in Railway variables and redeploy |
| Env vars not picked up on Vercel | Vercel bakes `VITE_*` vars at build time | Add/update env var in Vercel dashboard → **Redeploy** (not just refresh) |
| Railway health check fails | `/health` endpoint not responding within 100 s | Check Railway build logs; ensure `requirements.txt` installs correctly and `main.py` exports `app` |
| Frontend shows blank page | SPA routing issue or wrong output dir | Confirm `vercel.json` rewrite rule is present and `outputDirectory` is `dist` |
| Cold start slow (~5–10 s) | Railway free tier spins down after inactivity | First request after idle is slow — expected on free tier |

---

## Smoke Test

Run the included smoke test script after both services are live:

```bash
chmod +x smoke_test.sh
./smoke_test.sh https://YOUR-APP.railway.app https://YOUR-FRONTEND.vercel.app
```

See `./smoke_test.sh` for details on what is verified.
