import pytest

import config
import search_web


def test_require_key_exits_when_missing(monkeypatch):
    monkeypatch.setattr(config, "FREESOUND_API_KEY", None)
    with pytest.raises(SystemExit):
        search_web._require_key()


def test_require_key_passes_when_set(monkeypatch):
    monkeypatch.setattr(config, "FREESOUND_API_KEY", "abc123")
    search_web._require_key()
