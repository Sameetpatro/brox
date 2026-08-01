"""Filesystem utilities — file and directory helpers."""

from __future__ import annotations

import shutil
from pathlib import Path

from bro.config.defaults import DEFAULT_IGNORE_PATTERNS
from bro.utils.logger import get_logger

logger = get_logger(__name__)


def ensure_dir(path: Path) -> Path:
    """Create directory if it doesn't exist, return the path."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_write(path: Path, content: str, overwrite: bool = False) -> bool:
    """Write content to a file, creating parent directories as needed."""
    if path.exists() and not overwrite:
        logger.debug("Skipping existing file: %s", path)
        return False
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")
    return True


def safe_copy(src: Path, dst: Path, overwrite: bool = False) -> bool:
    """Copy a file, creating parent directories as needed."""
    if dst.exists() and not overwrite:
        return False
    ensure_dir(dst.parent)
    shutil.copy2(src, dst)
    return True


def remove_dir(path: Path) -> bool:
    """Safely remove a directory tree."""
    try:
        if path.exists():
            shutil.rmtree(path)
            return True
    except OSError as e:
        logger.error("Failed to remove directory %s: %s", path, e)
    return False


def scan_directory(
    root: Path,
    ignore_patterns: list[str] | None = None,
    max_depth: int = 5,
) -> dict[str, list[str]]:
    """Scan a directory tree and return structure as {dir: [files]}."""
    patterns = ignore_patterns or DEFAULT_IGNORE_PATTERNS
    structure: dict[str, list[str]] = {}

    def _should_ignore(path: Path) -> bool:
        name = path.name
        for pattern in patterns:
            if pattern.startswith("*"):
                if name.endswith(pattern[1:]):
                    return True
            elif name == pattern:
                return True
        return False

    def _scan(current: Path, depth: int) -> None:
        if depth > max_depth:
            return
        if _should_ignore(current):
            return

        rel = str(current.relative_to(root))
        files: list[str] = []

        try:
            for item in sorted(current.iterdir()):
                if _should_ignore(item):
                    continue
                if item.is_file():
                    files.append(item.name)
                elif item.is_dir():
                    _scan(item, depth + 1)
        except PermissionError:
            pass

        if files or depth == 0:
            structure[rel] = files

    _scan(root, 0)
    return structure


def get_file_size_str(path: Path) -> str:
    """Get human-readable file size."""
    if not path.exists():
        return "0 B"
    size: float = float(path.stat().st_size)
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"
