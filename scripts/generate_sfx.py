"""Generate a NEW sound effect from a text description using ElevenLabs.

This does not find an existing sound — it synthesizes a fresh one that
matches the description. Use as a last resort, after both the local
library (search_sfx.py) and Freesound (search_web.py) come up weak.

Usage:
    python generate_sfx.py --text "deep cinematic impact with reverb tail" --output impact.mp3

Requires a paid API key: https://elevenlabs.io/app/settings/api-keys
Set it once with: python scripts/setup.py
Each call costs money — confirm with the user before running.
"""
import argparse
import sys

import requests

import config

API_URL = "https://api.elevenlabs.io/v1/sound-generation"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", required=True, help="Description of the sound to generate")
    parser.add_argument("--duration", type=float, default=None, help="Seconds, 0.5-22 (default: auto)")
    parser.add_argument("--output", default="generated.mp3", help="Output file path")
    args = parser.parse_args()

    if not config.ELEVENLABS_API_KEY:
        print(
            "No ElevenLabs API key set. Get a key at "
            "https://elevenlabs.io/app/settings/api-keys then run:\n"
            "  python scripts/setup.py",
            file=sys.stderr,
        )
        sys.exit(1)

    payload = {"text": args.text}
    if args.duration is not None:
        payload["duration_seconds"] = args.duration

    resp = requests.post(
        API_URL,
        headers={"xi-api-key": config.ELEVENLABS_API_KEY, "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    if resp.status_code != 200:
        print(f"ElevenLabs error {resp.status_code}: {resp.text[:500]}", file=sys.stderr)
        sys.exit(1)

    with open(args.output, "wb") as f:
        f.write(resp.content)
    print(f"Generated -> {args.output}")


if __name__ == "__main__":
    main()
