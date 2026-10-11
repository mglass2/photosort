"""Tkinter shell: shows one photo at a time and routes Left/Right key
presses to discard/keep moves. Deliberately thin - all real logic lives in
file_manager.py and image_loader.py, which are unit tested; this module is
not practical to exercise headlessly and is excluded from coverage (see
.coveragerc)."""
from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path
from typing import Optional

from PIL import ImageTk

import activity_log
import duplicate_checker
import file_manager
import image_loader
from config import DEFAULT_WINDOW_SIZE


class PhotoSorterApp:
    def __init__(
        self,
        source_dir: Path,
        photo_storage_dir: Optional[Path] = None,
        skip_duplicate_check: bool = False,
    ):
        self.source_dir = source_dir
        self.keep_dir, self.discard_dir, self.duplicates_dir = file_manager.ensure_sort_folders(
            source_dir
        )
        self.duplicate_filenames = self._build_duplicate_index(
            photo_storage_dir, skip_duplicate_check
        )
        self.queue: list[Path] = []
        self.total_count = 0
        self.current_photo = None  # keep a reference so Tk doesn't garbage-collect it

        self.root = tk.Tk()
        self.root.title("Photo Sorter")
        width, height = DEFAULT_WINDOW_SIZE
        self.root.geometry(f"{width}x{height}")

        self.status_label = tk.Label(self.root, text="", anchor="w")
        self.status_label.pack(side="bottom", fill="x")

        self.image_label = tk.Label(self.root, bg="black")
        self.image_label.pack(side="top", fill="both", expand=True)
        self.image_label.bind("<Configure>", lambda event: self._redraw_current())

        self.root.bind("<Right>", lambda event: self._sort_current(keep=True))
        self.root.bind("<Left>", lambda event: self._sort_current(keep=False))
        self.root.bind("<Escape>", lambda event: self.root.destroy())
        self.root.bind("q", lambda event: self.root.destroy())

        # Force geometry to be computed now, otherwise winfo_width/height
        # below would return a stale placeholder size (1px) since the
        # window hasn't been mapped/drawn yet at this point.
        self.root.update_idletasks()
        self._load_queue()

    def run(self) -> None:
        self.root.mainloop()

    @staticmethod
    def _build_duplicate_index(
        photo_storage_dir: Optional[Path], skip_duplicate_check: bool
    ) -> Optional[set[str]]:
        if skip_duplicate_check or photo_storage_dir is None:
            return None
        try:
            return duplicate_checker.build_filename_index(photo_storage_dir)
        except NotADirectoryError as error:
            print(
                f"Warning: {error} - continuing without duplicate checking.",
                file=sys.stderr,
            )
            return None

    def _load_queue(self) -> None:
        self.queue = file_manager.list_unsorted_images(
            self.source_dir, sort_key=image_loader.get_capture_time
        )
        self.total_count = len(self.queue)
        self._redraw_current()

    def _redraw_current(self) -> None:
        if not self.queue:
            self.image_label.configure(image="", text="All done!", fg="white")
            self.current_photo = None
            self.status_label.configure(text="No unsorted photos remain.")
            self.root.title("Photo Sorter")
            return

        path = self.queue[0]
        try:
            image = image_loader.open_image(path)
        except image_loader.UnreadableImageError as error:
            print(f"Skipping unreadable file: {error}")
            self.queue.pop(0)
            self._redraw_current()
            return

        # winfo_width/height return 1 (not 0) before the widget has been
        # drawn, so an `or` fallback on falsiness alone isn't enough.
        width = self.image_label.winfo_width()
        height = self.image_label.winfo_height()
        max_width = width if width > 1 else DEFAULT_WINDOW_SIZE[0]
        max_height = height if height > 1 else DEFAULT_WINDOW_SIZE[1]
        scaled = image_loader.scale_to_fit(image, max_width, max_height)
        self.current_photo = ImageTk.PhotoImage(scaled)
        self.image_label.configure(image=self.current_photo, text="")

        position = self.total_count - len(self.queue) + 1
        self.status_label.configure(text=f"[{position}/{self.total_count}] {path.name}")
        self.root.title(f"Photo Sorter — {path.name}")

    def _sort_current(self, keep: bool) -> None:
        if not self.queue:
            return
        path = self.queue.pop(0)
        is_duplicate = self.duplicate_filenames is not None and duplicate_checker.is_duplicate(
            path.name, self.duplicate_filenames
        )
        destination_dir = file_manager.choose_destination(
            keep, is_duplicate, self.keep_dir, self.discard_dir, self.duplicates_dir
        )
        file_manager.move_file(path, destination_dir)
        activity_log.log_move(path, destination_dir, self.source_dir)
        self._redraw_current()
