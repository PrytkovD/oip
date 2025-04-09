from typing import Optional

import requests

from oip.base.page.downloading import PageDownloader
from oip.base.page.page import Page
from oip.impl.util.util import clean


class RequestsPageDownloader(PageDownloader):
    def download(self, url: str) -> Optional[Page]:
        try:
            response = requests.get(url)
            response.raise_for_status()
            return Page(url=url, content=clean(response.text))
        except Exception as e:
            return None


DEFAULT_PAGE_DOWNLOADER = RequestsPageDownloader()


def default_page_downloader() -> PageDownloader:
    return DEFAULT_PAGE_DOWNLOADER
