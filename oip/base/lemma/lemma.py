from typing import List

from oip.base.token.token import Token


class Lemma:
    def __init__(self, lemma: Token, tokens: List[Token]):
        self.lemma = lemma
        self.tokens = set(tokens)


class PageLemmas:
    def __init__(self, page_url: str, lemmas: List[Lemma]):
        self.page_url = page_url
        self.lemmas = lemmas
