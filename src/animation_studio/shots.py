"""Load shots.json v1, validate all inputs before rendering, resolve asset paths."""

from __future__ import annotations

import math
import re
from pathlib import Path

from .workspace import UserError, read_json


def load_shots(pdir: Path) -> list[dict]:
    try:
        data = read_json(pdir / "shots.json")
    except (UserError, UnicodeError) as exc:
        raise UserError(f"shots.json (root): JSON: {exc}") from exc
    if not isinstance(data, dict) or type(data.get("version")) is not int or data["version"] != 1:
        raise UserError("shots.json (root): version must be 1")
    if not isinstance(data.get("shots"), list) or not data["shots"]:
        raise UserError("shots.json (root): shots must be a nonempty list")
    manifest = read_json(pdir / "assets/manifest.json", {"assets": []})
    if not isinstance(manifest, dict) or not isinstance(manifest.get("assets"), list):
        raise UserError("shots.json (root): assets/manifest.json: invalid assets list")
    assets = {a["path"]: a for a in manifest["assets"] if isinstance(a, dict) and isinstance(a.get("path"), str)}
    seen, resolved = set(), []
    for index, shot in enumerate(data["shots"]):
        label = f"shot[{index}]" + (f" ({shot.get('id')})" if isinstance(shot, dict) else "")

        def fail(field, reason):
            raise UserError(f"{label}: {field}: {reason}")

        def duration(value, field):
            if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
                fail(field, "must be a finite number > 0")
            return float(value)

        def asset(value, field, kind):
            if not isinstance(value, str) or value not in assets:
                fail(field, "asset not in assets/manifest.json")
            path = (pdir / value).resolve()
            if Path(value).is_absolute() or not path.is_relative_to(pdir.resolve()) or not path.is_file():
                fail(field, "asset must be an existing project-relative file")
            if assets[value].get("kind") != kind:
                fail(field, f"asset kind must be {kind}")
            return path

        if not isinstance(shot, dict):
            fail("shot", "must be an object")
        sid = shot.get("id")
        if not isinstance(sid, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,31}", sid):
            fail("id", "invalid format")
        if sid in seen:
            fail("id", "duplicate")
        seen.add(sid)
        if ("image" in shot) == ("layers" in shot):
            fail("image/layers", "specify exactly one")
        if "layers" in shot:
            if not isinstance(shot["layers"], list) or not 2 <= len(shot["layers"]) <= 3:
                fail("layers", "must contain 2–3 assets, bottom to top")
            images = [asset(v, f"layers[{i}]", "image") for i, v in enumerate(shot["layers"])]
        else:
            images = [asset(shot["image"], "image", "image")]
        camera = shot.get("camera", "static")
        if camera not in ("static", "push_in", "pull_out", "pan_left", "pan_right", "parallax"):
            fail("camera", "unknown camera")
        if camera == "parallax" and "layers" not in shot:
            fail("camera", "parallax requires layers")
        transition = shot.get("transition", "cut")
        if transition not in ("cut", "crossfade"):
            fail("transition", "unknown transition")
        if "subtitle" in shot and not isinstance(shot["subtitle"], str):
            fail("subtitle", "must be a string")
        seconds = duration(shot["duration_s"], "duration_s") if "duration_s" in shot else 0
        audio = None
        if "audio" in shot:
            audio = asset(shot["audio"], "audio", "audio")
            seconds = max(seconds, duration(assets[shot["audio"]].get("duration_s"), "audio.duration_s"))
        elif not seconds:
            fail("duration_s", "required without audio")
        resolved.append(dict(id=sid, images=images, audio=audio, duration_s=seconds,
                             subtitle=shot.get("subtitle", ""), camera=camera, transition=transition))
    return resolved
