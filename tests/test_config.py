import json

import config


def test_load_user_config_missing_file(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "USER_CONFIG_PATH", tmp_path / "config.json")
    assert config._load_user_config() == {}


def test_load_user_config_reads_values(monkeypatch, tmp_path):
    cfg_path = tmp_path / "config.json"
    cfg_path.write_text(json.dumps({"library_dir": "C:/sfx", "freesound_api_key": "abc"}), encoding="utf-8")
    monkeypatch.setattr(config, "USER_CONFIG_PATH", cfg_path)
    assert config._load_user_config() == {"library_dir": "C:/sfx", "freesound_api_key": "abc"}


def test_load_user_config_corrupt_json_returns_empty(monkeypatch, tmp_path):
    cfg_path = tmp_path / "config.json"
    cfg_path.write_text("not valid json", encoding="utf-8")
    monkeypatch.setattr(config, "USER_CONFIG_PATH", cfg_path)
    assert config._load_user_config() == {}
