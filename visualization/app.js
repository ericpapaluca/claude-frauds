// Hackathon Factory Pipeline — Real Session Data Dashboard

let allEvents = [];
let replaySpeed = 0; // 0 = instant, 1 = real-time, 5 = 5x
let livePolling = false;
let pollInterval = null;

// Agent name → chip element ID mapping
const agentChipMap = {
    'Data Engineering SME': 'agent-data',
    'AI Engineering SME': 'agent-ai',
    'Platform Engineering SME': 'agent-platform',
    'Security Engineering SME': 'agent-security',
    'Hackathon Lead Engineer': 'agent-coordinator',
    'Frontend Developer': 'agent-frontend',
    'Backend Developer': 'agent-backend',
    'DevOps Engineer': 'agent-devops',
    'QA Engineer': 'agent-qa',
    'Tech Lead': 'agent-techlead',
};

// Load events from JSON files
async function loadEvents() {
    const sources = [
        './hackathon-factory-events.json',
        './implementation-events.json',
    ];

    let events = [];
    let loadedFrom = [];

    for (const src of sources) {
        try {
            const resp = await fetch(src);
            if (resp.ok) {
                const data = await resp.json();
                events.push(...data);
                loadedFrom.push(src.split('/').pop());
            }
        } catch (e) {
            // File doesn't exist yet - that's fine
        }
    }

    document.getElementById('data-source').textContent =
        loadedFrom.length ? `Sources: ${loadedFrom.join(', ')}` : 'No event files found';
    document.getElementById('event-counter').textContent = `${events.length} events loaded`;

    return events;
}

// Render a single event as a message in the appropriate stream
function renderEvent(event) {
    const layer = event.layer;
    let streamId = 'ideas-messages';
    if (layer === 'implementation') streamId = 'impl-messages';

    const stream = document.getElementById(streamId);
    if (!stream) return;

    // Skip non-content events for display (thread_spawned handled via chip updates)
    if (event.type === 'thread_spawned') {
        updateAgentChip(event.agent, 'working');
        return;
    }

    if (event.type === 'complete') {
        if (layer === 'ideas-factory') {
            document.getElementById('ideas-status').textContent = 'complete';
            document.getElementById('ideas-status').className = 'layer-status done';
            setStage('consensus');
        } else {
            document.getElementById('impl-status').textContent = 'complete';
            document.getElementById('impl-status').className = 'layer-status done';
            setStage('complete');
            document.getElementById('complete-section').style.display = 'block';
        }
        return;
    }

    if (event.type === 'handoff') {
        document.getElementById('handoff').classList.add('active');
        setStage('handoff');
        // Also show as a special message
        const el = createMessageEl(event, true);
        stream.appendChild(el);
        stream.scrollTop = stream.scrollHeight;
        return;
    }

    // For delegate, reply, message events - render as message bubble
    if (!event.content && event.type !== 'delegate') return;

    const el = createMessageEl(event, false);
    stream.appendChild(el);
    stream.scrollTop = stream.scrollHeight;

    // Update agent chip statuses
    if (event.type === 'reply') {
        updateAgentChip(event.agent, 'done');
    }
    if (event.type === 'delegate') {
        updateAgentChip(event.target, 'working');
    }

    // Update layer status
    if (layer === 'ideas-factory') {
        document.getElementById('ideas-status').textContent = 'running';
        document.getElementById('ideas-status').className = 'layer-status active';
        setStage('ideation');
    } else if (layer === 'implementation') {
        document.getElementById('impl-status').textContent = 'running';
        document.getElementById('impl-status').className = 'layer-status active';
        setStage('build');
    }
}

