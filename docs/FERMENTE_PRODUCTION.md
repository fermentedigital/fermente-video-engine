# FERMENTE production preset

Target: pt-BR vertical short-form videos (9:16), usually 30–45 seconds.

Defaults prepared by `scripts/fermente_bootstrap.py`:
- OpenAI as LLM provider
- Pexels as primary media source
- Pixabay optional fallback
- `match_materials_to_script = true`
- sequential 3-second clips
- Edge TTS `pt-BR-FranciscaNeural-Female`
- subtitles enabled at the bottom
- low background-music volume
- automatic publishing disabled
- API bound to `127.0.0.1`

## Setup

```bash
uv sync --frozen --python 3.11
export FERMENTE_OPENAI_API_KEY="..."
export FERMENTE_PEXELS_API_KEY="..."
uv run python scripts/fermente_bootstrap.py
```

Optional:

```bash
export FERMENTE_PIXABAY_API_KEY="..."
export FERMENTE_ENGINE_API_KEY="..."
export FERMENTE_FISH_API_KEY="..."
```

The bootstrap writes only to the ignored local `config.toml`. Existing configuration is backed up to `config.toml.bak`.

## First automatic short

```bash
uv run python cli.py \
  --video-subject "Por que a cerveja IPA é tão amarga?" \
  --video-language pt-BR \
  --video-source pexels \
  --video-aspect 9:16 \
  --video-concat-mode sequential \
  --video-clip-duration 3 \
  --match-materials-to-script \
  --voice-name pt-BR-FranciscaNeural-Female
```

Output is written under `storage/tasks/<task-id>/`.

## Production rules

Media should be true vertical footage whenever possible. Do not use storyboard grids, baked-in captions, timestamps, logos, or UI as source media. Text belongs to the subtitle/compositing stage. Search terms should follow the narrative order and request distinct visual beats rather than repeating one generic clip.

Fish Audio remains optional until visual quality is approved. Edge TTS is the zero-cost baseline.

Do not enable automatic publishing until the quality gate is stable. If the API is exposed beyond localhost, configure `FERMENTE_ENGINE_API_KEY`, TLS, and network restrictions first.
