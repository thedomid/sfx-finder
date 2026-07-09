import pytest

import config
import generate_sfx


def test_require_key_exits_when_missing(monkeypatch):
    monkeypatch.setattr(config, "ELEVENLABS_API_KEY", None)
    with pytest.raises(SystemExit):
        generate_sfx._require_key()


def test_require_key_passes_when_set(monkeypatch):
    monkeypatch.setattr(config, "ELEVENLABS_API_KEY", "abc123")
    generate_sfx._require_key()
