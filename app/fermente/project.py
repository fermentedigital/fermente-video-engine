"""Portable editorial-project contract for FERMENTE renders."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal


Profile = Literal["short-ptbr", "editorial-pilot", "youtube-long"]


@dataclass(frozen=True)
class Scene:
    id: str
    narration: str
    media_query: str = ""
    local_media: str = ""
    media_type: Literal["video", "image", "auto"] = "auto"
    expected_duration_seconds: float | None = None
    visual_instruction: str = ""
    priority: int = 0


@dataclass(frozen=True)
class FermenteVideoProject:
    title: str
    language: str
    profile: Profile
    scenes: list[Scene]
    expected_duration_seconds: int | None = None
    output: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)

    @property
    def script(self) -> str:
        return "\n\n".join(
            scene.narration.strip() for scene in self.scenes if scene.narration.strip()
        )

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.title.strip():
            errors.append("title is required")
        if not self.language.strip():
            errors.append("language is required")
        if not self.scenes:
            errors.append("at least one scene is required")
        ids = [scene.id for scene in self.scenes]
        if len(ids) != len(set(ids)):
            errors.append("scene ids must be unique")
        for scene in self.scenes:
            if not scene.id.strip() or not scene.narration.strip():
                errors.append("each scene needs id and narration")
        if (
            self.profile == "youtube-long"
            and self.expected_duration_seconds
            and self.expected_duration_seconds < 420
        ):
            errors.append("youtube-long expected_duration_seconds must be at least 420")
        if self.profile == "editorial-pilot" and self.expected_duration_seconds and not 60 <= self.expected_duration_seconds <= 180:
            errors.append("editorial-pilot expected_duration_seconds must be between 60 and 180")
        return errors

    def local_media(self, base: Path) -> list[Path]:
        return [
            (base / scene.local_media).resolve()
            for scene in self.scenes
            if scene.local_media
        ]

    def repeated_media(self, base: Path) -> list[str]:
        paths = [str(path) for path in self.local_media(base)]
        return sorted({path for path in paths if paths.count(path) > 1})

    @classmethod
    def load(cls, path: str | Path) -> "FermenteVideoProject":
        source = Path(path)
        data = json.loads(source.read_text(encoding="utf-8"))
        scenes = [Scene(**scene) for scene in data.pop("scenes", [])]
        project = cls(scenes=scenes, **data)
        errors = project.validate()
        if errors:
            raise ValueError("invalid FermenteVideoProject: " + "; ".join(errors))
        return project

    def as_dict(self) -> dict:
        return asdict(self)
