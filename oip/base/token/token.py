from typing import List


class Token:
    def __init__(self, value: str):
        self.value = value


class PageTokens:
    def __init__(self, page_url, tokens: List[Token]):
        self.page_url = page_url
        self.tokens = tokens
