"""A single running log of every move the sorter makes, kept inside the
photo source folder across all runs and all dates."""
from __future__ import annotations

import datetime
from pathlib import Path
from typing import Optional

from config import LOG_FILENAME


def log_path_for(source_dir: Path) -> Path:
    return source_dir / LOG_FILENAME


def format_entry(
    source_path: Path, destination_dir: Path, timestamp: datetime.datetime
) -> str:
    filename = source_path.resolve()
    folder = destination_dir.resolve()
    when = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    return f"{filename} moved to {folder} - {when}"


def append_entry(log_path: Path, entry: str) -> None:
    with log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(entry + "\n")


def log_move(
    source_path: Path,
    destination_dir: Path,
    source_dir: Path,
    timestamp: Optional[datetime.datetime] = None,
) -> None:
    entry = format_entry(source_path, destination_dir, timestamp or datetime.datetime.now())
    append_entry(log_path_for(source_dir), entry)
