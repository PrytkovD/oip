from abc import ABC, abstractmethod
from typing import List, Optional

from oip.base.page.page import Page


class Crawler(ABC):
    @abstractmethod
    def crawl(self, urls: List[str], max_pages: Optional[int] = None) -> List[Page]:
        return NotImplemented
