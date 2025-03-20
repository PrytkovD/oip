from typing import List

from oip.index import IndexEntryRepository, IndexEntry
from oip.page import PageRepository
from oip.downloader import PageDownloader
from oip.util import url_to_file_path


class Crawler:
    def __init__(
            self,
            page_downloader: PageDownloader,
            page_repository: PageRepository,
            index_entry_repository: IndexEntryRepository
    ):
        self._page_downloader = page_downloader
        self._page_repository = page_repository
        self._index_entry_repository = index_entry_repository

    def crawl(self, urls: List[str], max_pages: int):
        pages = 0
        for index, url in enumerate(urls):
            try:
                print(f'Crawling page {pages + 1}/{max_pages}: {url}')
                page = self._page_downloader.download(url)
                self._page_repository.save(page)
                index_entry = IndexEntry(page_url=page.url, page_file_path=url_to_file_path(page.url))
                self._index_entry_repository.save(index_entry)
                pages += 1
                if pages >= max_pages:
                    break
            except Exception as e:
                print(f'Error: {e}')
