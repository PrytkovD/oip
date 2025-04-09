from abc import ABC, abstractmethod
from typing import Optional, List


class PageIndex(ABC):
    @abstractmethod
    def get_all_page_urls(self) -> List[str]:
        return NotImplemented

    @abstractmethod
    def get_file_path_by_page_url(self, url: str) -> Optional[str]:
        return NotImplemented

    @abstractmethod
    def add_entry(self, page_url: str, file_path: str):
        return NotImplemented


class PageIndexEntry:
    def __init__(self, page_file_path: str, page_url: str):
        self.page_file_path = page_file_path
        self.page_url = page_url

    def __eq__(self, other):
        return self.page_file_path == other.page_file_path

    def __hash__(self):
        return hash(self.page_file_path)

    def __lt__(self, other) -> bool:
        return self.page_file_path < other.page_file_path
