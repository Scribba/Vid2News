from pathlib import Path
from typing import Optional


def get_repo_root(start_path: Optional[Path] = None) -> Path:
    start_path = start_path or Path.cwd()
    start_path = start_path.resolve()
    if start_path.is_file():
        start_path = start_path.parent

    for parent in [start_path] + list(start_path.parents):
        if (parent / "configs").is_dir():
            return parent

    return start_path
