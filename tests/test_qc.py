import copy
import hashlib

import pytest

from animation_studio import qc, render
from animation_studio.__main__ import main
from animation_studio.animatic import run_ffmpeg, srt_cues
from animation_studio.assets import import_assets
from animation_studio.media import _ffprobe
from animation_studio.workspace import atomic_write_json, read_json


@pytest.mark.parametrize("field,value", [(None, None), ("width", 640), ("height", 720),
    ("sample_aspect_ratio", "2:1"), ("r_frame_rate", "24/1"), ("avg_frame_rate", "29/1"),
    ("codec_name", "mpeg4"), ("audio", "mp3")])
def test_format(field, value):
    v = dict(codec_type="video", width=1920, height=1080, sample_aspect_ratio="1:1",
             r_frame_rate="30/1", avg_frame_rate="30/1", codec_name="h264")
    a = dict(codec_type="audio", codec_name="aac")
    if field:
        (a if field == "audio" else v)["codec_name" if field == "audio" else field] = value
    assert qc.format_check(dict(streams=[v, a]))["status"] == ("FAIL" if field else "PASS")


@pytest.mark.parametrize("seconds,expected,match,in_range", [(30, 30, True, True), (60, 60, True, True),
    (30.1, 30, True, True), (29.9, 30, True, False), (30.101, 30, False, True), (60.1, 60, True, False)])
def test_duration_boundaries(seconds, expected, match, in_range):
    assert [x["status"] == "PASS" for x in qc.duration_checks(seconds, expected)] == [match, in_range]


@pytest.mark.parametrize("start,end,count,passed", [("000", "000", 1, True), ("100", "100", 1, True),
    ("101", "101", 1, False), ("000", "000", 0, False), ("000", "000", 2, False)])
def test_subtitles(start, end, count, passed):
    expected = "1\n00:00:01,000 --> 00:00:02,000\nTiếng Việt\n\n"
    actual = f"1\n00:00:01,{start} --> 00:00:02,{end}\nTiếng Việt\n\n" * count
    assert (qc.subtitle_check(actual, expected)["status"] == "PASS") == passed


@pytest.mark.parametrize("video,audio,black,freeze,loud", [
    ("testsrc2", "sine=frequency=440", False, False, True),
    ("color=black", "sine=frequency=440,volume=-9dB", True, True, False),
    ("color=red", "anullsrc=r=48000:cl=stereo", False, True, False)])
def test_lavfi_measurements(tmp_path, video, audio, black, freeze, loud):
    film = tmp_path / "film.mp4"
    run_ffmpeg(["-f", "lavfi", "-i", f"{video}:s=160x90:r=30" if video.startswith("color") else "testsrc2=s=160x90:r=30",
                "-f", "lavfi", "-i", audio, "-t", "1", "-c:v", "libx264", "-threads", "1",
                "-af", "loudnorm=I=-16" if loud else "anull", "-c:a", "aac", str(film)])
    log = run_ffmpeg(["-v", "info", "-i", str(film), "-vf", f"blackdetect=d=0.5,freezedetect=n={qc.FREEZE_NOISE_DB}dB:d=0.5",
                      "-af", "ebur128", "-f", "null", "-"])
    checks = qc.detection_checks(log, 1, [])
    assert [x["status"] == "FAIL" for x in checks] == [black, freeze, not loud]
    if black:
        assert checks[0]["measured"][0][1] >= 0.6
    assert qc.detection_checks(log, 1, [[0, 0.5], [0.5, 1.5]])[1]["status"] == "PASS"
    assert qc.format_check(_ffprobe(film))["status"] == "FAIL"


@pytest.mark.parametrize("allowed,spans,uncovered,status", [
    ([[38.2, 43.7]], [[38.23, 42.9], [42.9, 43.95]], [[43.7, 43.95]], "PASS"),
    ([[38.2, 43.7]], [[38.23, 42.9], [42.9, 44.3]], [[43.7, 44.3]], "FAIL"),
    ([[38.2, 43.7]], [[45, 45.6]], [[45.0, 45.6]], "FAIL"),
    ([[38.2, 43.7]], [[45, 45.4]], [[45.0, 45.4]], "PASS"),
    ([[38.2, 43.7]], [[42.9, 44.2]], [[43.7, 44.2]], "FAIL"),
    ([[38.2, 43.7]], [[38, 44]], [[38.0, 38.2], [43.7, 44.0]], "FAIL"),
    ([[40, 42], [38.2, 41], [42, 43.7]], [[38, 44]], [[38.0, 38.2], [43.7, 44.0]], "FAIL"),
    ([[38.2, 43.7]], [[45, 45.3], [46, 46.3]], [[45.0, 45.3], [46.0, 46.3]], "PASS")])
