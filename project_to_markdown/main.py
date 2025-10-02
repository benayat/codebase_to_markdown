# main.py for project_to_markdown package

# The following code is moved from __main__.py

import argparse
import fnmatch
import io
from pathlib import Path
from typing import List, Tuple


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a Python project into a single Markdown file."
    )
    parser.add_argument(
        "-r",
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Root directory of the Python project to export",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("project_export.md"),
        help="Output Markdown file",
    )
    parser.add_argument(
        "-t",
        "--title",
        type=str,
        default="Project Documentation",
        help="Title for the Markdown document",
    )
    parser.add_argument(
        "--include-exts",
        type=str,
        default=".py,.md",
        help="Comma-separated list of file extensions to include",
    )
    parser.add_argument(
        "--exclude-dirs",
        type=str,
        default="",
        help="Comma-separated list of directory names to exclude",
    )
    parser.add_argument(
        "--exclude-files",
        type=str,
        default="",
        help="Comma-separated list of file names to exclude",
    )
    parser.add_argument(
        "--use-gitignore",
        action="store_true",
        help="Respect .gitignore files in the export",
    )
    parser.add_argument(
        "--all-files",
        action="store_true",
        help="Include all files in the export, not just tracked files",
    )
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=10_000_000,
        help="Maximum size of files to include (in bytes)",
    )
    return parser.parse_args()


def build_tree(
    root: Path,
    files_only: bool = False,
    exclude_dirs: set = None,
    exclude_files: set = None,
    include_exts: set = None,
    max_bytes: int = None
) -> List[Tuple[Path, bool]]:
    if exclude_dirs is None:
        exclude_dirs = set()
    if exclude_files is None:
        exclude_files = set()
    if include_exts is None:
        include_exts = set()

    structure = []
    for path in sorted(root.rglob("*")):
        if path.is_dir():
            # Exclude directories that match exclusion patterns
            if any(
                fnmatch.fnmatch(path.name, pattern)
                for pattern in exclude_dirs
            ):
                continue
            structure.append((path, True))
        elif not files_only:
            # Check if file is in an excluded directory
            if any(
                any(fnmatch.fnmatch(parent.name, pattern) for pattern in exclude_dirs)
                for parent in path.parents
            ):
                continue

            # Check if file matches excluded file patterns
            if exclude_files and any(fnmatch.fnmatch(path.name, pattern) for pattern in exclude_files):
                continue

            # Check file extension if include_exts is specified
            if include_exts and not any(fnmatch.fnmatch(path.suffix, pattern) for pattern in include_exts):
                continue

            # Check file size if max_bytes is specified
            if max_bytes and path.stat().st_size > max_bytes:
                continue

            structure.append((path, False))
    return structure


def render_tree_markdown(root: Path, structure_paths: List[Path]) -> str:
    tree_md = []
    for path in structure_paths:
        rel_path = path.relative_to(root)
        tree_md.append(f"- {'📁' if path.is_dir() else '📄'} {rel_path}")
    return "\n".join(tree_md)


def collect_files(
    root: Path,
    include_exts: set,
    exclude_dirs: set,
    exclude_files: set,
    use_gitignore: bool,
    all_files: bool,
    max_bytes: int,
) -> List[Path]:
    files = []
    for path in sorted(root.rglob("*")):
        if path.is_dir():
            continue

        # Check if file is in an excluded directory
        if any(
            any(fnmatch.fnmatch(parent.name, pattern) for pattern in exclude_dirs)
            for parent in path.parents
        ):
            continue

        if any(fnmatch.fnmatch(path.name, pattern) for pattern in exclude_files):
            continue
        if not any(fnmatch.fnmatch(path.suffix, pattern) for pattern in include_exts):
            continue
        if path.stat().st_size > max_bytes:
            continue
        files.append(path)
    return files


def write_markdown(
    root: Path, files: List[Path], tree_md: str, out_path: Path, title: str
) -> None:
    with io.open(out_path, "w", encoding="utf-8") as md_file:
        # Write the document title
        md_file.write(f"# {title}\n\n")

        # Write the tree structure
        md_file.write("## Project Structure\n")
        md_file.write(tree_md)
        md_file.write("\n\n")

        # Write each file's content
        for file_path in files:
            rel_path = file_path.relative_to(root)
            md_file.write(f"## {rel_path}\n")
            with io.open(file_path, "r", encoding="utf-8") as src_file:
                content = src_file.read()
                md_file.write("```\n")
                md_file.write(content)
                md_file.write("\n```\n\n")


def main():
    args = parse_args()

    root: Path = args.root.resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"[error] Root directory not found: {root}")

    include_exts = {e.strip().lower() for e in args.include_exts.split(",") if e.strip()}
    exclude_dirs = {d.strip() for d in args.exclude_dirs.split(",") if d.strip()}
    exclude_files = {f.strip() for f in args.exclude_files.split(",") if f.strip()}

    # Build a structure list for the tree (dirs + files) to display at top
    structure_entries = build_tree(
        root,
        files_only=False,
        exclude_dirs=exclude_dirs,
        exclude_files=exclude_files,
        include_exts=include_exts,
        max_bytes=int(args.max_bytes)
    )
    structure_paths = [p for p, _is_dir in structure_entries]
    tree_md = render_tree_markdown(root, structure_paths)

    # Now collect *actual* files to export (respects filters)
    files = collect_files(
        root=root,
        include_exts=include_exts,
        exclude_dirs=exclude_dirs,
        exclude_files=exclude_files,
        use_gitignore=args.use_gitignore,
        all_files=bool(args.all_files),
        max_bytes=int(args.max_bytes),
    )

    # Write Markdown
    out_path: Path = args.output if args.output.is_absolute() else Path.cwd() / args.output
    write_markdown(root, files, tree_md, out_path, title=args.title)

    print(f"[ok] Wrote {len(files)} files into: {out_path}")


if __name__ == "__main__":
    main()
