from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path

import toml

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "config.example.toml"
TARGET = ROOT / "config.toml"


def _env(*names: str) -> str:
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return ""


def _csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def build_config(existing: dict | None = None) -> dict:
    cfg = toml.load(EXAMPLE)
    existing = existing or {}

    for section, value in existing.items():
        if isinstance(value, dict) and isinstance(cfg.get(section), dict):
            cfg[section].update(value)
        else:
            cfg[section] = value

    cfg["log_level"] = "INFO"
    cfg["listen_host"] = "127.0.0.1"
    cfg["project_name"] = "Fermente Video Engine"
    cfg["project_description"] = "FERMENTE — Ideias que crescem"

    app = cfg.setdefault("app", {})
    app.update(
        {
            "llm_provider": "openai",
            "video_source": "pexels",
            "match_materials_to_script": True,
            "subtitle_provider": "edge",
            "upload_post_enabled": False,
            "upload_post_auto_upload": False,
        }
    )

    ui = cfg.setdefault("ui", {})
    ui.update(
        {
            "language": "pt",
            "video_language": "pt-BR",
            "paragraph_number": 3,
            "video_concat_mode": "sequential",
            "video_transition_mode": "None",
            "video_aspect_pexels": "9:16",
            "video_aspect_pixabay": "9:16",
            "video_aspect_coverr": "9:16",
            "video_clip_duration": 3,
            "video_clip_speed": 1.0,
            "video_count": 1,
            "voice_name": "pt-BR-FranciscaNeural-Female",
            "voice_volume": 1.0,
            "voice_rate": 1.0,
            "bgm_type": "random",
            "bgm_volume": 0.12,
            "subtitle_enabled": True,
            "subtitle_position": "bottom",
            "font_size": 54,
            "text_fore_color": "#FFFFFF",
            "stroke_color": "#000000",
            "stroke_width": 2.0,
        }
    )

    openai_key = _env("FERMENTE_OPENAI_API_KEY", "OPENAI_API_KEY")
    if openai_key:
        app["openai_api_key"] = openai_key

    pexels = _env("FERMENTE_PEXELS_API_KEY", "PEXELS_API_KEY")
    if pexels:
        app["pexels_api_keys"] = _csv(pexels)

    pixabay = _env("FERMENTE_PIXABAY_API_KEY", "PIXABAY_API_KEY")
    if pixabay:
        app["pixabay_api_keys"] = _csv(pixabay)

    api_key = _env("FERMENTE_ENGINE_API_KEY", "MPT_API_KEY")
    if api_key:
        app["api_key"] = api_key

    fish_key = _env("FERMENTE_FISH_API_KEY", "FISH_API_KEY")
    if fish_key:
        cfg.setdefault("fish_audio", {})["api_key"] = fish_key

    return cfg


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare a safe local config.toml for the FERMENTE video pipeline."
    )
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="ignore an existing config.toml instead of preserving its private settings",
    )
    args = parser.parse_args()

    if not EXAMPLE.exists():
        raise SystemExit(f"missing template: {EXAMPLE}")

    existing = None
    if TARGET.exists() and not args.fresh:
        existing = toml.load(TARGET)
        backup = TARGET.with_suffix(".toml.bak")
        shutil.copy2(TARGET, backup)
        print(f"backup: {backup}")

    cfg = build_config(existing)
    TARGET.write_text(toml.dumps(cfg), encoding="utf-8")

    app = cfg["app"]
    missing = []
    if not app.get("openai_api_key"):
        missing.append("OPENAI_API_KEY")
    if not app.get("pexels_api_keys") and not app.get("pixabay_api_keys"):
        missing.append("PEXELS_API_KEY or PIXABAY_API_KEY")

    print(f"written: {TARGET}")
    print("preset: pt-BR, 9:16, sequential scenes, 3s clips, Edge TTS")
    if missing:
        print("missing for full automatic generation: " + ", ".join(missing))
    else:
        print("FERMENTE automatic generation credentials: ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