def test_freeze_uncovered_duration(allowed, spans, uncovered, status):
    log = "\n".join(f"freeze_start: {a}\nfreeze_end: {b}" for a, b in spans)
    check = qc.detection_checks(log, 50, allowed)[1]
    assert check["status"] == status
    assert check["measured"] == spans
    assert check["detail"] == f"outside static windows: {uncovered}"


@pytest.mark.parametrize("camera", ["push_in", "pan_left", "parallax"])
def test_moving_render_no_freeze(shot_project, make_png, camera):
    ws, pdir, assets = shot_project
    detail = make_png("detail.png", detail=True)
    import_assets(ws, "p1", "image", [detail], dict(license="CC0", source_tool="ffmpeg"))
    image = read_json(pdir / "assets/manifest.json")["assets"][-1]["path"]
    shot = dict(id="move", duration_s=3, camera=camera, image=image)
    if camera == "parallax":
        shot.pop("image")
        shot["layers"] = [image, assets[2]]
    atomic_write_json(pdir / "shots.json", dict(version=1, shots=[shot]))
    render.build_render(ws, "p1")
    assert next(c for c in qc.check_render(ws, "p1")["checks"] if c["name"] == "freeze")["status"] == "PASS"


def test_reproducibility_alpha_atomic_and_cli(shot_project, make_png, monkeypatch, capsys):
    ws, pdir, assets = shot_project
    import_assets(ws, "p1", "image", [make_png("empty.png", alpha=True, color="red@0")],
                  dict(license="CC0", source_tool="ffmpeg"))
    image = read_json(pdir / "assets/manifest.json")["assets"][-1]["path"]
    atomic_write_json(pdir / "shots.json", dict(version=1, music=assets[3], shots=[
        dict(id="a", image=image, duration_s=30, subtitle="Tiếng Việt")]))
    out = pdir / "render"
    out.mkdir()
    (out / "film.mp4").write_bytes(b"unchanged")
    (out / "subtitles.srt").write_bytes(srt_cues(qc.load_shots(pdir))[0])
    info = dict(streams=[dict(codec_type="video", width=1920, height=1080, sample_aspect_ratio="1:1",
        r_frame_rate="30/1", avg_frame_rate="30/1", codec_name="h264"), dict(codec_type="audio", codec_name="aac")],
        format=dict(duration="30"))
    monkeypatch.setattr(qc, "_ffprobe", lambda p: info)
    monkeypatch.setattr(qc, "run_ffmpeg", lambda *args: "I: -16.0 LUFS")
    monkeypatch.setattr(qc, "pcm", lambda p: b"audio")
    first = qc.check_render(ws, "p1", compare=True)
    assert first["overall"] == "PASS" and first["checks"][-1]["status"] == "WARN"
    assert first["audio_pcm_sha256"] == hashlib.sha256(b"audio").hexdigest()
    second = qc.check_render(ws, "p1", first, compare=True)
    assert second["checks"][-2]["status"] == "PASS"
    changed = copy.deepcopy(second)
    changed["audio_pcm_sha256"] = "tampered"
    failed = qc.check_render(ws, "p1", changed, compare=True)
    assert failed["checks"][-2]["status"] == "FAIL"
    assert main(["--workspace", str(ws), "check", "p1"]) == 2
    assert read_json(out / "qc.json")["checks"][-2] == failed["checks"][-2]
    for path in (pdir / assets[3], pdir / image):
        original = path.read_bytes()
        path.write_bytes(original + b"changed")
        atomic_write_json(out / "qc.json", second)
        assert qc.check_render(ws, "p1")["checks"][-2]["status"] == "SKIP"
        assert qc.check_render(ws, "p1", first, compare=True)["checks"][-2]["status"] == "SKIP"
        path.write_bytes(original)
    qc.check_render(ws, "p1", compare=True)
    assert main(["--workspace", str(ws), "check", "p1"]) == 0
    assert "WARN layer_alpha:" in capsys.readouterr().out
    assert (out / "film.mp4").read_bytes() == b"unchanged"
    assert sorted(p.name for p in out.iterdir()) == ["film.mp4", "qc.json", "subtitles.srt"]
    def fail_replace(*args):
        raise OSError("interrupted replace")
    previous = (out / "qc.json").read_bytes()
    with monkeypatch.context() as patch:
        patch.setattr("animation_studio.workspace.os.replace", fail_replace)
        with pytest.raises(OSError, match="interrupted"):
            qc.check_render(ws, "p1")
    assert (out / "qc.json").read_bytes() == previous and len(list(out.iterdir())) == 3
    (out / "film.mp4").unlink()
    assert main(["--workspace", str(ws), "check", "p1"]) == 1
    atomic_write_json(pdir / "shots.json", {})
    assert main(["--workspace", str(ws), "check", "p1"]) == 1
