"""Static shot segments, content-addressed resume, concat and Vietnamese subtitles."""

from __future__ import annotations

import hashlib
import subprocess
import tempfile
from pathlib import Path

from .hashing import canonical_json, sha256_file
from .shots import load_shots
from .workspace import UserError, atomic_write_bytes, project_dir

FONTS = Path(__file__).resolve().parent / "fonts"
VIDEO = ["-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30", "-threads", "1"]
AUDIO = ["-c:a", "aac", "-ar", "48000", "-ac", "2"]
SCALE = "scale=1920:1080:force_original_aspect_ratio=decrease"


def run_ffmpeg(args: list[str], cwd: Path | None = None) -> str:
    """Run within the command budget; return stderr for FFmpeg measurement filters."""
    try:
        proc = subprocess.run(["ffmpeg", "-v", "error", "-y", *args], cwd=cwd,
                              capture_output=True, text=True, timeout=240)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise UserError(f"ffmpeg failed: {exc}") from exc
    if proc.returncode:
        raise UserError(f"ffmpeg failed: {proc.stderr.strip()}")
    return proc.stderr


def _segment(shot: dict, target: Path) -> None:
    args, filters = [], []
    for i, path in enumerate(shot["images"]):
        args += ["-loop", "1", "-framerate", "30", "-i", str(path)]
        # Transparent padding on upper layers preserves the lower image.
        color = "black" if i == 0 else "black@0"
        filters.append(f"[{i}:v]{SCALE},format=rgba,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color={color},setsar=1[v{i}]")
    count, layer = len(shot["images"]), "v0"
    for i in range(1, count):
        filters.append(f"[{layer}][v{i}]overlay=0:0:format=auto[o{i}]")
        layer = f"o{i}"
    if shot["audio"]:
        args += ["-i", str(shot["audio"])]
    else:
        args += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
    filters.append(f"[{count}:a]apad[a]")
    with tempfile.TemporaryDirectory(dir=target.parent) as temp:
        output = Path(temp) / "segment.mp4"
        run_ffmpeg([*args, "-filter_complex_threads", "1", "-filter_complex", ";".join(filters),
              "-map", f"[{layer}]", "-map", "[a]", "-t", str(shot["duration_s"]),
              *VIDEO, *AUDIO, str(output)])
        output.replace(target)


def _timestamp(seconds: float) -> str:
    ms = round(seconds * 1000)
    hours, ms = divmod(ms, 3600000)
    minutes, ms = divmod(ms, 60000)
    seconds, ms = divmod(ms, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{ms:03}"


def srt_cues(shots: list[dict]) -> tuple[bytes, list[str]]:
    """Build captions on the nominal shot timeline, independent of transitions."""
    cues, elapsed = [], 0.0
    for shot in shots:
        end = elapsed + shot["duration_s"]
        if shot["subtitle"].strip():
            text = "\n".join(line for line in shot["subtitle"].splitlines() if line.strip())
            cues.append(f"{len(cues) + 1}\n{_timestamp(elapsed)} --> {_timestamp(end)}\n{text}\n\n")
        elapsed = end
    return "".join(cues).encode("utf-8"), cues


def subtitle_filter(stage: Path, subtitles: bytes, cues: list[str]) -> str:
    """Stage safe local filenames and the bundled font for subtitle burning."""
    atomic_write_bytes(stage / "subtitles.srt", subtitles)
    (stage / "fonts").symlink_to(FONTS, target_is_directory=True)
    return "subtitles=subtitles.srt:fontsdir=fonts:force_style='FontName=Be Vietnam Pro'" if cues else "null"


def build_animatic(workspace: Path, project_id: str) -> tuple[int, int, Path]:
    pdir = project_dir(workspace, project_id).resolve()
    shots = load_shots(pdir)  # Validate the complete list before creating output.
    planned = []
    for shot in shots:
        inputs = [*shot["images"], *([shot["audio"]] if shot["audio"] else [])]
        key = hashlib.sha256(canonical_json({
            "assets": [sha256_file(p) for p in inputs], "images": len(shot["images"]),
            "duration_s": shot["duration_s"], "video": VIDEO, "audio": AUDIO,
            "scale": SCALE, "pipeline": "static-overlay-apad-v1",
        }).encode("utf-8")).hexdigest()
        planned.append((shot, key))
    out = pdir / "animatic"
    cache = out / "segments"
    cache.mkdir(parents=True, exist_ok=True)
    built = reused = 0
    segments = []
    subtitles, cues = srt_cues(shots)
    elapsed = sum(shot["duration_s"] for shot in shots)
    for shot, key in planned:
        segment = cache / f"{key}.mp4"
        if segment.is_file():
            reused += 1
        else:
            _segment(shot, segment)
            built += 1
        segments.append(segment)
    target = out / "animatic.mp4"
    with tempfile.TemporaryDirectory(dir=out) as temp:
        stage = Path(temp)
        # Local filenames keep FFmpeg filter/concat quoting independent of workspace names.
        for i, segment in enumerate(segments):
            (stage / f"{i}.mp4").symlink_to(segment)
        listing = "".join(f"file '{i}.mp4'\nduration {shot['duration_s']}\n" for i, shot in enumerate(shots))
        atomic_write_bytes(stage / "concat.txt", listing.encode())
        run_ffmpeg(["-f", "concat", "-safe", "0", "-i", "concat.txt", "-c", "copy", "joined.mp4"], stage)
        vf = subtitle_filter(stage, subtitles, cues)
        run_ffmpeg(["-i", "joined.mp4", "-vf", vf, *VIDEO, "-c:a", "copy", "-t", str(elapsed),
              "-movflags", "+faststart", "animatic.mp4"], stage)
        atomic_write_bytes(out / "subtitles.srt", subtitles)
        (stage / "animatic.mp4").replace(target)
    return built, reused, target
