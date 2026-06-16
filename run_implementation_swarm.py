"""
Run the Implementation Swarm against a project proposal.

Takes a proposal markdown file (e.g., wattwatch-project-proposal.md) from the
Ideas Factory output and coordinates 4 specialists to build a working demo.

Usage:
    python run_implementation_swarm.py outputs/wattwatch-project-proposal.md
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path
from anthropic import Anthropic

PROPOSAL_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("outputs/wattwatch-project-proposal.md")
OUTPUT_DIR = Path("implementation")


def load_proposal() -> str:
    """Load the proposal markdown"""
    if not PROPOSAL_PATH.exists():
        raise SystemExit(f"Proposal not found: {PROPOSAL_PATH}")
    print(f"Loading proposal: {PROPOSAL_PATH}")
    return PROPOSAL_PATH.read_text()


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("Set ANTHROPIC_API_KEY before running.")

    if not Path(".implementation_coordinator_id").exists():
        raise SystemExit(
            "Run create_implementation_specialists.py, upload_implementation_skills.py, "
            "and create_implementation_coordinator.py first."
        )

    coordinator_id = Path(".implementation_coordinator_id").read_text().strip()
    environment_id = Path(".environment_id").read_text().strip()

    client = Anthropic()

    proposal = load_proposal()
    project_name = PROPOSAL_PATH.stem.replace("-project-proposal", "")

    print(f"\nStarting implementation session against Tech Lead {coordinator_id}...")
    print(f"Project: {project_name}")
    print(f"Output will be in: {OUTPUT_DIR / project_name}/\n")

    session = client.beta.sessions.create(
        agent=coordinator_id,
        environment_id=environment_id,
        title=f"Implementation — {project_name}",
    )
    Path(".last_implementation_session_id").write_text(session.id)

    user_message = (
        f"A project proposal has been approved by the Ideas Factory. "
        f"Coordinate the implementation team to build a working demo.\n\n"
        f"CRITICAL: You have 5-10 minutes TOTAL execution time. Work FAST.\n\n"
        f"Instructions:\n"
        f"1. Parse proposal: extract project name, tech stack, core architecture\n"
        f"2. Delegate to ALL 4 specialists IN PARALLEL:\n"
        f"   - Frontend Dev: React UI (3-4 min) - App.jsx + Dashboard + ONE chart\n"
        f"   - Backend Dev: FastAPI (4-5 min) - main.py + health check + core endpoints\n"
        f"   - DevOps: Deployment configs (2 min) - railway.toml + vercel.json + DEPLOYMENT.md\n"
        f"   - QA: Validation (2 min) - smoke_test.sh + QA_CHECKLIST.md\n"
        f"3. Coordinate integration: ensure Frontend API calls match Backend endpoints\n"
        f"4. Output to: ./implementation/{project_name}/\n\n"
        f"PRIORITIZE: Health check + ONE endpoint + ONE UI component = minimum viable demo\n\n"
        f"Proposal:\n\n{proposal}"
    )

    # Event logging for dashboard visualization
    events_log: list[dict] = []
    events_path = OUTPUT_DIR / "implementation-events.json"
    OUTPUT_DIR.mkdir(exist_ok=True)

    def log_event(event_type, agent, content=None, target=None):
        entry = {
            "timestamp": datetime.now().isoformat() + "Z",
            "type": event_type,
            "agent": agent,
            "layer": "implementation",
        }
        if content:
            entry["content"] = content
        if target:
            entry["target"] = target
        events_log.append(entry)
        events_path.write_text(json.dumps(events_log, indent=2))

    # Stream the events
    print("=== IMPLEMENTATION STREAM ===\n")
    final_text_parts: list[str] = []

    with client.beta.sessions.events.stream(session.id) as stream:
        client.beta.sessions.events.send(
            session.id,
            events=[{"type": "user.message", "content": [{"type": "text", "text": user_message}]}],
        )

        for event in stream:
            t = event.type
            if t == "session.thread_created":
                print(f"  [specialist spawned]   {event.agent_name}", flush=True)
                log_event("thread_spawned", event.agent_name)
            elif t == "session.thread_status_running":
                name = getattr(event, "agent_name", "?")
                print(f"  [working]              {name}", flush=True)
            elif t == "agent.thread_message_sent":
                print(f"  [delegate →]           {event.to_agent_name}", flush=True)
                log_event("delegate", "Tech Lead", target=event.to_agent_name)
            elif t == "agent.thread_message_received":
                print(f"  [complete ←]           {event.from_agent_name}", flush=True)
                log_event("reply", event.from_agent_name)
            elif t == "agent.message":
                for block in event.content:
                    if getattr(block, "type", None) == "text":
                        final_text_parts.append(block.text)
                        print(block.text, end="", flush=True)
                        log_event("message", getattr(event, "agent_name", "Tech Lead"), content=block.text)
            elif t == "agent.tool_use":
                tool_name = getattr(event, 'name', '?')
                print(f"  [tool: {tool_name}]", flush=True)
                log_event("tool_use", getattr(event, "agent_name", "?"), content=tool_name)
            elif t == "session.status_idle":
                print("\n\n[implementation finished]")
                log_event("complete", "system")
                break

    # Save transcript
    OUTPUT_DIR.mkdir(exist_ok=True)
    transcript_path = OUTPUT_DIR / f"{project_name}-transcript.txt"
    transcript_path.write_text("".join(final_text_parts))
    print(f"\nTranscript saved: {transcript_path}")

    # Check for generated files
    project_dir = OUTPUT_DIR / project_name
    if project_dir.exists():
        file_count = sum(1 for _ in project_dir.rglob('*') if _.is_file())
        print(f"\n✅ Implementation complete!")
        print(f"📁 Output directory: {project_dir}")
        print(f"📝 Files generated: {file_count}")
        print(f"\n🔗 View session: https://platform.claude.com/sessions/{session.id}")
    else:
        print(f"\n⚠️  No output directory created. Check transcript for issues.")
        print(f"🔗 View session: https://platform.claude.com/sessions/{session.id}")


if __name__ == "__main__":
    main()
