"""Search Freesound.org for licensed, downloadable sound effects (real internet search).

Usage:
    python search_web.py --text "soft cartoon pop" --top 8
    python search_web.py --ref path/to/clip.wav --top 8   # match by uploaded audio

Requires a free API key: https://freesound.org/apiv2/apply/
Set it once with: python scripts/setup.py

Prints ranked matches as JSON: name, url, license, preview_url (directly
playable/downloadable, no auth needed), duration.
"""
import argparse
import json
import sys

import requests

import config

API_BASE = "https://freesound.org/apiv2"
FIELDS = "id,name,url,license,previews,duration,username,tags"


def _require_key():
    if not config.FREESOUND_API_KEY:
        print(
            "No Freesound API key set. Get a free key at "
            "https://freesound.org/apiv2/apply/ then run:\n"
            "  python scripts/setup.py",
            file=sys.stderr,
        )
        sys.exit(1)


def search_by_text(query, top):
    resp = requests.get(
        f"{API_BASE}/search/text/",
        params={
            "query": query,
            "token": config.FREESOUND_API_KEY,
            "fields": FIELDS,
            "page_size": top,
            "sort": "score",
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get("results", [])


def search_by_audio(path, top):
    with open(path, "rb") as f:
        upload = requests.post(
            f"{API_BASE}/sounds/upload/",
            headers={"Authorization": f"Token {config.FREESOUND_API_KEY}"},
            files={"audiofile": f},
            timeout=60,
        )
    upload.raise_for_status()
    filename = upload.json()["filename"]

    resp = requests.get(
        f"{API_BASE}/search/content/",
        params={
            "target_file": filename,
            "token": config.FREESOUND_API_KEY,
            "fields": FIELDS,
            "page_size": top,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get("results", [])


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="Text description of the sound")
    group.add_argument("--ref", help="Path to a reference audio clip to match against")
    parser.add_argument("--top", type=int, default=8)
    args = parser.parse_args()

    _require_key()

    results = search_by_text(args.text, args.top) if args.text else search_by_audio(args.ref, args.top)

    out = [
        {
            "rank": i + 1,
            "name": r["name"],
            "url": r["url"],
            "license": r.get("license"),
            "preview_url": r.get("previews", {}).get("preview-hq-mp3"),
            "duration": r.get("duration"),
            "user": r.get("username"),
        }
        for i, r in enumerate(results)
    ]
    print(json.dumps({"query": args.text or args.ref, "results": out}, indent=2))


if __name__ == "__main__":
    main()
