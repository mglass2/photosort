"""CLI entry point for the photo sorter."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

from config import DEFAULT_PHOTO_STORAGE_DIR


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Cycle through photos in a folder, sorting them into 'keep' and "
            "'discard' subfolders using the Right/Left arrow keys. Never "
            "deletes anything."
        )
    )
    parser.add_argument("source_dir", type=Path, help="Folder containing photos to sort")
    parser.add_argument(
        "--photo-storage-dir",
        type=Path,
        default=Path(DEFAULT_PHOTO_STORAGE_DIR),
        help=(
            "Folder (searched recursively) to check for existing photos with "
            f"the same filename before keeping a photo. Default: {DEFAULT_PHOTO_STORAGE_DIR}"
        ),
    )
    parser.add_argument(
        "--skip-duplicate-check",
        action="store_true",
        help="Don't check kept photos against the photo storage folder at all.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    source_dir = args.source_dir.expanduser().resolve()

    if not source_dir.is_dir():
        print(f"Error: '{source_dir}' is not a directory.", file=sys.stderr)
        return 1

    from viewer_app import PhotoSorterApp  # deferred: avoids requiring a display for --help

    PhotoSorterApp(
        source_dir,
        photo_storage_dir=args.photo_storage_dir.expanduser().resolve(),
        skip_duplicate_check=args.skip_duplicate_check,
    ).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
