# FERMENTE production profiles

FERMENTE is an extension layer over MoneyPrinterTurbo. Files in `app/fermente/`
and `scripts/fermente_*` are FERMENTE-owned; core `app/services/`, WebUI and CLI
remain upstream-compatible.

## `short-ptbr`

pt-BR, vertical 9:16, 30–60 seconds, sequential 3-second clips, Edge TTS
`pt-BR-FranciscaNeural-Female`, subtitles, and no automatic publishing.

## `youtube-long`

Landscape 16:9 (normally 1920×1080), configurable editorial target (initially
7–12 minutes), any language, Edge `en-US-AndrewNeural-Male` as a neutral technical
baseline, subtitles, and no automatic publishing. It does **not** fabricate duration
by repeating narrative or clips: the external editorial package must contain enough
scenes and narration for its intended duration.

Background music is OFF for both profiles. Upstream music files are not a FERMENTE
production dependency. Only own, explicitly commercially licensed, suitable public
domain, or commercially licensed/generated tracks may be added later.

Defaults prepared by `scripts/fermente_bootstrap.py`:
- OpenAI as LLM provider
- Pexels as primary media source
- Pixabay optional fallback
- `match_materials_to_script = true`
- sequential 3-second clips
- Edge TTS `pt-BR-FranciscaNeural-Female`
- subtitles enabled at the bottom
- background music disabled
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

## External editorial project and no-cost horizontal test

`FermenteVideoProject` is a portable JSON package with title, language, profile,
expected duration and ordered scenes. A scene has narrated text plus a media query,
optional local media file, media type and visual instruction. Local media is the
first priority; provider queries are retained for a future licensed-provider adapter.

Create two local test clips next to a project JSON, then run:

```bash
uv run python scripts/fermente_render_project.py examples/fermente/youtube-long-local.json
```

The adapter feeds the existing CLI using ordered local scenes, Edge TTS, SRT subtitles,
FFmpeg and no paid API. It prints a structured `PASS`, `WARN` or `FAIL` quality gate.
For an actual 7–12 minute render, provide a project whose scene narration genuinely
has that duration; the included example is deliberately small and only verifies the pipeline.

Check Edge TTS alone (file, valid format and non-zero duration):

```bash
uv run python scripts/fermente_edge_tts_smoke.py --voice en-US-AndrewNeural
```

## Quality gate

`app/fermente/quality.py` checks file existence and minimum size, ffprobe readability,
duration, expected aspect/resolution, audio/video streams, subtitle presence, scene count,
media repetition and likely credential strings in captured logs. It is intentionally
deterministic; it does not claim to judge editorial quality visually.

Output is written under `storage/tasks/<task-id>/`.

## Production rules

Media should be true vertical footage whenever possible. Do not use storyboard grids, baked-in captions, timestamps, logos, or UI as source media. Text belongs to the subtitle/compositing stage. Search terms should follow the narrative order and request distinct visual beats rather than repeating one generic clip.

Fish Audio remains optional until visual quality is approved. Edge TTS is the zero-cost baseline.

Do not enable automatic publishing until the quality gate is stable. If the API is exposed beyond localhost, configure `FERMENTE_ENGINE_API_KEY`, TLS, and network restrictions first.

## Credentials for production

No secret belongs in Git. `FERMENTE_OPENAI_API_KEY` is only needed for automatic
script/term generation; `FERMENTE_PEXELS_API_KEY` or `FERMENTE_PIXABAY_API_KEY` only
for provider media; Fish needs its own key. A production YouTube upload would later
require a Google OAuth client and channel authorization. None are needed for the local test.
