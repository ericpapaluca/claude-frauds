"""
Run the Hackathon Ideas Factory against a challenge brief.

Inlines the challenge + past wins + available APIs into the user message.
Streams events as they come in so you can watch the parallel specialist
deliberation—this is the demo, narrate it live.

Saves the final transcript and deliverables to outputs/.

Usage:
    python run_hackathon_factory.py
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

from anthropic import Anthropic


CHALLENGE_PATH = Path("synthetic-data/hackathon-challenge-climate-iot.md")
SUPPORTING_FILES = [
    Path("synthetic-data/past-hackathon-wins.json"),
    Path("synthetic-data/available-apis-and-datasets.md"),
]
OUTPUT_DIR = Path("outputs")


def load_inputs_as_context() -> str:
    blocks = []
    for path in [CHALLENGE_PATH, *SUPPORTING_FILES]:
        if not path.exists():
            print(f"  WARNING: {path} missing — skipping")
            continue
        print(f"  including {path.name}")
        blocks.append(f"=====  DOCUMENT: {path.name}  =====\n{path.read_text()}")
    return "\n\n".join(blocks)


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("Set ANTHROPIC_API_KEY before running.")

    if not Path(".coordinator_id").exists() or not Path(".environment_id").exists():
        raise SystemExit(
            "Missing .coordinator_id or .environment_id. Run "
            "create_specialists.py, upload_skills.py, then create_coordinator.py first."
        )

    coordinator_id = Path(".coordinator_id").read_text().strip()
    environment_id = Path(".environment_id").read_text().strip()

    client = Anthropic()

    print("Loading hackathon challenge + supporting docs...")
    context = load_inputs_as_context()

    print(f"\nStarting session against coordinator {coordinator_id}...")
    session = client.beta.sessions.create(
        agent=coordinator_id,
        environment_id=environment_id,
        title="Hackathon Ideas Factory — Climate Tech Challenge",
    )
    Path(".last_session_id").write_text(session.id)

    user_message = (
        "A hackathon challenge has just been posted. Please run the Ideas Factory process:\n"
        "1. Read the challenge yourself. Understand the problem, constraints, and judging criteria.\n"
        "2. Brainstorm 2-3 promising project ideas that address the challenge.\n"
        "3. Delegate ALL ideas to ALL FOUR engineering specialists in parallel. "
        "Each specialist evaluates every idea comparatively.\n"
        "4. Synthesize their assessments and select the strongest idea "
        "(or iterate if all have critical blockers).\n"
        "5. Produce a complete project proposal with implementation plan as a structured markdown document.\n\n"
        "Specialists have domain-specific skills attached (data engineering, AI/ML, platform, security). "
        "Focus on ideas that are demo-able in 48 hours by a 2-4 person team.\n\n"
        + ("HARD CONSTRAINT — READ THIS FIRST:\n"
           "The following ideas have ALREADY BEEN BUILT and are BANNED. "
           "You MUST NOT propose any of these or variations of them:\n"
           "- WattWatch (energy anomaly detection + work orders) — BANNED\n"
           "- CarbonPilot (grid-aware load shifting) — BANNED\n"
           "- Carbon Co-Pilot (conversational facility advisor) — BANNED\n"
           "- Any anomaly detection dashboard — BANNED\n"
           "- Any load-shifting/scheduling tool — BANNED\n\n"
           "You must propose 3 NOVEL ideas from completely different angles. "
           "Examples of fresh directions (pick your own, don't copy these either):\n"
           "- Gamification / carbon leaderboards between facilities\n"
           "- Supply chain carbon footprint tracking\n"
           "- Digital twin simulation\n"
           "- Predictive maintenance for carbon-heavy equipment\n"
           "- Employee engagement / behavior nudging\n"
           "- Carbon credit marketplace\n\n"
           "If ANY of your 3 ideas resembles WattWatch or CarbonPilot, "
           "the entire submission is DISQUALIFIED.\n\n" if "--fresh" in sys.argv else "")
        + f"{context}"
    )

    # Event logging for dashboard visualization
    events_log: list[dict] = []
    # Write to live file if --fresh, otherwise main file
    events_filename = "live-factory-events.json" if "--fresh" in sys.argv else "hackathon-factory-events.json"
    events_path = OUTPUT_DIR / events_filename
    OUTPUT_DIR.mkdir(exist_ok=True)

    def log_event(event_type, agent, content=None, target=None):
        entry = {
            "timestamp": datetime.now().isoformat() + "Z",
            "type": event_type,
            "agent": agent,
            "layer": "ideas-factory",
        }
        if content:
            entry["content"] = content
        if target:
            entry["target"] = target
        events_log.append(entry)
        events_path.write_text(json.dumps(events_log, indent=2))

    # Stream the events — this is the demo. Watch for parallel thread spawns.
    print("\n=== EVENT STREAM (this is the demo) ===\n")
    final_text_parts: list[str] = []

    with client.beta.sessions.events.stream(session.id) as stream:
        client.beta.sessions.events.send(
            session.id,
            events=[
                {
                    "type": "user.message",
                    "content": [{"type": "text", "text": user_message}],
                }
            ],
        )
        for event in stream:
            t = event.type
            if t == "session.thread_created":
                print(f"  [thread spawned]   {event.agent_name}", flush=True)
                log_event("thread_spawned", event.agent_name)
            elif t == "session.thread_status_running":
                name = getattr(event, "agent_name", "?")
                print(f"  [thread running]   {name}", flush=True)
            elif t == "agent.thread_message_received":
                print(f"  [reply ←]          {event.from_agent_name}", flush=True)
                log_event("reply", event.from_agent_name)
            elif t == "agent.thread_message_sent":
                print(f"  [delegate →]       {event.to_agent_name}", flush=True)
                log_event("delegate", "Hackathon Lead Engineer", target=event.to_agent_name)
            elif t == "agent.message":
                for block in event.content:
                    if getattr(block, "type", None) == "text":
                        final_text_parts.append(block.text)
                        print(block.text, end="", flush=True)
                        log_event("message", getattr(event, "agent_name", "Coordinator"), content=block.text)
            elif t == "agent.tool_use":
                print(f"\n  [tool: {getattr(event, 'name', '?')}]", flush=True)
                log_event("tool_use", getattr(event, "agent_name", "?"), content=getattr(event, "name", "unknown"))
            elif t == "session.status_idle":
                print("\n\n[swarm finished]")
                log_event("complete", "system")
                break

    # Write handoff event linking to implementation
    log_event("handoff", "Hackathon Lead Engineer", content="Proposal ready for implementation")

    OUTPUT_DIR.mkdir(exist_ok=True)
    transcript_path = OUTPUT_DIR / "hackathon-factory-transcript.txt"
    transcript_path.write_text("".join(final_text_parts))
    print(f"\nHackathon Factory transcript saved to {transcript_path}")

    # Pull every file the agents produced in the container
    print("\nDownloading deliverables from the session container...")
    files = client.beta.files.list(
        scope_id=session.id,
        betas=["managed-agents-2026-04-01"],
    )
    file_count = 0
    for f in files.data:
        out_path = OUTPUT_DIR / f.filename
        print(f"  {f.filename}  ->  {out_path}")
        content = client.beta.files.download(f.id)
        content.write_to_file(str(out_path))
        file_count += 1

    if file_count == 0:
        print("  (no files found — agents may have produced text-only output)")
    else:
        print(f"\nDownloaded {file_count} file(s) to {OUTPUT_DIR}/")

    print(f"\nView the full session (including all sub-agent threads) at:")
    print(f"  https://platform.claude.com/sessions/{session.id}")


if __name__ == "__main__":
    main()
