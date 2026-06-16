"""
Download files from the implementation session.
"""

import os
from pathlib import Path
from anthropic import Anthropic

SESSION_ID = "sesn_013NsuJKpzpAvM4yLDMExd5p"
OUTPUT_DIR = Path("implementation/wattwatch")

def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("Set ANTHROPIC_API_KEY")

    client = Anthropic(api_key=api_key)

    print(f"Downloading files from session {SESSION_ID}...")

    # List files in the session
    files = client.beta.files.list(
        scope_id=SESSION_ID,
        betas=["managed-agents-2026-04-01"],
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    file_count = 0
    for f in files.data:
        # Get the filename and create directory structure
        filename = f.filename
        out_path = OUTPUT_DIR / filename

        # Create parent directories if needed
        out_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"  Downloading: {filename}")

        # Download the file
        content = client.beta.files.download(f.id)
        content.write_to_file(str(out_path))

        file_count += 1

    print(f"\n✅ Downloaded {file_count} files to {OUTPUT_DIR}/")

    # List what we got
    print("\nFiles downloaded:")
    for file in sorted(OUTPUT_DIR.rglob('*')):
        if file.is_file():
            print(f"  - {file.relative_to(OUTPUT_DIR)}")

if __name__ == "__main__":
    main()
