# WattWatch QA Checklist

## 🚀 Pre-Demo Smoke Test (5 min before pitch)

Run: `./smoke_test.sh` or `API_URL=https://wattwatch-api.railway.app ./smoke_test.sh`

- [ ] Backend health check returns 200 with `"status":"ok"`
- [ ] Frontend loads at production URL within 3 seconds
- [ ] Frontend successfully fetches `/facilities` (check Network tab)
- [ ] At least 8 anomalies visible in the feed
- [ ] Clicking an anomaly opens the work order panel
- [ ] Work order panel shows: **title**, **likely cause**, **action**, **£ impact**, **kg CO2 impact**
- [ ] LineChart renders with readings data (power_kw over time)
- [ ] "Assign to Tech" button shows confirmation toast after click
- [ ] Impact projection shows >0 tons CO2 / >£0 cost savings
- [ ] No console errors in browser DevTools (F12)

---

## 🎬 Live Demo Flow Validation (per demo script)

**5-Minute Pitch Structure:**
- [ ] **Hook (0:00-0:30):** "Factory leaving lights on between 2-4 AM..." — practiced and smooth
- [ ] **Persona (0:30-1:30):** Maria's story + problem statement delivered in <60s
- [ ] **Transition (1:30-1:45):** Tagline "Waze for industrial energy waste" shown on slide
- [ ] **Live Demo (1:45-3:45):** Fits entire demo in 2-minute window

**Magic Moments (must nail these):**
- [ ] **Moment 1:** Facility map or list shows pulsing red anomaly indicators
- [ ] **Moment 2:** Click anomaly → work order panel slides in with Claude-generated title, cause, action, £ + kg CO2 numbers
- [ ] **Moment 3:** Click "Assign to Tech" → toast confirms assignment, anomaly status updates
- [ ] **Moment 4:** Impact projection refreshes to show aggregate savings

**Timing & Responsiveness:**
- [ ] Live demo runs end-to-end in <2 minutes (with no stalls)
- [ ] API latency <500ms per call (check Network tab)
- [ ] Mobile view is responsive (test on iPhone/Android or DevTools)

---

## 🔌 API Contract Validation (Frontend ↔ Backend)

**Contract Match:**
- [ ] Frontend `getFacilities()` returns array of: `{id, name, region, lat, lng, status, current_power_kw}`
- [ ] Frontend `getAnomalies()` receives array with embedded `work_order` object
  - [ ] `work_order.title` present (string, ~5-15 words)
  - [ ] `work_order.likely_cause` present (string)
  - [ ] `work_order.action` present (string)
  - [ ] `work_order.urgency` present (enum: high/medium/low)
  - [ ] `work_order.co2_impact_kg_per_day` present (number, positive)
  - [ ] `work_order.cost_impact_gbp_per_day` present (number, positive)
- [ ] Frontend `getFacility(id)` reads `readings` array with `{timestamp, power_kw}`
- [ ] Frontend `assignAnomaly(id)` POSTs to `/anomalies/{id}/assign` and receives `{status, assigned_at}`
- [ ] Frontend `getStats()` reads `{facilities_total, anomalies_total, resolved_count}`
- [ ] Frontend `getImpactProjection()` reads `{total_co2_kg, total_cost_gbp, projection_100_facilities}`

**Environment Variable Check:**
- [ ] `VITE_API_URL` env var in Vercel points to Railway backend (e.g., `https://wattwatch-api.railway.app`)
- [ ] No `localhost` URLs in production build
- [ ] Dev environment uses `http://localhost:8000` for local testing

---

## 🛡️ Failure Mode Checks

**Graceful Degradation:**
- [ ] If backend is slow (>2s), frontend shows loading spinner (not frozen)
- [ ] If backend returns 500, frontend displays error message (not white screen)
- [ ] If API call fails, error boundary catches it (no JavaScript crash)
- [ ] Backup demo video recorded and accessible in pitch materials (hidden contingency)

