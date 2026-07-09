import json

import setup


def test_setup_writes_config(monkeypatch, tmp_path):
    cfg_dir = tmp_path / ".sfx-finder"
    monkeypatch.setattr(setup, "CONFIG_DIR", cfg_dir)
    monkeypatch.setattr(setup, "CONFIG_PATH", cfg_dir / "config.json")

    answers = iter(["C:/Users/me/SFX", "freesound-key", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    setup.main()

    saved = json.loads((cfg_dir / "config.json").read_text(encoding="utf-8"))
    assert saved == {
        "library_dir": "C:/Users/me/SFX",
        "freesound_api_key": "freesound-key",
        "elevenlabs_api_key": "",
    }


def test_setup_keeps_existing_value_on_blank_answer(monkeypatch, tmp_path):
    cfg_dir = tmp_path / ".sfx-finder"
    cfg_dir.mkdir()
    cfg_path = cfg_dir / "config.json"
    cfg_path.write_text(json.dumps({"library_dir": "C:/old", "freesound_api_key": "", "elevenlabs_api_key": ""}), encoding="utf-8")
    monkeypatch.setattr(setup, "CONFIG_DIR", cfg_dir)
    monkeypatch.setattr(setup, "CONFIG_PATH", cfg_path)

    answers = iter(["", "", ""])  # blank = keep existing
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    setup.main()

    saved = json.loads(cfg_path.read_text(encoding="utf-8"))
    assert saved["library_dir"] == "C:/old"
