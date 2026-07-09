---
name: sfx-finder
description: Search a local sound-effects library by text description or by reference audio clip, using CLAP audio embeddings. Also searches Freesound.org for real downloadable licensed sounds, and can generate a new sound effect via ElevenLabs as a last resort. Use this skill whenever the user wants to find a sound effect, locate a sound in their SFX library, find sounds similar to a clip, identify/extract a sound from a video, or asks things like "find me a whoosh", "what pack is this sound from", "I need something that sounds like this", or mentions SFX, sound effects, or their sound library at all.
---

# SFX Finder

Finds sound effects, first in the user's local library, then (if nothing good) on the internet via Freesound, then (last resort) generates one with ElevenLabs. Claude cannot hear audio — all listening is done by the bundled scripts. Claude's job is to run the right script, interpret the similarity scores, and present results.

There is no fingerprint database for generic sound effects (unlike Shazam for commercial music). None of these workflows can tell the user "this exact sound in your video came from pack X" — they can only find or make something that sounds similar. Never imply otherwise.

Per-user settings (library folder, API keys) live in `~/.sfx-finder/config.json`, outside this repo — nothing personal is ever hardcoded or committed. `scripts/config.py` reads that file automatically.

## Workflows

### 0. First-time setup (only if unconfigured)

Check whether `~/.sfx-finder/config.json` exists and has a `library_dir` set. If not:

- Ask the user where their SFX folder is (and optionally for Freesound/ElevenLabs API keys).
- Write `~/.sfx-finder/config.json` directly with the Write tool: `{"library_dir": "...", "freesound_api_key": "...", "elevenlabs_api_key": "..."}`. Don't run `scripts/setup.py` via Bash for this — it's an interactive `input()`-based script meant for a human typing in a real terminal, and will hang when run non-interactively.
- Then proceed to indexing.

### 1. First-time setup / re-indexing

Run whenever the library has new files or `database/sfx_index.npz` doesn't exist:

```
python scripts/index_sfx.py
```

- Incremental: skips files already indexed with unchanged mtime. Safe to run anytime.
- First run downloads the CLAP model (~600MB, one time) and can take a few minutes on a big library. Warn the user before the first run.

### 2. Search by text description (most common)

```
python scripts/search_sfx.py --text "soft cartoon pop" --top 8
```

Use when the user describes the sound in words. Write the query as a literal description of the sound itself (texture, source, character), not video-editing jargon. Good: "deep cinematic impact with reverb tail". Bad: "transition for my reel".

### 3. Search by reference clip ("find something like this")

```
python scripts/search_sfx.py --ref "C:/path/to/clip.wav" --top 8
```

Use when the user provides an audio file to match against.

### 4. Extract a sound from a video first

If the user gives a video and a timestamp:

```
python scripts/extract_clip.py --input "C:/path/video.mp4" --start 0:07 --duration 2 --output clip.wav
```

Then search with `--ref clip.wav`. If no timestamp given, ask for the approximate moment. Never modify the original file.

### 5. Search the internet (Freesound) — when the local library comes up weak

```
python scripts/search_web.py --text "soft cartoon pop" --top 8
python scripts/search_web.py --ref "C:/path/to/clip.wav" --top 8
```

Real search over Freesound.org's library of licensed, downloadable sounds. Requires `FREESOUND_API_KEY` (see `scripts/config.py` for setup instructions) — if unset, the script prints a signup link; relay it to the user. Results include a `preview_url` the user can play/download directly, plus the sound's license — always surface the license, don't let the user assume everything is free-for-commercial-use.

### 6. Generate a new sound (ElevenLabs) — last resort, costs money

```
python scripts/generate_sfx.py --text "deep cinematic impact with reverb tail" --output impact.mp3
```

This does not find an existing sound — it synthesizes a new one from the description. Only reach for this after local + Freesound search both come up weak, and **always confirm with the user first** since each call is billed. Requires `ELEVENLABS_API_KEY` (see `scripts/config.py`).

## Interpreting results

`search_sfx.py` prints ranked matches as JSON: filename, path, cosine similarity score.

- **> 0.55**: strong match, likely what they want
- **0.40–0.55**: plausible, present as candidates
- **< 0.40**: weak — say so honestly. Suggest better query phrasings and offer external search keywords (Freesound, Pixabay, Mixkit, Splice, Epidemic Sound) instead of pretending a weak match is good.

Present results as a short ranked list with full file paths so the user can drag files straight into their editor. Don't pad the output — the user is a video editor mid-session, keep it fast and scannable.

## Rules

- Never claim to have listened to or heard audio. The scripts measure similarity; Claude reports it.
- For reference-clip queries, trim to the 1–3 seconds containing just the sound effect for best results (extract_clip.py can do this).
- If CLAP/torch isn't installed, the scripts print install instructions — relay them to the user rather than improvising alternatives.
- Do not download SFX from unofficial rips or bypass paid libraries. Suggest legitimate sources only.
- Freesound results carry a license per sound — always surface it, never assume free-for-commercial-use.
- Never call generate_sfx.py without the user explicitly confirming first — it's a paid API call per use.
