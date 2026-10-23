import json

from animation_studio.__main__ import main

ARGS = ["--source", "http://x", "--rights", "public domain"]


def story_dir(ws):
    return ws / "projects" / "p1" / "story"


def test_import_verbatim_and_metadata(tmp_path):
    f = tmp_path / "s.txt"
    data = "Xin chào\r\nthế giới\n".encode("utf-8")
    f.write_bytes(data)
    assert main(["--workspace", str(tmp_path / "ws"), "import-story", "p1", str(f), "--title", "T", *ARGS]) == 0
    d = story_dir(tmp_path / "ws")
    assert (d / "source.txt").read_bytes() == data
    meta = json.loads((d / "story.json").read_text(encoding="utf-8"))
    for k in ("id", "title", "source", "author", "translator", "genre", "rights", "sha256", "imported_at"):
        assert k in meta
    assert meta["review_status"] == "pending" and meta["title"] == "T" and meta["id"] == "p1"


def test_required_flags(tmp_path):
    import pytest
    f = tmp_path / "s.txt"
    f.write_text("x")
    with pytest.raises(SystemExit):
        main(["--workspace", str(tmp_path), "import-story", "p1", str(f), "--source", "s"])


def test_reimport_same_unchanged_different_rejected(tmp_path, capsys):
    ws = str(tmp_path / "ws")
    f = tmp_path / "s.txt"
    f.write_text("one")
    assert main(["--workspace", ws, "import-story", "p1", str(f), *ARGS]) == 0
    d = story_dir(tmp_path / "ws")
    before = ((d / "source.txt").read_bytes(), (d / "story.json").read_bytes())
    capsys.readouterr()
    assert main(["--workspace", ws, "import-story", "p1", str(f), *ARGS]) == 0
    assert "unchanged" in capsys.readouterr().out
    f.write_text("two")
    assert main(["--workspace", ws, "import-story", "p1", str(f), *ARGS]) != 0
    assert before == ((d / "source.txt").read_bytes(), (d / "story.json").read_bytes())
