"""import-assets: validate and probe a batch, copy into the workspace, update manifest once."""

from __future__ import annotations

from pathlib import Path

from .hashing import sha256_file
from .media import probe
from .workspace import UserError, atomic_write_bytes, atomic_write_json, project_dir, read_json, utc_now

DIRS = {"image": "images", "audio": "audio"}
EXTENSIONS = {"image": {".png", ".jpg", ".jpeg"}, "audio": {".wav", ".mp3"}}


def import_assets(workspace: Path, project_id: str, kind: str, files: list[Path], meta: dict) -> tuple[int, int]:
    """Return (added, skipped). All-or-nothing: any invalid file aborts before anything is written."""
    pdir = project_dir(workspace, project_id)
    manifest_path = pdir / "assets" / "manifest.json"
    manifest = read_json(manifest_path, {"assets": []})
    known = {a["sha256"] for a in manifest["assets"]}
    planned: list[tuple[Path, str, dict]] = []
    skipped = 0
    for f in files:
        if f.suffix.lower() not in EXTENSIONS[kind]:
            raise UserError(f"{f}: extension not allowed for {kind} (allowed: {sorted(EXTENSIONS[kind])})")
        if not f.is_file():
            raise UserError(f"file not found: {f}")
        media = probe(f, kind)
        sha = sha256_file(f)
        if sha in known:
            skipped += 1
            continue
        known.add(sha)
        planned.append((f, sha, media))
    if not planned:
        return 0, skipped
    for f, sha, media in planned:
        rel = f"assets/{DIRS[kind]}/{sha[:12]}-{f.name}"
        atomic_write_bytes(pdir / rel, f.read_bytes())
        manifest["assets"].append({
            "sha256": sha,
            "kind": kind,
            "path": rel,
            "original_name": f.name,
            "size_bytes": f.stat().st_size,
            "source_tool": meta["source_tool"],
            "model": meta.get("model"),
            "declared_cost_usd": meta.get("declared_cost_usd", 0),
            "license": meta["license"],
            "imported_at": utc_now(),
            **media,
        })
    atomic_write_json(manifest_path, manifest)
    return len(planned), skipped
