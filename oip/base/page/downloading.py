from abc import ABC, abstractmethod
from typing import Optional

from oip.base.page.page import Page


class PageDownloader(ABC):
    @abstractmethod
    def download(self, url: str) -> Optional[Page]:
        return NotImplemented
