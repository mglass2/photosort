"""Loading, EXIF-orientation correction, and scaling of a single image.
Pure logic with no GUI dependency, so it's unit-testable headlessly."""
from __future__ import annotations

import datetime
from pathlib import Path

from PIL import ExifTags, Image, UnidentifiedImageError

try:
    import pillow_heif

    pillow_heif.register_heif_opener()
except ImportError:
    pillow_heif = None

_ORIENTATION_TAG = next(
    (tag for tag, name in ExifTags.TAGS.items() if name == "Orientation"), None
)
_DATETIME_ORIGINAL_TAG = next(
    (tag for tag, name in ExifTags.TAGS.items() if name == "DateTimeOriginal"), None
)
_EXIF_ROTATION_DEGREES = {3: 180, 6: 270, 8: 90}


class UnreadableImageError(Exception):
    """Raised when a file can't be opened as an image."""


def open_image(path: Path) -> Image.Image:
    try:
        image = Image.open(path)
        image.load()
    except (UnidentifiedImageError, OSError) as error:
        raise UnreadableImageError(f"Cannot open image '{path.name}': {error}") from error
    return _apply_exif_orientation(image)


def _apply_exif_orientation(image: Image.Image) -> Image.Image:
    if _ORIENTATION_TAG is None:
        return image
    try:
        orientation = image.getexif().get(_ORIENTATION_TAG)
    except Exception:
        return image
    rotation = _EXIF_ROTATION_DEGREES.get(orientation)
    return image.rotate(rotation, expand=True) if rotation else image


def scale_to_fit(image: Image.Image, max_width: int, max_height: int) -> Image.Image:
    if max_width <= 0 or max_height <= 0:
        raise ValueError("max_width and max_height must be positive")
    scale = min(max_width / image.width, max_height / image.height, 1.0)
    new_size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
    return image.resize(new_size, Image.LANCZOS)


def get_capture_time(path: Path) -> datetime.datetime:
    """EXIF capture time when available, otherwise filesystem mtime."""
    try:
        if _DATETIME_ORIGINAL_TAG is not None:
            raw = Image.open(path).getexif().get(_DATETIME_ORIGINAL_TAG)
            if raw:
                return datetime.datetime.strptime(raw, "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass
    return datetime.datetime.fromtimestamp(path.stat().st_mtime)
