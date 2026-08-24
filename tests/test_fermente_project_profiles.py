from app.fermente.project import FermenteVideoProject, Scene


def project(profile, seconds):
    return FermenteVideoProject("Test", "en-US", profile, [Scene("one", "Text")], seconds)


def test_editorial_pilot_82_seconds_is_valid():
    assert project("editorial-pilot", 82).validate() == []


def test_youtube_long_82_seconds_is_invalid():
    assert "at least 420" in project("youtube-long", 82).validate()[0]


def test_youtube_long_420_seconds_is_valid():
    assert project("youtube-long", 420).validate() == []
