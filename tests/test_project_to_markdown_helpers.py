from __future__ import annotations

from pathlib import Path

from project_to_markdown.project_to_markdown import (
    _escape_backticks,
    _matches_ext,
    _normalize_ext_patterns,
)


def test_normalize_ext_patterns():
    patterns = _normalize_ext_patterns([".py", "py", "*.md", "TXT"])
    assert "*.py" in patterns
    assert "*.md" in patterns
    assert "*.txt" in patterns


def test_matches_ext():
    patterns = _normalize_ext_patterns(["py", "md"])
    assert _matches_ext(Path("demo.py"), patterns)
    assert _matches_ext(Path("readme.md"), patterns)
    assert not _matches_ext(Path("note.txt"), patterns)


def test_escape_backticks():
    raw = "a```b"
    escaped = _escape_backticks(raw)
    assert "```" not in escaped
    assert "``\u200b`" in escaped

