"""Motion segments, timeline transitions and deterministic voice/music mastering."""

from __future__ import annotations

import hashlib
import json
import math
import tempfile
from pathlib import Path

from .animatic import AUDIO, VIDEO, run_ffmpeg, srt_cues, subtitle_filter
from .hashing import canonical_json, sha256_file
from .shots import load_shots
from .workspace import atomic_write_bytes, project_dir, read_json

LOUDNESS = "loudnorm=I=-16:TP=-1.5:LRA=11"


def _segment(shot: dict, seconds: float, target: Path) -> None:
    args, filters = [], []
    camera = shot["camera"]
    # Integer crop steps on this canvas are at most half an output pixel.
    progress = f"min(on/{max(shot['duration_s'] * 30 - 1, 1)},1)"
    ease = f"({progress})*({progress})*(3-2*({progress}))"
    for i, image in enumerate(shot["images"]):
        args += ["-framerate", "30", "-i", str(image)]
        w, h = (4608, 2592) if camera == "parallax" else (3840, 2160)
        base = (f"[{i}:v]scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos,"
                f"format=rgba,crop={w}:{h},setsar=1,loop=-1:1:0,setpts=N/(30*TB)")
        if camera == "parallax":
            amplitude = (0.02, 0.05, 0.08)[i]
            base += f",crop=3840:2160:x='(iw-ow)/2+3840*{amplitude}*({ease.replace('on/', 'n/')}-0.5)':y='(ih-oh)/2':exact=1"
        filters.append(f"{base}[v{i}]")
    layer = "v0"
    for i in range(1, len(shot["images"])):
        filters.append(f"[{layer}][v{i}]overlay=0:0:format=auto[o{i}]")
        layer = f"o{i}"
    motion = ""
    if camera not in ("static", "parallax"):
        zoom = f"1+0.15*({ease})" if camera == "push_in" else f"1.15-0.15*({ease})"
        x = "(iw-iw/zoom)/2"
        if camera in ("pan_left", "pan_right"):
            zoom = "1.15"
            fraction = f"1-({ease})" if camera == "pan_left" else ease
            x = f"(iw-iw/zoom)*({fraction})"
        motion = f"format=yuv444p,zoompan=z='{zoom}':x='{x}':y='(ih-ih/zoom)/2':d=1:s=3840x2160:fps=30,"
    filters.append(f"[{layer}]{motion}scale=1920:1080:flags=lanczos,setsar=1[v]")
    with tempfile.TemporaryDirectory(dir=target.parent) as temp:
        output = Path(temp) / "segment.mp4"
        run_ffmpeg([*args, "-filter_complex_threads", "1", "-filter_complex", ";".join(filters),
                    "-map", "[v]", "-an", "-t", str(seconds), *VIDEO, str(output)])
        output.replace(target)


def _audio(shots: list[dict], music: Path | None, total: float, stage: Path) -> None:
    args = ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
    filters, voices, elapsed = [f"[0:a]atrim=duration={total}[silence]"], ["[silence]"], 0.0
    for shot in shots:
        if shot["audio"]:
            index = len(voices)
            args += ["-i", str(shot["audio"])]
            filters.append(f"[{index}:a]aresample=48000,aformat=channel_layouts=stereo,"
                           f"atrim=duration={shot['duration_s']},asetpts=PTS-STARTPTS,"
                           f"adelay={round(elapsed * 48000)}S:all=1[a{index}]")
            voices.append(f"[a{index}]")
        elapsed += shot["duration_s"]
    filters.append(f"{''.join(voices)}amix=inputs={len(voices)}:duration=first:normalize=0[voice]")
    output = "voice"
    if music:
        args += ["-stream_loop", "-1", "-i", str(music)]
        filters += ["[voice]asplit[voiceout][sidechain]",
                    f"[{len(voices)}:a]aresample=48000,aformat=channel_layouts=stereo,"
                    f"atrim=duration={total},asetpts=PTS-STARTPTS,volume=-18dB,"
                    f"afade=t=out:st={max(0, total - 1)}:d={min(1, total)}[music]",
                    "[music][sidechain]sidechaincompress=threshold=0.005:ratio=20:attack=5:release=100[ducked]",
                    "[voiceout][ducked]amix=inputs=2:duration=first:normalize=0[mix]"]
        output = "mix"
    run_ffmpeg([*args, "-filter_complex_threads", "1", "-filter_complex", ";".join(filters),
                "-map", f"[{output}]", "-t", str(total), "-c:a", "pcm_s24le", "mixed.wav"], stage)
    measured = run_ffmpeg(["-nostats", "-v", "info", "-i", "mixed.wav", "-af", f"{LOUDNESS}:print_format=json",
                           "-f", "null", "-"], stage)
    # Decode one object, allowing FFmpeg progress/log lines after its closing brace.
    stats, _ = json.JSONDecoder().raw_decode(measured, measured.rfind("{"))
    normalizer = "anull"
    if math.isfinite(float(stats["input_i"])) and float(stats["input_i"]) >= -70:
        normalizer = (f"{LOUDNESS}:linear=true:measured_I={stats['input_i']}:measured_TP={stats['input_tp']}:"
                      f"measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}:"
                      f"offset={stats['target_offset']}")
    run_ffmpeg(["-i", "mixed.wav", "-af", normalizer, "-ar", "48000", "-ac", "2",
                "-c:a", "pcm_s24le", "audio.wav"], stage)


