#!/usr/bin/env python3
"""Small no-key Edge TTS verification used locally and by CI."""

from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
from pathlib import Path

import edge_tts


async def generate(text: str, voice: str, output: Path) -> None:
    await edge_tts.Communicate(text, voice=voice).save(str(output))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--voice", default="en-US-AndrewNeural")
    parser.add_argument("--text", default="FERMENTE Edge TTS technical smoke test.")
    parser.add_argument("--output", default="/tmp/fermente-edge-tts-smoke.mp3")
    args = parser.parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    asyncio.run(generate(args.text, args.voice, output))
    probe = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration,format_name",
            "-of",
            "json",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    details = json.loads(probe.stdout)["format"]
    duration = float(details.get("duration", 0) or 0)
    if not output.is_file() or output.stat().st_size < 512 or duration <= 0:
        raise SystemExit("Edge TTS smoke produced an invalid audio file")
    print(
        json.dumps(
            {
                "voice": args.voice,
                "file": str(output),
                "duration_seconds": duration,
                "format": details.get("format_name"),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
