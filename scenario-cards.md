# Scenario Cards — Hackathon Ideas Factory

Each scenario represents a different hackathon theme. Each is shaped like real engineering work: a lead engineer orchestrates and 4 domain specialists own their lanes.

---

## Card A — Climate Tech IoT (default scenario, fully wired in starter code)

**Coordinator:** "Hackathon Lead Engineer"
- Reads the hackathon challenge
- Brainstorms 2-3 project ideas
- Routes all ideas to specialists for comparative evaluation
- Synthesizes assessments into a complete implementation plan

**Specialists:**
1. **Data Engineering SME** (skill: data-engineering-patterns) — evaluates data architecture, pipeline feasibility, scalability
2. **AI Engineering SME** (skill: ai-engineering-playbook) — assesses ML/AI components, model selection, integration complexity
3. **Platform Engineering SME** (skill: platform-architecture-guide) — reviews infrastructure, deployment strategy, operational feasibility
4. **Security Engineering SME** (skill: security-checklist) — identifies security risks, compliance issues, quick wins

**The trigger:** `synthetic-data/hackathon-challenge-climate-iot.md` (a 48-hour challenge to build carbon footprint monitoring for industrial facilities)

**The deliverable:** A structured markdown implementation plan at `outputs/[Idea-Name]-Proposal.md` with:
- Executive summary
- Technical architecture (data + AI + platform + security)
- Phased implementation plan (Hours 0-12, 12-24, 24-36, 36-48)
- Resource requirements and cost estimates
- Risk assessment and demo strategy

---

## Card B — FinTech Innovation (alternative scenario)

**Coordinator:** "Hackathon Lead Engineer"
- Reads the hackathon challenge
- Brainstorms 2-3 project ideas
- Routes all ideas to specialists for evaluation
- Produces implementation plan

**Specialists:**
1. **Data Engineering SME** — evaluates financial data pipelines, real-time processing
2. **AI Engineering SME** — assesses fraud detection, credit scoring, personalization ML
3. **Platform Engineering SME** — reviews API design, payment integration, scalability
4. **Security Engineering SME** — identifies PCI-DSS compliance, fraud prevention, auth security

**The trigger:** A synthetic FinTech challenge (you'll need to create `hackathon-challenge-fintech.md`)

**The deliverable:** Implementation plan markdown with focus on compliance and security

---

## Card C — Healthcare Tech (alternative scenario)

**Coordinator:** "Hackathon Lead Engineer"
- Reads the hackathon challenge
- Brainstorms 2-3 project ideas
- Routes all ideas to specialists for evaluation
- Produces implementation plan

**Specialists:**
1. **Data Engineering SME** — evaluates patient data pipelines, FHIR integration, time-series health metrics
2. **AI Engineering SME** — assesses diagnostic AI, patient risk prediction, NLP for medical records
3. **Platform Engineering SME** — reviews telehealth infrastructure, EMR integration, mobile app deployment
4. **Security Engineering SME** — identifies HIPAA compliance, PHI protection, access controls

**The trigger:** A synthetic Healthcare challenge (you'll need to create `hackathon-challenge-healthtech.md`)

**The deliverable:** Implementation plan markdown with heavy focus on compliance and patient privacy

---

## Picking guidance

| If your team is... | Pick |
| --- | --- |
| Just want the cleanest path | A (Climate Tech IoT — code is ready) |
| Working on FinTech products | B (FinTech — requires custom challenge file) |
| Working on Healthcare products | C (Healthcare — requires custom challenge file) |
