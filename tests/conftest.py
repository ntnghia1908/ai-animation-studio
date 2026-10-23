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
    def make(name="img.png", alpha=False, color="red"):
        path = tmp_path / "src" / name
        path.parent.mkdir(exist_ok=True)
        fmt = "rgba" if alpha else "rgb24"
        _ffmpeg("-f", "lavfi", "-i", f"color=c={color}:s=64x48", "-frames:v", "1",
                "-vf", f"format={fmt}", str(path))
        return path
    return make


@pytest.fixture
def make_wav(tmp_path):
    def make(name="voice.wav", seconds=1):
        path = tmp_path / "src" / name
        path.parent.mkdir(exist_ok=True)
        _ffmpeg("-f", "lavfi", "-i", f"sine=frequency=440:duration={seconds}", str(path))
        return path
    return make
