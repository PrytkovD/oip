from typing import Optional, List

from database.select import select_from
from oip.base.page_index.page_index import PageIndex, PageIndexEntry
from oip.base.util.repository import Repository
from oip.impl.util.tables import PAGE


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


class DatabasePageIndex(PageIndex):
    def get_all_page_urls(self) -> List[str]:
        records = select_from(PAGE).columns(PAGE.url).execute()

        return list(set(record[PAGE.url] for record in records))

    def get_file_path_by_page_url(self, url: str) -> Optional[str]:
        return NotImplemented

    def add_entry(self, page_url: str, file_path: str):
        pass


DEFAULT_PAGE_INDEX = DatabasePageIndex()


def default_page_index() -> PageIndex:
    return DEFAULT_PAGE_INDEX
