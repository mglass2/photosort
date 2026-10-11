from pathlib import Path

import pytest
from PIL import Image

import image_loader


def _make_image(path: Path, size=(20, 10), color="red") -> Path:
    Image.new("RGB", size, color=color).save(path)
    return path


def test_open_image_loads_a_valid_image(tmp_path):
    path = _make_image(tmp_path / "photo.jpg")

    image = image_loader.open_image(path)

    assert image.size == (20, 10)


def test_open_image_raises_for_corrupt_file(tmp_path):
    path = tmp_path / "broken.jpg"
    path.write_bytes(b"not actually an image")

    with pytest.raises(image_loader.UnreadableImageError):
        image_loader.open_image(path)


def test_scale_to_fit_preserves_aspect_ratio():
    image = Image.new("RGB", (200, 100))

    scaled = image_loader.scale_to_fit(image, max_width=100, max_height=100)

    assert scaled.size == (100, 50)


def test_scale_to_fit_never_upscales():
    image = Image.new("RGB", (50, 50))

    scaled = image_loader.scale_to_fit(image, max_width=500, max_height=500)

    assert scaled.size == (50, 50)


def test_scale_to_fit_rejects_non_positive_bounds():
    image = Image.new("RGB", (50, 50))

    with pytest.raises(ValueError):
        image_loader.scale_to_fit(image, max_width=0, max_height=100)


def test_get_capture_time_falls_back_to_mtime_without_exif(tmp_path):
    path = _make_image(tmp_path / "photo.png")

    result = image_loader.get_capture_time(path)

    assert result is not None
