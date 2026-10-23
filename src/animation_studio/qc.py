"""Output measurements and fixed P1a quality checks; never modify the film."""

import hashlib
import re
from pathlib import Path

from .animatic import run_ffmpeg, srt_cues
from .hashing import canonical_json, sha256_file
from .media import _ffmpeg_bytes, _ffprobe, fully_transparent
from .shots import load_shots
from .workspace import UserError, atomic_write_json, project_dir, read_json

# -60 dB misclassifies smoothstep motion on sparse images (0–0.8 s in a 3 s push).
FREEZE_NOISE_DB = -70


def pcm(path: Path) -> bytes:
    return _ffmpeg_bytes(["-i", str(path), "-vn", "-ar", "48000", "-ac", "2", "-f", "s16le", "-"])


def _item(name, passed, measured, threshold, detail="", status=None):
    return dict(name=name, status=status or ("PASS" if passed else "FAIL"),
                measured=measured, threshold=threshold, detail=detail)


def format_check(info):
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), {})
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), {})
    measured = {k: v.get(k) for k in ("width", "height", "sample_aspect_ratio", "r_frame_rate", "avg_frame_rate")}
    measured.update(video=v.get("codec_name"), audio=a.get("codec_name"))
    expected = dict(width=1920, height=1080, sample_aspect_ratio="1:1", r_frame_rate="30/1",
                    avg_frame_rate="30/1", video="h264", audio="aac")
    return _item("format", measured == expected, measured, expected)


def duration_checks(seconds, expected):
    return [_item("duration_match", abs(seconds - expected) <= 0.1 + 1e-9, seconds,
                  dict(expected_s=expected, tolerance_s=0.1)),
            _item("duration_range", 30 <= seconds <= 60, seconds, [30, 60])]


def _cue_times(text):
    result = []
    for block in text.strip().split("\n\n") if text.strip() else []:
        lines = block.splitlines()
        if len(lines) < 3 or not re.fullmatch(r"\d+", lines[0]):
            return None
        match = re.fullmatch(r"(\d{2,}):(\d{2}):(\d{2}),(\d{3}) --> (\d{2,}):(\d{2}):(\d{2}),(\d{3})", lines[1])
        if not match:
            return None
        values = list(map(int, match.groups()))
        result.append([sum(x * m for x, m in zip(values[i:i+4], (3600, 60, 1, 0.001))) for i in (0, 4)])
    return result


def subtitle_check(actual, expected):
    cues, wanted = _cue_times(actual), _cue_times(expected)
    passed = cues is not None and len(cues) == len(wanted) and all(
        start - 0.1 - 1e-9 <= a <= b <= end + 0.1 + 1e-9
        for (a, b), (start, end) in zip(cues, wanted))
    return _item("subtitles", passed, cues, dict(cues=len(wanted), tolerance_s=0.1))


