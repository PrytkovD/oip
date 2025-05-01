import shutil
import threading
from typing import Optional, Iterable


class Progress:
    def __init__(
            self,
            iterable: Optional[Iterable] = None,
            description: str = '',
            max_value: Optional[int] = None
    ):
        if iterable is None and max_value is None:
            raise ValueError("max_value must be specified when iterable is None")

        self.iterable = iterable
        self.description = description
        self.max_value = max_value if max_value is not None else len(iterable) if iterable is not None else 0
        self.count = 0
        self.finalized = False
        self.lock = threading.Lock()
        self.iterator: Optional[Iterable] = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._finalize_progress()

    def __iter__(self):
        if self.iterable is not None:
            self.iterator = iter(self.iterable)
        else:
            self.iterator = iter(())
        return self

    def __next__(self):
        if self.iterator is None:
            raise StopIteration

        try:
            value = next(self.iterator)
        except StopIteration as e:
            with self.lock:
                self._finalize_progress()
            raise e

        with self.lock:
            if not self.finalized:
                self.count += 1
                self._update_progress()
        return value

    def increment(self, delta: int = 1):
        with self.lock:
            if self.finalized:
                return
            self.count = min(self.count + delta, self.max_value)
            self._update_progress()

    def _update_progress(self):
        if self.finalized:
            return

        progress_percent = min(int((self.count / self.max_value) * 100), 100)
        terminal_width = shutil.get_terminal_size(fallback=(80, 24)).columns
        max_width = 80
        width = min(terminal_width, max_width)

        description_width = 0
        if self.description:
            description_width = len(self.description) + 8 - len(self.description) % 8 + 1
        progress_width = 4 + 1
        progress_bar_width = width - description_width - progress_width - 2

        filled_symbol = '█'
        unfilled_symbol = ' '

        filled_width = int(progress_percent * progress_bar_width / 100)
        unfilled_width = progress_bar_width - filled_width

        print(
            f"{self.description:<{description_width}}|{filled_symbol * filled_width}{unfilled_symbol * unfilled_width}| {progress_percent}%",
            end="\r"
        )

        if progress_percent >= 100:
            self._finalize_progress()

    def _finalize_progress(self):
        if self.finalized:
            return

        terminal_width = shutil.get_terminal_size(fallback=(80, 24)).columns
        max_width = 80
        width = min(terminal_width, max_width)

        description_width = 0
        if self.description:
            description_width = len(self.description) + 8 - len(self.description) % 8 + 1

        if self.description:
            print(f"{self.description:<{description_width}}{' ':<{width - description_width}}")
        else:
            print(" " * width, end="\r")

        self.finalized = True


def progress(
        iterable: Optional[Iterable] = None,
        description: str = '',
        max_value: Optional[int] = None
) -> Progress:
    return Progress(iterable, description, max_value)