from abc import ABC, abstractmethod

from oip.base.page.page import Page
from oip.base.token.token import PageTokens


class Tokenizer(ABC):
    @abstractmethod
    def tokenize(self, page: Page) -> PageTokens:
        return NotImplemented
