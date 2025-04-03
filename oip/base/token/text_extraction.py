from abc import ABC, abstractmethod

from oip.base.page.page import Page


class TextExtractor(ABC):
    @abstractmethod
    def extract(self, page: Page) -> str:
        return NotImplemented
