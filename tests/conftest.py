"""Shared fixtures: network guard and FFmpeg-generated media (no media committed)."""

import socket
import subprocess

import pytest


@pytest.fixture(autouse=True)
def _no_real_services(monkeypatch):
    """Block connections to any non-loopback host (pattern from youtube-auto-short@f47813d:tests/conftest.py)."""
    real_connect = socket.socket.connect
    real_connect_ex = socket.socket.connect_ex

    def _check(addr):
        if isinstance(addr, tuple) and len(addr) >= 2 and isinstance(addr[0], str):
            host = addr[0]
            if not (host in ("127.0.0.1", "::1", "localhost") or host.startswith("127.")):
                raise AssertionError(f"test tried to reach a real service: {host}:{addr[1]}")

    def guarded(self, addr):
        _check(addr)
        return real_connect(self, addr)

    def guarded_ex(self, addr):
        _check(addr)
        return real_connect_ex(self, addr)

    monkeypatch.setattr(socket.socket, "connect", guarded)
    monkeypatch.setattr(socket.socket, "connect_ex", guarded_ex)


def _ffmpeg(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


@pytest.fixture
def make_png(tmp_path):
    def make(name="img.png", alpha=False, color="red", patch=False, detail=False):
        path = tmp_path / "src" / name
        path.parent.mkdir(exist_ok=True)
        fmt = "rgba" if alpha else "rgb24"
        source = f"color=c={color}:s=64x48"
        if detail:
            source += ",drawbox=x=16:y=16:w=8:h=8:color=lime:t=fill"
        if patch:
            source += ",format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='if(between(X,24,39)*between(Y,16,31),255,0)'"
        _ffmpeg("-f", "lavfi", "-i", source, "-frames:v", "1",
                "-vf", f"format={fmt}", str(path))
        return path
    return make


@pytest.fixture
def shot_project(tmp_path, make_png, make_wav):
    from animation_studio.assets import import_assets
    from animation_studio.workspace import read_json
    ws = tmp_path / "ws ' có dấu"
    meta = {"license": "CC0", "source_tool": "ffmpeg"}
    import_assets(ws, "p1", "image", [make_png(), make_png("blue.png", color="blue"),
                  make_png("patch.png", alpha=True, color="lime", patch=True)], meta)
    import_assets(ws, "p1", "audio", [make_wav()], meta)
    pdir = ws / "projects/p1"
    assets = read_json(pdir / "assets/manifest.json")["assets"]
    return ws, pdir, [a["path"] for a in assets]


@pytest.fixture
def make_wav(tmp_path):
    def make(name="voice.wav", seconds=1, frequency=440):
        path = tmp_path / "src" / name
        path.parent.mkdir(exist_ok=True)
        _ffmpeg("-f", "lavfi", "-i", f"sine=frequency={frequency}:duration={seconds}", str(path))
        return path
    return make
