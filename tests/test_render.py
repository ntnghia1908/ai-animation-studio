import array
import hashlib
import json
import math
import re
import shutil
import subprocess

import pytest

from animation_studio import animatic, render
from animation_studio.__main__ import main
from animation_studio.assets import import_assets
from animation_studio.hashing import canonical_json, sha256_file
from animation_studio.workspace import UserError, atomic_write_json, read_json


def ffmpeg(*args):
    return subprocess.run(["ffmpeg", "-v", "error", *map(str, args)],
                          check=True, capture_output=True, timeout=240)


def frame(path, seconds):
    return list(zip(*[iter(ffmpeg("-ss", seconds, "-i", path, "-vf", "scale=320:180,format=rgb24",
                                 "-frames:v", 1, "-f", "rawvideo", "-").stdout)] * 3))


def box(pixels, channel):
    points = [(i % 320, i // 320) for i, p in enumerate(pixels)
              if p[channel] > 160 and sum(p) - p[channel] < 100]
    assert points
    xs, ys = zip(*points)
    return (sum(xs) / len(xs), sum(ys) / len(ys), max(xs) - min(xs))


def pcm(path):
    return ffmpeg("-i", path, "-vn", "-f", "s16le", "-").stdout


@pytest.mark.parametrize("suffix", ["\nsize=N/A time=00:00:02.00 speed=10x\r\n", "\n"])
def test_loudnorm_measurement_ignores_trailing_progress(tmp_path, monkeypatch, suffix):
    stats = {"input_i": "-24", "input_tp": "-10", "input_lra": "0",
             "input_thresh": "-34", "target_offset": "0"}
    calls = []

    def fake_ffmpeg(args, cwd=None):
        calls.append(args)
        return 'earlier log {"ignored": true}\n' + json.dumps(stats) + suffix

    monkeypatch.setattr(render, "run_ffmpeg", fake_ffmpeg)
    render._audio([], None, 2, tmp_path)
    assert "-nostats" in calls[1]
    applied = calls[-1][calls[-1].index("-af") + 1]
    assert "measured_I=-24" in applied and "measured_thresh=-34" in applied


@pytest.mark.parametrize("cameras", [("push_in", "pull_out"), ("pan_left", "pan_right"), ("static", "static")])
def test_camera_direction_and_cover(shot_project, make_png, cameras):
    ws, pdir, _ = shot_project
    import_assets(ws, "p1", "image", [make_png("detail.png", detail=True)],
                  {"license": "CC0", "source_tool": "ffmpeg"})
    image = read_json(pdir / "assets/manifest.json")["assets"][-1]["path"]
    atomic_write_json(pdir / "shots.json", {"version": 1, "shots": [
        dict(id=f"s{i}", image=image, duration_s=0.6, camera=c) for i, c in enumerate(cameras)]})
    _, _, out = render.build_render(ws, "p1")
    for i, camera in enumerate(cameras):
        first, last = frame(out, i * 0.6), frame(out, i * 0.6 + 17 / 30)
        x0, _, w0 = box(first, 1)
        x1, _, w1 = box(last, 1)
        assert first[0][0] > 230  # cover fills the edge, including for 4:3 input
        if camera in ("push_in", "pull_out"):
            direction = 1 if camera == "push_in" else -1
            assert direction * (w1 - w0) >= 3 and direction * (x0 - x1) > 4
        elif camera.startswith("pan"):
            assert (x1 - x0) * (1 if camera == "pan_left" else -1) > 20
        else:
            assert max(abs(a - b) for p, q in zip(first, last) for a, b in zip(p, q)) < 12


def test_parallax_layers_move_at_different_speeds(shot_project, make_png):
    ws, pdir, _ = shot_project
    import_assets(ws, "p1", "image", [make_png("bg.png", detail=True),
                  make_png("fg.png", alpha=True, color="blue", patch=True)],
                  {"license": "CC0", "source_tool": "ffmpeg"})
    layers = [a["path"] for a in read_json(pdir / "assets/manifest.json")["assets"][-2:]]
    atomic_write_json(pdir / "shots.json", {"version": 1, "shots": [
        dict(id="p", layers=layers, duration_s=0.6, camera="parallax"),
        dict(id="s", image=layers[0], duration_s=0.2)]})
    _, _, out = render.build_render(ws, "p1")
    first, last = frame(out, 0), frame(out, 17 / 30)
    shifts = [box(first, c)[0] - box(last, c)[0] for c in (1, 2)]
    assert shifts[0] > 3 and shifts[1] > shifts[0] * 1.5


@pytest.mark.parametrize("transition,second", [("cut", "cut"), ("crossfade", "cut"),
                                               ("cut", "crossfade"), ("crossfade", "crossfade")])
def test_timeline_format_subtitles_and_silence(shot_project, transition, second, monkeypatch):
    ws, pdir, assets = shot_project
    shots = [dict(id="a", image=assets[0], duration_s=0.6, transition=transition),
             dict(id="b", image=assets[1], duration_s=0.8, transition=second, subtitle="Ngày xưa có một thư sinh…"),
             dict(id="c", image=assets[0], duration_s=0.6, transition="crossfade")]
    atomic_write_json(pdir / "shots.json", {"version": 1, "shots": shots})
    calls, real = [], render.run_ffmpeg

    def record(args, cwd=None):
        calls.append(args)
        if args[-1] == "film.mp4":
            assert (cwd / "fonts").resolve() == animatic.FONTS
        return real(args, cwd)

    monkeypatch.setattr(render, "run_ffmpeg", record)
    _, _, out = render.build_render(ws, "p1")
    info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format",
                                     "-of", "json", str(out)], check=True, capture_output=True).stdout)
    v, a = info["streams"]
    assert (v["width"], v["height"], v["r_frame_rate"], v["codec_name"]) == (1920, 1080, "30/1", "h264")
    assert (a["codec_name"], a["sample_rate"], a["channels"]) == ("aac", "48000", 2)
    assert abs(float(info["format"]["duration"]) - 2) <= 0.1
    assert not any(pcm(out))
    assert (out.parent / "subtitles.srt").read_text() == (
        "1\n00:00:00,600 --> 00:00:01,400\nNgày xưa có một thư sinh…\n\n")
    assert any("FontName=Be Vietnam Pro" in arg for call in calls for arg in call)
    burned = ffmpeg("-ss", 1, "-i", out, "-vf", "crop=1440:240:240:840,format=rgb24",
                    "-frames:v", 1, "-f", "rawvideo", "-").stdout
    assert sum(min(burned[i:i+3]) > 220 for i in range(0, len(burned), 3)) > 100
    before, boundary, middle, after = [frame(out, t)[80 * 320 + 20] for t in (17/30, 18/30, 0.85, 1.4)]
    assert before[0] > 240
    assert after[0 if second == "cut" else 2] > 240  # boundary stays at exactly 1.4 s
    if second == "crossfade":
        mid = frame(out, 1.65)[80 * 320 + 20]
        assert 80 < mid[0] < 180 and 80 < mid[2] < 180
    if transition == "crossfade":
        assert boundary[0] > 240 and 80 < middle[0] < 180 and 80 < middle[2] < 180
    else:
        assert boundary[2] > 240 and middle[2] > 240
    for segment in (out.parent / "segments").glob("*.mp4"):
        assert not subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
                                   "stream=codec_name", "-of", "csv=p=0", str(segment)],
                                  check=True, capture_output=True).stdout


