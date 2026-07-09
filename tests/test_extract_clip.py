import extract_clip


def test_windows_hint_mentions_winget():
    assert "winget" in extract_clip._FFMPEG_INSTALL["Windows"]


def test_mac_hint_mentions_brew():
    assert "brew" in extract_clip._FFMPEG_INSTALL["Darwin"]


def test_default_hint_mentions_apt_for_linux():
    assert "apt" in extract_clip._FFMPEG_INSTALL_DEFAULT
