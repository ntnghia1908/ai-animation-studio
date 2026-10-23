import subprocess
import sys

import pytest

from animation_studio.__main__ import main

STORY_ARGS = ["--source", "src", "--rights", "own"]


def run(ws, *args):
    return main(["--workspace", str(ws), *args])


def test_help_lists_commands():
    out = subprocess.run([sys.executable, "-m", "animation_studio", "--help"], capture_output=True, text=True)
    assert out.returncode == 0 and "import-story" in out.stdout and "import-assets" in out.stdout


def test_workspace_from_config_expands_home(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("HOME", str(tmp_path))
    cfg = tmp_path / "config.toml"
    cfg.write_text('workspace = "~/data"\n')
    story = tmp_path / "s.txt"
    story.write_text("x", encoding="utf-8")
    assert main(["--config", str(cfg), "import-story", "p1", str(story), *STORY_ARGS]) == 0
    assert (tmp_path / "data" / "projects" / "p1" / "story" / "source.txt").is_file()


@pytest.mark.parametrize("project", ["Bad_ID", "UPPER", ""])
def test_bad_project_id_no_files(tmp_path, project, capsys):
    story = tmp_path / "s.txt"
    story.write_text("x")
    ws = tmp_path / "ws"
    assert run(ws, "import-story", project, str(story), *STORY_ARGS) != 0
    assert not ws.exists() and "invalid project id" in capsys.readouterr().err


def test_missing_workspace_and_config(tmp_path, capsys):
    story = tmp_path / "s.txt"
    story.write_text("x")
    assert main(["--config", str(tmp_path / "none.toml"), "import-story", "p", str(story), *STORY_ARGS]) != 0
    assert "no workspace" in capsys.readouterr().err


def test_gitignore_and_example():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    assert "config.toml" in (root / ".gitignore").read_text().split()
    assert "workspace" in (root / "config.example.toml").read_text()
