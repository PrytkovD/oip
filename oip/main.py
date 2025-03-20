from typing import List

from oip.crawler import Crawler
from oip.index import IndexEntryRepository, FileIndexEntryRepository
from oip.page import PageRepository, FilePageRepository
from oip.downloader import PageDownloader, RequestsPageDownloader


def get_urls() -> List[str]:
    return [f'https://www.rfc-editor.org/rfc/rfc{x}.html' for x in range(1, 1001)]


def crawl(
        urls: List[str],
        max_pages: int = 100,
        downloader: PageDownloader = RequestsPageDownloader(),
        repository: PageRepository = FilePageRepository(),
        index_entry_repository: IndexEntryRepository = FileIndexEntryRepository()
):
    crawler = Crawler(downloader, repository, index_entry_repository)
    crawler.crawl(urls, max_pages)


def main():
    urls = get_urls()
    crawl(urls)


if __name__ == "__main__":
    main()
