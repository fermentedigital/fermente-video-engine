# FERMENTE production preset

This fork keeps MoneyPrinterTurbo's core pipeline and adds an operational preset for FERMENTE short-form videos.

## Target output

- language: pt-BR
- aspect ratio: 9:16
- typical duration: 30–45 seconds
- material order: sequential and matched to script
- source: Pexels first, Pixabay optional fallback
- narration: Edge TTS by default (`pt-BR-FranciscaNeural-Female`)
- subtitles: enabled, bottom aligned, white with black outline
- background music: low volume
- publishing: disabled until a human explicitly enables it

## Bootstrap

From the repository root:

```bash
uv sync --frozen --python 3.11
uv run python scripts/fermente_bootstrap.py
```

The script creates or updates the ignored local `config.toml`. If one already exists it is backed up to `config.toml.bak` first.

## Credentials

Do not commit credentials. Set environment variables before running the bootstrap:

```bash
export FERMENTE_OPENAI_API_KEY="..."
export FERMENTE_PEXELS_API_KEY="..."
# optional
export FERMENTE_PIXABAY_API_KEY="..."
export FERMENTE_ENGINE_API_KEY="..."
export FERMENTE_FISH_API_KEY="..."
```

`OPENAI_API_KEY`, `PEXELS_API_KEY`, `PIXABAY_API_KEY`, `MPT_API_KEY`, and `FISH_API_KEY` are also accepted as fallbacks.

For full automatic generation, the minimum is one LLM key plus one media-provider key. Edge TTS does not require a TTS API key.

## Generate a first short

After bootstrapping:

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

The final MP4 is written under `storage/tasks/<task-id>/`.

## Visual rules

The production rule is simple: generated or selected media must not contain baked-in captions, logos, UI, timestamps, or storyboard grids. Text belongs to the subtitle/compositing stage. Prefer true vertical footage. If a source frame already has a final composition, use `contain`/fit behavior rather than destructive automatic crop.

Search/material terms should follow narrative order. A typical IPA short should request distinct visual beats such as beer pour, fresh hop cones, boiling wort, hop addition, aroma close-up, style comparison, and tasting—not repeat one generic beer clip across the full narration.

## Fish Audio

Fish Audio is optional. Keep Edge TTS as the zero-cost baseline until visual quality is approved. Once `FERMENTE_FISH_API_KEY` is configured, Fish Audio voices can be selected through the existing MoneyPrinterTurbo TTS support.

## Security

The bootstrap binds the service to `127.0.0.1` by default. If the API is later exposed through a reverse proxy or public server, configure `FERMENTE_ENGINE_API_KEY`, TLS, and network access controls first.

Automatic cross-posting remains disabled by the preset. Publishing should only be enabled after the generated-video quality gate is stable.
