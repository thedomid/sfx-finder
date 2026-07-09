# Contributing

## Dev setup

```bash
git clone https://github.com/thedomid/sfx-finder
cd sfx-finder
pip install -r requirements-dev.txt
```

This installs just enough to run the test suite (`numpy`, `requests`, `pytest`) — the full `requirements.txt` (`torch`, `transformers`, `librosa`, `soundfile`) is only needed to actually run the skill against real audio, not to develop or test it.

## Running tests

```bash
pytest
```

The suite only exercises pure logic — config loading, file filtering, key-presence checks — never the actual CLAP model or a live network call, so it runs in under a second and needs no API keys or GPU.

## Making changes

- Keep `scripts/config.py` as the single source of truth for settings; never hardcode a personal path or API key anywhere else.
- If you touch `scripts/*.py`, add or update a test in `tests/`.
- If you change setup steps or add a workflow, update `README.md` and `SKILL.md` together — they're read by humans and by Claude respectively, and should stay in sync.
- Open a PR against `main`. CI runs the test suite on Windows, Mac, and Linux.
