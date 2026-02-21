from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture()
def make_file(tmp_path: Path):
    def _make(rel_path: str, content: str | bytes = "") -> Path:
        path = tmp_path / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")
        return path

    return _make

