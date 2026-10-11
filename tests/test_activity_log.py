import datetime
from pathlib import Path

import activity_log


def test_log_path_for_is_inside_source_dir(tmp_path):
    assert activity_log.log_path_for(tmp_path) == tmp_path / "sort_log.txt"


def test_format_entry_matches_expected_format(tmp_path):
    source_path = tmp_path / "photo.jpg"
    destination_dir = tmp_path / "keep_2026-10-11"
    timestamp = datetime.datetime(2026, 10, 11, 14, 32, 10)

    entry = activity_log.format_entry(source_path, destination_dir, timestamp)

    assert entry == (
        f"{source_path.resolve()} moved to {destination_dir.resolve()} - 2026-10-11 14:32:10"
    )


def test_append_entry_appends_without_overwriting(tmp_path):
    log_path = tmp_path / "sort_log.txt"

    activity_log.append_entry(log_path, "first entry")
    activity_log.append_entry(log_path, "second entry")

    assert log_path.read_text().splitlines() == ["first entry", "second entry"]


def test_log_move_writes_a_formatted_entry_to_the_source_dirs_log(tmp_path):
    source_path = tmp_path / "photo.jpg"
    destination_dir = tmp_path / "discard"
    timestamp = datetime.datetime(2026, 10, 11, 9, 0, 0)

    activity_log.log_move(source_path, destination_dir, tmp_path, timestamp=timestamp)

    log_path = tmp_path / "sort_log.txt"
    assert log_path.read_text().strip() == (
        f"{source_path.resolve()} moved to {destination_dir.resolve()} - 2026-10-11 09:00:00"
    )


def test_log_move_appends_across_multiple_calls_like_separate_runs(tmp_path):
    destination_dir = tmp_path / "keep_2026-10-11"

    activity_log.log_move(
        tmp_path / "a.jpg", destination_dir, tmp_path, timestamp=datetime.datetime(2026, 10, 11, 9, 0, 0)
    )
    activity_log.log_move(
        tmp_path / "b.jpg", destination_dir, tmp_path, timestamp=datetime.datetime(2026, 10, 12, 9, 0, 0)
    )

    lines = (tmp_path / "sort_log.txt").read_text().splitlines()
    assert len(lines) == 2
    assert "a.jpg" in lines[0]
    assert "b.jpg" in lines[1]
