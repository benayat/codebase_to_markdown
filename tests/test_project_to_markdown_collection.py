from __future__ import annotations

from pathlib import Path

from project_to_markdown.project_to_markdown import (
    build_tree_from_files,
    build_tree_from_scan,
    collect_files,
    render_tree_markdown,
)


def _write(tmp_path: Path, rel_path: str, content: str = "") -> Path:
    path = tmp_path / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_collect_files_deep_paths_included(tmp_path: Path):
    _write(tmp_path, "src/domain/agentspec/file.py", "print('ok')")
    files = collect_files(
        root=tmp_path,
        include_patterns=["*.py"],
        exclude_dirs=set(),
        exclude_files=set(),
        use_gitignore=False,
        all_files=False,
        max_bytes=0,
        prune_excluded_dirs=True,
    )
    rel = [p.relative_to(tmp_path) for p in files]
    assert Path("src/domain/agentspec/file.py") in rel


def test_collect_files_excludes_parent_dir(tmp_path: Path):
    _write(tmp_path, "src/domain/agentspec/file.py", "print('ok')")
    files = collect_files(
        root=tmp_path,
        include_patterns=["*.py"],
        exclude_dirs={"src"},
        exclude_files=set(),
        use_gitignore=False,
        all_files=False,
        max_bytes=0,
        prune_excluded_dirs=False,
    )
    assert files == []


def test_collect_files_max_bytes(tmp_path: Path):
    _write(tmp_path, "src/large.py", "x" * 10)
    files = collect_files(
        root=tmp_path,
        include_patterns=["*.py"],
        exclude_dirs=set(),
        exclude_files=set(),
        use_gitignore=False,
        all_files=False,
        max_bytes=5,
        prune_excluded_dirs=True,
    )
    assert files == []


def test_collect_files_exclude_files(tmp_path: Path):
    _write(tmp_path, "src/app.py", "print('ok')")
    files = collect_files(
        root=tmp_path,
        include_patterns=["*.py"],
        exclude_dirs=set(),
        exclude_files={"app.py"},
        use_gitignore=False,
        all_files=False,
        max_bytes=0,
        prune_excluded_dirs=True,
    )
    assert files == []


def test_build_tree_from_scan_prune_dirs(tmp_path: Path):
    _write(tmp_path, "skipdir/inner.py", "print('skip')")
    entries = build_tree_from_scan(
        root=tmp_path,
        exclude_dirs={"skipdir"},
        exclude_files=set(),
        include_patterns=["*.py"],
        max_bytes=0,
        prune_excluded_dirs=True,
    )
    rels = [p.relative_to(tmp_path) for p, _ in entries]
    assert Path("skipdir") not in rels
    assert Path("skipdir/inner.py") not in rels


def test_build_tree_from_scan_no_prune_dirs(tmp_path: Path):
    _write(tmp_path, "skipdir/inner.py", "print('skip')")
    entries = build_tree_from_scan(
        root=tmp_path,
        exclude_dirs={"skipdir"},
        exclude_files=set(),
        include_patterns=["*.py"],
        max_bytes=0,
        prune_excluded_dirs=False,
    )
    rels = [p.relative_to(tmp_path) for p, _ in entries]
    assert Path("skipdir") in rels
    assert Path("skipdir/inner.py") not in rels


def test_build_tree_from_files_includes_parents(tmp_path: Path):
    f = _write(tmp_path, "a/b/c.py", "print('ok')")
    entries = build_tree_from_files(tmp_path, [f])
    rels = {p.relative_to(tmp_path) for p, _ in entries}
    assert Path("a") in rels
    assert Path("a/b") in rels
    assert Path("a/b/c.py") in rels


def test_render_tree_markdown_contains_paths(tmp_path: Path):
    f = _write(tmp_path, "a/b/c.py", "print('ok')")
    md = render_tree_markdown(tmp_path, [f.parent, f])
    lines = md.splitlines()
    assert any(line.endswith("a/b") for line in lines)
    assert any(line.endswith("a/b/c.py") for line in lines)
