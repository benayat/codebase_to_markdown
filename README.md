# project-to-markdown

Export a Python project into a single Markdown file.

## Features
- Recursively scans a project directory
- Includes code and markdown files (configurable)
- Outputs a single, well-structured Markdown file
- Supports file/directory exclusion and size limits

## Installation

```sh
pip install project-to-markdown
```

Or, for local development:

```sh
pip install .
```

## Usage

From the command line:

```sh
project-to-markdown --root path/to/project --output export.md --include-exts .py,.md --exclude-dirs .venv,.git --title "My Project"
```

### Options
- `--root`         Root directory of the project (default: current directory)
- `--output`       Output Markdown file (default: project_export.md)
- `--title`        Title for the Markdown document
- `--include-exts` Comma-separated list of file extensions to include (default: .py,.md)
- `--exclude-dirs` Comma-separated list of directory names to exclude
- `--exclude-files`Comma-separated list of file names to exclude
- `--use-gitignore`Respect .gitignore files in the export
- `--all-files`    Include all files, not just tracked files
- `--max-bytes`    Maximum size of files to include (default: 10,000,000)

## Example

```sh
project-to-markdown --root my_project --output my_project.md --title "My Project"
```

## License

MIT License

---

Created by Your Name. Contributions welcome!