**Seeded Data & Reliability:**
- [ ] Pre-seeded hero anomalies visible on first load (no polling required)
- [ ] DEMO_MODE flag tested (if implemented): ensures consistent data for replay
- [ ] Database seed script documented in README

**Network Conditions:**
- [ ] Tested on slow 3G (DevTools throttle): still usable <5s load time
- [ ] Tested on zero connection: graceful error message shown
- [ ] Tested with backend offline: frontend handles 503 cleanly

---

## 📊 Impact Numbers Sanity Check

**Per-Anomaly Realism:**
- [ ] Each anomaly `cost_impact_gbp_per_day` is between **£50–£5,000/day** (realistic for industrial waste)
- [ ] Each anomaly `co2_impact_kg_per_day` is between **5–200 kg CO2/day**
- [ ] Numbers align with facility size (large facility → larger impact)
- [ ] No anomalies show £0 or 0 kg (always actionable)

**Projection Numbers:**
- [ ] `/impact/projection` `total_cost_gbp` scales sensibly with anomaly count
  - Example: 10 anomalies × £500 avg = £5,000/day total → £1.8M/year
- [ ] `projection_100_facilities` multiplies current by realistic factor (10–100×)
- [ ] Numbers are cited in the pitch slide (credibility via data)

---

## 🎤 Pitch Quality (Judges' View)

**Narrative Arc:**
- [ ] Hook is memorable: "Factory leaving lights on between 2–4 AM..." (concrete, relatable)
- [ ] Persona (Maria) is sympathetic: overworked, lacks visibility into energy waste
- [ ] Problem-solution flow is clear: "No one sees it" → "WattWatch detects it" → "Work orders fix it"
- [ ] Call-to-action: "Join us in preventing industrial energy waste"

**Slide Deck Integration:**
- [ ] Title slide: "WattWatch" + tagline visible
- [ ] Problem slide: Factory image + Maria quote
- [ ] Solution slide: Product screenshot or diagram
- [ ] Impact slide: Real numbers from `/impact/projection` (e.g., "£1.8M annual savings across 100 facilities")
- [ ] Call-to-action slide: Clear next step

**Delivery:**
- [ ] Practiced minimum 3 full rehearsals (pitch + live demo together)
- [ ] Timing is 4:50–5:00 (pitch + demo, no rush, no stall)
- [ ] Eye contact + confident delivery
- [ ] No filler words ("um," "uh") during demo

---

## 🚨 Known Limitations (Be Transparent)

- [ ] **Synthetic Data:** Demo uses seeded/mock sensor data. Real integration via IoT gateways documented in roadmap.
- [ ] **Single-Tenant:** v1 is single-facility per instance. Multi-tenant auth on roadmap.
- [ ] **No SMS/Email:** Work orders stay in-app by design (security). SMS notifications are opt-in Phase 2.
- [ ] **Demo Mode:** Some anomalies are deterministic for demo replay. Polling worker in production runs continuously.
- [ ] **Auth:** v1 uses API key in header. OAuth2 coming in v1.1.

**Judges' Expectation:** These are honest, not apologetic. Show awareness + roadmap.

---

## ✅ Sign-Off Checklist (QA Lead)

- [ ] smoke_test.sh runs to completion with 8/8 or 7/8 pass
- [ ] All critical API endpoints tested (health, facilities, anomalies, assign, stats, projection)
- [ ] Frontend loads and displays data within 3s
- [ ] No CORS or API URL errors in console
- [ ] Work order structure matches API contract exactly
- [ ] Impact numbers are plausible and aligned with proposal
- [ ] Pitch narrative is practiced and smooth
- [ ] Backup demo or recording available
- [ ] All env vars set correctly in both backend (Railway) and frontend (Vercel)

**Status:** ☐ READY TO DEMO | ☐ NEEDS FIXES

**Blocker Notes (if any):**
```
[Document any critical issues found]
```

---

**Last Updated:** 2 minutes before pitch  
**Tested By:** QA Lead  
**Backend URL:** (fill in: http://localhost:8000 or Railway URL)  
**Frontend URL:** (fill in: http://localhost:5173 or Vercel URL)
