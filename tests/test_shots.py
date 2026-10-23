import pytest

from animation_studio.__main__ import main
from animation_studio.shots import load_shots
from animation_studio.workspace import atomic_write_json


@pytest.mark.parametrize("case,field", [
    ("json", "JSON"), ("version", "version"), ("shots", "shots"), ("empty", "shots"),
    ("not_object", "shot"), ("duplicate", "id"), ("bad_id", "id"), ("both", "image/layers"),
    ("neither", "image/layers"), ("one_layer", "layers"), ("four_layers", "layers"),
    ("missing_asset", "image"), ("wrong_kind", "image"), ("bad_audio", "audio"),
    ("no_duration", "duration_s"), ("camera", "camera"), ("transition", "transition"),
    ("parallax", "camera"), ("subtitle", "subtitle"), ("zero", "duration_s"),
    ("negative", "duration_s"), ("nan", "duration_s"), ("bool", "duration_s"),
])
def test_invalid_shots_exit_without_output(shot_project, case, field, capsys):
    ws, pdir, assets = shot_project
    shot = dict(id="s1", image=assets[0], duration_s=1)
    data = {"version": 1, "shots": [shot]}
    if case in ("version", "shots"):
        del data[case]
    elif case == "empty":
        data["shots"] = []
    elif case == "not_object":
        data["shots"] = [None]
    elif case == "duplicate":
        data["shots"].append(shot.copy())
    elif case == "bad_id":
        shot["id"] = "Bad ID"
    elif case == "both":
        shot["layers"] = assets[:2]
    elif case == "neither":
        del shot["image"]
    elif case in ("one_layer", "four_layers"):
        del shot["image"]
        shot["layers"] = [assets[0]] * (1 if case == "one_layer" else 4)
    elif case in ("missing_asset", "wrong_kind"):
        shot["image"] = "assets/images/missing.png" if case == "missing_asset" else assets[3]
    elif case == "bad_audio":
        shot["audio"] = assets[0]
    elif case == "no_duration":
        del shot["duration_s"]
    elif case in ("camera", "transition", "subtitle"):
        shot[case] = 123
    elif case == "parallax":
        shot["camera"] = "parallax"
    elif case in ("zero", "negative", "nan", "bool"):
        shot["duration_s"] = {"zero": 0, "negative": -1, "nan": float("nan"), "bool": True}[case]
    atomic_write_json(pdir / "shots.json", data)
    if case == "json":
        (pdir / "shots.json").write_text("{")
    assert main(["--workspace", str(ws), "animatic", "p1"]) != 0
    error = capsys.readouterr().err
    assert field in error and ("shot[" in error or "(root)" in error)
    assert not (pdir / "animatic").exists()


@pytest.mark.parametrize("requested,expected", [(None, 1), (0.5, 1), (2, 2)])
def test_duration_resolution_and_defaults(shot_project, requested, expected):
    _, pdir, assets = shot_project
    shot = dict(id="s1", image=assets[0], audio=assets[3])
    if requested is not None:
        shot["duration_s"] = requested
    atomic_write_json(pdir / "shots.json", {"version": 1, "shots": [
        shot, dict(id="s2", layers=assets[:3], duration_s=0.7, camera="parallax", transition="crossfade")]})
    first, second = load_shots(pdir)
    assert first["duration_s"] == expected and second["duration_s"] == 0.7
    assert first["camera"] == "static" and first["transition"] == "cut"
    assert first["images"][0].is_absolute() and first["audio"].is_absolute()
