"""Listing unsorted images and moving them. Never deletes anything - the
only filesystem operation here is a move (rename) into keep/ or discard/."""
from __future__ import annotations

import datetime
import shutil
from pathlib import Path
from typing import Callable, Optional

from config import DISCARD_DIRNAME, DUPLICATES_DIRNAME, KEEP_DIR_PREFIX, SUPPORTED_EXTENSIONS


def keep_dirname(today: Optional[datetime.date] = None) -> str:
    """Name of the keep folder for a given day, e.g. 'keep_2026-03-15'.
    Reusing the same day's folder across multiple runs just means mkdir
    sees it already exists."""
    return f"{KEEP_DIR_PREFIX}_{(today or datetime.date.today()).isoformat()}"


def ensure_sort_folders(
    source_dir: Path, today: Optional[datetime.date] = None
) -> tuple[Path, Path, Path]:
    keep_dir = source_dir / keep_dirname(today)
    discard_dir = source_dir / DISCARD_DIRNAME
    duplicates_dir = source_dir / DUPLICATES_DIRNAME
    keep_dir.mkdir(exist_ok=True)
    discard_dir.mkdir(exist_ok=True)
    duplicates_dir.mkdir(exist_ok=True)
    return keep_dir, discard_dir, duplicates_dir


def list_unsorted_images(
    source_dir: Path,
    sort_key: Optional[Callable[[Path], object]] = None,
) -> list[Path]:
    """Images directly inside source_dir. Anything already moved into a
    keep_YYYY-MM-DD/ or discard/ subfolder is a directory entry, not a
    file, so it's excluded by the is_file() check below without needing
    to know those subfolder names."""
    if not source_dir.is_dir():
        raise NotADirectoryError(f"Source folder does not exist: {source_dir}")

    images = [
        path
        for path in source_dir.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    key = sort_key if sort_key is not None else (lambda path: path.name.lower())
    return sorted(images, key=key)


def _non_colliding_destination(destination_dir: Path, filename: str) -> Path:
    candidate = destination_dir / filename
    if not candidate.exists():
        return candidate

    stem, suffix = Path(filename).stem, Path(filename).suffix
    counter = 1
    while True:
        candidate = destination_dir / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def choose_destination(
    keep: bool,
    is_duplicate: bool,
    keep_dir: Path,
    discard_dir: Path,
    duplicates_dir: Path,
) -> Path:
    """Where a sorted photo should go. Duplicates are only ever checked for
    kept photos - a discard is always a discard, duplicate or not."""
    if not keep:
        return discard_dir
    return duplicates_dir if is_duplicate else keep_dir


def move_file(source_path: Path, destination_dir: Path) -> Path:
    """Moves source_path into destination_dir without ever overwriting an
    existing file there. This relocates the file - it still exists on disk,
    just at a new path."""
    destination_dir.mkdir(exist_ok=True)
    destination_path = _non_colliding_destination(destination_dir, source_path.name)
    shutil.move(str(source_path), str(destination_path))
    return destination_path