// Create a message element
function createMessageEl(event, isSpecial) {
    const el = document.createElement('div');
    el.className = `msg ${event.type}${isSpecial ? ' handoff' : ''}`;
    el.setAttribute('data-agent', event.agent || '');

    const time = event.timestamp
        ? new Date(event.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
        : '';

    let agentLabel = '';
    if (event.type === 'delegate') {
        agentLabel = `<span class="from">${event.agent}</span><span class="arrow">→</span>${event.target}`;
    } else if (event.type === 'reply') {
        agentLabel = `<span class="from">${event.agent}</span><span class="arrow">→</span>Coordinator`;
    } else {
        agentLabel = `<span class="from">${event.agent || 'System'}</span>`;
    }

    const content = event.content || (event.type === 'delegate' ? `Delegating to ${event.target}...` : '');
    const displayContent = content.length > 1500 ? content.slice(0, 1500) + '\n\n[... truncated]' : content;

    el.innerHTML = `
        <div class="msg-header">
            <span class="msg-agents">${agentLabel}</span>
            <span class="msg-time">${time}</span>
        </div>
        <div class="msg-content">${escapeHtml(displayContent)}</div>
    `;

    return el;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Update agent chip status
function updateAgentChip(agentName, status) {
    // Try exact match first
    let chipId = agentChipMap[agentName];

    // Fuzzy match if exact fails
    if (!chipId) {
        for (const [name, id] of Object.entries(agentChipMap)) {
            if (agentName && (agentName.includes(name) || name.includes(agentName))) {
                chipId = id;
                break;
            }
        }
    }

    if (!chipId) return;

    const chip = document.getElementById(chipId);
    if (!chip) return;

    chip.classList.remove('working', 'done');
    chip.classList.add(status);
}

// Set progress stage
function setStage(stageName) {
    const stages = ['ideation', 'consensus', 'handoff', 'build', 'complete'];
    const idx = stages.indexOf(stageName);

    stages.forEach((s, i) => {
        const el = document.getElementById(`stage-${s}`);
        if (!el) return;
        el.classList.remove('active', 'completed');
        if (i < idx) el.classList.add('completed');
        if (i === idx) el.classList.add('active');
    });
}

// Replay events with timing
async function replayEvents(events, speed) {
    // Clear existing messages
    document.getElementById('ideas-messages').innerHTML = '';
    document.getElementById('impl-messages').innerHTML = '';
    resetChips();

    if (speed === 0) {
        // Instant: render all at once
        events.forEach(e => renderEvent(e));
        return;
    }

    // Timed replay
    for (let i = 0; i < events.length; i++) {
        renderEvent(events[i]);

        if (i < events.length - 1) {
            const curr = new Date(events[i].timestamp);
            const next = new Date(events[i + 1].timestamp);
            let gap = (next - curr) / speed;
            gap = Math.min(gap, 2000); // Cap at 2s
            gap = Math.max(gap, 50);   // Min 50ms
            await sleep(gap);
        }
    }
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function resetChips() {
    document.querySelectorAll('.agent-chip').forEach(chip => {
        chip.classList.remove('working', 'done');
    });
    document.getElementById('ideas-status').textContent = 'waiting';
    document.getElementById('ideas-status').className = 'layer-status';
    document.getElementById('impl-status').textContent = 'waiting';
    document.getElementById('impl-status').className = 'layer-status';
    document.getElementById('handoff').classList.remove('active');
    document.getElementById('complete-section').style.display = 'none';
    setStage('ideation');
}

// Live polling mode
function startLivePolling() {
    livePolling = true;
    let lastCount = 0;

    pollInterval = setInterval(async () => {
        const events = await loadEvents();
        if (events.length > lastCount) {
            // Render new events only
            const newEvents = events.slice(lastCount);
            newEvents.forEach(e => renderEvent(e));
            lastCount = events.length;
        }
    }, 2000);
}

function stopLivePolling() {
    livePolling = false;
    if (pollInterval) clearInterval(pollInterval);
}

// Button handlers
document.getElementById('btn-instant').addEventListener('click', async () => {
    setActiveButton('btn-instant');
    stopLivePolling();
    const events = await loadEvents();
    allEvents = events;
    await replayEvents(events, 0);
});

document.getElementById('btn-5x').addEventListener('click', async () => {
    setActiveButton('btn-5x');
    stopLivePolling();
    const events = await loadEvents();
    allEvents = events;
    await replayEvents(events, 5);
});

document.getElementById('btn-1x').addEventListener('click', async () => {
    setActiveButton('btn-1x');
    stopLivePolling();
    const events = await loadEvents();
    allEvents = events;
    await replayEvents(events, 1);
});

document.getElementById('btn-live').addEventListener('click', () => {
    setActiveButton('btn-live');
    resetChips();
    document.getElementById('ideas-messages').innerHTML = '';
    document.getElementById('impl-messages').innerHTML = '';
    startLivePolling();
});

function setActiveButton(id) {
    document.querySelectorAll('.speed-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(id).classList.add('active');
}

// Replay WattWatch button — loads SAVED data (not live symlinks)
document.getElementById('btn-replay').addEventListener('click', async () => {
    stopLivePolling();
    resetChips();
    document.getElementById('ideas-messages').innerHTML = '';
    document.getElementById('impl-messages').innerHTML = '';
    document.getElementById('complete-section').style.display = 'none';

    // Load saved WattWatch events from dedicated API endpoint
    let events = [];
    try {
        const resp = await fetch('/events/wattwatch');
        events = await resp.json();
    } catch(e) {}

    allEvents = events;

    if (events.length === 0) {
        document.getElementById('data-source').textContent = 'No saved WattWatch data found';
        return;
    }

    document.getElementById('data-source').textContent = `Replay: WattWatch (${events.length} events)`;
    document.getElementById('event-counter').textContent = `${events.length} events`;

    // Get current speed setting
    const activeBtn = document.querySelector('.speed-btn.active');
    let speed = 0;
    if (activeBtn?.id === 'btn-5x') speed = 5;
    if (activeBtn?.id === 'btn-1x') speed = 1;

    await replayEvents(events, speed);
});

// Generate New Idea button
document.getElementById('btn-generate').addEventListener('click', async () => {
    const btn = document.getElementById('btn-generate');

    if (btn.classList.contains('running')) return;

    btn.classList.add('running');
    btn.textContent = '⏳ Running pipeline...';

    // Clear existing state
    resetChips();
    document.getElementById('ideas-messages').innerHTML = '';
    document.getElementById('impl-messages').innerHTML = '';
    document.getElementById('complete-section').style.display = 'none';

    try {
        const resp = await fetch('/run', { method: 'POST' });
        const data = await resp.json();

        if (!data.ok) {
            btn.textContent = '❌ ' + data.message;
            btn.classList.remove('running');
            return;
        }

        // Switch to live polling mode
        setActiveButton('btn-live');
        startPipelinePolling(btn);

    } catch (e) {
        // If pipeline server isn't running, show helpful message
        btn.textContent = '⚠️ Start pipeline_server.py first';
        btn.classList.remove('running');
        setTimeout(() => {
            btn.textContent = '⚡ Generate New Idea';
        }, 3000);
    }
});

// Poll pipeline status and events during generation
function startPipelinePolling(btn) {
    let lastEventCount = 0;

    const poll = setInterval(async () => {
        try {
            // Check status
            const statusResp = await fetch('/status');
            const status = await statusResp.json();

            btn.textContent = `⏳ ${status.message}`;

            // Update layer statuses based on pipeline state
            if (status.state === 'running-ideas') {
                document.getElementById('ideas-status').textContent = 'running';
                document.getElementById('ideas-status').className = 'layer-status active';
                setStage('ideation');
            } else if (status.state === 'running-impl') {
                document.getElementById('ideas-status').textContent = 'complete';
                document.getElementById('ideas-status').className = 'layer-status done';
                document.getElementById('impl-status').textContent = 'running';
                document.getElementById('impl-status').className = 'layer-status active';
                document.getElementById('handoff').classList.add('active');
                setStage('build');
            }

            // Load events from API
            const eventsResp = await fetch('/events');
            const events = await eventsResp.json();

            if (events.length > lastEventCount) {
                const newEvents = events.slice(lastEventCount);
                newEvents.forEach(e => renderEvent(e));
                lastEventCount = events.length;
                document.getElementById('event-counter').textContent = `${events.length} events (live)`;
                document.getElementById('data-source').textContent = `Live: ${status.state}`;
            }

            // Check if done
            if (status.state === 'complete' || status.state === 'error') {
                clearInterval(poll);
                btn.classList.remove('running');

                if (status.state === 'complete') {
                    btn.textContent = '⚡ Generate New Idea';
                    document.getElementById('complete-section').style.display = 'block';
                    document.getElementById('impl-status').textContent = 'complete';
                    document.getElementById('impl-status').className = 'layer-status done';
                    setStage('complete');
                } else {
                    btn.textContent = '❌ ' + status.message;
                    setTimeout(() => { btn.textContent = '⚡ Generate New Idea'; }, 5000);
                }
            }
        } catch (e) {
            // Server might not be ready yet, keep polling
        }
    }, 2000);
}

// Start clean — no auto-load
