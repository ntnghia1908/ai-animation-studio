import json
import subprocess

import pytest

from animation_studio import animatic
from animation_studio.__main__ import main
from animation_studio.media import probe
from animation_studio.workspace import UserError, atomic_write_json


def pixels(path, time, crop):
    result = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(time), "-i", str(path),
                             "-vf", f"crop={crop},format=rgb24", "-frames:v", "1",
                             "-f", "rawvideo", "-"], check=True, capture_output=True)
    return list(zip(*[iter(result.stdout)] * 3))


def test_output_subtitles_layers_and_resume(shot_project, capsys, monkeypatch):
    ws, pdir, assets = shot_project
    shots = [dict(id="s1", image=assets[0], audio=assets[3], subtitle="Ngày xưa có một thư sinh…"),
             dict(id="s2", layers=[assets[1], assets[2]], duration_s=1.07, camera="parallax",
                  transition="crossfade", subtitle="Chồng lớp và nhịp kể."),
             dict(id="s3", image=assets[0], duration_s=0.5)]
    atomic_write_json(pdir / "shots.json", {"version": 1, "shots": shots})
    calls, real_run = [], animatic.run_ffmpeg

    def record(args, cwd=None):
        calls.append(args)
        if args[-1] == "animatic.mp4":
            assert (cwd / "fonts").resolve() == animatic.FONTS
        real_run(args, cwd)

    monkeypatch.setattr(animatic, "run_ffmpeg", record)
    args = ["--workspace", str(ws), "animatic", "p1"]
    assert main(args) == 0
    assert "animatic built=3 reused=0 ->" in capsys.readouterr().out
    out = pdir / "animatic/animatic.mp4"
    assert probe(out, "image")["width"] == 1920 and probe(out, "image")["height"] == 1080
    assert abs(probe(out, "audio")["duration_s"] - 2.57) <= 0.1
    info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format",
                                     "-of", "json", str(out)], check=True, capture_output=True).stdout)
    video, audio = info["streams"]
    assert (video["codec_name"], video["r_frame_rate"], video["pix_fmt"]) == ("h264", "30/1", "yuv420p")
    assert (audio["codec_name"], audio["sample_rate"], audio["channels"]) == ("aac", "48000", 2)
    assert abs(float(info["format"]["duration"]) - 2.57) <= 0.1
    for time, audible in [(0.3, True), (1.3, False)]:
        pcm = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(time), "-i", str(out),
                              "-t", "0.1", "-vn", "-f", "s16le", "-"], check=True, capture_output=True).stdout
        assert pcm and any(pcm) == audible
    # 4:3 red image fills x=240..1680: black outside, red inside.
    assert max(pixels(out, 0.4, "2:2:100:400")[0]) < 10
    red = pixels(out, 0.4, "2:2:400:400")[0]
    assert red[0] > 220 and max(red[1:]) < 20
    blue = pixels(out, 1.4, "2:2:400:400")[0]
    green = pixels(out, 1.4, "2:2:960:540")[0]
    assert blue[2] > 220 and max(blue[:2]) < 20
    assert green[1] > 220 and max(green[::2]) < 20
    srt = (out.parent / "subtitles.srt").read_text(encoding="utf-8")
    assert srt == ("1\n00:00:00,000 --> 00:00:01,000\nNgày xưa có một thư sinh…\n\n"
                   "2\n00:00:01,000 --> 00:00:02,070\nChồng lớp và nhịp kể.\n\n")
    # Bright glyph pixels are absent from the uncaptioned segment, present after burn.
    cache = out.parent / "segments"
    segment = next(p for p in cache.glob("*.mp4") if abs(probe(p, "audio")["duration_s"] - 1) < 0.1
                   and pixels(p, 0.4, "2:2:960:540")[0][0] > 220)
    assert not any(min(p) > 220 for p in pixels(segment, 0.4, "1440:240:240:840"))
    assert sum(min(p) > 220 for p in pixels(out, 0.4, "1440:240:240:840")) > 100
    assert any("FontName=Be Vietnam Pro" in arg and "fontsdir=fonts" in arg for call in calls for arg in call)
    assert (animatic.FONTS / "BeVietnamPro-Regular.ttf").is_file()
    assert "SIL OPEN FONT LICENSE" in (animatic.FONTS / "OFL.txt").read_text()
    before = {p.name: p.stat().st_mtime_ns for p in cache.glob("*.mp4")}
    calls.clear()
    assert main(args) == 0
    assert "built=0 reused=3" in capsys.readouterr().out
    assert before == {p.name: p.stat().st_mtime_ns for p in cache.glob("*.mp4")}
    assert len(calls) == 2  # concat and final subtitle encode only
    shots[1]["duration_s"] = 1.5
    atomic_write_json(pdir / "shots.json", {"version": 1, "shots": shots})
    assert main(args) == 0
    assert "built=1 reused=2" in capsys.readouterr().out
    assert all((cache / name).stat().st_mtime_ns == mtime for name, mtime in before.items())
    assert len(list(cache.glob("*.mp4"))) == 4


def test_no_subtitles_and_failed_final_keeps_output(shot_project, monkeypatch):
    ws, pdir, assets = shot_project
    atomic_write_json(pdir / "shots.json", {"version": 1, "shots": [
        dict(id="s1", layers=[assets[0], assets[2], assets[2]], duration_s=0.5)]})
    _, _, out = animatic.build_animatic(ws, "p1")
    assert (out.parent / "subtitles.srt").read_bytes() == b""
    before = out.read_bytes()
    real_run = animatic.run_ffmpeg

    def fail_final(args, cwd=None):
        if args[-1] == "animatic.mp4":
            raise UserError("simulated final encode failure")
        real_run(args, cwd)

    monkeypatch.setattr(animatic, "run_ffmpeg", fail_final)
    with pytest.raises(UserError, match="simulated"):
        animatic.build_animatic(ws, "p1")
    assert out.read_bytes() == before
    assert sorted(p.name for p in out.parent.iterdir()) == ["animatic.mp4", "segments", "subtitles.srt"]
