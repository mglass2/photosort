from pathlib import Path

import main
from config import DEFAULT_PHOTO_STORAGE_DIR


def test_parse_args_requires_source_dir():
    args = main.parse_args(["/some/folder"])

    assert args.source_dir == Path("/some/folder")


def test_parse_args_defaults_photo_storage_dir_and_duplicate_check():
    args = main.parse_args(["/some/folder"])

    assert args.photo_storage_dir == Path(DEFAULT_PHOTO_STORAGE_DIR)
    assert args.skip_duplicate_check is False


def test_parse_args_allows_overriding_photo_storage_dir_and_skipping_check():
    args = main.parse_args(
        ["/some/folder", "--photo-storage-dir", "/other/pictures", "--skip-duplicate-check"]
    )

    assert args.photo_storage_dir == Path("/other/pictures")
    assert args.skip_duplicate_check is True


def test_main_returns_error_code_for_missing_directory(tmp_path, capsys):
    missing = tmp_path / "nope"

    exit_code = main.main([str(missing)])

    assert exit_code == 1
    assert "not a directory" in capsys.readouterr().err
