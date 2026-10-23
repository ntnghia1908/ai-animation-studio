# ai-animation-studio

## Setup

```bash
conda create -n animation-studio python=3.12
conda activate animation-studio
pip install -e ".[dev]"      # needs ffmpeg/ffprobe on PATH
cp config.example.toml config.toml   # workspace = "~/animation-studio-data"
```

## Usage

```bash
python -m animation_studio import-story my-story story.txt --title "Title" --source "URL" --rights "public domain"
python -m animation_studio import-assets my-story --kind image --license CC0 --source-tool comfyui a.png b.png
```

`--workspace DIR` overrides `config.toml`. Data goes to `<workspace>/projects/<project>/{story,assets}/`.

## Animatic

Write `<workspace>/projects/<project>/shots.json` using paths from `assets/manifest.json`:

```json
{"version": 1, "shots": [
  {"id": "s01", "image": "assets/images/<file>.png", "audio": "assets/audio/<voice>.wav", "subtitle": "Ngày xưa…"},
  {"id": "s02", "layers": ["assets/images/<bg>.png", "assets/images/<fg>.png"], "duration_s": 2}
]}
```

Use either `image` or 2–3 `layers` (bottom to top). Without audio, `duration_s` is required;
with audio, the shot lasts the longer of `duration_s` and the imported audio duration.
Optional `camera` (`static`, `push_in`, `pull_out`, `pan_left`, `pan_right`, `parallax`)
and `transition` (`cut`, `crossfade`) are validated; this animatic uses static layers and straight cuts.
`parallax` requires layers. Shot IDs must be unique lowercase letters/digits/`_`/`-`,
starting with a letter or digit, up to 32 characters.

```bash
python -m animation_studio animatic my-story
```

Output: `<project>/animatic/animatic.mp4` (1080p, 30 fps, H.264/AAC), plus `subtitles.srt`.
Vietnamese subtitles use the bundled Be Vietnam Pro font (SIL OFL).
Unchanged segments in `animatic/segments/` are reused; deleting that cache is safe.

## Render

```bash
python -m animation_studio render my-story
```

Uses the same shots, with smooth camera moves, layered parallax and 0.5 s crossfades.
Use 16:9 images: render fills the frame and crops excess edges. Optional root field
`"music": "assets/audio/<music>.wav"` selects imported audio from the manifest;
render loops/trims it and ducks it under voices. Animatic ignores this field.
Output: `<project>/render/{film.mp4, subtitles.srt, segments/}` (1080p H.264/AAC,
30 fps, target −16 LUFS). Unchanged video segments are reused; the cache is disposable.

## Test

```bash
python -m pytest -q
node scripts/quality-gate.mjs
```
