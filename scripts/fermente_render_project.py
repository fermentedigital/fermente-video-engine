#!/usr/bin/env python3
"""Compile a FermenteVideoProject into the existing local-material CLI pipeline."""

from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from app.fermente.project import FermenteVideoProject  # noqa: E402
from app.fermente.quality import evaluate  # noqa: E402

PRESETS = {
    "short-ptbr": {
        "aspect": "9:16",
        "voice": "pt-BR-FranciscaNeural-Female",
        "clip": 3,
    },
    "youtube-long": {"aspect": "16:9", "voice": "en-US-AndrewNeural-Male", "clip": 6},
}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("project")
    p.add_argument("--output-json", default="")
    a = p.parse_args()
    project_path = Path(a.project).resolve()
    project = FermenteVideoProject.load(project_path)
    preset = PRESETS[project.profile]
    base = project_path.parent
    media = project.local_media(base)
    if not media:
        raise SystemExit(
            "This adapter is reproducible only with local_media for every scene; media_query is retained for future licensed providers."
        )
    missing = [str(x) for x in media if not x.is_file()]
    if missing:
        raise SystemExit("missing local media: " + ", ".join(missing))
    cmd = [
        sys.executable,
        "cli.py",
        "--video-subject",
        project.title,
        "--video-script",
        project.script,
        "--video-language",
        project.language,
        "--video-source",
        "local",
        "--video-materials",
        ",".join(str(x) for x in media),
        "--video-aspect",
        preset["aspect"],
        "--video-concat-mode",
        "sequential",
        "--video-clip-duration",
        str(preset["clip"]),
        "--voice-name",
        preset["voice"],
        "--subtitle-enabled",
        "--bgm-type",
        "none",
        "--stop-at",
        "video",
    ]
    run = subprocess.run(cmd, capture_output=True, text=True)
    print(run.stdout)
    print(run.stderr, file=sys.stderr)
    if run.returncode:
        return run.returncode
    task_files = sorted(
        (ROOT / "storage/tasks").glob("*/*.mp4"), key=lambda x: x.stat().st_mtime
    )
    video = task_files[-1]
    srt = video.parent / "subtitle.srt"
    result = evaluate(
        video,
        aspect=preset["aspect"],
        subtitles=srt,
        scene_count=len(project.scenes),
        repeated_media=project.repeated_media(base),
        log_text=run.stdout + run.stderr,
    )
    payload = {
        "project": project.as_dict(),
        "video": str(video),
        "quality_gate": result.as_dict(),
    }
    print(json.dumps(payload, ensure_ascii=False))
    if a.output_json:
        Path(a.output_json).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    return 0 if result.status != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