@pytest.mark.parametrize("music", [False, True])
def test_loudness_ducking_resume_pcm_and_atomic_output(shot_project, make_wav, tmp_path, music, monkeypatch, capsys):
    ws, pdir, assets = shot_project
    data = {"version": 1, "shots": [dict(id="a", image=assets[0], duration_s=1),
            dict(id="b", image=assets[1], duration_s=2, audio=assets[3]),
            dict(id="c", image=assets[0], duration_s=1)]}
    if music:
        import_assets(ws, "p1", "audio", [make_wav("music.wav", seconds=0.6, frequency=880)],
                      {"license": "CC0", "source_tool": "ffmpeg"})
        data["music"] = read_json(pdir / "assets/manifest.json")["assets"][-1]["path"]
    atomic_write_json(pdir / "shots.json", data)
    real, calls = render.run_ffmpeg, []

    def record(args, cwd=None):
        calls.append(args)
        result = real(args, cwd)
        if args[-1] == "mixed.wav":
            shutil.copyfile(cwd / "mixed.wav", tmp_path / "mixed.wav")
        return result

    monkeypatch.setattr(render, "run_ffmpeg", record)
    assert main(["--workspace", str(ws), "render", "p1"]) == 0
    assert "render built=2 reused=1 ->" in capsys.readouterr().out
    out = pdir / "render/film.mp4"
    measured = ffmpeg("-v", "info", "-i", out, "-af", "ebur128", "-f", "null", "-").stderr.decode()
    assert abs(float(re.findall(r"I:\s+(-?[\d.]+) LUFS", measured)[-1]) + 16) <= 1
    assert any("linear=true" in arg for call in calls for arg in call)
    raw = array.array("f", ffmpeg("-i", tmp_path / "mixed.wav", "-ac", 1, "-ar", 48000,
                                 "-f", "f32le", "-").stdout)
    if music:
        # Correlation isolates 880 Hz music from the simultaneous 440 Hz voice.
        def level(start):
            window = raw[round(start * 48000):round((start + 0.5) * 48000)]
            return abs(sum(v * complex(math.cos(2*math.pi*880*i/48000),
                                       math.sin(2*math.pi*880*i/48000)) for i, v in enumerate(window)))
        assert 20 * math.log10(level(0.2) / level(1.2)) >= 6
    else:
        assert not any(raw[:48000]) and max(raw[48000:96000]) > 0.05 and not any(raw[96000:])
    digest = hashlib.sha256(pcm(out)).hexdigest()
    before = {p.name: p.stat().st_mtime_ns for p in (out.parent / "segments").glob("*.mp4")}
    assert render.build_render(ws, "p1")[:2] == (0, 3)
    assert hashlib.sha256(pcm(out)).hexdigest() == digest
    assert before == {p.name: p.stat().st_mtime_ns for p in (out.parent / "segments").glob("*.mp4")}
    data["shots"][1]["camera"] = "push_in"
    atomic_write_json(pdir / "shots.json", data)
    assert render.build_render(ws, "p1")[:2] == (1, 2)
    previous = out.read_bytes(), (out.parent / "subtitles.srt").read_bytes()

    def fail_final(args, cwd=None):
        if args[-1] == "film.mp4":
            raise UserError("simulated final encode failure")
        return real(args, cwd)

    monkeypatch.setattr(render, "run_ffmpeg", fail_final)
    with pytest.raises(UserError, match="simulated"):
        render.build_render(ws, "p1")
    assert previous == (out.read_bytes(), (out.parent / "subtitles.srt").read_bytes())
    assert sorted(p.name for p in out.parent.iterdir()) == ["film.mp4", "segments", "subtitles.srt"]


def test_animatic_cache_identity_and_music_ignored(shot_project):
    ws, pdir, assets = shot_project
    atomic_write_json(pdir / "shots.json", {"version": 1, "music": assets[3], "shots": [
        dict(id="a", image=assets[0], duration_s=0.2)]})
    assert animatic.build_animatic(ws, "p1")[:2] == (1, 0)
    original = {"assets": [sha256_file(pdir / assets[0])], "images": 1, "duration_s": 0.2,
                "video": animatic.VIDEO, "audio": animatic.AUDIO, "scale": animatic.SCALE,
                "pipeline": "static-overlay-apad-v1"}
    key = hashlib.sha256(canonical_json(original).encode()).hexdigest()
    assert (pdir / f"animatic/segments/{key}.mp4").is_file()
    assert not any(pcm(pdir / "animatic/animatic.mp4"))