def build_render(workspace: Path, project_id: str) -> tuple[int, int, Path]:
    pdir = project_dir(workspace, project_id).resolve()
    shots = load_shots(pdir)  # Validate music and every shot before creating output.
    music = read_json(pdir / "shots.json").get("music")
    total = sum(shot["duration_s"] for shot in shots)
    out = pdir / "render"
    cache = out / "segments"
    cache.mkdir(parents=True, exist_ok=True)
    segments, built, reused = [], 0, 0
    for i, shot in enumerate(shots):
        seconds = shot["duration_s"] + (0.5 if i < len(shots) - 1 and shot["transition"] == "crossfade" else 0)
        key = hashlib.sha256(canonical_json({
            "assets": [sha256_file(p) for p in shot["images"]], "duration_s": seconds,
            "motion_duration_s": shot["duration_s"], "camera": shot["camera"], "video": VIDEO,
            "pipeline": "cover2x-smoothstep-parallax-v1",
        }).encode("utf-8")).hexdigest()
        segment = cache / f"{key}.mp4"
        if segment.is_file():
            reused += 1
        else:
            _segment(shot, seconds, segment)
            built += 1
        segments.append(segment)
    subtitles, cues = srt_cues(shots)
    target = out / "film.mp4"
    with tempfile.TemporaryDirectory(dir=out) as temp:
        stage = Path(temp)
        _audio(shots, pdir / music if music else None, total, stage)
        vf = subtitle_filter(stage, subtitles, cues)
        args, filters = [], []
        for i, segment in enumerate(segments):
            args += ["-i", str(segment)]
            filters.append(f"[{i}:v]settb=AVTB,setpts=PTS-STARTPTS[v{i}]")
        layer, elapsed = "v0", shots[0]["duration_s"]
        for i in range(1, len(shots)):
            if shots[i - 1]["transition"] == "crossfade":
                # Pad very short incoming shots so xfade can finish; later cuts/final -t trim it.
                filters.append(f"[v{i}]tpad=stop_mode=clone:stop_duration=0.5[p{i}]")
                filters.append(f"[{layer}][p{i}]xfade=duration=0.5:offset={elapsed}[j{i}]")
            else:
                filters.append(f"[{layer}]trim=duration={elapsed},setpts=PTS-STARTPTS[c{i}]")
                filters.append(f"[c{i}][v{i}]concat=n=2:v=1:a=0[j{i}]")
            layer = f"j{i}"
            elapsed += shots[i]["duration_s"]
        filters.append(f"[{layer}]{vf}[video]")
        run_ffmpeg([*args, "-i", "audio.wav", "-filter_complex_threads", "1", "-filter_complex",
                    ";".join(filters), "-map", "[video]", "-map", f"{len(segments)}:a", *VIDEO, *AUDIO,
                    "-t", str(total), "-movflags", "+faststart", "film.mp4"], stage)
        atomic_write_bytes(out / "subtitles.srt", subtitles)
        (stage / "film.mp4").replace(target)
    return built, reused, target
