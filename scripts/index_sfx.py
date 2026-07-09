"""Index the SFX library: embed every audio file with CLAP and cache vectors.

Incremental: files already in the manifest with an unchanged mtime are skipped.
Run this any time you add new sounds.

Usage:
    python index_sfx.py            # index/update
    python index_sfx.py --rebuild  # force full re-index
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

import config
import clap_utils

BATCH_SIZE = 8


def scan_library():
    if not config.LIBRARY_DIR:
        print("No library folder configured. Run: python scripts/setup.py", file=sys.stderr)
        sys.exit(1)
    if not config.LIBRARY_DIR.exists():
        print(
            f"Library folder not found: {config.LIBRARY_DIR}\n"
            "Run: python scripts/setup.py to fix it.",
            file=sys.stderr,
        )
        sys.exit(1)
    files = [
        p
        for p in sorted(config.LIBRARY_DIR.rglob("*"))
        if p.suffix.lower() in config.AUDIO_EXTS and p.is_file()
    ]
    return files


def load_existing():
    if config.INDEX_PATH.exists() and config.MANIFEST_PATH.exists():
        data = np.load(config.INDEX_PATH)
        manifest = json.loads(config.MANIFEST_PATH.read_text(encoding="utf-8"))
        return data["embeddings"], manifest
    return None, {"files": []}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rebuild", action="store_true", help="Force full re-index")
    args = parser.parse_args()

    config.DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    files = scan_library()
    print(f"Found {len(files)} audio files in {config.LIBRARY_DIR}")

    old_emb, manifest = (None, {"files": []}) if args.rebuild else load_existing()
    old_map = {}
    if old_emb is not None:
        for i, entry in enumerate(manifest["files"]):
            old_map[entry["path"]] = (i, entry["mtime"])

    kept_embs, new_entries, to_embed = [], [], []
    for p in files:
        key = str(p)
        mtime = p.stat().st_mtime
        if key in old_map and abs(old_map[key][1] - mtime) < 1e-6:
            kept_embs.append(old_emb[old_map[key][0]])
            new_entries.append({"path": key, "name": p.name, "mtime": mtime})
        else:
            to_embed.append((p, mtime))

    print(f"Unchanged: {len(kept_embs)} | To embed: {len(to_embed)}")
    embedded = []
    if to_embed:
        clap_utils.load_model()
        start = time.time()
        for i in range(0, len(to_embed), BATCH_SIZE):
            batch = to_embed[i : i + BATCH_SIZE]
            waves, valid = [], []
            for p, mtime in batch:
                try:
                    waves.append(clap_utils.load_audio(p))
                    valid.append((p, mtime))
                except Exception as e:
                    print(f"  skip (unreadable): {p.name} ({e})", file=sys.stderr)
            if not waves:
                continue
            embs = clap_utils.embed_audio_batch(waves)
            for (p, mtime), emb in zip(valid, embs):
                embedded.append(emb)
                new_entries.append({"path": str(p), "name": p.name, "mtime": mtime})
            done = min(i + BATCH_SIZE, len(to_embed))
            print(f"  embedded {done}/{len(to_embed)} ({time.time() - start:.0f}s)")

    all_embs = kept_embs + embedded
    if not all_embs:
        print("Nothing indexed - library is empty or all files unreadable.", file=sys.stderr)
        sys.exit(1)

    np.savez_compressed(config.INDEX_PATH, embeddings=np.vstack(all_embs))
    config.MANIFEST_PATH.write_text(
        json.dumps({"files": new_entries}, indent=2), encoding="utf-8"
    )
    print(f"Index saved: {len(new_entries)} files -> {config.INDEX_PATH}")


if __name__ == "__main__":
    main()
