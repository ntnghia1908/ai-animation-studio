"""import-story: store story text verbatim with provenance (immutable once imported)."""

from __future__ import annotations

from pathlib import Path

from .hashing import sha256_file
from .workspace import UserError, atomic_write_bytes, atomic_write_json, project_dir, utc_now


def import_story(workspace: Path, project_id: str, file: Path, meta: dict) -> str:
    """Return "imported" or "unchanged"; raise UserError on conflict or bad input."""
    pdir = project_dir(workspace, project_id)
    if not file.is_file():
        raise UserError(f"story file not found: {file}")
    data = file.read_bytes()
    try:
        data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise UserError(f"{file}: not valid UTF-8") from exc
    sha = sha256_file(file)
    source = pdir / "story" / "source.txt"
    if source.exists():
        if sha256_file(source) == sha:
            return "unchanged"
        raise UserError(f"project {project_id} already has a different story; imported stories are immutable")
    # Metadata first: source.txt is the commit marker, so a crash in between is retried, not "unchanged".
    atomic_write_json(pdir / "story" / "story.json", {
        "id": project_id,
        "title": meta.get("title") or file.stem,
        "source": meta["source"],
        "author": meta.get("author"),
        "translator": meta.get("translator"),
        "genre": meta.get("genre"),
        "rights": meta["rights"],
        "review_status": "pending",
        "sha256": sha,
        "imported_at": utc_now(),
    })
    atomic_write_bytes(source, data)
    return "imported"
