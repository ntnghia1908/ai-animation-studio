"""Atomic IO, JSON read, UTC timestamp and project paths.

atomic_write_bytes, atomic_write_json, utc_now copied from
youtube-auto-short@f47813d:src/auto_short/workspace.py.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path

_PROJECT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")


class UserError(Exception):
    """Invalid input or state; message is shown to the user."""


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def atomic_write_bytes(path: Path, data: bytes) -> None:
    """Write via a temp file in the same directory, then ``os.replace``."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        umask = os.umask(0)
        os.umask(umask)
        os.fchmod(fd, 0o666 & ~umask)
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def atomic_write_json(path: Path, obj: object) -> None:
    text = json.dumps(obj, indent=2, ensure_ascii=False) + "\n"
    atomic_write_bytes(path, text.encode("utf-8"))


def read_json(path: Path, default: object = None) -> object:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise UserError(f"cannot read {path}: {exc}") from exc


def validate_project_id(project_id: str) -> str:
    if not _PROJECT_ID_RE.match(project_id):
        raise UserError(
            f"invalid project id {project_id!r}: use lowercase letters, digits and '-' "
            "(start with letter or digit, max 64 chars)"
        )
    return project_id


def project_dir(workspace: Path, project_id: str) -> Path:
    return workspace / "projects" / validate_project_id(project_id)
