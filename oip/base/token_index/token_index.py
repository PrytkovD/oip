from abc import ABC, abstractmethod
from typing import List

from oip.base.token.token import Token


class TokenIndex(ABC):
    @abstractmethod
    def get_page_urls_by_token(self, token: Token) -> List[str]:
        return NotImplemented

    @abstractmethod
    def add_entry(self, token: Token, page_url: str):
        return NotImplemented


class TokenIndexEntry:
    def __init__(self, lemma: Token, page_urls: List[str]):
        self.lemma = lemma
        self.page_urls = set(page_urls)

    def __eq__(self, other):
        return self.lemma == other.lemma

    def __lt__(self, other) -> bool:
        return self.lemma < other.lemma

    def __hash__(self):
        return hash(self.lemma)
