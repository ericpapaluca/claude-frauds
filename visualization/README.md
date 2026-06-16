# Multi-Agent Hackathon Factory Pipeline Visualization

Interactive web dashboard showing both specialist swarm layers in action.

## Features

- **Two-layer architecture view**: Ideas Factory → Implementation Swarm
- **Live status indicators**: Watch specialists work in real-time
- **Event log**: Track all delegation and completion events
- **Animated data flow**: See proposals flowing from Layer 1 to Layer 2
- **Responsive design**: Works on desktop and mobile

## Quick Start

```bash
cd visualization
python -m http.server 8000
```

Then open: **http://localhost:8000**

## What You'll See

### Layer 1: Ideas Factory
- **Coordinator**: Hackathon Lead Engineer (Opus 4.7)
- **4 Specialists**: Data, AI, Platform, Security engineering SMEs
- **Output**: Project proposal markdown (e.g., `wattwatch-project-proposal.md`)

### Data Flow
- Animated visualization showing proposal flowing from Layer 1 → Layer 2

### Layer 2: Implementation Swarm
- **Coordinator**: Tech Lead (Opus 4.7)
- **4 Specialists**: Frontend, Backend, DevOps, QA engineers
- **Time Budget**: 5-10 minutes total execution time
- **Output**: Working demo codebase (frontend/ + backend/ + configs)

### Event Log
- Real-time events showing:
  - Specialist spawning
  - Work delegation
  - Progress updates
  - Completion notifications

## Controls

- **🔄 Refresh**: Restart the simulation
- **📊 Toggle View**: Switch between normal/compact view
- **Clear**: Clear the event log
- **Auto-scroll**: Keep log scrolled to latest (checkbox)

## Architecture

Pure HTML/CSS/JavaScript - no build step required!

- `index.html` - Dashboard structure
- `styles.css` - Styling and animations
- `app.js` - Simulation logic and event handling

## Simulation Flow

1. **Layer 1 starts**: Coordinator brainstorms 3 ideas
2. **Specialists evaluate**: All 4 specialists rank ideas in parallel
3. **Idea selected**: Based on specialist rankings
4. **Proposal generated**: 377-line markdown document
5. **Layer 2 starts**: Tech Lead parses proposal
6. **Implementation begins**: 4 specialists generate code in parallel
7. **Integration validated**: Coordinator ensures everything fits
8. **Demo complete**: Deployable codebase ready

## Live Data Integration (Future)

To connect to real Claude session data:

1. Update `app.js` to fetch from Claude Console API
2. Add session IDs for Layer 1 and Layer 2
3. Poll for events and update status indicators
4. Display actual specialist outputs

Example:
```javascript
async function fetchSessionEvents(sessionId) {
    const response = await fetch(`https://api.claude.com/sessions/${sessionId}/events`);
    const events = await response.json();
    // Update UI based on events
}
```

## Customization

### Change Colors
Edit `styles.css`:
- Layer 1 color: `#667eea` (purple)
- Layer 2 color: `#11998e` (teal)

### Adjust Timing
Edit `app.js` simulation timeouts to speed up/slow down

### Add Specialists
Add more cards to the `.specialists-grid` in `index.html`

## Tech Stack

- **HTML5** - Structure
- **CSS3** - Styling (Grid, Flexbox, Animations)
- **Vanilla JavaScript** - Interactivity (no frameworks!)

## Browser Compatibility

- Chrome/Edge: ✅
- Firefox: ✅
- Safari: ✅
- Mobile browsers: ✅

## Screenshots

### Desktop View
Two swarm layers side-by-side with animated data flow

### Mobile View
Stacked layout with touch-friendly controls

## Credits

Built for the Multi-Agent Hackathon Factory project  
Claude Managed Agents API | Anthropic
