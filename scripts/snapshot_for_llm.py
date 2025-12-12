# scripts/snapshot_for_llm.py

import os
import sys
import zipfile
from datetime import datetime
from pathlib import Path


def should_exclude_dir(dir_name: str) -> bool:
    """Return True if this directory should be skipped entirely."""
    return dir_name in {
        ".git",
        "venv",
        ".venv",
        "__pycache__",
        "logs",
    }


def should_include_file(path: Path) -> bool:
    """Return True if this file should be included in the snapshot."""
    # Exclude memory JSONL logs (these can be large / private)
    if path.parts and "memory" in path.parts and path.suffix == ".jsonl":
        return False

    # Allow these extensions
    exts = {
        ".py",
        ".md",
        ".txt",
        ".json",
        ".toml",
        ".yaml",
        ".yml",
    }

    if path.suffix in exts:
        return True

    # Special-case filenames without useful suffix
    basename = path.name
    if basename == ".gitignore":
        return True
    if basename.startswith("requirements") and basename.endswith(".txt"):
        return True

    return False


def create_snapshot_zip() -> Path:
    """
    Create a ZIP archive of the project suitable for uploading to an LLM.

    - Runs from scripts/, infers project root as parent directory.
    - Excludes venvs, .git, __pycache__, logs, and memory/*.jsonl.
    """
    scripts_dir = Path(__file__).resolve().parent
    project_root = scripts_dir.parent

    timestamp = datetime.utcnow().isoformat(timespec="seconds").replace(":", "-")
    snapshot_name = f"morningstar_snapshot_{timestamp}.zip"
    snapshot_path = project_root / snapshot_name

    print(f"Project root: {project_root}")
    print(f"Creating snapshot: {snapshot_path}")

    with zipfile.ZipFile(snapshot_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(project_root):
            root_path = Path(root)

            # Skip excluded directories
            dirs[:] = [d for d in dirs if not should_exclude_dir(d)]

            for fname in files:
                file_path = root_path / fname

                # Don't include the snapshot itself if re-running
                if file_path == snapshot_path:
                    continue

                if not should_include_file(file_path):
                    continue

                # Store paths relative to project root inside the zip
                arcname = file_path.relative_to(project_root)
                zf.write(file_path, arcname)
                print(f"  + {arcname}")

    return snapshot_path


def main() -> None:
    snapshot_path = create_snapshot_zip()
    print("\nSnapshot created.")
    print(f"Upload this file to your LLM: {snapshot_path}")


if __name__ == "__main__":
    # Allow running directly: python scripts/snapshot_for_llm.py
    sys.exit(main())