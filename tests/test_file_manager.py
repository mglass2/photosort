import datetime
from pathlib import Path

import pytest

import file_manager


def _touch(path: Path) -> Path:
    path.write_bytes(b"fake image data")
    return path


def test_list_unsorted_images_filters_by_extension_and_sorts(tmp_path):
    _touch(tmp_path / "b.jpg")
    _touch(tmp_path / "a.png")
    _touch(tmp_path / "notes.txt")

    result = file_manager.list_unsorted_images(tmp_path)

    assert [p.name for p in result] == ["a.png", "b.jpg"]


def test_list_unsorted_images_excludes_keep_discard_and_duplicates_contents(tmp_path):
    _touch(tmp_path / "a.jpg")
    keep_dir = tmp_path / "keep_2026-03-15"
    keep_dir.mkdir()
    _touch(keep_dir / "already_sorted.jpg")
    discard_dir = tmp_path / "discard"
    discard_dir.mkdir()
    _touch(discard_dir / "already_discarded.jpg")
    duplicates_dir = tmp_path / "duplicates"
    duplicates_dir.mkdir()
    _touch(duplicates_dir / "already_duplicate.jpg")

    result = file_manager.list_unsorted_images(tmp_path)

    assert [p.name for p in result] == ["a.jpg"]


def test_list_unsorted_images_raises_for_missing_folder(tmp_path):
    with pytest.raises(NotADirectoryError):
        file_manager.list_unsorted_images(tmp_path / "does_not_exist")


def test_move_file_moves_into_destination(tmp_path):
    source = _touch(tmp_path / "photo.jpg")
    destination_dir = tmp_path / "keep"

    result = file_manager.move_file(source, destination_dir)

    assert result == destination_dir / "photo.jpg"
    assert result.exists()
    assert not source.exists()


def test_move_file_never_overwrites_existing_file(tmp_path):
    source = _touch(tmp_path / "photo.jpg")
    destination_dir = tmp_path / "keep"
    destination_dir.mkdir()
    existing = _touch(destination_dir / "photo.jpg")
    existing_contents = existing.read_bytes()

    result = file_manager.move_file(source, destination_dir)

    assert result == destination_dir / "photo_1.jpg"
    assert existing.read_bytes() == existing_contents
    assert result.exists()


def test_keep_dirname_includes_the_given_date():
    assert file_manager.keep_dirname(datetime.date(2026, 3, 15)) == "keep_2026-03-15"


def test_ensure_sort_folders_creates_dated_keep_discard_and_duplicates(tmp_path):
    today = datetime.date(2026, 3, 15)

    keep_dir, discard_dir, duplicates_dir = file_manager.ensure_sort_folders(tmp_path, today=today)

    assert keep_dir == tmp_path / "keep_2026-03-15"
    assert discard_dir == tmp_path / "discard"
    assert duplicates_dir == tmp_path / "duplicates"
    assert keep_dir.is_dir()
    assert discard_dir.is_dir()
    assert duplicates_dir.is_dir()


def test_ensure_sort_folders_reuses_same_keep_folder_for_the_same_day(tmp_path):
    today = datetime.date(2026, 3, 15)

    first_keep_dir, _, _ = file_manager.ensure_sort_folders(tmp_path, today=today)
    _touch(first_keep_dir / "already_kept.jpg")
    second_keep_dir, _, _ = file_manager.ensure_sort_folders(tmp_path, today=today)

    assert first_keep_dir == second_keep_dir
    assert (second_keep_dir / "already_kept.jpg").exists()


def test_ensure_sort_folders_uses_a_different_keep_folder_on_a_different_day(tmp_path):
    first_keep_dir, _, _ = file_manager.ensure_sort_folders(tmp_path, today=datetime.date(2026, 3, 15))
    second_keep_dir, _, _ = file_manager.ensure_sort_folders(tmp_path, today=datetime.date(2026, 3, 16))

    assert first_keep_dir != second_keep_dir


KEEP_DIR = Path("/source/keep_2026-03-15")
DISCARD_DIR = Path("/source/discard")
DUPLICATES_DIR = Path("/source/duplicates")


def test_choose_destination_discard_always_goes_to_discard_dir():
    for is_duplicate in (True, False):
        destination = file_manager.choose_destination(
            keep=False,
            is_duplicate=is_duplicate,
            keep_dir=KEEP_DIR,
            discard_dir=DISCARD_DIR,
            duplicates_dir=DUPLICATES_DIR,
        )
        assert destination == DISCARD_DIR


def test_choose_destination_keep_non_duplicate_goes_to_keep_dir():
    destination = file_manager.choose_destination(
        keep=True,
        is_duplicate=False,
        keep_dir=KEEP_DIR,
        discard_dir=DISCARD_DIR,
        duplicates_dir=DUPLICATES_DIR,
    )
    assert destination == KEEP_DIR


def test_choose_destination_keep_duplicate_goes_to_duplicates_dir():
    destination = file_manager.choose_destination(
        keep=True,
        is_duplicate=True,
        keep_dir=KEEP_DIR,
        discard_dir=DISCARD_DIR,
        duplicates_dir=DUPLICATES_DIR,
    )
    assert destination == DUPLICATES_DIR
