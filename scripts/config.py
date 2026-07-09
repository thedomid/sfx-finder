"""sfx-finder configuration.

Per-user settings (library folder, API keys) live outside the repo in
~/.sfx-finder/config.json so this repo has nothing personal to accidentally
commit. Run `python scripts/setup.py` to create/edit it, or (if you're using
this through Claude) just tell Claude your library folder and it will write
the file for you.
"""
import json
import os
from pathlib import Path

USER_CONFIG_DIR = Path.home() / ".sfx-finder"
USER_CONFIG_PATH = USER_CONFIG_DIR / "config.json"


def _load_user_config():
    if USER_CONFIG_PATH.exists():
        try:
            return json.loads(USER_CONFIG_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


_user = _load_user_config()

# Root folder containing your sound effects (searched recursively).
# None until setup.py has been run (or Claude has written the config file).
LIBRARY_DIR = Path(_user["library_dir"]).expanduser() if _user.get("library_dir") else None

# Where the embedding index is cached — inside this repo, but gitignored
# since it's personal (built from your own library).
SKILL_ROOT = Path(__file__).resolve().parent.parent
DATABASE_DIR = SKILL_ROOT / "database"
INDEX_PATH = DATABASE_DIR / "sfx_index.npz"
MANIFEST_PATH = DATABASE_DIR / "manifest.json"

# Audio file extensions to index
AUDIO_EXTS = {".wav", ".mp3", ".flac", ".ogg", ".aiff", ".aif", ".m4a"}

# CLAP model (audio + text in the same embedding space, runs locally, free)
CLAP_MODEL = "laion/clap-htsat-unfused"

# CLAP expects 48kHz mono
SAMPLE_RATE = 48000

# Max seconds of audio to embed per file (long ambiences get truncated)
MAX_SECONDS = 10.0

# Optional: real internet search over licensed, downloadable sound effects.
# Free key: https://freesound.org/apiv2/apply/ — set via `python scripts/setup.py`.
# Falls back to the FREESOUND_API_KEY env var if no user config is set (e.g. CI).
FREESOUND_API_KEY = _user.get("freesound_api_key") or os.environ.get("FREESOUND_API_KEY")

# Optional: generates a NEW sound effect from a text description (not a match
# to an existing sound). Paid, per-call. Key: https://elevenlabs.io/app/settings/api-keys
# — set via `python scripts/setup.py`. Falls back to ELEVENLABS_API_KEY env var.
ELEVENLABS_API_KEY = _user.get("elevenlabs_api_key") or os.environ.get("ELEVENLABS_API_KEY")
