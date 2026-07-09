"""Search the indexed SFX library by text description or reference audio clip.

Usage:
    python search_sfx.py --text "soft cartoon pop" --top 8
    python search_sfx.py --ref path/to/clip.wav --top 8

Prints ranked matches as JSON (name, path, score). Cosine similarity:
> 0.55 strong, 0.40-0.55 plausible, < 0.40 weak.
"""
import argparse
import json
import sys

import numpy as np

import config
import clap_utils


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="Text description of the sound")
    group.add_argument("--ref", help="Path to a reference audio clip")
    parser.add_argument("--top", type=int, default=8, help="Number of results")
    args = parser.parse_args()

    if not config.INDEX_PATH.exists():
        print("No index found. Run: python index_sfx.py", file=sys.stderr)
        sys.exit(1)

    embeddings = np.load(config.INDEX_PATH)["embeddings"]
    manifest = json.loads(config.MANIFEST_PATH.read_text(encoding="utf-8"))["files"]

    if args.text:
        query = clap_utils.embed_text(args.text)
        query_desc = {"type": "text", "query": args.text}
    else:
        wave = clap_utils.load_audio(args.ref)
        query = clap_utils.embed_audio_batch([wave])[0]
        query_desc = {"type": "audio", "query": args.ref}

    scores = embeddings @ query  # both L2-normalized -> cosine similarity
    order = np.argsort(-scores)[: args.top]

    results = [
        {
            "rank": i + 1,
            "name": manifest[idx]["name"],
            "path": manifest[idx]["path"],
            "score": round(float(scores[idx]), 4),
        }
        for i, idx in enumerate(order)
    ]
    print(json.dumps({"query": query_desc, "results": results}, indent=2))


if __name__ == "__main__":
    main()
