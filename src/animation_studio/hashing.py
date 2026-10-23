"""Hash helpers.

Copied from youtube-auto-short@f47813d:src/auto_short/hashing.py
(sha256_file and canonical_json).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

_CHUNK = 1024 * 1024


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while chunk := fh.read(_CHUNK):
            h.update(chunk)
    return h.hexdigest()


def canonical_json(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
