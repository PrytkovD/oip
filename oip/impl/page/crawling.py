from typing import List, Optional

from oip.base.page.crawling import Crawler
from oip.base.page.downloading import PageDownloader
from oip.base.page.page import Page
from oip.impl.page.downloading import default_page_downloader


class SimpleCrawler(Crawler):
    def __init__(self, page_downloader: PageDownloader):
        self._page_downloader = page_downloader

    def crawl(self, urls: List[str], max_pages: Optional[int] = None) -> List[Page]:
        pages = list[Page]()

        max_pages = min(len(urls), max_pages)

        for index, url in enumerate(urls):
            page = self._page_downloader.download(url)

            if page is not None:
                pages.append(page)

            if len(pages) >= max_pages:
                break

        return pages


DEFAULT_CRAWLER = SimpleCrawler(default_page_downloader())


def default_crawler() -> SimpleCrawler:
    return DEFAULT_CRAWLER
