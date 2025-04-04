from typing import List

from oip.base.token.token import Token


class Lemma:
    def __init__(self, lemma: Token, tokens: List[Token]):
        self.lemma = lemma
        self.tokens = set(tokens)

    def __eq__(self, other):
        return self.lemma == other.lemma

    def __lt__(self, other) -> bool:
        return self.lemma < other.lemma

    def __hash__(self):
        return hash(self.lemma)


class PageLemmas:
    def __init__(self, page_url: str, lemmas: List[Lemma]):
        self.page_url = page_url
        self.lemmas = lemmas

    def __eq__(self, other):
        return self.page_url == other.page_url

    def __hash__(self):
        return hash(self.page_url)
