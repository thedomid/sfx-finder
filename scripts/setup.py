"""First-time interactive setup for sfx-finder.

Run once: python scripts/setup.py

Writes ~/.sfx-finder/config.json (outside the repo — nothing personal ever
gets committed). Safe to re-run any time to change settings; existing values
are shown as defaults.
"""
import json
import stat
from pathlib import Path

CONFIG_DIR = Path.home() / ".sfx-finder"
CONFIG_PATH = CONFIG_DIR / "config.json"


def _prompt(label, current, secret=False):
    shown = ("set" if current else "not set") if secret else (current or "")
    answer = input(f"{label} [{shown}]: ").strip()
    return answer if answer else current


def main():
    existing = {}
    if CONFIG_PATH.exists():
        existing = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        print(f"Existing config found at {CONFIG_PATH} - press enter to keep a value.\n")
    else:
        print("SFX Finder setup - press enter to skip optional fields.\n")

    library_dir = _prompt("Path to your SFX library folder (required)", existing.get("library_dir", ""))
    freesound_key = _prompt("Freesound API key (optional)", existing.get("freesound_api_key", ""), secret=True)
    elevenlabs_key = _prompt("ElevenLabs API key (optional)", existing.get("elevenlabs_api_key", ""), secret=True)

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        json.dumps(
            {
                "library_dir": library_dir,
                "freesound_api_key": freesound_key,
                "elevenlabs_api_key": elevenlabs_key,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    try:
        CONFIG_PATH.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 0600 — file holds API keys
    except OSError:
        pass

    print(f"\nSaved to {CONFIG_PATH}")
    if library_dir:
        print("Next: python scripts/index_sfx.py")
    else:
        print("No library folder set - re-run setup.py before indexing.")


if __name__ == "__main__":
    main()
