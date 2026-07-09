# sfx-finder

[![tests](https://github.com/thedomid/sfx-finder/actions/workflows/test.yml/badge.svg)](https://github.com/thedomid/sfx-finder/actions/workflows/test.yml)
[![license](https://img.shields.io/github/license/thedomid/sfx-finder)](LICENSE)

A [Claude Code](https://claude.com/claude-code) skill for video editors. Finds sound effects, in this order:

1. **Your own library** — semantic search over sound files you already own, by text description or by a reference clip (including one you extract straight out of a video). Runs locally and free, using [CLAP](https://huggingface.co/laion/clap-htsat-unfused) audio embeddings.
2. **Freesound.org** — if nothing in your library is close, search a huge library of real, licensed, downloadable sound effects. Free, needs an API key.
3. **ElevenLabs** — last resort: generate a brand-new sound effect from a text description. Paid, per call.

**What this is not:** there's no fingerprint database for generic sound effects (unlike Shazam for commercial music), so this can't tell you "the sound in that video came from pack X." It can only find or make something that sounds similar.

## Requirements

- Python 3.10+
- [ffmpeg](https://ffmpeg.org/) on your PATH (only needed for extracting clips from video)
  - Windows: `winget install Gyan.FFmpeg`
  - Mac: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`

## Install

```bash
git clone https://github.com/thedomid/sfx-finder ~/.claude/skills/sfx-finder
cd ~/.claude/skills/sfx-finder
pip install -r requirements.txt
```

Then install torch (kept out of `requirements.txt` since the right command differs by platform):

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

If you're driving this through Claude rather than a terminal, just tell Claude your library folder — it can write that config file for you directly.

## Usage

Build the index (first run downloads the CLAP model, ~600MB, one time):

```bash
python scripts/index_sfx.py
```

Search by description:

```bash
python scripts/search_sfx.py --text "soft cartoon pop" --top 8
```

Search by a reference clip:

```bash
python scripts/search_sfx.py --ref path/to/clip.wav --top 8
```

Pull a clip out of a video first:

```bash
python scripts/extract_clip.py --input video.mp4 --start 0:07 --duration 2 --output clip.wav
```

Search the internet (Freesound) when your library comes up weak:

```bash
python scripts/search_web.py --text "soft cartoon pop" --top 8
```

Generate a new sound as a last resort (costs money):

```bash
python scripts/generate_sfx.py --text "deep cinematic impact with reverb tail" --output impact.mp3
```

## API keys (optional)

- Freesound (free): https://freesound.org/apiv2/apply/
- ElevenLabs (paid): https://elevenlabs.io/app/settings/api-keys

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) — dev setup only needs `pip install -r requirements-dev.txt`, no torch/GPU required to run the test suite.

## License

MIT — see [LICENSE](LICENSE).
