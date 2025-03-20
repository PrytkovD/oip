from abc import ABC, abstractmethod

import requests

from oip.page import Page


class PageDownloader(ABC):
    @abstractmethod
    def download(self, url: str) -> Page:
        return NotImplemented


class DownloadError(Exception):
    pass


class RequestsPageDownloader(PageDownloader):
    def download(self, url: str) -> Page:
        try:
            response = requests.get(url)
            response.raise_for_status()
            return Page(url=url, content=response.text)
        except Exception as e:
            raise DownloadError from e
