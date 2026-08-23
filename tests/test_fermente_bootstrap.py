from scripts import fermente_bootstrap


def test_fermente_preset_defaults(monkeypatch):
    for name in (
        "FERMENTE_OPENAI_API_KEY",
        "OPENAI_API_KEY",
        "FERMENTE_PEXELS_API_KEY",
        "PEXELS_API_KEY",
        "FERMENTE_PIXABAY_API_KEY",
        "PIXABAY_API_KEY",
        "FERMENTE_ENGINE_API_KEY",
        "MPT_API_KEY",
        "FERMENTE_FISH_API_KEY",
        "FISH_API_KEY",
    ):
        monkeypatch.delenv(name, raising=False)

    cfg = fermente_bootstrap.build_config()
    app = cfg["app"]
    ui = cfg["ui"]

    assert cfg["listen_host"] == "127.0.0.1"
    assert app["llm_provider"] == "openai"
    assert app["video_source"] == "pexels"
    assert app["match_materials_to_script"] is True
    assert app["upload_post_auto_upload"] is False
    assert ui["video_language"] == "pt-BR"
    assert ui["video_aspect_pexels"] == "9:16"
    assert ui["video_concat_mode"] == "sequential"
    assert ui["video_clip_duration"] == 3
    assert ui["voice_name"] == "pt-BR-FranciscaNeural-Female"
    assert ui["bgm_volume"] == 0.12


def test_fermente_preset_reads_secrets_from_environment(monkeypatch):
    monkeypatch.setenv("FERMENTE_OPENAI_API_KEY", "openai-test")
    monkeypatch.setenv("FERMENTE_PEXELS_API_KEY", "pexels-a,pexels-b")
    monkeypatch.setenv("FERMENTE_PIXABAY_API_KEY", "pixabay-test")
    monkeypatch.setenv("FERMENTE_ENGINE_API_KEY", "engine-test")
    monkeypatch.setenv("FERMENTE_FISH_API_KEY", "fish-test")

    cfg = fermente_bootstrap.build_config()

    assert cfg["app"]["openai_api_key"] == "openai-test"
    assert cfg["app"]["pexels_api_keys"] == ["pexels-a", "pexels-b"]
    assert cfg["app"]["pixabay_api_keys"] == ["pixabay-test"]
    assert cfg["app"]["api_key"] == "engine-test"
    assert cfg["fish_audio"]["api_key"] == "fish-test"
