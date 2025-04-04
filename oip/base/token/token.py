from typing import List


class Token:
    def __init__(self, value: str):
        self.value = value

    def __eq__(self, other):
        return self.value == other.value

    def __lt__(self, other) -> bool:
        return self.value < other.value

    def __hash__(self):
        return hash(self.value)


class PageTokens:
    def __init__(self, page_url, tokens: List[Token]):
        self.page_url = page_url
        self.tokens = tokens

    def __eq__(self, other):
        return self.page_url == other.page_url

    def __hash__(self):
        return hash(self.page_url)
