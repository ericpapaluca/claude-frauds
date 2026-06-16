# Hackathon Challenge — Climate Tech IoT

**Organizer:** GreenTech Alliance  
**Theme:** Climate Tech & IoT Innovation  
**Duration:** 48 hours  
**Team size:** 2-4 people  
**Issued:** June 14, 2026  
**Submission deadline:** June 16, 2026 @ 5:00 PM PT

## Challenge Statement

Industrial facilities account for 30% of global carbon emissions, yet most lack real-time visibility into their energy consumption and emissions patterns. Existing solutions are expensive, require complex hardware installations, and provide limited actionable insights.

**Your challenge:** Build a solution that helps industrial facilities monitor, understand, and reduce their carbon footprint using IoT sensor data and AI-powered insights.

### The Problem

1. **Data fragmentation:** Sensor data lives in siloed systems (HVAC, machinery, utility meters)
2. **No real-time feedback:** Facility managers see emissions data weeks after the fact
3. **Lack of actionability:** Raw numbers don't translate to "what should we do now?"
4. **High barrier to entry:** Enterprise solutions cost $50K+ and take months to deploy

## Constraints

- **Tech stack:** No specific requirements, but must run on standard cloud infrastructure
- **Data sources:** Must work with simulated IoT sensor data (provided) or public datasets
- **Target users:** Facility managers, sustainability officers at industrial sites
- **Judging criteria:**
  - Impact potential (40%): Would this actually help reduce emissions?
  - Technical execution (30%): Does it work? Is the architecture sound?
  - Design/UX (20%): Is it usable by non-technical facility managers?
  - Pitch quality (10%): Can you articulate the value in 5 minutes?

## Resources Provided

### Available APIs & Datasets

1. **Simulated IoT Sensor API** (provided by organizers)
   - Endpoint: `https://api.greentech-hackathon.org/sensors`
   - Data: Temperature, power consumption, CO2 levels from 50 simulated facilities
   - Frequency: Real-time updates every 5 seconds
   - Format: JSON

2. **Carbon Intensity API** (public)
   - Endpoint: `https://api.carbonintensity.org.uk/`
   - Data: Grid carbon intensity by region (how "dirty" the electricity is)
   - Use case: Calculate actual carbon footprint, not just kWh

3. **Weather Data API** (OpenWeatherMap - free tier)
   - Understand correlation between weather and energy use
   - Predict heating/cooling needs

4. **Pre-trained ML Models** (HuggingFace)
   - Time-series forecasting models for energy prediction
   - Anomaly detection models for identifying waste

### Infrastructure Credits

- **$50 AWS credit** per team (EC2, S3, RDS)
- **$25 OpenAI API credit** (GPT-4, embeddings)
- **$25 Anthropic API credit** (Claude for data analysis/insights)
- **Free hosting:** Vercel, Railway, Render free tiers available

### Mentorship

- IoT specialists available Saturday 2-4 PM
- Climate science advisor available Sunday 10 AM-12 PM
- ML/AI mentors on-call via Slack

## Deliverables

### 1. Working Demo (REQUIRED)
- **Hosted application** (must be accessible via URL) OR
- **Local demo** (with clear setup instructions + video recording)
- Must demonstrate core functionality end-to-end

### 2. Pitch Presentation (5 minutes)
- Problem + solution (2 min)
- Live demo (2 min)
- Impact projection (1 min: "If 100 facilities used this, we'd reduce X tons of CO2")

### 3. GitHub Repository (REQUIRED)
- Clean README with:
  - What it does
  - How to run it
  - Tech stack
  - Team members
- Organized code (not one 500-line file)
- Environment variables documented

## Judging Criteria (Detailed)

### Impact Potential (40 points)

- **Measurable carbon reduction:** Does it help facilities actually reduce emissions?
- **Actionable insights:** Does it tell users what to DO, not just what IS?
- **Scalability:** Could this work for 10 facilities? 1000?
- **Cost to deploy:** Is it affordable for mid-size facilities ($50K budget)?

### Technical Execution (30 points)

- **Correctness:** Does it work? Are calculations accurate?
- **Architecture:** Clean separation of concerns, not spaghetti code
- **Data handling:** Proper storage, no obvious bottlenecks
- **Error handling:** Graceful degradation if API fails

