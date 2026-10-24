"""Media probing with ffprobe (pattern from youtube-auto-short@f47813d:src/auto_short/compilation/probe.py)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .workspace import UserError


def _ffmpeg_bytes(args: list[str]) -> bytes:
    """Decode binary media; run_ffmpeg is intended for text measurement logs."""
    try:
        proc = subprocess.run(["ffmpeg", "-v", "error", *args], capture_output=True, timeout=240)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise UserError(f"ffmpeg failed: {exc}") from exc
    if proc.returncode:
        raise UserError(f"ffmpeg failed: {proc.stderr.decode(errors='replace').strip()}")
    return proc.stdout


def fully_transparent(path: Path) -> bool:
    """Only decode alpha-capable image formats; retain even tiny 16-bit alpha."""
    fmt = probe(path, "image")["pix_fmt"]
    if not fmt.startswith(("rgba", "bgra", "argb", "abgr", "yuva", "gbrap", "ya", "pal8")):
        return False
    alpha = _ffmpeg_bytes(["-i", str(path), "-vf", "format=rgba64le,alphaextract",
                           "-frames:v", "1", "-pix_fmt", "gray16le", "-f", "rawvideo", "-"])
    return bool(alpha) and not any(alpha)


def _ffprobe(path: Path) -> dict:
    try:
        proc = subprocess.run(
            ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
            capture_output=True, text=True, timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise UserError(f"ffprobe failed for {path}: {exc}") from exc
    if proc.returncode != 0:
        raise UserError(f"ffprobe failed for {path}: {proc.stderr.strip() or 'unreadable media'}")
    return json.loads(proc.stdout or "{}")


def probe(path: Path, kind: str) -> dict:
    """Return image {width,height,pix_fmt} or audio {duration_s,sample_rate,channels}."""
    info = _ffprobe(path)
    want = "video" if kind == "image" else "audio"
    stream = next((s for s in info.get("streams", []) if s.get("codec_type") == want), None)
    if stream is None:
        raise UserError(f"{path}: no {want} stream, not a valid {kind}")
    if kind == "image":
        if not all(stream.get(k) for k in ("width", "height", "pix_fmt")):
            raise UserError(f"{path}: not a valid image (incomplete stream info)")
        return {"width": stream["width"], "height": stream["height"], "pix_fmt": stream["pix_fmt"]}
    try:
        duration = float(stream.get("duration") or info["format"]["duration"])
    except (KeyError, ValueError) as exc:
        raise UserError(f"{path}: cannot determine audio duration") from exc
    return {
        "duration_s": round(duration, 3),
        "sample_rate": int(stream["sample_rate"]),
        "channels": stream["channels"],
    }
