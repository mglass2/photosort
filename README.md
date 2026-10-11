# Photo Sorter

A small desktop utility for quickly triaging a folder of photos (e.g. everything you just copied off your phone) into "keep" and "discard" piles using only the arrow keys. It never deletes anything — it's your fast first pass, and you review/delete manually afterward.

## Features

- Displays photos one at a time, scaled to fit the window
- **Right arrow** to keep, **left arrow** to discard — no mouse needed
- Sorts photos by capture date (EXIF) when available, otherwise filename
- Corrects EXIF rotation so photos display upright
- Supports JPEG, PNG, GIF, BMP, TIFF, WEBP, and HEIC/HEIF (iPhone photos)
- Fully resumable — quit anytime and re-run to pick up where you left off
- **Never deletes files.** "Discard" just moves a photo into a `discard/` subfolder for you to delete by hand later
- Keep folder is named by date (`keep_YYYY-MM-DD/`) and reused automatically if you run the tool more than once on the same day
- Before keeping a photo, checks whether a file with the same name already exists anywhere in your photo storage location (recursively) — if so, it's routed to `duplicates/` instead of `keep_YYYY-MM-DD/`
- Every move (keep, discard, or duplicate) is appended to a single running log, `sort_log.txt`, in the source folder

## Requirements

- Python 3.11+
- [Docker](https://www.docker.com/) (optional, only needed to run the test suite)

## Installation

```bash
cd "/Volumes/Crucial X9 Pro 1TB/Software/photosort"
pip install -r requirements.txt
```

## Usage

```bash
python main.py /path/to/photo/folder
python main.py /path/to/photo/folder --photo-storage-dir /path/to/your/photo/library
python main.py /path/to/photo/folder --skip-duplicate-check
```

| Key | Action |
|---|---|
| → | Keep (move photo into `keep_YYYY-MM-DD/`, or `duplicates/` if it's a duplicate) |
| ← | Discard (move photo into `discard/`) |
| Esc / q | Quit |

Each run creates (or reuses) a `keep_YYYY-MM-DD/` subfolder named for today's date, plus `discard/` and `duplicates/` subfolders, inside the folder you point it at. Running the tool again later the same day reuses that same dated keep folder; running it tomorrow starts a fresh `keep_YYYY-MM-DD/` for that day. Each photo you sort is **moved** (not copied) into one of those subfolders, so the source folder gradually empties out as you go. If a destination filename already exists, the moved file is renamed with a numeric suffix (e.g. `IMG_001_1.jpg`) rather than overwriting it.

### Duplicate checking

When you press → (keep), the tool checks whether a file with the same name already exists anywhere under a photo storage location (searched recursively), before actually moving it:

- **Default location:** `/Volumes/Crucial X9 Pro 1TB/Pictures` (set via `DEFAULT_PHOTO_STORAGE_DIR` in `config.py`)
- **Override it:** `--photo-storage-dir /some/other/path`
- **Skip checking entirely:** `--skip-duplicate-check`
- **If the storage location can't be read** (e.g. an external drive isn't mounted), the tool prints a warning and continues without duplicate checking rather than refusing to start
- A duplicate match is a **matching filename only** for now (not file contents) — this may get stricter later
- Matches go into a `duplicates/` subfolder created inside the source folder, alongside `keep_YYYY-MM-DD/` and `discard/`

Quit at any time with `Esc` or `q` — your progress isn't lost, since already-sorted photos are simply no longer in the source folder. Re-running the tool on the same folder picks up with whatever's left.

### Activity log

Every move is appended to `sort_log.txt` in the source folder — one running log shared across every run of the tool and every date, never truncated or overwritten. Each line has the form:

```
/full/path/to/photo.jpg moved to /full/path/to/destination/folder - 2026-10-11 14:32:10
```

Both the photo's original full path and the destination folder's full path are logged (not just filenames), and the timestamp reflects when the move happened, not when the photo was taken.

## How it works

The project is split into small, single-purpose modules:

```
photosort/
├── main.py            # CLI entry point
├── config.py           # Shared constants (supported extensions, window size, default paths)
├── file_manager.py      # Listing unsorted images, choosing a destination, moving files without overwriting
├── image_loader.py       # Loading, EXIF-orientation correction, and scaling
├── duplicate_checker.py  # Building a filename index and checking for duplicates
├── activity_log.py       # Appending move records to the running sort_log.txt
├── viewer_app.py         # Tkinter UI shell that wires the above together
├── requirements.txt
├── tests/                # Unit tests for the non-GUI modules above
├── Dockerfile.test
└── pyproject.toml
```

`file_manager.py`, `image_loader.py`, `duplicate_checker.py`, and `activity_log.py` contain all the real logic and have no GUI dependency, so they're covered by unit tests. `viewer_app.py` is a thin Tkinter shell that isn't practically testable headlessly, so it's excluded from the coverage gate (see `pyproject.toml`).

## Running tests

Tests run inside Docker:

```bash
docker build -f Dockerfile.test -t photosort-test .
docker run --rm photosort-test
```

This runs the full pytest suite with coverage reporting and fails the build if coverage drops below 80%.

## Non-destructive guarantee

No code path in this project calls a file-deletion API. The only filesystem-mutating operation is a move (`shutil.move`) from the source folder into `keep_YYYY-MM-DD/`, `discard/`, or `duplicates/`. The photo storage location used for duplicate checking is only ever read, never written to. Worst case, a photo ends up in the wrong subfolder — it's never lost, and can be moved back by hand.
