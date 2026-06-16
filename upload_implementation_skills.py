"""
Upload implementation skills and attach to the right specialist agents.

Usage:
    python upload_implementation_skills.py
"""

import json
import os
from pathlib import Path

from anthropic import Anthropic
from anthropic.lib import files_from_dir


# Map skill directory name → specialist key that should get it
SKILL_TO_SPECIALIST = {
    "frontend-patterns": "frontend-dev",
    "backend-patterns": "backend-dev",
    "devops-patterns": "devops",
    "qa-patterns": "qa",
}


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("Set ANTHROPIC_API_KEY before running.")

    specialist_ids_path = Path(".implementation_specialist_ids.json")
    if not specialist_ids_path.exists():
        raise SystemExit("Run create_implementation_specialists.py first.")
    specialist_ids = json.loads(specialist_ids_path.read_text())

    client = Anthropic()

    # List existing custom skills so we can detect and reuse any prior uploads
    print("Checking for existing skills...")
    existing_by_title: dict[str, str] = {}
    for page in client.beta.skills.list(source="custom"):
        existing_by_title[page.display_title] = page.id

    uploaded: dict[str, str] = {}

    for skill_name, specialist_key in SKILL_TO_SPECIALIST.items():
        skill_dir = Path("skills") / skill_name
        if not (skill_dir / "SKILL.md").exists():
            print(f"  Skipping {skill_name} — no SKILL.md found")
            continue

        display_title = skill_name.replace("-", " ").title()

        # 1. Upload the skill (or reuse if one already exists with this title)
        if display_title in existing_by_title:
            skill_id = existing_by_title[display_title]
            print(f"Reusing existing skill: {skill_name} ({skill_id})")
        else:
            print(f"Uploading skill: {skill_name}...")
            skill = client.beta.skills.create(
                display_title=display_title,
                files=files_from_dir(skill_dir),
            )
            skill_id = skill.id
            print(f"  -> {skill_id}")

        uploaded[skill_name] = skill_id

        # 2. Attach to specialist
        if specialist_key not in specialist_ids:
            print(f"  WARNING: specialist '{specialist_key}' not found, skipping attach")
            continue

        specialist_id = specialist_ids[specialist_key]
        print(f"  attaching to specialist `{specialist_key}` ({specialist_id})...")

        agent = client.beta.agents.retrieve(specialist_id)
        new_skills = list(agent.skills or []) + [
            {"type": "custom", "skill_id": skill_id, "version": "latest"}
        ]

        client.beta.agents.update(
            specialist_id,
            skills=new_skills,
            version=agent.version,
        )
        print(f"  attached ✓")

    print(f"\nUploaded {len(uploaded)} skills and attached them to specialists.")
    print("Next: python run_implementation_swarm.py outputs/wattwatch-project-proposal.md")


if __name__ == "__main__":
    main()
