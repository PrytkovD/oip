import csv
import os
import re
from collections import deque
from typing import List, Dict, Any, Iterator

from database.record import Record


class FilePageStorage:
    def __init__(self, table: 'Table', page_size: int, storage_dir: str, cache_size: int = 3) -> None:
        self._table = table
        self._page_size = page_size
        self._storage_dir = storage_dir
        self._cache_size = cache_size
        os.makedirs(self._storage_dir, exist_ok=True)

        self._page_numbers: List[int] = []

        file_name_pattern = re.compile(f'^{self._table.name}_([0-9]+)\\.csv$')
        for file_name in sorted(os.listdir(self._storage_dir)):
            match = file_name_pattern.match(file_name)
            if match:
                page_number = int(match.group(1))
                self._page_numbers.append(page_number)

        self._cache_queue = deque[int](maxlen=self._cache_size)
        self._pages: Dict[int, Page] = {}
        self._cache_queue: deque[int] = deque(maxlen=self._cache_size)
        self._pages: Dict[int, Page] = {}

    def _get_page(self, page_number: int) -> 'Page':
        if page_number not in self._page_numbers:
            self._page_numbers.append(page_number)

        if page_number not in self._cache_queue:
            if len(self._cache_queue) >= self._cache_size:
                oldest_page_number = self._cache_queue.popleft()
                oldest_page = self._pages.pop(oldest_page_number, None)
                if oldest_page:
                    oldest_page.dump()
            self._cache_queue.append(page_number)

        page = self._pages.get(page_number)

        if page is None:
            page = Page(self._table, page_number, self._page_size, self._storage_dir)
            page.load()
            self._pages[page_number] = page

        return page

    def insert(self, record_data: Dict[str, Any]):
        count = sum(
            self._count_on_disk(page_number) if page_number not in self._cache_queue else len(self._pages[page_number])
            for page_number in set(self._page_numbers)
        )
        page_number = (count // self._page_size) + 1
        page = self._get_page(page_number)
        while page.is_full:
            page_number += 1
            page = self._get_page(page_number)
        page.append(record_data)

    def __iter__(self) -> Iterator[Record]:
        for page_number in sorted(self._page_numbers):
            page = self._get_page(page_number)
            yield from page
        self.dump_all()

    def _count_on_disk(self, page_number: int) -> int:
        path = self._get_page_file_path(page_number)
        try:
            with open(path, 'r') as file:
                reader = csv.reader(file)
                return sum(1 for _ in reader) - 1
        except Exception:
            return 0

    def dump_all(self):
        for page_number in list(self._cache_queue):
            page = self._pages.get(page_number)
            if page:
                page.dump()

    def _get_page_file_path(self, page_number: int) -> str:
        return os.path.join(self._storage_dir, f'{self._table.name}_{page_number}.csv')


from database.table import Table
from database.page import Page
