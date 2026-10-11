from pathlib import Path

import pytest

import duplicate_checker


def _touch(path: Path) -> Path:
    path.write_bytes(b"fake image data")
    return path


def test_build_filename_index_finds_files_recursively(tmp_path):
    _touch(tmp_path / "top.jpg")
    nested = tmp_path / "2026" / "vacation"
    nested.mkdir(parents=True)
    _touch(nested / "nested.jpg")

    index = duplicate_checker.build_filename_index(tmp_path)

    assert index == {"top.jpg", "nested.jpg"}


def test_build_filename_index_raises_for_missing_folder(tmp_path):
    with pytest.raises(NotADirectoryError):
        duplicate_checker.build_filename_index(tmp_path / "does_not_exist")


def test_is_duplicate_true_for_matching_filename():
    assert duplicate_checker.is_duplicate("photo.jpg", {"photo.jpg", "other.jpg"})


def test_is_duplicate_false_for_non_matching_filename():
    assert not duplicate_checker.is_duplicate("new.jpg", {"other.jpg"})
