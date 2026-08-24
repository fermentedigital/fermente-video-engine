"""Deterministic, non-AI render validation for FERMENTE."""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class QualityResult:
    status: str
    reasons: list[str] = field(default_factory=list)
    details: dict = field(default_factory=dict)

    def as_dict(self):
        return asdict(self)


def _probe(path: Path) -> dict:
    completed = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_format",
            "-show_streams",
            "-of",
            "json",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(completed.stdout)


def evaluate(
    video: str | Path,
    *,
    aspect: str,
    subtitles: str | Path | None = None,
    scene_count: int = 0,
    repeated_media: list[str] | None = None,
    log_text: str = "",
) -> QualityResult:
    video = Path(video)
    failures = []
    warnings = []
    details = {"path": str(video)}
    if not video.is_file():
        return QualityResult("FAIL", ["video file is missing"], details)
    if video.stat().st_size < 1024:
        failures.append("video is implausibly small")
    try:
        probe = _probe(video)
    except Exception as exc:
        return QualityResult("FAIL", [f"ffprobe cannot read video: {exc}"], details)
    streams = probe.get("streams", [])
    fmt = probe.get("format", {})
    duration = float(fmt.get("duration", 0) or 0)
    details["duration_seconds"] = duration
    if duration <= 0:
        failures.append("video duration is zero")
    visual = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    if not visual:
        failures.append("video stream is missing")
    else:
        ratio = visual.get("width", 0) / max(visual.get("height", 1), 1)
        expected = {"16:9": 16 / 9, "9:16": 9 / 16, "1:1": 1}[aspect]
        details["resolution"] = [visual.get("width"), visual.get("height")]
        if abs(ratio - expected) > 0.03:
            failures.append(f"unexpected aspect ratio {ratio:.3f}; expected {aspect}")
    if not audio:
        failures.append("audio stream is missing")
    if subtitles is not None and not Path(subtitles).is_file():
        failures.append("subtitles enabled but SRT is missing")
    if scene_count < 1:
        warnings.append("no scene count supplied")
    if repeated_media:
        warnings.append("repeated media: " + ", ".join(repeated_media))
    if re.search(
        r"(?i)(api[_ -]?key|authorization|bearer)\s*[:=]\s*[^\s]{8,}", log_text
    ):
        failures.append("possible credential in logs")
    return QualityResult(
        "FAIL" if failures else "WARN" if warnings else "PASS",
        failures + warnings,
        details,
    )
