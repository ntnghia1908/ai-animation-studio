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

## Test

```bash
python -m pytest -q
node scripts/quality-gate.mjs
```
