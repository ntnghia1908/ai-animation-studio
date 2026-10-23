"""Workspace resolution: --workspace, else config.toml key ``workspace``."""

from __future__ import annotations

import tomllib
from pathlib import Path

from .workspace import UserError


def resolve_workspace(workspace_arg: str | None, config_path: Path) -> Path:
    if workspace_arg:
        return Path(workspace_arg).expanduser()
    if not config_path.is_file():
        raise UserError(f"no workspace: pass --workspace or create {config_path} (see config.example.toml)")
    try:
        data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise UserError(f"cannot read {config_path}: {exc}") from exc
    value = data.get("workspace")
    if not isinstance(value, str) or not value:
        raise UserError(f"{config_path}: missing string key 'workspace'")
    return Path(value).expanduser()
