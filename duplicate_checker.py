"""Checking whether a kept photo already exists in the user's photo
storage location. A file counts as a duplicate if a file with the same
name exists anywhere in that location or its subfolders (recursively)."""
from __future__ import annotations

from pathlib import Path


def build_filename_index(storage_dir: Path) -> set[str]:
    """All filenames found anywhere under storage_dir, built once so each
    later duplicate check is an O(1) lookup instead of a fresh recursive
    walk."""
    if not storage_dir.is_dir():
        raise NotADirectoryError(f"Photo storage folder does not exist: {storage_dir}")
    return {path.name for path in storage_dir.rglob("*") if path.is_file()}


def is_duplicate(filename: str, filename_index: set[str]) -> bool:
    return filename in filename_index
