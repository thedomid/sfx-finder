# sfx-finder

[![tests](https://github.com/thedomid/sfx-finder/actions/workflows/test.yml/badge.svg)](https://github.com/thedomid/sfx-finder/actions/workflows/test.yml)
[![license](https://img.shields.io/github/license/thedomid/sfx-finder)](LICENSE)
[![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue.svg)](requirements.txt)

A [Claude Code](https://claude.com/claude-code) skill for video editors: stop scrolling through folders (or Freesound, or your memory) to find that one sound effect. Describe it, or point at a clip, and it finds the closest match — in your own library first, then on the internet, then generated from scratch if nothing exists yet.

## How it works

Three tiers, in order, stopping as soon as something's good enough:

| Tier | What it does | Cost |
|---|---|---|
| **1. Your library** | Semantic search over sound files you already own, using [CLAP](https://huggingface.co/laion/clap-htsat-unfused) audio embeddings — matches by text description or by a reference clip | Free, runs locally |
| **2. Freesound.org** | Real search over a huge library of licensed, downloadable sound effects, when nothing in your library is close | Free API key |
| **3. ElevenLabs** | Generates a brand-new sound effect from a text description, as a last resort | Paid, per call |

You can also pull tier 1/2's reference clip straight out of a video: give it a file and a timestamp and it extracts the sound with `ffmpeg`, no manual editing needed.

### What this is *not*

There's no fingerprint database for generic sound effects — unlike Shazam, which works because it has a massive catalog of registered commercial songs. So this can't tell you *"the sound in that video came from pack X."* It can only find or make something that sounds close. If you need the exact original, you're back to asking whoever made the video.

## Requirements

- Python 3.10+
- [ffmpeg](https://ffmpeg.org/) on your PATH — only needed if you extract clips from video
  - Windows: `winget install Gyan.FFmpeg`
  - Mac: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`

## Install

```bash
git clone https://github.com/thedomid/sfx-finder ~/.claude/skills/sfx-finder
cd ~/.claude/skills/sfx-finder
pip install -r requirements.txt
```

Then install torch — kept out of `requirements.txt` since the right command differs by platform:

```bash
# Windows / Linux — CPU-only build (much smaller download, GPU not needed)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Mac
pip install torch
```

## Setup

```bash
python scripts/setup.py
```

Asks for your SFX library folder, plus optional Freesound/ElevenLabs API keys. Saves to `~/.sfx-finder/config.json` — outside this repo, so nothing personal ever ends up in git. Re-run any time to change settings.

> **Using this through Claude?** Just tell it your library folder in plain English — it writes that config file for you, no terminal needed.

## Quick start

```bash
python scripts/index_sfx.py                              # one-time: embed your library
python scripts/search_sfx.py --text "soft cartoon pop"    # find something in it
```

First run downloads the CLAP model (~600MB, one time, cached after that).

## Usage

```bash
# --- Local library ---
python scripts/index_sfx.py                                  # build/update the index
python scripts/index_sfx.py --rebuild                        # force a full re-index
python scripts/search_sfx.py --text "deep cinematic impact with reverb tail" --top 8
python scripts/search_sfx.py --ref path/to/clip.wav --top 8  # match by audio instead of words

# --- Pull a reference clip out of a video first ---
python scripts/extract_clip.py --input video.mp4 --start 0:07 --duration 2 --output clip.wav
python scripts/search_sfx.py --ref clip.wav

# --- Internet search (Freesound), when the library comes up weak ---
python scripts/search_web.py --text "soft cartoon pop" --top 8
python scripts/search_web.py --ref clip.wav --top 8

# --- Generate a new sound (ElevenLabs), last resort — costs money per call ---
python scripts/generate_sfx.py --text "deep cinematic impact with reverb tail" --output impact.mp3
```

### Reading the scores

`search_sfx.py` and `search_web.py` print ranked matches as JSON with a cosine similarity score:

| Score | Meaning |
|---|---|
| `> 0.55` | Strong match — probably what you want |
| `0.40–0.55` | Plausible — worth a listen, not a sure thing |
| `< 0.40` | Weak — try rephrasing the query, or fall through to Freesound/ElevenLabs |

Write text queries as a literal description of the sound itself (texture, source, character) — "deep cinematic impact with reverb tail," not "transition for my reel." For reference-clip queries, trim to the 1–3 seconds that contain just the effect.

## API keys (optional)

Only needed for tiers 2 and 3 — tier 1 (your own library) works with neither.

- Freesound (free): https://freesound.org/apiv2/apply/
- ElevenLabs (paid): https://elevenlabs.io/app/settings/api-keys

## Troubleshooting

- **`ffmpeg not found on PATH`** — install it (see [Requirements](#requirements)) and restart your terminal.
- **`No library folder configured`** — run `python scripts/setup.py`.
- **`No Freesound/ElevenLabs API key set`** — the script prints a signup link; get a key, then re-run `setup.py`.
- **Every match scores low (`< 0.40`)** — your library probably just doesn't have anything close; rephrase the text query first, then try Freesound.
- **torch install is slow or grabs several GB** — you're pulling the default CUDA build. Use the CPU-only index URL from [Install](#install) instead; it's a fraction of the size and CLAP inference doesn't need a GPU.

## Project structure

```text
sfx-finder/
├── SKILL.md              # instructions Claude reads to operate this skill
├── scripts/
│   ├── config.py          # loads ~/.sfx-finder/config.json + env var fallbacks
│   ├── setup.py            # interactive first-run config
│   ├── clap_utils.py       # CLAP model loading + embedding helpers
│   ├── index_sfx.py        # builds the local embedding index
│   ├── search_sfx.py       # search the local index (text or reference clip)
│   ├── extract_clip.py     # pull an audio clip out of a video via ffmpeg
│   ├── search_web.py       # Freesound.org search
│   └── generate_sfx.py     # ElevenLabs sound generation
└── tests/                 # pure-logic unit tests (no model/network required)
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) — dev setup only needs `pip install -r requirements-dev.txt`, no torch/GPU required to run the test suite.

## License

MIT — see [LICENSE](LICENSE).
