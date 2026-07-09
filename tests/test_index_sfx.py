import pytest

import config
import index_sfx


def test_scan_library_filters_by_extension(monkeypatch, tmp_path):
    (tmp_path / "sound.wav").write_bytes(b"x")
    (tmp_path / "notes.txt").write_bytes(b"x")
    (tmp_path / "clip.mp3").write_bytes(b"x")
    monkeypatch.setattr(config, "LIBRARY_DIR", tmp_path)

    names = {f.name for f in index_sfx.scan_library()}

    assert names == {"sound.wav", "clip.mp3"}


def test_scan_library_exits_when_unconfigured(monkeypatch):
    monkeypatch.setattr(config, "LIBRARY_DIR", None)
    with pytest.raises(SystemExit):
        index_sfx.scan_library()


def test_scan_library_exits_when_folder_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "LIBRARY_DIR", tmp_path / "does-not-exist")
    with pytest.raises(SystemExit):
        index_sfx.scan_library()