def detection_checks(log, seconds, allowed):
    black = [[float(a), float(b)] for a, b in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", log)]
    frozen, start = [], None
    for event, value in re.findall(r"freeze_(start|end):\s*([\d.]+)", log):
        if event == "start":
            start = float(value)
        elif start is not None:
            frozen.append([start, float(value)])
            start = None
    if start is not None:
        frozen.append([start, seconds])  # freezedetect does not emit freeze_end at EOF.
    # Merge static windows before subtracting their coverage from each frozen span.
    merged = []
    for a, b in sorted(allowed):
        if merged and a <= merged[-1][1] + 1e-6:
            merged[-1][1] = max(b, merged[-1][1])
        else:
            merged.append([a, b])
    uncovered, invalid = [], False
    for start, end in frozen:
        parts, cursor = [], start
        for a, b in merged:
            if a >= end:
                break
            if b <= cursor:
                continue
            if cursor < a:
                parts.append([cursor, a])
            cursor = min(end, b)
        if cursor < end:
            parts.append([cursor, end])
        uncovered.extend(parts)
        invalid |= sum(b - a for a, b in parts) >= 0.5 - 1e-9
    loudness = re.findall(r"I:\s+(-?[\d.]+) LUFS", log)
    integrated = float(loudness[-1]) if loudness else None
    return [_item("black", not black, black, "blackdetect d=0.5; default thresholds"),
            _item("freeze", not invalid, frozen, dict(allowed_s=allowed, duration_s=0.5, noise_db=FREEZE_NOISE_DB),
                  f"outside static windows: {uncovered}" if uncovered else ""),
            _item("loudness", integrated is not None and -17 <= integrated <= -15, integrated, [-17, -15])]


def reproducibility(current, previous, compare):
    if previous and previous.get("input_key") == current["input_key"]:
        if not compare:
            kept = next((x for x in previous.get("checks", []) if x["name"] == "reproducible"), None)
            if kept:
                return kept
        else:
            passed = (abs(current["duration_s"] - previous.get("duration_s", -1)) <= 0.1 + 1e-9
                      and all(current[k] == previous.get(k) for k in ("shots", "audio_pcm_sha256")))
            return _item("reproducible", passed, {k: current[k] for k in ("duration_s", "shots", "audio_pcm_sha256")},
                         "same duration (±0.1 s), shots and audio PCM SHA256")
    return _item("reproducible", True, None, "previous render with same input_key", status="SKIP")


def check_render(workspace: Path, project_id: str, previous=None, *, compare=False) -> dict:
    pdir = project_dir(workspace, project_id).resolve()
    shots = load_shots(pdir)
    film, target = pdir / "render/film.mp4", pdir / "render/qc.json"
    if not film.is_file():
        raise UserError(f"film not found: {film}")
    if not compare:
        previous = read_json(target)
    data = read_json(pdir / "shots.json")
    assets = {p for shot in shots for p in [*shot["images"], *([shot["audio"]] if shot["audio"] else [])]}
    if data.get("music"):
        assets.add(pdir / data["music"])
    key = dict(shots=data, assets={str(p.relative_to(pdir)): sha256_file(p) for p in sorted(assets)},
               pipeline="cover2x-smoothstep-parallax-v1")
    info = _ffprobe(film)
    seconds, elapsed, timeline, allowed = float(info["format"]["duration"]), 0.0, [], []
    for i, shot in enumerate(shots):
        end = elapsed + shot["duration_s"]
        timeline.append([shot["id"], elapsed, end])
        if shot["camera"] == "static":
            allowed.append([elapsed, end + (0.5 if i < len(shots)-1 and shot["transition"] == "crossfade" else 0)])
        elapsed = end
    log = run_ffmpeg(["-nostats", "-v", "info", "-threads", "1", "-i", str(film), "-filter_threads", "1",
                      "-vf", f"blackdetect=d=0.5,freezedetect=n={FREEZE_NOISE_DB}dB:d=0.5", "-af", "ebur128",
                      "-f", "null", "-"])
    srt = film.parent / "subtitles.srt"
    expected, _ = srt_cues(shots)
    transparent = [str(p.relative_to(pdir)) for p in sorted({p for s in shots for p in s["images"]}) if fully_transparent(p)]
    report = dict(input_key=hashlib.sha256(canonical_json(key).encode()).hexdigest(), duration_s=seconds,
                  shots=timeline, audio_pcm_sha256=hashlib.sha256(pcm(film)).hexdigest()
                  if any(s["codec_type"] == "audio" for s in info["streams"]) else None)
    checks = [format_check(info), *duration_checks(seconds, elapsed),
              subtitle_check(srt.read_text(encoding="utf-8") if srt.is_file() else "", expected.decode()),
              *detection_checks(log, seconds, allowed), reproducibility(report, previous, compare),
              _item("layer_alpha", True, transparent, "no fully transparent shot images",
                    status="WARN" if transparent else "PASS", detail=", ".join(transparent))]
    report.update(checks=checks, overall="FAIL" if any(c["status"] == "FAIL" for c in checks) else "PASS")
    atomic_write_json(target, report)
    return report