### Design/UX (20 points)

- **Usability:** Can a non-technical facility manager use it?
- **Visualization:** Charts/graphs that make data intuitive
- **Mobile-friendly:** Bonus points for responsive design
- **Loading states:** No frozen screens during data fetching

### Pitch Quality (10 points)

- **Clarity:** Can you explain it in 30 seconds?
- **Confidence:** Do you believe in this solution?
- **Storytelling:** Did you make us care about the problem?

## Bonus Challenges (Optional)

- **Real-time alerts:** SMS/email when anomalies detected
- **Predictive maintenance:** "Your chiller is using 20% more power than normal - check it"
- **Peer comparison:** "Your facility uses 15% more energy than similar sites"
- **ROI calculator:** "Fixing these 3 issues saves $12K/year"
- **Multi-facility dashboard:** Manage 10+ sites in one view

## Constraints & Rules

### What's NOT Allowed

- Using existing commercial solutions (e.g., just embedding a Tableau dashboard)
- Fake data in the demo (must pull from provided API or public datasets)
- Claiming capabilities you didn't build ("In production, this would also...")

### What's Strongly Encouraged

- Using provided APIs and datasets (shows you can work with real-world constraints)
- Focusing on ONE use case deeply vs many use cases shallowly
- Building for 48 hours of work, not 48 weeks

### Intellectual Property

- You own what you build
- Open-source encouraged but not required
- Organizers may showcase winning projects (with permission)

## Example Use Cases (Inspiration, Not Requirements)

1. **Energy Waste Detective:** Real-time dashboard showing which machines are consuming power when they shouldn't be (e.g., HVAC running when building is empty)

2. **Carbon Budget Tracker:** Facility sets monthly carbon target, app shows "you have 5 tons left this month" and suggests optimizations

3. **Smart Scheduling Assistant:** AI analyzes when grid carbon intensity is lowest and suggests "run your furnace 2-4 AM when grid is 40% cleaner"

4. **Emissions Leaderboard:** Gamify sustainability—rank facilities by carbon efficiency, show how to move up

5. **Predictive Alerts:** ML model detects "your power consumption is spiking on hot days" and suggests "invest in better insulation"

## Timeline

**Friday 5 PM:** Kickoff, team formation, challenge reveal  
**Friday 6-8 PM:** Initial brainstorming, tech stack decisions  
**Friday 8 PM - Midnight:** Optional hacking (most teams grab dinner and plan)  

**Saturday 8 AM:** Venue opens, serious hacking begins  
**Saturday 2-4 PM:** IoT mentor office hours  
**Saturday 8 PM:** Optional pizza + team check-ins  
**Saturday Midnight:** Recommended sleep cutoff (you need rest for Sunday demo)  

**Sunday 8 AM:** Venue opens, final push begins  
**Sunday 10 AM-12 PM:** Climate advisor office hours  
**Sunday 2 PM:** Code freeze, deploy to production  
**Sunday 3 PM:** Presentation rehearsals  
**Sunday 4-6 PM:** Demos & judging  
**Sunday 6:30 PM:** Awards ceremony  

## FAQ

**Q: Can we use commercial APIs beyond the ones listed?**  
A: Yes, but stay within free tiers. Don't spend your own money.

**Q: Can we use a database?**  
A: Yes. Postgres, MongoDB, SQLite all fine. Supabase/PlanetScale free tiers recommended.

**Q: Do we need real IoT hardware?**  
A: No! Use the simulated sensor API we provide.

**Q: Can we pre-write code before Friday?**  
A: No. All code must be written during the 48-hour window. Using libraries/frameworks is fine.

**Q: What if our demo breaks during judging?**  
A: Have a backup video recording. Judges understand hackathon chaos.

**Q: Can we use AI assistants like GitHub Copilot?**  
A: Yes, coding assistants are allowed.

## Contact

- **Slack:** #climate-iot-hackathon  
- **Mentor on-call:** @mentor-bot in Slack  
- **Emergency:** hackathon@greentech alliance.org  

---

**Good luck! Build something that matters. 🌍**