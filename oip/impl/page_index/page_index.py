from typing import Optional, List

from oip.base.page_index.page_index import PageIndex, PageIndexEntry
from oip.base.util.repository import Repository
from oip.impl.page_index.repository import default_page_index_entry_repository


class SimplePageIndex(PageIndex):
    def __init__(self, repository: Repository[PageIndexEntry]):
        self._repository = repository

    def get_all_page_urls(self) -> List[str]:
        return [index_entry.page_url for index_entry in self._repository.load_all()]

    def get_file_path_by_page_url(self, url: str) -> Optional[str]:
        index_entry = self._repository.load(url)
        if not index_entry:
            return None
        return index_entry.page_file_path

    def add_entry(self, page_url: str, file_path: str):
        index_entry = PageIndexEntry(page_url=page_url, page_file_path=file_path)
        self._repository.save(index_entry)


DEFAULT_PAGE_INDEX = SimplePageIndex(default_page_index_entry_repository())


def default_page_index() -> PageIndex:
    return DEFAULT_PAGE_INDEX
