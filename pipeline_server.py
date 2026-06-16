"""
Pipeline API server — triggers the full Ideas Factory → Implementation Swarm
pipeline from the dashboard. Serves event files for the visualization.

Endpoints:
  POST /run       — Start the full pipeline (non-blocking)
  GET  /status    — Current pipeline status (idle, running-ideas, running-impl, complete)
  GET  /events    — Combined event log from both stages

Usage:
    python pipeline_server.py
"""

import json
import os
import subprocess
import threading
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Pipeline Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

PIPELINE_STATUS = {"state": "idle", "message": "Ready to generate"}
PIPELINE_LOCK = threading.Lock()

OUTPUTS_DIR = Path("outputs")
IMPL_DIR = Path("implementation")
VENV_PYTHON = Path("venv/bin/python")


def run_pipeline():
    """Run the full pipeline in a background thread."""
    global PIPELINE_STATUS

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    env = {**os.environ, "ANTHROPIC_API_KEY": api_key}
    python = str(VENV_PYTHON) if VENV_PYTHON.exists() else "python3"

    try:
        viz_dir = Path("visualization")

        # Clear the live event files (separate from saved WattWatch data)
        live_factory = OUTPUTS_DIR / "live-factory-events.json"
        live_impl = IMPL_DIR / "live-impl-events.json"
        live_factory.write_text("[]")
        live_impl.write_text("[]")

        # Point symlinks to live files
        for link_name, target in [
            ("hackathon-factory-events.json", f"../{live_factory}"),
            ("implementation-events.json", f"../{live_impl}"),
        ]:
            link = viz_dir / link_name
            if link.exists() or link.is_symlink():
                link.unlink()
            link.symlink_to(target)

        # Stage 1: Ideas Factory
        PIPELINE_STATUS = {"state": "running-ideas", "message": "Layer 1: Generating ideas..."}

        result = subprocess.run(
            [python, "run_hackathon_factory.py", "--fresh"],
            env=env,
            capture_output=True,
            text=True,
            timeout=600,
        )

        if result.returncode != 0:
            PIPELINE_STATUS = {"state": "error", "message": f"Ideas Factory failed: {result.stderr[:200]}"}
            return

        # Symlink event file for dashboard
        if events_path.exists():
            (viz_dir / "hackathon-factory-events.json").symlink_to(f"../{events_path}")

        # Stage 2: Implementation Swarm
        PIPELINE_STATUS = {"state": "running-impl", "message": "Layer 2: Building demo..."}

        # Find the proposal that was just generated
        proposals = sorted(OUTPUTS_DIR.glob("*-proposal*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not proposals:
            PIPELINE_STATUS = {"state": "error", "message": "No proposal generated"}
            return

        proposal = proposals[0]

        result = subprocess.run(
            [python, "run_implementation_swarm.py", str(proposal)],
            env=env,
            capture_output=True,
            text=True,
            timeout=600,
        )

        if result.returncode != 0:
            PIPELINE_STATUS = {"state": "error", "message": f"Implementation failed: {result.stderr[:200]}"}
            return

        # Symlink impl event file
        if impl_events_path.exists():
            (viz_dir / "implementation-events.json").symlink_to(f"../{impl_events_path}")

        PIPELINE_STATUS = {"state": "complete", "message": "Pipeline complete! Demo ready."}

    except subprocess.TimeoutExpired:
        PIPELINE_STATUS = {"state": "error", "message": "Pipeline timed out (10 min limit)"}
    except Exception as e:
        PIPELINE_STATUS = {"state": "error", "message": f"Pipeline error: {str(e)[:200]}"}


@app.post("/run")
def trigger_pipeline():
    """Start the pipeline (non-blocking)."""
    global PIPELINE_STATUS

    with PIPELINE_LOCK:
        if PIPELINE_STATUS["state"].startswith("running"):
            return {"ok": False, "message": "Pipeline already running"}

        PIPELINE_STATUS = {"state": "starting", "message": "Initializing pipeline..."}
        thread = threading.Thread(target=run_pipeline, daemon=True)
        thread.start()

    return {"ok": True, "message": "Pipeline started"}


@app.get("/status")
def get_status():
    """Get current pipeline status."""
    return PIPELINE_STATUS


@app.get("/events")
def get_events():
    """Get combined LIVE events from current/latest run."""
    events = []

    # Check live files first, fall back to main files
    for path in [
        OUTPUTS_DIR / "live-factory-events.json",
        IMPL_DIR / "live-impl-events.json",
        OUTPUTS_DIR / "hackathon-factory-events.json",
        IMPL_DIR / "implementation-events.json",
    ]:
        if path.exists():
            try:
                data = json.loads(path.read_text())
                if data:
                    events.extend(data)
                    break  # Use first non-empty source per stage
            except json.JSONDecodeError:
                pass

    return events


@app.get("/events/wattwatch")
def get_wattwatch_events():
    """Get saved WattWatch replay events."""
    events = []

    for path in [
        OUTPUTS_DIR / "hackathon-factory-events.json",
        IMPL_DIR / "implementation-events.json",
    ]:
        if path.exists():
            try:
                events.extend(json.loads(path.read_text()))
            except json.JSONDecodeError:
                pass

    return events


# Serve visualization static files (follow_symlink for event JSON files)
app.mount("/", StaticFiles(directory="visualization", html=True, follow_symlink=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
