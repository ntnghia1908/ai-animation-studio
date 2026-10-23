import json

import pytest

from animation_studio.__main__ import main

META = ["--license", "CC0", "--source-tool", "gen"]


def run(ws, *args):
    return main(["--workspace", str(ws), "import-assets", "p1", *args])


def manifest(ws):
    return json.loads((ws / "projects" / "p1" / "assets" / "manifest.json").read_text())["assets"]


def snapshot(ws):
    return sorted(str(p.relative_to(ws)) for p in ws.rglob("*"))


@pytest.mark.parametrize("alpha", [False, True])
def test_image_manifest_and_alpha(tmp_path, make_png, alpha):
    ws = tmp_path / "ws"
    png = make_png(alpha=alpha)
    assert run(ws, "--kind", "image", *META, "--model", "m", str(png)) == 0
    (a,) = manifest(ws)
    assert (ws / "projects" / "p1" / a["path"]).is_file()
    assert a["path"].startswith("assets/images/") and a["original_name"] == "img.png"
    assert (a["width"], a["height"]) == (64, 48)
    assert ("a" in a["pix_fmt"]) == alpha
    assert a["declared_cost_usd"] == 0 and a["model"] == "m" and a["license"] == "CC0"
    assert len(a["sha256"]) == 64 and a["source_tool"] == "gen" and a["imported_at"]


def test_audio_manifest(tmp_path, make_wav):
    ws = tmp_path / "ws"
    assert run(ws, "--kind", "audio", *META, str(make_wav(seconds=2))) == 0
    (a,) = manifest(ws)
    assert abs(a["duration_s"] - 2) < 0.1 and a["path"].startswith("assets/audio/")


def test_license_required(tmp_path, make_png):
    with pytest.raises(SystemExit):
        run(tmp_path / "ws", "--kind", "image", "--source-tool", "g", str(make_png()))


def test_duplicate_sha_not_copied(tmp_path, make_png, capsys):
    ws = tmp_path / "ws"
    a, b = make_png("a.png"), make_png("b.png")
    assert run(ws, "--kind", "image", *META, str(a)) == 0
    snap = snapshot(ws)
    assert run(ws, "--kind", "image", *META, str(a), str(b)) == 0
    assert snapshot(ws) == snap and len(manifest(ws)) == 1


@pytest.mark.parametrize("bad", ["x.gif", "broken.png"])
def test_bad_file_in_batch_changes_nothing(tmp_path, make_png, bad):
    ws = tmp_path / "ws"
    good, other = make_png("g1.png"), make_png("g2.png", color="blue")
    assert run(ws, "--kind", "image", *META, str(good)) == 0
    snap = snapshot(ws)
    before = (ws / "projects/p1/assets/manifest.json").read_bytes()
    badf = tmp_path / "src" / bad
    badf.write_bytes(b"not an image")
    assert run(ws, "--kind", "image", *META, str(other), str(badf)) != 0
    assert snapshot(ws) == snap
    assert (ws / "projects/p1/assets/manifest.json").read_bytes() == before


def test_atomic_write_leaves_no_temp(tmp_path):
    from animation_studio.workspace import atomic_write_json
    p = tmp_path / "d" / "f.json"
    atomic_write_json(p, {"a": 1})
    assert json.loads(p.read_text()) == {"a": 1}
    assert [x.name for x in p.parent.iterdir()] == ["f.json"]
