import runpy
from pathlib import Path

from app.fermente.project import FermenteVideoProject


ROOT = Path(__file__).resolve().parents[1]
RENDERER = runpy.run_path(str(ROOT / "scripts/fermente_render_project.py"))


def test_editorial_pilot_is_registered_in_renderer():
    preset = RENDERER["PRESETS"]["editorial-pilot"]
    assert preset["aspect"] == "16:9"


def test_editorial_project_selects_renderer_preset_without_keyerror():
    project = FermenteVideoProject.load(ROOT / "examples/fermente/ai-data-centers-water/project.json")
    assert RENDERER["PRESETS"][project.profile]["aspect"] == "16:9"


def test_existing_renderer_profiles_remain_registered():
    assert {"short-ptbr", "youtube-long"}.issubset(RENDERER["PRESETS"])
